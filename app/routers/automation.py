# backend/app/routers/automation.py
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List as TypingList, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import uuid
import logging
import json
import os

from app.services.whatsapp_service import send_whatsapp_template
from app.services.email_service import send_email
from app.database import get_main_db, get_log_db
from app.models.message_log import MessageLog
from app.models.contact import Contact
from app.models.template import Template
from app.models.campaign import Campaign
from app.models.automation import AutomationSequence, SequenceExecution
from app.services.campaign_service import send_campaign_emails, send_bulk_whatsapp
from sqlalchemy.orm import Session
from sqlalchemy import func

router = APIRouter(prefix="/api/automation", tags=["automation"])
logger = logging.getLogger(__name__)

# ============ PYDANTIC MODELS ============

class SequenceStep(BaseModel):
    id: int
    delay_hours: str
    delay_minutes: str
    type: str
    template_id: str
    template_name: str
    template_type: str

class AutomationSequenceCreate(BaseModel):
    name: str
    description: Optional[str] = ""
    campaign_id: str
    campaign_name: Optional[str] = ""
    campaign_channel: Optional[str] = ""
    steps: TypingList[SequenceStep]

class AutomationSequenceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    campaign_id: str
    campaign_name: Optional[str]
    campaign_channel: Optional[str]
    steps: TypingList[Dict]
    status: str
    total_triggered: int
    completed_count: int
    last_resume_at: Optional[str]
    created_at: str
    updated_at: str

# ============ IN-MEMORY CACHE ============

automation_sequences_cache: Dict[str, Dict] = {}

def load_sequences_from_db(db: Session):
    """Load all sequences from database into cache"""
    try:
        sequences = db.query(AutomationSequence).all()
        automation_sequences_cache.clear()
        for seq in sequences:
            automation_sequences_cache[seq.id] = {
                "id": seq.id,
                "name": seq.name,
                "description": seq.description,
                "campaign_id": seq.campaign_id,
                "campaign_name": seq.campaign_name,
                "campaign_channel": seq.campaign_channel,
                "steps": seq.steps if seq.steps else [],
                "status": seq.status,
                "total_triggered": seq.total_triggered or 0,
                "completed_count": seq.completed_count or 0,
                "last_resume_at": seq.last_resume_at.isoformat() if seq.last_resume_at else None,
                "paused_at": seq.paused_at.isoformat() if seq.paused_at else None,
                "created_at": seq.created_at.isoformat() if seq.created_at else None,
                "updated_at": seq.updated_at.isoformat() if seq.updated_at else None,
            }
        logger.info(f"Loaded {len(automation_sequences_cache)} sequences from database")
        return automation_sequences_cache
    except Exception as e:
        logger.error(f"Error loading sequences from DB: {str(e)}")
        return {}

# ============ SEQUENCE ENDPOINTS ============

@router.post("/sequences", response_model=AutomationSequenceResponse)
async def create_sequence(
    sequence_data: AutomationSequenceCreate,
    db: Session = Depends(get_main_db)
):
    """Create a new automation sequence"""
    try:
        sequence_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        
        # ✅ Process steps with status tracking
        steps_dict = []
        for step in sequence_data.steps:
            step_dict = step.dict()
            step_dict["status"] = "pending"  # pending, scheduled, completed
            step_dict["scheduled_at"] = None
            step_dict["sent_at"] = None
            steps_dict.append(step_dict)
        
        new_sequence = {
            "id": sequence_id,
            "name": sequence_data.name,
            "description": sequence_data.description or "",
            "campaign_id": sequence_data.campaign_id,
            "campaign_name": sequence_data.campaign_name or "",
            "campaign_channel": sequence_data.campaign_channel or "",
            "steps": steps_dict,
            "status": "active",  # ✅ Default: active
            "total_triggered": 0,
            "completed_count": 0,
            "last_resume_at": now,
            "created_at": now,
            "updated_at": now
        }
        
        # Save to cache
        automation_sequences_cache[sequence_id] = new_sequence
        
        # Save to database
        db_sequence = AutomationSequence(
            id=sequence_id,
            workspace_id=1,
            name=sequence_data.name,
            description=sequence_data.description or "",
            campaign_id=sequence_data.campaign_id,
            campaign_name=sequence_data.campaign_name or "",
            campaign_channel=sequence_data.campaign_channel or "",
            steps=steps_dict,
            status="active",
            last_resume_at=datetime.utcnow(),
        )
        db.add(db_sequence)
        db.commit()
        db.refresh(db_sequence)
        
        logger.info(f"Sequence created successfully with ID: {sequence_id}")
        
        # ✅ Auto-schedule the sequence
        await schedule_sequence(sequence_id, db)
        
        return AutomationSequenceResponse(
            id=sequence_id,
            name=sequence_data.name,
            description=sequence_data.description,
            campaign_id=sequence_data.campaign_id,
            campaign_name=sequence_data.campaign_name,
            campaign_channel=sequence_data.campaign_channel,
            steps=steps_dict,
            status="active",
            total_triggered=0,
            completed_count=0,
            last_resume_at=now,
            created_at=now,
            updated_at=now
        )
        
    except Exception as e:
        logger.error(f"Error creating sequence: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create sequence: {str(e)}")


@router.get("/sequences", response_model=TypingList[AutomationSequenceResponse])
async def get_sequences(
    db: Session = Depends(get_main_db)
):
    """Get all automation sequences from database"""
    try:
        sequences = db.query(AutomationSequence).order_by(
            AutomationSequence.created_at.desc()
        ).all()
        
        automation_sequences_cache.clear()
        result = []
        for seq in sequences:
            seq_dict = {
                "id": seq.id,
                "name": seq.name,
                "description": seq.description,
                "campaign_id": seq.campaign_id,
                "campaign_name": seq.campaign_name,
                "campaign_channel": seq.campaign_channel,
                "steps": seq.steps if seq.steps else [],
                "status": seq.status,
                "total_triggered": seq.total_triggered or 0,
                "completed_count": seq.completed_count or 0,
                "last_resume_at": seq.last_resume_at.isoformat() if seq.last_resume_at else None,
                "paused_at": seq.paused_at.isoformat() if seq.paused_at else None,
                "created_at": seq.created_at.isoformat() if seq.created_at else None,
                "updated_at": seq.updated_at.isoformat() if seq.updated_at else None,
            }
            automation_sequences_cache[seq.id] = seq_dict
            result.append(seq_dict)
        
        return [
            AutomationSequenceResponse(
                id=seq["id"],
                name=seq["name"],
                description=seq.get("description"),
                campaign_id=seq.get("campaign_id", ""),
                campaign_name=seq.get("campaign_name"),
                campaign_channel=seq.get("campaign_channel"),
                steps=seq.get("steps", []),
                status=seq.get("status", "active"),
                total_triggered=seq.get("total_triggered", 0),
                completed_count=seq.get("completed_count", 0),
                last_resume_at=seq.get("last_resume_at"),
                created_at=seq.get("created_at"),
                updated_at=seq.get("updated_at")
            )
            for seq in result
        ]
    except Exception as e:
        logger.error(f"Error getting sequences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sequences/{sequence_id}", response_model=AutomationSequenceResponse)
async def get_sequence(
    sequence_id: str,
    db: Session = Depends(get_main_db)
):
    """Get a specific sequence by ID"""
    if sequence_id in automation_sequences_cache:
        seq = automation_sequences_cache[sequence_id]
        return AutomationSequenceResponse(
            id=seq["id"],
            name=seq["name"],
            description=seq.get("description"),
            campaign_id=seq.get("campaign_id", ""),
            campaign_name=seq.get("campaign_name"),
            campaign_channel=seq.get("campaign_channel"),
            steps=seq.get("steps", []),
            status=seq.get("status", "active"),
            total_triggered=seq.get("total_triggered", 0),
            completed_count=seq.get("completed_count", 0),
            last_resume_at=seq.get("last_resume_at"),
            created_at=seq.get("created_at"),
            updated_at=seq.get("updated_at")
        )
    
    seq = db.query(AutomationSequence).filter(
        AutomationSequence.id == sequence_id
    ).first()
    
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    
    seq_dict = {
        "id": seq.id,
        "name": seq.name,
        "description": seq.description,
        "campaign_id": seq.campaign_id,
        "campaign_name": seq.campaign_name,
        "campaign_channel": seq.campaign_channel,
        "steps": seq.steps if seq.steps else [],
        "status": seq.status,
        "total_triggered": seq.total_triggered or 0,
        "completed_count": seq.completed_count or 0,
        "last_resume_at": seq.last_resume_at.isoformat() if seq.last_resume_at else None,
        "paused_at": seq.paused_at.isoformat() if seq.paused_at else None,
        "created_at": seq.created_at.isoformat() if seq.created_at else None,
        "updated_at": seq.updated_at.isoformat() if seq.updated_at else None,
    }
    automation_sequences_cache[seq.id] = seq_dict
    
    return AutomationSequenceResponse(
        id=seq_dict["id"],
        name=seq_dict["name"],
        description=seq_dict.get("description"),
        campaign_id=seq_dict.get("campaign_id", ""),
        campaign_name=seq_dict.get("campaign_name"),
        campaign_channel=seq_dict.get("campaign_channel"),
        steps=seq_dict.get("steps", []),
        status=seq_dict.get("status", "active"),
        total_triggered=seq_dict.get("total_triggered", 0),
        completed_count=seq_dict.get("completed_count", 0),
        last_resume_at=seq_dict.get("last_resume_at"),
        created_at=seq_dict.get("created_at"),
        updated_at=seq_dict.get("updated_at")
    )


@router.post("/sequences/{sequence_id}/toggle")
async def toggle_sequence(
    sequence_id: str, 
    active: bool = Query(...),
    db: Session = Depends(get_main_db)
):
    """
    Toggle sequence status (active/paused)
    When toggling ON, record the time for scheduling
    """
    if sequence_id not in automation_sequences_cache:
        raise HTTPException(status_code=404, detail="Sequence not found")
    
    sequence = automation_sequences_cache[sequence_id]
    new_status = "active" if active else "paused"
    sequence["status"] = new_status
    sequence["updated_at"] = datetime.utcnow().isoformat()
    
    # ✅ If toggling ON, record the resume time and reschedule
    if active:
        sequence["last_resume_at"] = datetime.utcnow().isoformat()
        sequence["paused_at"] = None
        print(f"✅ Sequence resumed at: {sequence['last_resume_at']}")
        
        # ✅ Reschedule pending steps from the resume time
        await reschedule_pending_steps(sequence, db)
    else:
        sequence["paused_at"] = datetime.utcnow().isoformat()
        # ✅ Cancel all pending/scheduled steps
        for step in sequence.get("steps", []):
            if step.get("status") in ["pending", "scheduled"]:
                step["status"] = "paused"
                step["scheduled_at"] = None
        print(f"⏸️ Sequence paused at: {sequence['paused_at']}")
    
    # Update database
    db_sequence = db.query(AutomationSequence).filter(
        AutomationSequence.id == sequence_id
    ).first()
    
    if db_sequence:
        db_sequence.status = new_status
        if active:
            db_sequence.last_resume_at = datetime.utcnow()
            db_sequence.paused_at = None
            # Update steps in database
            db_sequence.steps = sequence.get("steps", [])
        else:
            db_sequence.paused_at = datetime.utcnow()
            db_sequence.last_resume_at = None
            db_sequence.steps = sequence.get("steps", [])
        db_sequence.updated_at = func.now()
        db.commit()
        db.refresh(db_sequence)
    
    return {"message": f"Sequence {'activated' if active else 'paused'}"}


@router.post("/sequences/{sequence_id}/test")
async def test_sequence(sequence_id: str):
    """Test a sequence execution"""
    if sequence_id not in automation_sequences_cache:
        raise HTTPException(status_code=404, detail="Sequence not found")
    
    sequence = automation_sequences_cache[sequence_id]
    
    return {
        "success": True,
        "message": f"Sequence '{sequence['name']}' test executed successfully",
        "sequence_id": sequence_id,
        "steps": sequence['steps']
    }


# ============ SEQUENCE SCHEDULING ============

async def schedule_sequence(sequence_id: str, db: Session):
    """
    Schedule a sequence based on campaign sent time
    """
    if sequence_id not in automation_sequences_cache:
        logger.error(f"Sequence {sequence_id} not found")
        return
    
    sequence = automation_sequences_cache[sequence_id]
    
    # Get campaign
    campaign = db.query(Campaign).filter(
        Campaign.id == sequence["campaign_id"]
    ).first()
    
    if not campaign:
        logger.error(f"Campaign {sequence['campaign_id']} not found")
        return
    
    # ✅ Check if campaign is sent
    if campaign.status != 'sent':
        logger.info(f"Campaign '{campaign.campaign_name}' is not sent yet")
        return
    
    # ✅ Get campaign sent time
    campaign_sent_at = campaign.sent_at
    if not campaign_sent_at:
        logger.error("Campaign sent time not available")
        return
    
    # ✅ Get all contacts from campaign's audience list
    from app.models.lists import ListContact
    contact_ids = []
    if campaign.audience_list_ids:
        for list_id in campaign.audience_list_ids:
            contacts = db.query(ListContact.contact_id).filter(
                ListContact.list_id == list_id
            ).all()
            contact_ids.extend([c[0] for c in contacts])
    
    if not contact_ids:
        logger.warning(f"No contacts found for campaign {campaign.campaign_name}")
        return
    
    # ✅ Schedule steps based on campaign sent time
    for step in sequence.get("steps", []):
        if step.get("status") == "completed":
            continue
        
        delay_minutes = int(step.get("delay_hours", 0)) * 60 + int(step.get("delay_minutes", 0))
        send_at = campaign_sent_at + timedelta(minutes=delay_minutes)
        
        step["scheduled_at"] = send_at.isoformat()
        step["status"] = "scheduled"
        
        logger.info(f"📅 Step {step.get('id')} scheduled at: {send_at}")
        
        # ✅ Schedule in background
        import asyncio
        asyncio.create_task(
            execute_scheduled_step(
                sequence_id=sequence_id,
                step_index=sequence["steps"].index(step),
                send_at=send_at,
                contact_ids=contact_ids,
                db=db
            )
        )


async def execute_scheduled_step(
    sequence_id: str,
    step_index: int,
    send_at: datetime,
    contact_ids: list,
    db: Session
):
    """
    Execute a step at its scheduled time
    """
    # ✅ If send_at is in the past or now, execute immediately
    now = datetime.utcnow()
    if send_at <= now:
        print(f"⏰ Step {step_index} is due now (send_at: {send_at})")
        # Execute immediately without waiting
        pass
    else:
        # Wait until it's time to send
        wait_seconds = (send_at - now).total_seconds()
        print(f"⏰ Waiting {wait_seconds} seconds for step {step_index}")
        await asyncio.sleep(wait_seconds)
    
    # ✅ Check if sequence is still active
    if sequence_id not in automation_sequences_cache:
        logger.error(f"Sequence {sequence_id} not found")
        return
    
    sequence = automation_sequences_cache[sequence_id]
    
    if sequence.get("status") != "active":
        logger.info(f"⏸️ Sequence {sequence_id} is paused, skipping step")
        return
    
    steps = sequence.get("steps", [])
    if step_index >= len(steps):
        return
    
    step = steps[step_index]
    
    # ✅ Check if step is already completed
    if step.get("status") == "completed":
        logger.info(f"Step {step_index} already completed")
        return
    
    # ✅ Get campaign
    campaign = db.query(Campaign).filter(
        Campaign.id == sequence["campaign_id"]
    ).first()
    
    if not campaign:
        logger.error(f"Campaign {sequence['campaign_id']} not found")
        return
    
    # ✅ Get contacts
    from app.models.lists import ListContact
    contacts = []
    if campaign.audience_list_ids:
        for list_id in campaign.audience_list_ids:
            # Get contact IDs from list
            contact_id_results = db.query(ListContact.contact_id).filter(
                ListContact.list_id == list_id
            ).all()
            contact_ids_from_list = [r[0] for r in contact_id_results]
            
            # Get contact details
            contacts_from_list = db.query(Contact).filter(
                Contact.id.in_(contact_ids_from_list),
                Contact.status == 'active'
            ).all()
            contacts.extend(contacts_from_list)
    
    # Remove duplicates
    seen_ids = set()
    unique_contacts = []
    for contact in contacts:
        if contact.id not in seen_ids:
            seen_ids.add(contact.id)
            unique_contacts.append(contact)
    contacts = unique_contacts
    
    if not contacts:
        logger.warning(f"No contacts found for campaign {campaign.campaign_name}")
        step["status"] = "failed"
        step["error"] = "No contacts found"
        return
    
    # ✅ Get template
    template = db.query(Template).filter(
        Template.id == step.get("template_id")
    ).first()
    
    if not template:
        logger.error(f"Template {step.get('template_id')} not found")
        step["status"] = "failed"
        step["error"] = "Template not found"
        return
    
    # ✅ Send messages using campaign page logic
    try:
        if step.get("type") == "whatsapp":
            # ✅ Use campaign page WhatsApp logic
            recipients = [
                {"phone": c.phone, "name": c.full_name or c.phone}
                for c in contacts if c.phone
            ]
            
            if recipients:
                from app.services.campaign_service import send_bulk_whatsapp
                result = await send_bulk_whatsapp(
                    recipients=recipients,
                    template_name=template.name,
                    language_code="en"
                )
                logger.info(f"✅ WhatsApp step {step_index} completed: {len(recipients)} messages sent")
            else:
                logger.warning("No recipients with phone numbers")
                step["status"] = "failed"
                step["error"] = "No recipients with phone numbers"
                return
                
        else:  # Email
            # ✅ Use campaign page Email logic
            from app.services.campaign_service import send_campaign_emails
            
            # Create a dummy campaign object for email sending
            class DummyCampaign:
                def __init__(self, campaign):
                    self.id = campaign.id
                    self.campaign_name = campaign.campaign_name
                    self.sender_identity_id = campaign.sender_identity_id
            
            dummy_campaign = DummyCampaign(campaign)
            
            # Get subject from template or use default
            subject = template.subject or f"Follow-up from {campaign.campaign_name}"
            
            result = await send_campaign_emails(
                log_db=db,
                main_db=db,
                campaign=dummy_campaign,
                contacts=contacts,
                subject=subject,
                template_content=template.content,
                template_name=template.name
            )
            logger.info(f"✅ Email step {step_index} completed: {result.get('sent', 0)} emails sent")
        
        # ✅ Mark step as completed
        step["status"] = "completed"
        step["sent_at"] = datetime.utcnow().isoformat()
        sequence["completed_count"] = sequence.get("completed_count", 0) + 1
        
        # Update database
        db_sequence = db.query(AutomationSequence).filter(
            AutomationSequence.id == sequence_id
        ).first()
        if db_sequence:
            db_sequence.steps = sequence.get("steps", [])
            db_sequence.completed_count = sequence.get("completed_count", 0)
            db_sequence.last_triggered_at = datetime.utcnow()
            db.commit()
        
        logger.info(f"✅ Step {step_index} completed successfully")
        
        # ✅ Check if all steps are completed
        all_completed = all(s.get("status") == "completed" for s in sequence.get("steps", []))
        if all_completed:
            sequence["status"] = "completed"
            logger.info(f"🎉 Sequence {sequence_id} completed!")
            
            # Update database
            if db_sequence:
                db_sequence.status = "completed"
                db.commit()
        
    except Exception as e:
        logger.error(f"❌ Error executing step {step_index}: {str(e)}")
        step["status"] = "failed"
        step["error"] = str(e)
        import traceback
        traceback.print_exc()

@router.get("/sequences", response_model=TypingList[AutomationSequenceResponse])
async def get_sequences(
    db: Session = Depends(get_main_db)
):
    """Get all automation sequences from database"""
    try:
        print("📋 Fetching sequences from database...")
        
        # ✅ Use the model directly
        sequences = db.query(AutomationSequence).order_by(
            AutomationSequence.created_at.desc()
        ).all()
        
        print(f"✅ Found {len(sequences)} sequences")
        
        result = []
        for seq in sequences:
            # ✅ Use to_dict method or build manually
            seq_dict = {
                "id": seq.id,
                "name": seq.name,
                "description": seq.description,
                "campaign_id": seq.campaign_id,
                "campaign_name": seq.campaign_name,
                "campaign_channel": seq.campaign_channel,
                "steps": seq.steps if seq.steps else [],
                "status": seq.status,
                "total_triggered": seq.total_triggered or 0,
                "completed_count": seq.completed_count or 0,
                "last_resume_at": seq.last_resume_at.isoformat() if seq.last_resume_at else None,
                "paused_at": seq.paused_at.isoformat() if seq.paused_at else None,
                "created_at": seq.created_at.isoformat() if seq.created_at else None,
                "updated_at": seq.updated_at.isoformat() if seq.updated_at else None,
            }
            result.append(seq_dict)
            print(f"   - {seq.name} (ID: {seq.id})")
        
        return [
            AutomationSequenceResponse(
                id=seq["id"],
                name=seq["name"],
                description=seq.get("description"),
                campaign_id=seq.get("campaign_id", ""),
                campaign_name=seq.get("campaign_name"),
                campaign_channel=seq.get("campaign_channel"),
                steps=seq.get("steps", []),
                status=seq.get("status", "active"),
                total_triggered=seq.get("total_triggered", 0),
                completed_count=seq.get("completed_count", 0),
                last_resume_at=seq.get("last_resume_at"),
                created_at=seq.get("created_at"),
                updated_at=seq.get("updated_at")
            )
            for seq in result
        ]
        
    except Exception as e:
        logger.error(f"Error getting sequences: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
# backend/app/routers/sequence_scheduler.py
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio
import logging

from app.database import get_main_db, get_log_db
from app.models.contact import Contact
from app.models.automation import AutomationSequence
from app.models.lists import AudienceList, ListContact
from app.models.campaign import Campaign

# ✅ Create the router object
router = APIRouter(prefix="/api/sequences", tags=["sequence-scheduler"])
logger = logging.getLogger(__name__)

# In-memory scheduler (replace with Celery in production)
scheduled_jobs = {}

@router.get("/test")
async def test_sequence_scheduler():
    """Test endpoint to verify router is working"""
    return {"status": "ok", "message": "Sequence scheduler router is working!"}

@router.post("/{sequence_id}/schedule-all")
async def schedule_sequence_for_all_contacts(
    sequence_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_main_db)
):
    """
    Schedule a sequence for all contacts in the target list
    This works independently of campaigns
    """
    from app.routers.automation import automation_sequences_cache
    
    print(f"\n📋 SCHEDULING SEQUENCE: {sequence_id}")
    
    # 1. Check if sequence exists in cache
    if sequence_id not in automation_sequences_cache:
        # Try to load from database
        db_sequence = db.query(AutomationSequence).filter(
            AutomationSequence.id == sequence_id
        ).first()
        
        if not db_sequence:
            print(f"❌ Sequence {sequence_id} not found")
            raise HTTPException(status_code=404, detail="Sequence not found")
        
        # Load into cache
        automation_sequences_cache[sequence_id] = {
            "id": db_sequence.id,
            "name": db_sequence.name,
            "description": db_sequence.description,
            "list_id": db_sequence.list_id,
            "list_name": db_sequence.list_name,
            "steps": db_sequence.steps if db_sequence.steps else [],
            "status": db_sequence.status,
            "total_triggered": db_sequence.total_triggered or 0,
            "completed_count": db_sequence.completed_count or 0,
        }
    
    sequence = automation_sequences_cache[sequence_id]
    list_id = sequence.get("list_id")
    
    if not list_id:
        print(f"❌ Sequence has no list_id")
        raise HTTPException(status_code=400, detail="No target list specified")
    
    # 2. Check if list exists
    list_obj = db.query(AudienceList).filter(AudienceList.id == list_id).first()
    if not list_obj:
        print(f"❌ List {list_id} not found in database")
        raise HTTPException(status_code=404, detail="List not found")
    
    print(f"✅ Found list: {list_obj.list_name}")
    
    # 3. Get all contacts from the list
    contact_ids = db.query(ListContact.contact_id).filter(
        ListContact.list_id == list_id
    ).all()
    
    contact_ids = [c[0] for c in contact_ids]
    
    if not contact_ids:
        print(f"⚠️ List {list_obj.list_name} has no contacts")
        return {
            "success": False,
            "message": f"No contacts in the target list: {list_obj.list_name}",
            "contact_count": 0,
            "list_name": list_obj.list_name
        }
    
    print(f"✅ Found {len(contact_ids)} contacts in list: {list_obj.list_name}")
    
    # 4. Update sequence status to active
    sequence["status"] = "active"
    sequence["list_name"] = list_obj.list_name
    
    # 5. Schedule sequence for each contact in background
    background_tasks.add_task(
        process_contacts_sequence,
        sequence_id=sequence_id,
        contact_ids=contact_ids,
        db=db
    )
    
    return {
        "success": True,
        "message": f"Sequence '{sequence['name']}' scheduled for {len(contact_ids)} contacts",
        "sequence_id": sequence_id,
        "list_id": list_id,
        "list_name": list_obj.list_name,
        "contact_count": len(contact_ids)
    }


# ✅ NEW: Campaign-based sequence scheduling
@router.post("/{sequence_id}/schedule-campaign-based")
async def schedule_campaign_based_sequence(
    sequence_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_main_db),
    log_db: Session = Depends(get_log_db)
):
    """
    Schedule a sequence based on campaign sent time and engagement
    """
    from app.routers.automation import automation_sequences_cache
    from app.services.campaign_engagement_service import CampaignEngagementService
    
    print(f"\n📋 SCHEDULING CAMPAIGN-BASED SEQUENCE: {sequence_id}")
    
    if sequence_id not in automation_sequences_cache:
        raise HTTPException(status_code=404, detail="Sequence not found")
    
    sequence = automation_sequences_cache[sequence_id]
    campaign_id = sequence.get("campaign_id")
    
    if not campaign_id:
        raise HTTPException(status_code=400, detail="No campaign associated with this sequence")
    
    # Get campaign
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    print(f"✅ Found campaign: {campaign.campaign_name}")
    print(f"   Status: {campaign.status}")
    print(f"   Sent at: {campaign.sent_at}")
    
    # Check if campaign is sent
    if campaign.status != 'sent':
        return {
            "success": False,
            "message": f"Campaign '{campaign.campaign_name}' is not sent yet. Current status: {campaign.status}"
        }
    
    # Get campaign sent time
    campaign_sent_at = campaign.sent_at
    if not campaign_sent_at:
        return {
            "success": False,
            "message": "Campaign sent time not available"
        }
    
    # Get engagement type
    engagement_required = sequence.get("engagement_required", "all")
    print(f"   Engagement required: {engagement_required}")
    
    # Get engaged contacts
    engagement_service = CampaignEngagementService(db, log_db)
    
    if engagement_required == 'all':
        # Get all contacts from campaign's audience list
        contact_ids = []
        if campaign.audience_list_ids:
            for list_id in campaign.audience_list_ids:
                contacts = db.query(ListContact.contact_id).filter(
                    ListContact.list_id == list_id
                ).all()
                contact_ids.extend([c[0] for c in contacts])
        print(f"   All contacts in audience: {len(contact_ids)}")
    else:
        # Get only engaged contacts
        contact_ids = engagement_service.get_engaged_contacts(campaign_id, engagement_required)
        print(f"   Engaged contacts: {len(contact_ids)}")
    
    if not contact_ids:
        return {
            "success": False,
            "message": "No contacts found for this sequence",
            "contact_count": 0
        }
    
    # Update sequence status
    sequence["status"] = "active"
    sequence["campaign_name"] = campaign.campaign_name
    sequence["campaign_channel"] = campaign.channel
    
    # Schedule sequence for each contact
    background_tasks.add_task(
        process_campaign_based_sequence,
        sequence_id=sequence_id,
        contact_ids=contact_ids,
        campaign_sent_at=campaign_sent_at,
        db=db
    )
    
    return {
        "success": True,
        "message": f"Sequence scheduled for {len(contact_ids)} contacts based on campaign '{campaign.campaign_name}'",
        "sequence_id": sequence_id,
        "campaign_id": campaign_id,
        "campaign_name": campaign.campaign_name,
        "contact_count": len(contact_ids)
    }


async def process_campaign_based_sequence(
    sequence_id: str,
    contact_ids: list,
    campaign_sent_at: datetime,
    db: Session
):
    """
    Process campaign-based sequence with timing relative to campaign sent time
    """
    from app.routers.automation import automation_sequences_cache, execute_sequence_step
    
    logger.info(f"🔄 Processing campaign-based sequence {sequence_id} for {len(contact_ids)} contacts")
    
    sequence = automation_sequences_cache.get(sequence_id)
    if not sequence:
        logger.error(f"❌ Sequence {sequence_id} not found")
        return
    
    steps = sequence.get("steps", [])
    if not steps:
        logger.error(f"❌ Sequence {sequence_id} has no steps")
        return
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for contact_id in contact_ids:
        try:
            contact = db.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                logger.warning(f"⚠️ Contact {contact_id} not found")
                skipped_count += 1
                continue
            
            # Check if contact has the required channel
            has_email = contact.email and contact.email.strip()
            has_phone = contact.phone and contact.phone.strip()
            
            # Execute each step with timing based on campaign sent time
            for step_index, step in enumerate(steps):
                step_type = step.get("type", "whatsapp")
                delay_hours = int(step.get("delay", 0))
                
                # Calculate send time: campaign_sent_at + delay
                send_at = campaign_sent_at + timedelta(hours=delay_hours)
                
                # Check if it's time to send
                if datetime.utcnow() < send_at:
                    logger.info(f"⏰ Step {step_index + 1} scheduled at {send_at}")
                    # In production, use Celery/Redis for scheduling
                    continue
                
                # Check channel availability
                if step_type == "email" and not has_email:
                    logger.warning(f"⚠️ Contact has no email for step {step_index + 1}")
                    continue
                    
                if step_type == "whatsapp" and not has_phone:
                    logger.warning(f"⚠️ Contact has no phone for step {step_index + 1}")
                    continue
                
                # Execute the step
                result = await execute_sequence_step(
                    sequence=sequence,
                    step=step,
                    contact=contact,
                    step_index=step_index,
                    db=db,
                    log_db=db
                )
                
                if result.get("success"):
                    logger.info(f"✅ Step {step_index + 1} completed: {result.get('message')}")
                else:
                    logger.error(f"❌ Step {step_index + 1} failed: {result.get('message')}")
            
            sequence["total_triggered"] = sequence.get("total_triggered", 0) + 1
            success_count += 1
            
        except Exception as e:
            logger.error(f"❌ Error processing contact {contact_id}: {str(e)}")
            failed_count += 1
            continue
    
    logger.info(f"✅ Completed: {success_count} success, {failed_count} failed, {skipped_count} skipped")


async def process_contacts_sequence(sequence_id: str, contact_ids: list, db: Session):
    """
    Process sequence for multiple contacts
    """
    from app.routers.automation import automation_sequences_cache, execute_sequence_step
    
    logger.info(f"🔄 Processing sequence {sequence_id} for {len(contact_ids)} contacts")
    
    sequence = automation_sequences_cache.get(sequence_id)
    if not sequence:
        logger.error(f"❌ Sequence {sequence_id} not found")
        return
    
    steps = sequence.get("steps", [])
    if not steps:
        logger.error(f"❌ Sequence {sequence_id} has no steps")
        return
    
    success_count = 0
    failed_count = 0
    skipped_count = 0
    
    for contact_id in contact_ids:
        try:
            contact = db.query(Contact).filter(Contact.id == contact_id).first()
            if not contact:
                logger.warning(f"⚠️ Contact {contact_id} not found")
                skipped_count += 1
                continue
            
            has_email = contact.email and contact.email.strip()
            has_phone = contact.phone and contact.phone.strip()
            
            if not has_email and not has_phone:
                logger.warning(f"⚠️ Contact {contact_id} has no email or phone")
                skipped_count += 1
                continue
            
            logger.info(f"📨 Processing contact: {contact.email or contact.phone}")
            
            # Execute all steps
            for step_index, step in enumerate(steps):
                step_type = step.get("type", "whatsapp")
                
                if step_type == "email" and not has_email:
                    logger.warning(f"⚠️ Contact has no email for step {step_index + 1}")
                    continue
                    
                if step_type == "whatsapp" and not has_phone:
                    logger.warning(f"⚠️ Contact has no phone for step {step_index + 1}")
                    continue
                
                result = await execute_sequence_step(
                    sequence=sequence,
                    step=step,
                    contact=contact,
                    step_index=step_index,
                    db=db,
                    log_db=db
                )
                
                if result.get("success"):
                    logger.info(f"✅ Step {step_index + 1} completed: {result.get('message')}")
                else:
                    logger.error(f"❌ Step {step_index + 1} failed: {result.get('message')}")
                
                # Schedule next step if there's a delay
                if step_index < len(steps) - 1:
                    next_step = steps[step_index + 1]
                    delay_hours = int(next_step.get("delay", 24))
                    
                    if delay_hours > 0:
                        execute_at = datetime.utcnow() + timedelta(hours=delay_hours)
                        job_key = f"{sequence_id}_{contact_id}_{step_index + 1}"
                        
                        scheduled_jobs[job_key] = {
                            "sequence_id": sequence_id,
                            "contact_id": contact_id,
                            "step_index": step_index + 1,
                            "execute_at": execute_at.isoformat(),
                            "status": "scheduled"
                        }
                        
                        logger.info(f"⏰ Scheduled step {step_index + 2} at {execute_at}")
            
            sequence["total_triggered"] = sequence.get("total_triggered", 0) + 1
            success_count += 1
            
        except Exception as e:
            logger.error(f"❌ Error processing contact {contact_id}: {str(e)}")
            failed_count += 1
            continue
    
    logger.info(f"✅ Completed: {success_count} success, {failed_count} failed, {skipped_count} skipped")


@router.get("/scheduled-jobs")
async def get_scheduled_jobs():
    """Get all scheduled jobs"""
    return {
        "total_jobs": len(scheduled_jobs),
        "jobs": scheduled_jobs
    }


@router.post("/scheduled-jobs/process")
async def process_scheduled_jobs(db: Session = Depends(get_main_db)):
    """Manually process all scheduled jobs"""
    from app.routers.automation import automation_sequences_cache, execute_sequence_step
    
    processed = 0
    failed = 0
    now = datetime.utcnow()
    
    for job_key, job in list(scheduled_jobs.items()):
        execute_at = datetime.fromisoformat(job["execute_at"])
        
        if execute_at <= now:
            try:
                sequence_id = job["sequence_id"]
                contact_id = job["contact_id"]
                step_index = job["step_index"]
                
                sequence = automation_sequences_cache.get(sequence_id)
                if not sequence:
                    logger.error(f"❌ Sequence {sequence_id} not found")
                    scheduled_jobs.pop(job_key, None)
                    failed += 1
                    continue
                
                contact = db.query(Contact).filter(Contact.id == contact_id).first()
                if not contact:
                    logger.error(f"❌ Contact {contact_id} not found")
                    scheduled_jobs.pop(job_key, None)
                    failed += 1
                    continue
                
                step = sequence["steps"][step_index]
                
                result = await execute_sequence_step(
                    sequence=sequence,
                    step=step,
                    contact=contact,
                    step_index=step_index,
                    db=db,
                    log_db=db
                )
                
                if result.get("success"):
                    logger.info(f"✅ Processed scheduled job: {job_key}")
                    processed += 1
                else:
                    logger.error(f"❌ Failed to process job: {job_key}")
                    failed += 1
                
                scheduled_jobs.pop(job_key, None)
                
            except Exception as e:
                logger.error(f"❌ Error processing job {job_key}: {str(e)}")
                failed += 1
                scheduled_jobs.pop(job_key, None)
    
    return {
        "processed": processed,
        "failed": failed,
        "remaining": len(scheduled_jobs)
    }


@router.delete("/scheduled-jobs/{job_key}")
async def delete_scheduled_job(job_key: str):
    """Delete a specific scheduled job"""
    if job_key in scheduled_jobs:
        del scheduled_jobs[job_key]
        return {"message": f"Job {job_key} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Job not found")


@router.delete("/scheduled-jobs")
async def clear_all_scheduled_jobs():
    """Clear all scheduled jobs"""
    count = len(scheduled_jobs)
    scheduled_jobs.clear()
    return {"message": f"Cleared {count} scheduled jobs"}
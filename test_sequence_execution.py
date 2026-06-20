# backend/scripts/test_sequence_execution.py
import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from app.database import get_main_db
from app.models.campaign import Campaign
from app.models.automation import AutomationSequence
from app.routers.automation import execute_sequence_step

async def test_sequence_execution():
    """Test executing a sequence step"""
    
    print("\n" + "="*60)
    print("🧪 TEST SEQUENCE EXECUTION")
    print("="*60)
    
    db = next(get_main_db())
    
    try:
        # Get a campaign
        campaign = db.query(Campaign).filter(
            Campaign.status == 'sent',
            Campaign.sent_at.isnot(None)
        ).first()
        
        if not campaign:
            print("❌ No sent campaign found")
            return
        
        print(f"✅ Found campaign: {campaign.campaign_name}")
        print(f"   Sent at: {campaign.sent_at}")
        print(f"   Audience lists: {campaign.audience_list_ids}")
        
        # Get a sequence
        sequence = db.query(AutomationSequence).filter(
            AutomationSequence.campaign_id == campaign.id,
            AutomationSequence.status == 'active'
        ).first()
        
        if not sequence:
            print("❌ No active sequence found for this campaign")
            return
        
        print(f"✅ Found sequence: {sequence.name}")
        print(f"   Steps: {len(sequence.steps)}")
        
        for i, step in enumerate(sequence.steps):
            print(f"   Step {i+1}: {step.get('type')} - {step.get('delay_hours')}h {step.get('delay_minutes')}m")
        
        # Execute the first pending step
        step_index = None
        for i, step in enumerate(sequence.steps):
            if step.get('status') != 'completed':
                step_index = i
                break
        
        if step_index is None:
            print("❌ All steps are already completed")
            return
        
        print(f"\n📨 Executing step {step_index + 1}")
        
        # Get contacts from campaign
        from app.models.lists import ListContact
        from app.models.contact import Contact
        
        contact_ids = []
        if campaign.audience_list_ids:
            for list_id in campaign.audience_list_ids:
                ids = db.query(ListContact.contact_id).filter(
                    ListContact.list_id == list_id
                ).all()
                contact_ids.extend([r[0] for r in ids])
        
        if not contact_ids:
            print("❌ No contacts found")
            return
        
        print(f"✅ Found {len(contact_ids)} contacts")
        
        # Get first contact
        contact = db.query(Contact).filter(Contact.id.in_(contact_ids)).first()
        if not contact:
            print("❌ No contact found")
            return
        
        print(f"✅ Contact: {contact.email or contact.phone}")
        
        # Execute step
        step = sequence.steps[step_index]
        result = await execute_sequence_step(
            sequence={
                "id": sequence.id,
                "name": sequence.name,
                "campaign_id": sequence.campaign_id,
            },
            step=step,
            contact=contact,
            step_index=step_index,
            db=db,
            log_db=db
        )
        
        print(f"\n📊 Result:")
        print(f"   Success: {result.get('success')}")
        print(f"   Message: {result.get('message')}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_sequence_execution())
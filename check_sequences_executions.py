# check_sequences_executions.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_main_db
from app.models.automation import AutomationSequence, SequenceExecution
from app.models.campaign import Campaign
from datetime import datetime
import json

db = next(get_main_db())

print("=" * 60)
print("SEQUENCES AND EXECUTIONS CHECK")
print("=" * 60)

# Get all sequences
sequences = db.query(AutomationSequence).all()
print(f"\n📋 Total Sequences: {len(sequences)}")

if len(sequences) == 0:
    print("❌ No sequences found! Create a sequence first.")
    db.close()
    exit()

for seq in sequences:
    # Get campaign
    campaign = db.query(Campaign).filter(Campaign.id == seq.campaign_id).first()
    
    print(f"\n📋 Sequence: {seq.name}")
    print(f"   ID: {seq.id}")
    print(f"   Campaign: {seq.campaign_name}")
    print(f"   Campaign ID: {seq.campaign_id}")
    print(f"   Channel: {seq.channel}")
    print(f"   Is Active: {seq.is_active}")
    print(f"   Created: {seq.created_at}")
    
    # Check campaign sent_at
    if campaign:
        print(f"   Campaign sent_at: {campaign.sent_at}")
        print(f"   Campaign status: {campaign.status}")
    else:
        print(f"   ⚠️ Campaign not found!")
    
    # Parse steps
    try:
        if isinstance(seq.steps, str):
            steps = json.loads(seq.steps)
        else:
            steps = seq.steps
        print(f"   Steps: {json.dumps(steps, indent=2) if steps else 'None'}")
    except:
        print(f"   Steps: {seq.steps}")
    
    # Check executions
    executions = db.query(SequenceExecution).filter(
        SequenceExecution.sequence_id == seq.id
    ).all()
    
    print(f"   Executions: {len(executions)}")
    
    if len(executions) > 0:
        pending = sum(1 for e in executions if e.status == "pending")
        in_progress = sum(1 for e in executions if e.status == "in_progress")
        completed = sum(1 for e in executions if e.status == "completed")
        failed = sum(1 for e in executions if e.status == "failed")
        
        print(f"   - Pending: {pending}")
        print(f"   - In Progress: {in_progress}")
        print(f"   - Completed: {completed}")
        print(f"   - Failed: {failed}")
        
        if pending > 0:
            now = datetime.utcnow()
            due = [e for e in executions if e.status == "pending" and e.scheduled_at and e.scheduled_at <= now]
            print(f"   - Due now: {len(due)}")
            
            for e in due[:3]:
                print(f"     • {e.contact_phone} (scheduled: {e.scheduled_at})")
    else:
        print(f"   ⚠️ No executions found!")

db.close()
# check_campaign_sent_at.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_main_db
from app.models.campaign import Campaign
from datetime import datetime
import json

db = next(get_main_db())

# Find campaigns with sent_at values
campaigns = db.query(Campaign).filter(
    Campaign.status == "sent",
    Campaign.sent_at.isnot(None)
).order_by(Campaign.sent_at.desc()).limit(10).all()

print(f"Found {len(campaigns)} campaigns with sent_at")
print("=" * 60)

if len(campaigns) == 0:
    print("❌ No campaigns with sent_at found!")
    print("\nAll campaigns with status 'sent':")
    all_sent = db.query(Campaign).filter(Campaign.status == "sent").all()
    for c in all_sent[:10]:
        print(f"  - {c.campaign_name} (sent_at: {c.sent_at})")
    db.close()
    exit()

for c in campaigns:
    print(f"\n📧 {c.campaign_name}")
    print(f"   ID: {c.id}")
    print(f"   Channel: {c.channel}")
    print(f"   Sent at: {c.sent_at}")
    
    # Parse audience list IDs
    try:
        if c.audience_list_ids:
            list_ids = json.loads(c.audience_list_ids) if isinstance(c.audience_list_ids, str) else c.audience_list_ids
            print(f"   Audience Lists: {list_ids}")
    except:
        pass
    
    print(f"   Total Sent: {c.total_sent}")
    print(f"   Total Delivered: {c.total_delivered}")

db.close()
# check_scheduler.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.scheduler.campaign_scheduler import start_scheduler
from app.database import get_main_db
from app.models.campaign import Campaign
from datetime import datetime

print("Checking scheduler status...")
print("=" * 50)

# Check if there are any scheduled campaigns
db = next(get_main_db())

# Check campaigns that should have been sent
campaigns = db.query(Campaign).filter(
    Campaign.status == "scheduled",
    Campaign.scheduled_at <= datetime.utcnow()
).all()

print(f"Found {len(campaigns)} campaigns that should be sent:")
for c in campaigns:
    print(f"  - {c.campaign_name} (scheduled: {c.scheduled_at})")

# Check sent campaigns
sent_campaigns = db.query(Campaign).filter(
    Campaign.status == "sent"
).all()

print(f"\nFound {len(sent_campaigns)} already sent campaigns:")
for c in sent_campaigns:
    print(f"  - {c.campaign_name} (sent at: {c.sent_at})")

db.close() 
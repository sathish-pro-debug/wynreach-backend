# fix_sent_at.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_main_db
from app.models.campaign import Campaign
from datetime import datetime

db = next(get_main_db())

# Find all campaigns marked as "sent" but with None sent_at
campaigns = db.query(Campaign).filter(
    Campaign.status == "sent",
    Campaign.sent_at.is_(None)
).all()

print(f"Found {len(campaigns)} campaigns with status 'sent' but no sent_at timestamp")

if len(campaigns) == 0:
    print("✅ All sent campaigns have proper sent_at timestamps!")
    db.close()
    exit()

# Ask user what to do
print("\nOptions:")
print("1. Set sent_at to current time for all")
print("2. Set sent_at based on created_at (approximate)")
print("3. Skip and exit")

choice = input("Choose option (1-3): ")

if choice == "1":
    for c in campaigns:
        c.sent_at = datetime.utcnow()
        print(f"✅ Set {c.campaign_name} sent_at to now")
    db.commit()
    print(f"\n✅ Updated {len(campaigns)} campaigns!")

elif choice == "2":
    for c in campaigns:
        # Use created_at as approximate sent time
        if c.created_at:
            c.sent_at = c.created_at
            print(f"✅ Set {c.campaign_name} sent_at to {c.created_at}")
    db.commit()
    print(f"\n✅ Updated {len(campaigns)} campaigns!")

else:
    print("❌ No changes made")

db.close()
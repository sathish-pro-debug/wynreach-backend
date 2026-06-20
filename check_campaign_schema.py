# check_campaign_schema.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_main_db
from app.models.campaign import Campaign
from sqlalchemy import inspect

db = next(get_main_db())

# Get column names
inspector = inspect(Campaign)
columns = [c.name for c in inspector.columns]

print("Campaign Model Columns:")
print("=" * 40)
for col in columns:
    print(f"  - {col}")

# Also check a sample campaign
campaign = db.query(Campaign).first()
if campaign:
    print("\nSample Campaign Data:")
    print("=" * 40)
    for col in columns:
        value = getattr(campaign, col, None)
        print(f"  {col}: {value}")

db.close()
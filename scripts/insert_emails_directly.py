# E:\wynReach\backend\scripts\insert_emails_directly.py

import sys
import os
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import get_main_db

def insert_emails_directly():
    """Insert email addresses directly into the database"""
    
    print("\n" + "="*60)
    print("📧 Inserting Email Addresses Directly")
    print("="*60)
    
    # Connect to database
    db = next(get_main_db())
    
    # Get domain ID for wynsync.tech
    domain_query = text("""
        SELECT id FROM email_domains 
        WHERE domain = 'wynsync.tech' AND verification_status = 'verified'
        LIMIT 1
    """)
    domain_result = db.execute(domain_query).fetchone()
    
    if not domain_result:
        print("❌ Domain 'wynsync.tech' not found!")
        return
    
    domain_id = domain_result[0]
    print(f"✅ Found domain ID: {domain_id}")
    
    # List of emails to insert
    emails_to_insert = [
        {"email": "noreply@wynsync.tech", "status": "verified", "is_default": False},
        {"email": "sathish.athimoolam@wynsync.tech", "status": "verified", "is_default": False},
        {"email": "noreply@wynsync.tech", "status": "verified", "is_default": True},
    ]
    
    inserted = 0
    skipped = 0
    
    for email_data in emails_to_insert:
        email = email_data["email"]
        
        # Check if email already exists
        check_query = text("""
            SELECT id FROM email_addresses 
            WHERE email = :email
        """)
        existing = db.execute(check_query, {"email": email}).fetchone()
        
        if existing:
            print(f"  ⏭️  {email} - Already exists")
            skipped += 1
            continue
        
        # Insert the email
        email_id = str(uuid.uuid4())
        insert_query = text("""
            INSERT INTO email_addresses (
                id, user_id, domain_id, email, status, is_default, created_at, updated_at
            ) VALUES (
                :id, :user_id, :domain_id, :email, :status, :is_default, NOW(), NOW()
            )
        """)
        
        try:
            db.execute(insert_query, {
                "id": email_id,
                "user_id": "2",
                "domain_id": domain_id,
                "email": email,
                "status": email_data["status"],
                "is_default": email_data["is_default"]
            })
            db.commit()
            print(f"  ✅ {email} - Inserted successfully")
            inserted += 1
        except Exception as e:
            print(f"  ❌ {email} - Failed: {e}")
            db.rollback()
    
    db.close()
    
    print("\n" + "="*60)
    print("📊 RESULTS")
    print("="*60)
    print(f"  ✅ Inserted: {inserted}")
    print(f"  ⏭️  Skipped: {skipped}")
    print("="*60)
    
    if inserted > 0:
        print("\n💡 Refresh your frontend page to see the new email addresses!")

if __name__ == "__main__":
    insert_emails_directly()
    
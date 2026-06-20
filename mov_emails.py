# move_emails_to_new_domain.py
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_main_db
from app.models.sender_identity import EmailDomain, EmailAddress

db = next(get_main_db())

print("=" * 50)
print("MOVE EMAILS TO NEW DOMAIN")
print("=" * 50)

# Find the old domain (with emails)
old_domain = db.query(EmailDomain).filter(
    EmailDomain.id == "17ce2358-a8ac-4d97-b704-29a5d373d290"
).first()

# Find the new domain (your current domain)
new_domain = db.query(EmailDomain).filter(
    EmailDomain.domain == "wynsync.tech"
).first()

if not new_domain:
    print("❌ New domain not found")
    db.close()
    exit()

print(f"Old Domain ID: {old_domain.id if old_domain else 'Not found'}")
print(f"New Domain ID: {new_domain.id}")
print(f"New Domain User ID: {new_domain.user_id}")
print("-" * 40)

if old_domain:
    # Get emails from old domain
    emails = db.query(EmailAddress).filter(
        EmailAddress.domain_id == old_domain.id
    ).all()
    
    print(f"\n📧 Found {len(emails)} emails in old domain")
    
    # Move emails to new domain
    for email in emails:
        print(f"  Moving: {email.email}")
        email.domain_id = new_domain.id
        email.user_id = new_domain.user_id
    
    db.commit()
    print(f"\n✅ Moved {len(emails)} emails to new domain")
else:
    print("⚠️ Old domain not found - emails may be orphaned")
    
    # Check if there are any emails with orphaned domain_id
    orphaned_emails = db.query(EmailAddress).filter(
        EmailAddress.domain_id == "17ce2358-a8ac-4d97-b704-29a5d373d290"
    ).all()
    
    if orphaned_emails:
        print(f"Found {len(orphaned_emails)} orphaned emails")
        for email in orphaned_emails:
            print(f"  Orphaned: {email.email}")
            email.domain_id = new_domain.id
            email.user_id = new_domain.user_id
        db.commit()
        print(f"✅ Fixed {len(orphaned_emails)} orphaned emails")

# Verify
emails_after = db.query(EmailAddress).filter(
    EmailAddress.domain_id == new_domain.id
).all()
print(f"\n📧 Total emails in new domain: {len(emails_after)}")
for email in emails_after:
    print(f"   - {email.email} (User: {email.user_id})")

db.close()
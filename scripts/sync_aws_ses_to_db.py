# E:\wynReach\backend\scripts\sync_aws_ses_to_db.py
import sys
import os
import uuid

# Add the parent directory to path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import boto3
from sqlalchemy import text
from app.database import get_main_db
from app.core.config import settings

def sync_aws_ses_identities(user_id: str = "2"):
    
    """
    Sync AWS SES verified identities to local email_addresses table
    
    Args:
        user_id: Your user ID from the users table (default is "2" based on your data)
    """
    
    print("\n" + "="*60)
    print("🔄 Starting AWS SES to Local Database Sync")
    print("="*60)
    
    # Check AWS credentials
    if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
        print("❌ AWS credentials not found in settings!")
        print("Please check your AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        return
    
    print(f"✅ AWS credentials found")
    print(f"   Region: {settings.AWS_REGION}")
    
    # Connect to AWS SES
    try:
        ses_client = boto3.client(
            'ses',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        print("✅ Connected to AWS SES")
    except Exception as e:
        print(f"❌ Failed to connect to AWS SES: {e}")
        return
    
    # Get all verified identities from AWS SES

    try:
        response = ses_client.list_identities(
            IdentityType='EmailAddress',
            MaxItems=100
        )

        email_identities = response['Identities']
        print(f"📧 Found {len(email_identities)} email identities in AWS SES")
    except Exception as e:
        print(f"❌ Failed to list identities: {e}")
        return
    
    # Get verification status for each
    try:
        attrs_response = ses_client.get_identity_verification_attributes(
            Identities=email_identities
        )
        print("✅ Retrieved verification statuses")
    except Exception as e:
        print(f"❌ Failed to get verification attributes: {e}")
        return
    
    # Connect to local database
    try:
        db = next(get_main_db())
        print("✅ Connected to local database")
    except Exception as e:
        print(f"❌ Failed to connect to database: {e}")
        return
    
    # First, get all domains from email_domains table
    domain_query = text("""
        SELECT id, domain FROM email_domains 
        WHERE user_id = :user_id AND verification_status = 'verified'
    """)
    domains = db.execute(domain_query, {"user_id": user_id}).fetchall()
    
    if not domains:
        print(f"⚠️ No verified domains found for user_id: {user_id}")
        print("   Please make sure you have verified domains in your email_domains table")
        return
    
    domain_map = {domain[1]: domain[0] for domain in domains}  # domain -> domain_id
    
    print(f"\n📂 Found {len(domains)} verified domains:")
    for domain in domains:
        print(f"   - {domain[1]} (ID: {domain[0]})")
    
    print(f"\n📧 Processing {len(email_identities)} email addresses...")
    print("-"*60)
    
    synced_count = 0
    updated_count = 0
    skipped_count = 0
    
    for email in email_identities:
        status = attrs_response['VerificationAttributes'].get(email, {}).get('VerificationStatus', 'Pending')
        
        # Convert AWS status to our status
        local_status = 'verified' if status == 'Success' else 'pending'
        
        # Extract domain from email
        try:
            email_domain = email.split('@')[1]
        except:
            print(f"  ⚠️ Invalid email format: {email}")
            skipped_count += 1
            continue
        
        # Find matching domain in local DB
        domain_id = domain_map.get(email_domain)
        
        if not domain_id:
            print(f"  ⚠️ {email} - No matching verified domain found for '{email_domain}'")
            skipped_count += 1
            continue
        
        # Check if email already exists in local DB
        check_query = text("""
            SELECT id, status FROM email_addresses 
            WHERE email = :email AND user_id = :user_id
        """)
        existing = db.execute(check_query, {
            "email": email,
            "user_id": user_id
        }).fetchone()
        
        if existing:
            # Update status if needed
            if existing[1] != local_status:
                update_query = text("""
                    UPDATE email_addresses 
                    SET status = :status, updated_at = NOW()
                    WHERE id = :id
                """)
                db.execute(update_query, {"status": local_status, "id": existing[0]})
                db.commit()
                print(f"  🔄 {email} - Status updated: {existing[1]} → {local_status}")
                updated_count += 1
            else:
                print(f"  ✓ {email} - Already exists (Status: {local_status})")
            skipped_count += 1
            continue
        
        # Insert into local database
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
                "user_id": user_id,
                "domain_id": domain_id,
                "email": email,
                "status": local_status,
                "is_default": email.startswith('admin@') or email.startswith('contact@') or email.startswith('noreply@')
            })
            db.commit()
            print(f"  ✅ {email} - Synced to database (Status: {local_status})")
            synced_count += 1
        except Exception as e:
            print(f"  ❌ {email} - Failed to sync: {e}")

            db.rollback()
    
    db.close()
    
    print("\n" + "="*60)
    print("📊 SYNC COMPLETE!")
    print("="*60)
    print(f"  ✅ Newly synced: {synced_count}")
    print(f"  🔄 Updated: {updated_count}")
    print(f"  ⏭️  Skipped/Existing: {skipped_count}")
    print(f"  📧 Total AWS Identities: {len(email_identities)}")
    print("="*60)
    
    # Show what was synced
    if synced_count > 0:
        print("\n💡 Next steps:")
        print("   1. Refresh your frontend page")
        print("   2. The email addresses should now appear in the Sender Identity tab")
        print("   3. You can now use these emails to send campaigns")

def get_user_id_from_email(email: str):
    """Helper function to get user_id from email"""
    db = next(get_main_db())
    query = text("SELECT id FROM users WHERE email = :email")
    result = db.execute(query, {"email": email}).fetchone()
    db.close()
    return str(result[0]) if result else None

if __name__ == "__main__":
    print("\n🔧 AWS SES to Local Database Sync Tool")
    print("="*60)
    
    # Option to enter user_id manually
    user_id = input("Enter your user_id (press Enter for default '2'): ").strip()
    
    if not user_id:
        user_id = "2"
        print(f"Using default user_id: {user_id}")
    
    # Option to find user_id by email
    if user_id.lower() == 'find':
        email = input("Enter your email address: ").strip()
        user_id = get_user_id_from_email(email)
        if user_id:
            print(f"Found user_id: {user_id}")
        else:
            print(f"No user found with email: {email}")
            sys.exit(1)
    
    # Run the sync
    sync_aws_ses_identities(user_id=user_id)  
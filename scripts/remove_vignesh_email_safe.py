# E:\wynReach\backend\scripts\remove_vignesh_email_safe.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.database import get_main_db

def get_default_email(db):
    """Get the current default email from database"""
    default_query = text("""
        SELECT email FROM email_addresses 
        WHERE is_default = TRUE 
        AND status = 'verified'
        LIMIT 1
    """)
    result = db.execute(default_query).fetchone()
    return result[0] if result else None

def get_all_emails(db):
    """Get all email addresses"""
    query = text("""
        SELECT id, email, is_default, status 
        FROM email_addresses 
        ORDER BY is_default DESC, email
    """)
    return db.execute(query).fetchall()

def safe_remove_vignesh_email():
    """Safely remove vignesh.dhandapani@wynsync.tech from database"""
    
    print("\n" + "="*60)
    print("🗑️  Removing vignesh.dhandapani@wynsync.tech (Safe Mode)")
    print("="*60)
    
    db = next(get_main_db())
    
    # 1. Show all current emails
    print("\n📧 Current email addresses:")
    print("-"*60)
    all_emails = get_all_emails(db)
    for row in all_emails:
        default_marker = "⭐ " if row[2] else "   "
        print(f"{default_marker}{row[1]} - Status: {row[3]}")
    print("-"*60)
    
    # 2. Check if the vignesh email exists
    check_query = text("""
        SELECT id, email, is_default, status 
        FROM email_addresses 
        WHERE email = 'vignesh.dhandapani@wynsync.tech'
    """)
    result = db.execute(check_query).fetchone()
    
    if not result:
        print("\n❌ vignesh.dhandapani@wynsync.tech not found in database")
        db.close()
        return
    
    print(f"\n✅ Found email: {result[1]}")
    print(f"   ID: {result[0]}")
    print(f"   Is Default: {result[2]}")
    print(f"   Status: {result[3]}")
    
    # 3. Check if this is the default email
    if result[2]:  # is_default = True
        print("\n⚠️  WARNING: This is the DEFAULT email!")
        print("💡 You cannot delete the default email without setting a new one")
        
        # Get the next available email to set as default
        other_emails = text("""
            SELECT id, email FROM email_addresses 
            WHERE email != 'vignesh.dhandapani@wynsync.tech'
            AND status = 'verified'
            LIMIT 1
        """)
        new_default = db.execute(other_emails).fetchone()
        
        if new_default:
            print(f"\n💡 Setting '{new_default[1]}' as new default...")
            
            # Remove default from all emails
            db.execute(text("""
                UPDATE email_addresses 
                SET is_default = FALSE,
                    updated_at = NOW()
                WHERE is_default = TRUE
            """))
            
            # Set new default
            db.execute(text("""
                UPDATE email_addresses 
                SET is_default = TRUE,
                    updated_at = NOW()
                WHERE id = :id
            """), {"id": new_default[0]})
            
            db.commit()
            print(f"✅ '{new_default[1]}' set as new default")
        else:
            print("\n❌ No other verified email found!")
            print("💡 Please add another verified email first")
            db.close()
            return
    
    # 4. Check if this email is used in campaigns
    check_campaigns = text("""
        SELECT COUNT(*) FROM campaigns 
        WHERE sender_identity_id = :email_id
    """)
    campaign_count = db.execute(check_campaigns, {"email_id": result[0]}).scalar()
    
    if campaign_count > 0:
        print(f"\n⚠️  This email is used in {campaign_count} campaign(s)")
        print("💡 Reassigning campaigns to new default email...")
        
        # Get the new default email
        new_default_email = get_default_email(db)
        
        if new_default_email:
            # Reassign campaigns to new default
            reassign_campaigns = text("""
                UPDATE campaigns 
                SET sender_identity_id = (
                    SELECT id FROM email_addresses 
                    WHERE email = :new_default_email 
                    LIMIT 1
                )
                WHERE sender_identity_id = :email_id
            """)
            db.execute(reassign_campaigns, {
                "email_id": result[0],
                "new_default_email": new_default_email
            })
            db.commit()
            print(f"  ✅ Reassigned {campaign_count} campaign(s) to {new_default_email}")
        else:
            print("❌ No default email found to reassign campaigns")
            db.close()
            return
    
    # 5. Final confirmation
    print("\n" + "="*60)
    print(f"⚠️  You are about to delete: {result[1]}")
    print("="*60)
    confirm = input("\nType 'DELETE' to confirm: ")
    
    if confirm != "DELETE":
        print("❌ Deletion cancelled")
        db.close()
        return
    
    # 6. Delete the email
    delete_query = text("""
        DELETE FROM email_addresses 
        WHERE email = 'vignesh.dhandapani@wynsync.tech'
    """)
    db.execute(delete_query)
    db.commit()
    
    print("\n" + "="*60)
    print("✅ Email deleted successfully!")
    print("="*60)
    
    # 7. Verify deletion
    verify_query = text("""
        SELECT COUNT(*) FROM email_addresses 
        WHERE email = 'vignesh.dhandapani@wynsync.tech'
    """)
    count = db.execute(verify_query).scalar()
    
    if count == 0:
        print("✅ Verified: Email no longer exists in database")
    else:
        print("⚠️ Warning: Email still exists!")
    
    # 8. Show remaining emails
    print("\n📧 Remaining email addresses:")
    print("-"*60)
    remaining_emails = get_all_emails(db)
    for row in remaining_emails:
        default_marker = "⭐ " if row[2] else "   "
        print(f"{default_marker}{row[1]} - Status: {row[3]}")
    print("-"*60)
    
    # 9. Show current default
    current_default = get_default_email(db)
    if current_default:
        print(f"\n✅ Current default email: {current_default}")
    else:
        print("\n⚠️  No default email set!")
    
    db.close()

if __name__ == "__main__":
    safe_remove_vignesh_email()
# simple_migration.py - Place in E:\wynReach\backend\
import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, SessionLocal
from sqlalchemy import text
from app.models.sender_identity import EmailDomain, WhatsAppNumber

def run_migration():
    try:
        # Create a connection
        conn = engine.connect()
        
        # Check if email_addresses table exists
        result = conn.execute(text("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='email_addresses'
        """))
        
        if not result.fetchone():
            print("📝 Creating email_addresses table...")
            # Create email_addresses table
            conn.execute(text("""
                CREATE TABLE email_addresses (
                    id VARCHAR(50) PRIMARY KEY,
                    user_id VARCHAR(50) NOT NULL,
                    domain_id VARCHAR(50) NOT NULL,
                    email VARCHAR(255) UNIQUE NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Create indexes
            conn.execute(text("CREATE INDEX idx_email_user_id ON email_addresses(user_id)"))
            conn.execute(text("CREATE INDEX idx_email_domain_id ON email_addresses(domain_id)"))
            print("✅ email_addresses table created")
        else:
            print("✅ email_addresses table already exists")
        
        # Check if dmarc_status column exists in email_domains
        try:
            conn.execute(text("ALTER TABLE email_domains ADD COLUMN dmarc_status VARCHAR(20) DEFAULT 'pending'"))
            print("✅ Added dmarc_status column to email_domains")
        except Exception as e:
            if "duplicate column" in str(e).lower():
                print("✅ dmarc_status column already exists")
            else:
                print(f"Note: {e}")
        
        conn.commit()
        conn.close()
        print("\n🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nMake sure your database is running and configuration is correct")

if __name__ == "__main__":
    run_migration()
# backend/scripts/migrate_sequences.py
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.database import get_main_db
from sqlalchemy import text

def migrate_sequences():
    """Migrate automation_sequences table with new columns"""
    
    print("\n" + "="*60)
    print("🔧 MIGRATING AUTOMATION_SEQUENCES TABLE")
    print("="*60)
    
    db = next(get_main_db())
    
    try:
        # Check if table exists
        check = db.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'automation_sequences'
            )
        """)).scalar()
        
        if not check:
            print("❌ Table doesn't exist! Creating...")
            
            db.execute(text("""
                CREATE TABLE automation_sequences (
                    id VARCHAR(50) PRIMARY KEY,
                    workspace_id INTEGER DEFAULT 1,
                    name VARCHAR(255) NOT NULL,
                    description TEXT,
                    status VARCHAR(20) DEFAULT 'paused',
                    campaign_id VARCHAR(50),
                    campaign_name VARCHAR(255),
                    campaign_channel VARCHAR(20),
                    list_id VARCHAR(50),
                    list_name VARCHAR(255),
                    engagement_required VARCHAR(20) DEFAULT 'all',
                    send_re_engagement VARCHAR(20) DEFAULT 'skip',
                    re_engagement_template_id VARCHAR(50),
                    steps JSONB DEFAULT '[]',
                    total_triggered INTEGER DEFAULT 0,
                    completed_count INTEGER DEFAULT 0,
                    last_triggered_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """))
            db.commit()
            print("✅ Table created!")
        else:
            print("✅ Table exists! Adding new columns...")
            
            # Add campaign_id column
            try:
                db.execute(text("ALTER TABLE automation_sequences ADD COLUMN campaign_id VARCHAR(50)"))
                print("✅ Added campaign_id column")
            except Exception as e:
                print(f"⚠️ campaign_id column already exists: {e}")
            
            # Add campaign_name column
            try:
                db.execute(text("ALTER TABLE automation_sequences ADD COLUMN campaign_name VARCHAR(255)"))
                print("✅ Added campaign_name column")
            except Exception as e:
                print(f"⚠️ campaign_name column already exists: {e}")
            
            # Add campaign_channel column
            try:
                db.execute(text("ALTER TABLE automation_sequences ADD COLUMN campaign_channel VARCHAR(20)"))
                print("✅ Added campaign_channel column")
            except Exception as e:
                print(f"⚠️ campaign_channel column already exists: {e}")
            
            # Add engagement_required column
            try:
                db.execute(text("ALTER TABLE automation_sequences ADD COLUMN engagement_required VARCHAR(20) DEFAULT 'all'"))
                print("✅ Added engagement_required column")
            except Exception as e:
                print(f"⚠️ engagement_required column already exists: {e}")
            
            # Add send_re_engagement column
            try:
                db.execute(text("ALTER TABLE automation_sequences ADD COLUMN send_re_engagement VARCHAR(20) DEFAULT 'skip'"))
                print("✅ Added send_re_engagement column")
            except Exception as e:
                print(f"⚠️ send_re_engagement column already exists: {e}")
            
            # Add re_engagement_template_id column
            try:
                db.execute(text("ALTER TABLE automation_sequences ADD COLUMN re_engagement_template_id VARCHAR(50)"))
                print("✅ Added re_engagement_template_id column")
            except Exception as e:
                print(f"⚠️ re_engagement_template_id column already exists: {e}")
            
            db.commit()
        
        print("\n" + "="*60)
        print("✅ Migration completed successfully!")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        db.rollback()
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    migrate_sequences()
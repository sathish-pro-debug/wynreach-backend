# backend/scripts/create_sequence_tables.py
import sys
import os
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# ✅ Import using the correct names
from app.database import get_main_db
from sqlalchemy import text

def create_tables():
    """Create sequence tables using raw SQL"""
    
    print("\n" + "="*60)
    print("📋 CREATING SEQUENCE TABLES")
    print("="*60)
    
    db = next(get_main_db())
    
    try:
        # ✅ Create automation_sequences table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS automation_sequences (
                id VARCHAR(50) PRIMARY KEY,
                workspace_id INTEGER NOT NULL DEFAULT 1,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                status VARCHAR(20) DEFAULT 'paused',
                list_id VARCHAR(50),
                list_name VARCHAR(255),
                steps JSONB DEFAULT '[]',
                total_triggered INTEGER DEFAULT 0,
                completed_count INTEGER DEFAULT 0,
                last_triggered_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # ✅ Create sequence_executions table
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS sequence_executions (
                id VARCHAR(50) PRIMARY KEY,
                sequence_id VARCHAR(50) NOT NULL,
                contact_id INTEGER,
                current_step INTEGER DEFAULT 0,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                status VARCHAR(20) DEFAULT 'in_progress',
                last_message_sent_at TIMESTAMP,
                details JSONB DEFAULT '{}'
            )
        """))
        
        # ✅ Create indexes
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_automation_sequences_workspace_id 
            ON automation_sequences(workspace_id)
        """))
        
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_automation_sequences_status 
            ON automation_sequences(status)
        """))
        
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_sequence_executions_sequence_id 
            ON sequence_executions(sequence_id)
        """))
        
        db.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_sequence_executions_contact_id 
            ON sequence_executions(contact_id)
        """))
        
        db.commit()
        print("✅ Tables created successfully!")
        
        # ✅ Verify tables
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name IN ('automation_sequences', 'sequence_executions')
        """))
        tables = result.fetchall()
        
        if tables:
            print(f"\n📊 Tables created:")
            for table in tables:
                print(f"   ✅ {table[0]}")
        else:
            print("\n⚠️ Tables not found after creation")
            
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
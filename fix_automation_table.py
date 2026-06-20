# fix_automation_table.py
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import main_engine
from sqlalchemy import text

def fix_table():
    print("🔧 Fixing automation_rules table...")
    
    with main_engine.connect() as conn:
        # Drop existing table
        try:
            conn.execute(text("DROP TABLE IF EXISTS automation_rules"))
            print("✅ Dropped existing table")
        except Exception as e:
            print(f"Note: {e}")
        
        # Create new table without user_id
        conn.execute(text("""
            CREATE TABLE automation_rules (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                description TEXT,
                campaign_id VARCHAR(50) NOT NULL,
                campaign_name VARCHAR(255),
                campaign_channel VARCHAR(20) NOT NULL,
                trigger_type VARCHAR(50) NOT NULL,
                trigger_config JSON,
                condition_type VARCHAR(50) DEFAULT 'always',
                condition_config JSON,
                action_type VARCHAR(50) NOT NULL,
                action_config JSON,
                is_active BOOLEAN DEFAULT TRUE,
                execution_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
        print("✅ Created new automation_rules table")
        
        # Create indexes
        conn.execute(text("CREATE INDEX idx_automation_rules_campaign_id ON automation_rules(campaign_id)"))
        print("✅ Created indexes")
        
        conn.commit()
    
    print("\n🎉 Table fixed successfully!")

if __name__ == "__main__":
    fix_table()
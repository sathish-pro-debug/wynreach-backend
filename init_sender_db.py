# backend/init_sender_db.py
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import main_engine, Base
from app.models import sender_identity  # This imports the models and registers them with Base

def create_tables():
    print("=" * 50)
    print("Creating Sender Identity Tables")
    print("=" * 50)
    
    try:
        # Create all tables that haven't been created yet
        Base.metadata.create_all(bind=main_engine)
        print("✅ Tables created successfully!")
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(main_engine)
        existing_tables = inspector.get_table_names()
        
        print("\n📋 Tables in database:")
        for table in existing_tables:
            if table in ['email_domains', 'whatsapp_numbers', 'dns_records']:
                print(f"   ✅ {table}")
            else:
                print(f"   - {table}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_tables()
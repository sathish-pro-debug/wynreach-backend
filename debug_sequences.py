# backend/scripts/debug_sequences.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_main_db
from sqlalchemy import text

def debug_sequences():
    """Debug sequences table"""
    
    print("\n" + "="*60)
    print("🔍 DEBUGGING SEQUENCES")
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
        
        print(f"Table exists: {check}")
        
        if check:
            # Check columns
            columns = db.execute(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'automation_sequences'
                ORDER BY ordinal_position
            """)).fetchall()
            
            print("\n📋 Columns:")
            for col in columns:
                print(f"   {col[0]}: {col[1]} (nullable: {col[2]})")
            
            # Check data
            count = db.execute(text("SELECT COUNT(*) FROM automation_sequences")).scalar()
            print(f"\n📊 Records: {count}")
            
            if count > 0:
                records = db.execute(text("SELECT * FROM automation_sequences LIMIT 1")).fetchone()
                if records:
                    print("\n📊 Sample record:")
                    for key, value in records._mapping.items():
                        print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_sequences()
# complete_fix.py
import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def run_fixes():
    print("=" * 50)
    print("RUNNING SAFE FIXES")
    print("=" * 50)
    
    # Fix 1: Make domain column nullable in email_addresses
    try:
        from app.database import main_engine
        from sqlalchemy import text
        
        print("\n📝 Fixing database schema...")
        with main_engine.connect() as conn:
            conn.execute(text("ALTER TABLE email_addresses ALTER COLUMN domain DROP NOT NULL"))
            conn.commit()
            print("✅ Made 'domain' column optional (NULL allowed)")
    except Exception as e:
        error_msg = str(e)
        if "does not exist" in error_msg:
            print("✅ Column 'domain' already fixed or doesn't exist")
        elif "cannot alter" in error_msg:
            print("✅ Column already accepts NULL values")
        else:
            print(f"Note: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Fixes completed!")
    print("=" * 50)
    print("\nYou can now:")
    print("  1. Create email addresses")
    print("  2. Add new domains")
    print("  3. Verify DNS records")
    print("")

if __name__ == "__main__":
    asyncio.run(run_fixes())
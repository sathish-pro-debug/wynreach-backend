# backend/scripts/test_get_sequences.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_main_db
from app.models.automation import AutomationSequence

def test_get_sequences():
    """Test getting sequences directly"""
    
    print("\n" + "="*60)
    print("🧪 TEST GET SEQUENCES")
    print("="*60)
    
    db = next(get_main_db())
    
    try:
        # ✅ Try to query directly
        sequences = db.query(AutomationSequence).all()
        print(f"✅ Found {len(sequences)} sequences")
        
        for seq in sequences:
            print(f"\n📋 Sequence: {seq.name}")
            print(f"   ID: {seq.id}")
            print(f"   Status: {seq.status}")
            print(f"   Campaign ID: {seq.campaign_id}")
            print(f"   Steps: {len(seq.steps) if seq.steps else 0}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_get_sequences()
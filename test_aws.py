# test_aws.py
import asyncio
import sys
import os

# Add the current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_aws():
    print("\n" + "=" * 60)
    print("TESTING AWS SES CONNECTION")
    print("=" * 60 + "\n")
    
    try:
        from app.services.aws_ses_service import ses_service
        print("✅ Successfully imported ses_service\n")
        
        # Test getting status for wynsync.tech
        domain = "wynsync.tech"
        print(f"Testing verification status for: {domain}\n")
        
        status = await ses_service.get_verification_status(domain)
        
        print("\n" + "=" * 60)
        print("RESULTS:")
        print("=" * 60)
        print(f"Domain: {status['domain']}")
        print(f"Verification Status: {status['verification_status']}")
        print(f"Is Verified: {status['is_verified']}")
        print(f"DKIM Enabled: {status['dkim_enabled']}")
        print(f"DKIM Status: {status['dkim_verification_status']}")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_aws())
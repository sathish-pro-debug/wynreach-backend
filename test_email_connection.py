# backend/scripts/test_email_connection.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from datetime import datetime
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_email_connection():
    """Test email sending with full debugging"""
    
    print("\n" + "="*60)
    print("📧 TEST EMAIL CONNECTION")
    print("="*60)
    
    # 1. Check environment variables
    print("\n1️⃣ CHECKING ENVIRONMENT:")
    print(f"   SES_FROM_EMAIL: {os.getenv('SES_FROM_EMAIL')}")
    print(f"   AWS_REGION: {os.getenv('AWS_REGION')}")
    print(f"   AWS_ACCESS_KEY_ID: {os.getenv('AWS_ACCESS_KEY_ID')[:10]}...")
    
    # 2. Test AWS SES connection
    print("\n2️⃣ TESTING AWS SES CONNECTION:")
    try:
        ses_client = boto3.client(
            'ses',
            region_name=os.getenv("AWS_REGION", "ap-south-1"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        # Check if email is verified
        from_email = os.getenv("SES_FROM_EMAIL", "noreply@wynsync.tech")
        response = ses_client.get_identity_verification_attributes(
            Identities=[from_email]
        )
        
        print(f"   Verification Status: {response}")
        
        # List verified emails
        verified = ses_client.list_verified_email_addresses()
        print(f"   Verified emails: {verified['VerifiedEmailAddresses']}")
        
    except ClientError as e:
        print(f"   ❌ AWS Error: {e.response['Error']['Message']}")
        return
    except Exception as e:
        print(f"   ❌ Error: {str(e)}")
        return
    
    # 3. Send test email
    print("\n3️⃣ SENDING TEST EMAIL:")
    test_email = input("   Enter email address to test: ").strip()
    
    if not test_email:
        print("   ❌ No email provided")
        return
    
    print(f"   Sending to: {test_email}")
    print(f"   From: {os.getenv('SES_FROM_EMAIL', 'noreply@wynsync.tech')}")
    
    # ✅ FIX: Use 'recipients' instead of 'to_email'
    from app.services.email_service import send_email
    
    print("\n   📤 Attempting to send email...")
    
    result = await send_email(
        tenant_id=1,
        recipients=[test_email],  # ✅ Correct: recipients is a list
        subject="🧪 Test Email from WynReach",
        html_body=f"""
        <h1>✅ Test Email</h1>
        <p>This is a test email from WynReach.</p>
        <p>If you received this, your email system is working!</p>
        <hr>
        <p><small>Sent at: {datetime.now().isoformat()}</small></p>
        """,
        from_email=os.getenv("SES_FROM_EMAIL", "noreply@wynsync.tech")
    )
    
    print(f"\n📊 RESULT:")
    print(f"   Success: {result.get('success')}")
    print(f"   MessageId: {result.get('message_id')}")
    print(f"   Error: {result.get('error')}")
    
    if result.get('success'):
        print("\n✅ Email sent successfully!")
        print("📧 Check your inbox and spam folder.")
    else:
        print(f"\n❌ Failed: {result.get('error')}")
        print("💡 Check AWS SES configuration and verify the email address.")

if __name__ == "__main__":
    asyncio.run(test_email_connection())
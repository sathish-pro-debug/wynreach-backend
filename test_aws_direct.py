# complete_aws_diagnostic.py
import boto3
from botocore.exceptions import ClientError
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

print("=" * 60)
print("🚀 COMPLETE AWS SES DIAGNOSTIC")
print("=" * 60)

# Your AWS credentials
AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_REGION = settings.AWS_REGION

print(f"\n📋 Configuration Check:")
print(f"  Region: {AWS_REGION}")
print(f"  Access Key: {AWS_ACCESS_KEY_ID[:10]}...")
print(f"  Secret Key: {'*' * 10}")

# List of all SES actions to test
SES_ACTIONS = [
    # Quota & Account
    "ses:GetSendQuota",
    "ses:GetSendStatistics", 
    "ses:GetAccount",
    
    # Identity Management
    "ses:GetIdentityVerificationAttributes",
    "ses:GetIdentityDkimAttributes",
    "ses:GetIdentityMailFromDomainAttributes",
    "ses:GetIdentityNotificationAttributes",
    "ses:ListIdentities",
    "ses:ListEmailIdentities",
    
    # Domain Verification
    "ses:VerifyDomainIdentity",
    "ses:VerifyDomainDkim",
    "ses:DeleteIdentity",
    
    # Email Sending
    "ses:SendEmail",
    "ses:SendRawEmail",
    
    # Configuration
    "ses:ListConfigurationSets",
    "ses:GetConfigurationSet",
]

print("\n🔍 Testing AWS SES Permissions:")
print("-" * 60)

def test_action(action_name, client):
    """Test if a specific SES action is allowed"""
    try:
        # Map action to actual API call
        if action_name == "ses:GetSendQuota":
            client.get_send_quota()
        elif action_name == "ses:GetSendStatistics":
            client.get_send_statistics()
        elif action_name == "ses:GetAccount":
            client.get_account()
        elif action_name == "ses:GetIdentityVerificationAttributes":
            client.get_identity_verification_attributes(Identities=['example.com'])
        elif action_name == "ses:GetIdentityDkimAttributes":
            client.get_identity_dkim_attributes(Identities=['example.com'])
        elif action_name == "ses:ListIdentities":
            client.list_identities()
        elif action_name == "ses:ListEmailIdentities":
            client.list_email_identities()
        elif action_name == "ses:VerifyDomainIdentity":
            # Don't actually verify, just check permission
            try:
                client.verify_domain_identity(Domain='test-permission.com')
                return True, "SUCCESS (would work)"
            except ClientError as e:
                if "Already exists" in str(e):
                    return True, "SUCCESS (permission exists)"
                return False, f"FAILED: {e.response['Error']['Message']}"
        elif action_name == "ses:VerifyDomainDkim":
            try:
                client.verify_domain_dkim(Domain='test-permission.com')
                return True, "SUCCESS (would work)"
            except ClientError as e:
                if "Already exists" in str(e):
                    return True, "SUCCESS (permission exists)"
                return False, f"FAILED: {e.response['Error']['Message']}"
        else:
            return True, "SKIPPED (not tested)"
        
        return True, "✅ SUCCESS"
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'AccessDenied':
            return False, f"❌ DENIED: {e.response['Error']['Message']}"
        elif error_code == 'ValidationError':
            return True, f"⚠️ VALIDATION (permission exists, but test failed)"
        else:
            return False, f"❌ ERROR: {e.response['Error']['Message']}"
    except Exception as e:
        return False, f"❌ ERROR: {str(e)}"

try:
    # Create client
    client = boto3.client(
        'ses',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    
    results = {}
    
    for action in SES_ACTIONS:
        success, message = test_action(action, client)
        results[action] = success
        status_icon = "✅" if success else "❌"
        print(f"  {status_icon} {action:<50} {message[:60]}")
    
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    allowed = [a for a, s in results.items() if s]
    denied = [a for a, s in results.items() if not s]
    
    print(f"\n✅ Allowed: {len(allowed)}")
    for action in allowed:
        print(f"   - {action}")
    
    if denied:
        print(f"\n❌ Denied: {len(denied)}")
        for action in denied:
            print(f"   - {action}")
        
        print("\n🚨 MISSING PERMISSIONS NEEDED:")
        print("   Add these to your IAM policy:")
        print()
        print('{')
        print('    "Version": "2012-10-17",')
        print('    "Statement": [')
        print('        {')
        print('            "Effect": "Allow",')
        print('            "Action": [')
        for action in denied:
            print(f'                "{action}",')
        print('            ],')
        print('            "Resource": "*"')
        print('        }')
        print('    ]')
        print('}')
    
    print("\n" + "=" * 60)
    print("🔧 RECOMMENDED FIX")
    print("=" * 60)
    print("   1. Go to AWS Console → IAM → Users")
    print("   2. Click on SES-Whatsapp-Automation-Wynsync-Production")
    print("   3. Click 'Add permissions' → 'Attach existing policies directly'")
    print("   4. Search and select 'AmazonSESFullAccess'")
    print("   5. Click 'Add permissions'")
    print("   6. Wait 1-2 minutes")
    print("   7. Run this script again")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ Connection Error: {e}")
    print("\nPlease check:")
    print("1. AWS credentials in .env file")
    print("2. Internet connection")
    print("3. AWS region (ap-south-1)")
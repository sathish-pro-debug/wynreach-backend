# update_db.py
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_main_db
from app.models.sender_identity import EmailDomain
import boto3
from app.core.config import settings
import uuid
import json

# ✅ Get the database session correctly
db = next(get_main_db())

domain_name = "wynsync.tech"

# Check AWS status
client = boto3.client(
    'ses',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_REGION
)

response = client.get_identity_verification_attributes(
    Identities=[domain_name]
)

aws_status = response['VerificationAttributes'].get(domain_name, {}).get('VerificationStatus', 'Pending')

print(f"AWS Status for {domain_name}: {aws_status}")

if aws_status == 'Success':
    # Update database
    domain = db.query(EmailDomain).filter(
        EmailDomain.domain == domain_name
    ).first()
    
    if domain:
        domain.aws_verification_status = "success"
        domain.dkim_status = "verified"
        domain.spf_status = "verified"
        domain.dmarc_status = "verified"
        domain.verification_details = "✅ Domain verified in AWS SES"
        db.commit()
        print(f"✅ Updated {domain_name} to verified in database")
    else:
        print(f"❌ Domain {domain_name} not found in database")
        print("   Creating domain record...")
        
        # Create domain record
        new_domain = EmailDomain(
            id=str(uuid.uuid4()),
            user_id="2",  # Update with your user ID
            domain=domain_name,
            sender_name="WynSync",
            from_email="noreply@wynsync.tech",
            dkim_status="verified",
            spf_status="verified",
            dmarc_status="verified",
            aws_verification_token="already_verified",
            aws_dkim_tokens=json.dumps([]),
            aws_verification_status="success",
            verification_details="✅ Domain verified in AWS SES"
        )
        db.add(new_domain)
        db.commit()
        print(f"✅ Created {domain_name} with verified status")
else:
    print(f"⏳ Domain not yet verified in AWS (Status: {aws_status})")

db.close()
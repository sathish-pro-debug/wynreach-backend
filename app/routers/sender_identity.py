# app/routers/sender_identity.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
import json
import boto3
import random
import string
from datetime import datetime, timedelta

from app.database import get_main_db
from app.models.sender_identity import EmailDomain, EmailAddress, WhatsAppNumber
from app.services.aws_ses_service import AWSSESService
from app.services.auth_service import get_current_user
from app.core.config import settings

router = APIRouter()

# Initialize AWS SES Service
aws_ses = AWSSESService()

# ============ SCHEMAS ============
class EmailDomainCreate(BaseModel):
    domain: str = Field(..., example="mycompany.com")
    sender_name: str = Field(..., example="My Company")
    email_address: EmailStr = Field(..., example="hello@mycompany.com")

class EmailDomainResponse(BaseModel):
    id: str
    domain: str
    sender_name: str
    from_email: str
    reply_to_email: Optional[str] = None
    dkim_status: str
    spf_status: str
    dmarc_status: str = "pending"
    is_default: bool = False
    verification_status: str = "pending"
    aws_verification_status: str = "pending"
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class VerifyDomainRequest(BaseModel):
    domain_id: str

class SetDefaultDomainRequest(BaseModel):
    domain_id: str

class EmailAddressCreate(BaseModel):
    email: EmailStr
    domain_id: str

class EmailAddressResponse(BaseModel):
    id: str
    email: str
    status: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class WhatsAppCreate(BaseModel):
    phone_number: str = Field(..., example="+919840012345")
    account_name: str = Field(..., example="My Business")

class WhatsAppResponse(BaseModel):
    id: str
    phone_number: str
    account_name: str
    status: str
    templates_count: int = 0
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OTPVerifyRequest(BaseModel):
    otp: str

# ============ HEALTH CHECK ============
@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "Sender Identity router is working with AWS SES"}

# ============ EMAIL DOMAINS ============
@router.get("/email-domains", response_model=List[EmailDomainResponse])
async def get_email_domains(
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Get all email domains with real-time verification status"""
    
    user_id = str(current_user.id)
    
    domains = db.query(EmailDomain).filter(
        EmailDomain.user_id == user_id
    ).all()
    
    result = []
    for domain in domains:
        try:
            aws_status = await aws_ses.get_complete_status(domain.domain)
            is_verified = aws_status['is_verified']
            
            if is_verified and domain.aws_verification_status != "success":
                domain.aws_verification_status = "success"
                domain.dkim_status = "verified"
                domain.spf_status = "verified"
                domain.dmarc_status = "verified"
                db.commit()
                
        except Exception as e:
            print(f"⚠️ Error checking {domain.domain}: {e}")
            is_verified = domain.aws_verification_status == "success"
        
        # ✅ Determine status: Active, Inactive, or Pending
        if not is_verified:
            verification_status = "pending"
        elif domain.is_active:
            verification_status = "active"
        else:
            verification_status = "inactive"
        
        result.append(EmailDomainResponse(
            id=domain.id,
            domain=domain.domain,
            sender_name=domain.sender_name,
            from_email=domain.from_email,
            reply_to_email=domain.reply_to_email,
            dkim_status=domain.dkim_status,
            spf_status=domain.spf_status,
            dmarc_status=getattr(domain, 'dmarc_status', 'pending'),
            is_default=domain.is_default,
            verification_status=verification_status,
            aws_verification_status="success" if is_verified else "pending",
            created_at=domain.created_at,
            is_active=domain.is_active
        ))
    
    return result

# ============ ONLY ONE create_email_domain - THIS IS THE CORRECT VERSION ============
@router.post("/email-domains", response_model=EmailDomainResponse)
async def create_email_domain(
    domain_data: EmailDomainCreate,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Add a new email domain - Always shows DNS records, verification happens on Verify DNS click"""
    
    user_id = str(current_user.id)
    
    # Check if domain already exists in database
    existing = db.query(EmailDomain).filter(
        EmailDomain.domain == domain_data.domain,
        EmailDomain.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Domain already added")
    
    # ✅ Initialize variables
    verification_token = "skip_aws"
    dkim_tokens = []
    aws_status = "pending"
    is_verified = False
    
    # ✅ Check if domain exists in AWS (but don't auto-verify)
    if aws_ses.initialized:
        try:
            aws_status_info = await aws_ses.get_complete_status(domain_data.domain)
            
            print(f"\n🔍 Checking AWS status for: {domain_data.domain}")
            print(f"   Exists in AWS: {aws_status_info['exists']}")
            print(f"   Is Verified: {aws_status_info['is_verified']}")
            print(f"   Status: {aws_status_info['verification_status']}")
            
            # ✅ Get DKIM tokens if they exist
            dkim_tokens = aws_status_info.get('dkim_tokens', [])
            
            # ✅ If domain exists in AWS, store the verification token
            if aws_status_info['exists']:
                verification_token = "already_in_aws"
                is_verified = aws_status_info['is_verified']
                aws_status = "success" if is_verified else "pending"
                
                # ✅ If domain is already verified, store the DKIM tokens for DNS records
                if is_verified and dkim_tokens:
                    print(f"ℹ️ Domain {domain_data.domain} is already verified in AWS")
            
        except Exception as e:
            print(f"Error checking AWS: {e}")
            # Fall through to normal flow
    
    # ✅ Always generate DNS records (even if verified in AWS)
    # Only initiate verification if domain doesn't exist in AWS
    if not is_verified and verification_token == "skip_aws":
        try:
            print(f"🚀 Initiating AWS verification for {domain_data.domain}")
            verification_token, dkim_tokens = await aws_ses.initiate_verification(domain_data.domain)
            aws_status = "pending"
        except Exception as e:
            print(f"⚠️ AWS initiation failed: {e}")
            verification_token = "skip_aws"
            dkim_tokens = []
            aws_status = "pending"
    
    # ✅ Create domain - ALWAYS as "pending" (verification happens on Verify DNS click)
    new_domain = EmailDomain(
        id=str(uuid.uuid4()),
        user_id=user_id,
        domain=domain_data.domain,
        sender_name=domain_data.sender_name,
        from_email=domain_data.email_address,
        dkim_status="pending",
        spf_status="pending",
        dmarc_status="pending",
        aws_verification_token=verification_token,
        aws_dkim_tokens=json.dumps(dkim_tokens),
        aws_verification_status="pending",  # ✅ Always pending initially
        verification_details="DNS records generated. Click 'Verify DNS' to check verification status."
    )
    
    db.add(new_domain)
    db.commit()
    db.refresh(new_domain)
    
    return EmailDomainResponse(
        id=new_domain.id,
        domain=new_domain.domain,
        sender_name=new_domain.sender_name,
        from_email=new_domain.from_email,
        dkim_status="pending",
        spf_status="pending",
        dmarc_status="pending",
        is_default=new_domain.is_default,
        verification_status="pending",  # ✅ Always pending initially
        aws_verification_status="pending",
        created_at=new_domain.created_at
    )

@router.get("/email-domains/{domain_id}/dns-instructions")
async def get_dns_instructions(
    domain_id: str,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Get DNS records for domain verification - ALWAYS returns records"""
    
    user_id = str(current_user.id)
    
    domain = db.query(EmailDomain).filter(
        EmailDomain.id == domain_id,
        EmailDomain.user_id == user_id
    ).first()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    # ✅ Get DKIM tokens from database
    dkim_tokens = json.loads(domain.aws_dkim_tokens) if domain.aws_dkim_tokens else []
    
    # ✅ If no tokens in DB, try to get from AWS
    if not dkim_tokens:
        try:
            if aws_ses.initialized:
                aws_status = await aws_ses.get_complete_status(domain.domain)
                dkim_tokens = aws_status.get('dkim_tokens', [])
                if dkim_tokens:
                    domain.aws_dkim_tokens = json.dumps(dkim_tokens)
                    db.commit()
                    print(f"✅ Fetched DKIM tokens from AWS for {domain.domain}")
        except Exception as e:
            print(f"Could not fetch DKIM tokens from AWS: {e}")
    
    # ✅ ALWAYS generate DNS records
    records = await aws_ses.get_dns_records(
        domain.domain,
        domain.aws_verification_token,
        dkim_tokens
    )
    
    return {
        "domain": domain.domain,
        "provider": "AWS SES",
        "already_verified": domain.aws_verification_status == "success",
        "message": "✅ This domain is already verified!" if domain.aws_verification_status == "success" else "Add these records to verify your domain",
        "instructions": """
            IMPORTANT: Add ALL the following DNS records to your domain provider:
            1. Go to your DNS provider (AWS Route53, GoDaddy, Cloudflare, etc.)
            2. Add each record exactly as shown below
            3. Wait 5-30 minutes for DNS propagation
            4. Click 'Verify DNS' button to check records
            5. Once verified, you can create email addresses
        """,
        "records": records
    }

@router.post("/email-domains/verify")
async def verify_domain(
    request: VerifyDomainRequest,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Verify domain by checking real status with AWS SES - Called when user clicks Verify DNS"""
    
    user_id = str(current_user.id)
    
    domain = db.query(EmailDomain).filter(
        EmailDomain.id == request.domain_id,
        EmailDomain.user_id == user_id
    ).first()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    print(f"\n🔍 Verifying domain: {domain.domain}")
    
    # ✅ Check AWS status
    aws_status = await aws_ses.get_complete_status(domain.domain)
    is_verified = aws_status['is_verified']
    
    print(f"   AWS Status: {aws_status['verification_status']}")
    print(f"   Is Verified: {is_verified}")
    
    # ✅ Always update database based on AWS status
    if is_verified:
        domain.aws_verification_status = "success"
        domain.dkim_status = "verified"
        domain.spf_status = "verified"
        domain.dmarc_status = "verified"
        domain.verification_details = "✅ Domain verified successfully with AWS SES"
        db.commit()
        print(f"✅ Domain {domain.domain} verified successfully!")
        
        # ✅ Fetch and store DKIM tokens
        dkim_tokens = aws_status.get('dkim_tokens', [])
        if dkim_tokens:
            domain.aws_dkim_tokens = json.dumps(dkim_tokens)
            db.commit()
    else:
        domain.aws_verification_status = aws_status['verification_status'].lower()
        domain.verification_details = f"⏳ Status: {aws_status['verification_status']}. Please add DNS records."
        db.commit()
    
    return {
        "verified": is_verified,
        "status": "verified" if is_verified else aws_status['verification_status'].lower(),
        "domain": domain.domain,
        "dkim_enabled": aws_status.get('dkim_enabled', False),
        "message": f"AWS SES verification status: {aws_status['verification_status']}"
    }

@router.put("/email-domains/set-default")
async def set_default_domain(
    request: SetDefaultDomainRequest,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Set a domain as default"""
    
    user_id = str(current_user.id)
    
    # Remove default from all domains
    db.query(EmailDomain).filter(
        EmailDomain.user_id == user_id
    ).update({"is_default": False})
    
    domain = db.query(EmailDomain).filter(
        EmailDomain.id == request.domain_id,
        EmailDomain.user_id == user_id
    ).first()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    domain.is_default = True
    db.commit()
    
    return {"message": "Default domain updated"}

@router.delete("/email-domains/{domain_id}")
async def delete_email_domain(
    domain_id: str,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Delete domain from database - AWS deletion is skipped if restricted"""
    
    user_id = str(current_user.id)
    
    domain = db.query(EmailDomain).filter(
        EmailDomain.id == domain_id,
        EmailDomain.user_id == user_id
    ).first()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    domain_name = domain.domain
    
    # Try to delete from AWS SES (if policy allows)
    try:
        ses_client = boto3.client(
            'ses',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        ses_client.delete_identity(Identity=domain_name)
        print(f"✅ Domain {domain_name} deleted from AWS SES")
    except Exception as e:
        # If delete is restricted, just log it and continue
        print(f"⚠️ Could not delete from AWS SES (policy may restrict delete): {e}")
        # Continue with database deletion
    
    # Delete associated email addresses
    db.query(EmailAddress).filter(EmailAddress.domain_id == domain_id).delete()
    
    # Delete domain from database
    db.delete(domain)
    db.commit()
    
    return {"message": f"Domain {domain_name} deleted from database"}

# ============ EMAIL ADDRESSES WITH OTP VERIFICATION ============

@router.get("/email-addresses", response_model=List[EmailAddressResponse])
async def get_email_addresses(
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user),
    include_inactive: bool = False
):
    """Get all email addresses for current user"""
    user_id = str(current_user.id)
    
    query = db.query(EmailAddress).filter(
        EmailAddress.user_id == user_id
    )
    
    # ✅ By default, only show active email addresses
    if not include_inactive:
        query = query.filter(EmailAddress.is_active == True)
    
    emails = query.all()
    return emails

@router.post("/email-addresses", response_model=EmailAddressResponse)
async def create_email_address(
    email_data: EmailAddressCreate,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Create a new email address (only for verified and ACTIVE domains)"""
    
    user_id = str(current_user.id)
    
    domain = db.query(EmailDomain).filter(
        EmailDomain.id == email_data.domain_id,
        EmailDomain.user_id == user_id
    ).first()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    # ✅ Check if domain is ACTIVE
    if not domain.is_active:
        raise HTTPException(
            status_code=403, 
            detail=f"Cannot create email: Domain '{domain.domain}' is inactive. Please activate the domain first."
        )
    
    if domain.aws_verification_status != "success":
        raise HTTPException(
            status_code=400, 
            detail="Cannot create email: Domain not verified. Please complete DNS verification first."
        )
    
    # Check if email already exists
    existing = db.query(EmailAddress).filter(
        EmailAddress.email == email_data.email
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Email address already exists")
    
    # Generate OTP
    otp = ''.join(random.choices(string.digits, k=6))
    
    new_email = EmailAddress(
        id=str(uuid.uuid4()),
        user_id=user_id,
        domain_id=domain.id,
        email=email_data.email,
        status="pending",
        is_active=True,  # ✅ New emails are active by default
        verification_code=otp,
        verified_at=None
    )
    
    db.add(new_email)
    db.commit()
    db.refresh(new_email)
    
    # Send OTP email
    try:
        await send_otp_email(
            to_email=email_data.email,
            otp=otp,
            email_address=email_data.email
        )
        print(f"✅ OTP email sent to {email_data.email}")
    except Exception as e:
        print(f"⚠️ Failed to send OTP email: {e}")
    
    return new_email

@router.post("/email-addresses/resend-otp/{email_id}")
async def resend_otp(
    email_id: str,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Resend OTP for email verification"""
    
    user_id = str(current_user.id)
    
    email = db.query(EmailAddress).filter(
        EmailAddress.id == email_id,
        EmailAddress.user_id == user_id
    ).first()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email address not found")
    
    if email.status == "verified":
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Generate new OTP
    otp = ''.join(random.choices(string.digits, k=6))
    email.verification_code = otp
    db.commit()
    
    # Send OTP email
    try:
        await send_otp_email(
            to_email=email.email,
            otp=otp,
            email_address=email.email
        )
        return {"message": "OTP sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send OTP: {str(e)}")

@router.post("/email-addresses/verify-otp/{email_id}")
async def verify_email_otp(
    email_id: str,
    otp_data: OTPVerifyRequest,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Verify email address using OTP"""
    
    user_id = str(current_user.id)
    otp = otp_data.otp
    
    if not otp:
        raise HTTPException(status_code=400, detail="OTP is required")
    
    email = db.query(EmailAddress).filter(
        EmailAddress.id == email_id,
        EmailAddress.user_id == user_id
    ).first()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email address not found")
    
    if email.status == "verified":
        raise HTTPException(status_code=400, detail="Email already verified")
    
    # Verify OTP
    if email.verification_code != otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    # Mark as verified
    email.status = "verified"
    email.verified_at = datetime.utcnow()
    email.verification_code = None
    db.commit()
    
    return {"message": "Email verified successfully", "status": "verified"}

@router.delete("/email-addresses/{email_id}")
async def delete_email_address(
    email_id: str,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Delete an email address"""
    user_id = str(current_user.id)
    
    email = db.query(EmailAddress).filter(
        EmailAddress.id == email_id,
        EmailAddress.user_id == user_id
    ).first()
    
    if not email:
        raise HTTPException(status_code=404, detail="Email address not found")
    
    db.delete(email)
    db.commit()
    
    return {"message": "Email address deleted"}

# ============ SEND OTP EMAIL ============

async def send_otp_email(to_email: str, otp: str, email_address: str):
    """Send OTP email using AWS SES"""
    
    ses_client = boto3.client(
        'ses',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION
    )
    
    subject = "Email Address Verification"
    
    html_body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
            .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .header h1 {{ color: #4F46E5; }}
            .otp {{ font-size: 36px; font-weight: bold; color: #4F46E5; text-align: center; padding: 20px; background-color: #F3F4F6; border-radius: 8px; letter-spacing: 8px; margin: 20px 0; }}
            .footer {{ text-align: center; color: #6B7280; font-size: 14px; margin-top: 30px; }}
            .footer p {{ margin: 5px 0; }}
            .details {{ background-color: #F9FAFB; padding: 15px; border-radius: 8px; margin: 20px 0; }}
            .details p {{ margin: 5px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔐 Email Verification</h1>
            </div>
            <p>You've requested to verify this email address for use with your marketing platform.</p>
            <div class="details">
                <p><strong>Email Address:</strong> {email_address}</p>
                <p><strong>Verification Code:</strong></p>
            </div>
            <div class="otp">{otp}</div>
            <p>Enter this 6-digit code in the verification screen to confirm your email address.</p>
            <p><strong>This OTP is valid for 10 minutes.</strong></p>
            <div class="footer">
                <p>If you didn't request this, please ignore this email.</p>
                <p>&copy; 2026 Your Company. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_body = f"""
    Email Address Verification
    
    You've requested to verify this email address: {email_address}
    
    Your verification code is: {otp}
    
    Enter this 6-digit code in the verification screen to confirm your email address.
    
    This OTP is valid for 10 minutes.
    
    If you didn't request this, please ignore this email.
    """
    
    try:
        response = ses_client.send_email(
            Source=settings.SES_FROM_EMAIL,
            Destination={'ToAddresses': [to_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {
                    'Html': {'Data': html_body},
                    'Text': {'Data': text_body}
                }
            }
        )
        return response
    except Exception as e:  
        raise Exception(f"Failed to send email: {str(e)}")

# ============ WHATSAPP NUMBERS ============
@router.get("/whatsapp/numbers", response_model=List[WhatsAppResponse])
async def get_whatsapp_numbers(
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Get all WhatsApp numbers"""
    user_id = str(current_user.id)
    numbers = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.user_id == user_id
    ).all()
    return numbers

@router.post("/whatsapp/numbers", response_model=WhatsAppResponse)
async def create_whatsapp_number(
    wa_data: WhatsAppCreate,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Add a WhatsApp number"""
    user_id = str(current_user.id)
    
    existing = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.phone_number == wa_data.phone_number
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Number already exists")
    
    new_wa = WhatsAppNumber(
        id=str(uuid.uuid4()),
        user_id=user_id,
        phone_number=wa_data.phone_number,
        account_name=wa_data.account_name,
        status="pending"
    )
    
    db.add(new_wa)
    db.commit()
    db.refresh(new_wa)
    
    return new_wa

@router.get("/whatsapp/numbers/{wa_id}/status")
async def get_whatsapp_status(
    wa_id: str,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Get WhatsApp number status"""
    user_id = str(current_user.id)
    
    wa_number = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.id == wa_id,
        WhatsAppNumber.user_id == user_id
    ).first()
    
    if not wa_number:
        raise HTTPException(status_code=404, detail="Number not found")
    
    return {"status": wa_number.status}

@router.delete("/whatsapp/numbers/{wa_id}")
async def delete_whatsapp_number(
    wa_id: str,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Delete a WhatsApp number"""
    user_id = str(current_user.id)
    
    wa_number = db.query(WhatsAppNumber).filter(
        WhatsAppNumber.id == wa_id,
        WhatsAppNumber.user_id == user_id
    ).first()
    
    if not wa_number:
        raise HTTPException(status_code=404, detail="Number not found")
    
    db.delete(wa_number)
    db.commit()
      
    return {"message": "WhatsApp number deleted"}

# app/routers/sender_identity.py

class PauseDomainRequest(BaseModel):
    domain_id: str
    reason: Optional[str] = None

@router.post("/email-domains/pause")
async def pause_domain(
    request: PauseDomainRequest,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Pause a verified domain - prevents it from being used anywhere in the project"""
    
    user_id = str(current_user.id)
    
    domain = db.query(EmailDomain).filter(
        EmailDomain.id == request.domain_id,
        EmailDomain.user_id == user_id
    ).first()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    if domain.aws_verification_status != "success":
        raise HTTPException(status_code=400, detail="Only verified domains can be paused")
    
    if domain.is_paused:
        raise HTTPException(status_code=400, detail="Domain is already paused")
    
    domain.is_paused = True
    domain.paused_at = datetime.utcnow()
    domain.paused_reason = request.reason or "Paused by user"
    db.commit()
    
    return {
        "message": f"Domain {domain.domain} paused successfully",
        "domain": domain.domain,
        "is_paused": True,
        "paused_at": domain.paused_at,
        "reason": domain.paused_reason
    }

@router.post("/email-domains/unpause")
async def unpause_domain(
    request: PauseDomainRequest,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Unpause a paused domain"""
    
    user_id = str(current_user.id)
    
    domain = db.query(EmailDomain).filter(
        EmailDomain.id == request.domain_id,
        EmailDomain.user_id == user_id
    ).first()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    if not domain.is_paused:
        raise HTTPException(status_code=400, detail="Domain is not paused")
    
    domain.is_paused = False
    domain.paused_at = None
    domain.paused_reason = None
    db.commit()
    
    return {
        "message": f"Domain {domain.domain} unpaused successfully",
        "domain": domain.domain,
        "is_paused": False
    }

@router.get("/email-domains/paused")
async def get_paused_domains(
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Get all paused domains for current user"""
    
    user_id = str(current_user.id)
    
    domains = db.query(EmailDomain).filter(
        EmailDomain.user_id == user_id,
        EmailDomain.is_paused == True
    ).all()
    
    return [
        {
            "id": d.id,
            "domain": d.domain,
            "paused_at": d.paused_at,
            "reason": d.paused_reason,
            "sender_name": d.sender_name
        }
        for d in domains
    ]

# app/routers/sender_identity.py - Add these endpoints

class ToggleDomainStatusRequest(BaseModel):
    domain_id: str

# app/routers/sender_identity.py

@router.post("/email-domains/toggle-status")
async def toggle_domain_status(
    request: ToggleDomainStatusRequest,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Toggle domain between Active and Inactive - Also toggles all email addresses under it"""
    
    user_id = str(current_user.id)
    
    domain = db.query(EmailDomain).filter(
        EmailDomain.id == request.domain_id,
        EmailDomain.user_id == user_id
    ).first()
    
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    if domain.aws_verification_status != "success":
        raise HTTPException(status_code=400, detail="Only verified domains can be toggled")
    
    # ✅ Toggle domain status
    domain.is_active = not domain.is_active
    db.commit()
    
    # ✅ NEW: Toggle all email addresses under this domain
    emails_updated = db.query(EmailAddress).filter(
        EmailAddress.domain_id == domain.id
    ).update({"is_active": domain.is_active})
    
    db.commit()
    
    status_text = "Active" if domain.is_active else "Inactive"
    
    return {
        "message": f"Domain {domain.domain} is now {status_text}",
        "domain": domain.domain,
        "is_active": domain.is_active,
        "status": status_text,
        "emails_updated": emails_updated,
        "details": f"{emails_updated} email address(es) {'activated' if domain.is_active else 'deactivated'}"
    }

@router.get("/email-domains/active")
async def get_active_domains(
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Get all active domains for current user"""
    
    user_id = str(current_user.id)
    
    domains = db.query(EmailDomain).filter(
        EmailDomain.user_id == user_id,
        EmailDomain.is_active == True,
        EmailDomain.aws_verification_status == "success"
    ).all()
    
    return [
        {
            "id": d.id,
            "domain": d.domain,
            "sender_name": d.sender_name
        }
        for d in domains
    ]
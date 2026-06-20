# app/services/aws_ses_service.py
import boto3
from botocore.exceptions import ClientError
from typing import Dict, List, Optional, Tuple
from app.core.config import settings

class AWSSESService:
    def __init__(self):
        print(f"Initializing AWS SES with region: {settings.AWS_REGION}")
        
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            print("⚠️ AWS credentials not configured")
            self.initialized = False
            self.client = None
            return
        
        try:
            self.client = boto3.client(
                'ses',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            
            # Test connection with GetSendQuota
            try:
                self.client.get_send_quota()
                print("✅ AWS SES client initialized successfully")
                self.initialized = True
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code == 'AccessDenied':
                    print(f"⚠️ AWS SES initialized but missing permissions: {e.response['Error']['Message']}")
                    print("   Falling back to limited mode...")
                    try:
                        self.client.list_identities(MaxItems=1)
                        print("✅ AWS SES initialized in limited mode")
                        self.initialized = True
                    except:
                        self.initialized = False
                        self.client = None
                else:
                    print(f"❌ AWS SES initialization failed: {e}")
                    self.initialized = False
                    self.client = None
                    
        except Exception as e:
            print(f"❌ AWS SES initialization failed: {e}")
            self.initialized = False
            self.client = None
    
    async def get_complete_status(self, domain: str) -> Dict:
        """Get complete verification status from AWS SES"""
        if not self.initialized or not self.client:
            return {
                'domain': domain,
                'exists': False,
                'is_verified': False,
                'verification_status': 'Unknown',
                'dkim_enabled': False,
                'dkim_status': 'Unknown',
                'error': 'AWS not configured'
            }
        
        try:
            verify_response = self.client.get_identity_verification_attributes(
                Identities=[domain]
            )
            
            dkim_response = self.client.get_identity_dkim_attributes(
                Identities=[domain]
            )
            
            attrs = verify_response['VerificationAttributes'].get(domain, {})
            dkim_attrs = dkim_response['DkimAttributes'].get(domain, {})
            
            verification_status = attrs.get('VerificationStatus', 'NotStarted')
            
            return {
                'domain': domain,
                'exists': domain in verify_response['VerificationAttributes'],
                'is_verified': verification_status == 'Success',
                'verification_status': verification_status,
                'dkim_enabled': dkim_attrs.get('DkimEnabled', False),
                'dkim_status': dkim_attrs.get('DkimVerificationStatus', 'NotStarted'),
                'dkim_tokens': dkim_attrs.get('DkimTokens', [])
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            print(f"AWS Error for {domain}: {error_code} - {error_msg}")
            
            return {
                'domain': domain,
                'exists': False,
                'is_verified': False,
                'verification_status': 'Error',
                'error_code': error_code,
                'error_message': error_msg,
                'dkim_enabled': False,
                'dkim_status': 'Error'
            }
        except Exception as e:
            print(f"Unexpected error for {domain}: {e}")
            return {
                'domain': domain,
                'exists': False,
                'is_verified': False,
                'verification_status': 'Error',
                'error': str(e),
                'dkim_enabled': False,
                'dkim_status': 'Error'
            }
    
    async def initiate_verification(self, domain: str) -> Tuple[str, List[str]]:
        """Initiate domain verification with AWS SES"""
        if not self.initialized or not self.client:
            raise Exception("AWS SES not initialized")
        
        try:
            verify_response = self.client.verify_domain_identity(
                Domain=domain
            )
            verification_token = verify_response.get('VerificationToken')
            print(f"✅ Domain verification initiated for {domain}")
            
            dkim_response = self.client.verify_domain_dkim(
                Domain=domain
            )
            dkim_tokens = dkim_response.get('DkimTokens', [])
            print(f"✅ DKIM enabled for {domain}, tokens: {len(dkim_tokens)}")
            
            return verification_token, dkim_tokens
            
        except ClientError as e:
            error_msg = e.response['Error']['Message']
            print(f"❌ Failed to initiate verification for {domain}: {error_msg}")
            raise Exception(f"AWS SES verification failed: {error_msg}")
    
    async def get_dns_records(self, domain: str, verification_token: str, dkim_tokens: List[str]) -> List[Dict]:
        """Generate DNS records for domain verification - ALWAYS returns all records"""
        records = []
        
        # 1. Domain verification TXT record
        if verification_token and verification_token != "skip_aws" and verification_token != "already_in_aws":
            records.append({
                "type": "TXT",
                "name": f"_amazonses.{domain}",
                "value": verification_token,
                "description": "AWS SES Domain Verification - Proves you own this domain"
            })
        else:
            # If no token, show a sample
            records.append({
                "type": "TXT",
                "name": f"_amazonses.{domain}",
                "value": "YOUR_VERIFICATION_TOKEN_FROM_AWS",
                "description": "AWS SES Domain Verification - Add the token provided by AWS SES"
            })
        
        # 2. SPF record - ALWAYS show this
        records.append({
            "type": "TXT",
            "name": domain,
            "value": "v=spf1 include:amazonses.com ~all",
            "description": "SPF Record - Authorizes AWS SES to send emails for your domain"
        })
        
        # 3. DKIM records - ALWAYS show these (usually 3)
        if dkim_tokens:
            for i, token in enumerate(dkim_tokens, 1):
                records.append({
                    "type": "CNAME",
                    "name": f"{token}._domainkey.{domain}",
                    "value": f"{token}.dkim.amazonses.com",
                    "description": f"DKIM Record {i} - Digitally signs emails from your domain"
                })
        else:
            # If no DKIM tokens, show placeholders
            for i in range(1, 4):
                records.append({
                    "type": "CNAME",
                    "name": f"dkim{i}._domainkey.{domain}",
                    "value": f"dkim{i}.dkim.amazonses.com",
                    "description": f"DKIM Record {i} - Add the DKIM token provided by AWS SES"
                })
        
        # 4. DMARC record - ALWAYS show this
        records.append({
            "type": "TXT",
            "name": f"_dmarc.{domain}",
            "value": f"v=DMARC1; p=none; rua=mailto:dmarc@{domain}",
            "description": "DMARC Record - Tells email providers how to handle unauthenticated emails"
        })
        
        return records
    
    async def check_send_quota(self) -> Dict:
        """Check AWS SES sending limits"""
        if not self.initialized or not self.client:
            return {'error': 'AWS not configured'}
        
        try:
            response = self.client.get_send_quota()
            return {
                'max_24_hour_send': response.get('Max24HourSend', 0),
                'sent_last_24_hours': response.get('SentLast24Hours', 0),
                'max_send_rate': response.get('MaxSendRate', 0)
            }
        except ClientError as e:
            print(f"❌ Failed to get send quota: {e}")
            return {'error': str(e)}


# Create global instance
ses_service = AWSSESService() 
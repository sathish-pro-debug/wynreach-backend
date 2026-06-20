#!/usr/bin/env python3
"""
Test Campaign Email Script
==========================
This script tests the complete email campaign flow:
1. Creates test data (audience list, contacts, template)
2. Creates a campaign
3. Sends a test email
4. Finalizes and sends campaign immediately
5. Verifies campaign status

Usage:
  python test_campaign_email.py

Or in Python:
  from test_campaign_email import run_email_test
  run_email_test()
"""

import asyncio
import sys
from datetime import datetime, timezone
from sqlalchemy.orm import Session

# Add the app to path
sys.path.insert(0, '/'.join(__file__.split('/')[:-1]))

from app.database import SessionLocal
from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.lists import AudienceList, ListContact
from app.models.template import Template
from app.services.email_service import send_email
from app.services.campaign_service import finalize_campaign, send_test_email
from app.schemas.campaign_finalize import CampaignFinalize
from app.schemas.campaign_test_email import TestEmailRequest


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")


def print_step(step_num, title):
    """Print a step header"""
    print(f"\n📍 STEP {step_num}: {title}")
    print(f"   {'-'*60}")


def print_success(msg):
    """Print success message"""
    print(f"   ✅ {msg}")


def print_info(msg):
    """Print info message"""
    print(f"   ℹ️  {msg}")


def print_error(msg):
    """Print error message"""
    print(f"   ❌ {msg}")


async def run_email_test(test_email: str = None):
    """
    Run complete email campaign test
    
    Args:
        test_email: Email address to send test to (default: wynreach.noreply@gmail.com)
    """
    
    if not test_email:
        test_email = "wynreach.noreply@gmail.com"
    
    db = SessionLocal()
    
    print_section("🚀 CAMPAIGN EMAIL SYSTEM TEST")
    
    try:
        # ============================================================
        # STEP 1: Test SMTP Configuration
        # ============================================================
        print_step(1, "Testing SMTP Configuration")
        
        from app.services.email_service import EmailService
        service = EmailService()
        settings = service._get_active_settings()
        
        if not settings.smtp_user:
            print_error("SMTP_USER not configured in environment variables")
            return False
        
        try:
            import smtplib
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_user, settings.smtp_password)
            print_success(f"SMTP connection successful")
            print_info(f"Host: {settings.smtp_host}:{settings.smtp_port}")
            print_info(f"User: {settings.smtp_user}")
        except Exception as e:
            print_error(f"SMTP connection failed: {e}")
            return False
        
        # ============================================================
        # STEP 2: Create Test Audience List
        # ============================================================
        print_step(2, "Creating Test Audience List")
        
        # Check if test list exists
        test_list = db.query(AudienceList).filter(
            AudienceList.list_name == "Test Campaign List"
        ).first()
        
        if test_list:
            print_info(f"Using existing test list (ID: {test_list.id})")
            audience_list_id = test_list.id
        else:
            test_list = AudienceList(
                list_name="Test Campaign List",
                description="Auto-generated test list for campaign email testing"
            )
            db.add(test_list)
            db.commit()
            db.refresh(test_list)
            print_success(f"Created test audience list (ID: {test_list.id})")
            audience_list_id = test_list.id
        
        # ============================================================
        # STEP 3: Create Test Contacts
        # ============================================================
        print_step(3, "Creating Test Contacts")
        
        test_contacts_data = [
            {"full_name": "Test User 1", "email": test_email, "phone": "+1234567890"},
            {"full_name": "Test User 2", "email": test_email, "phone": "+1234567891"},
            {"full_name": "Test User 3", "email": test_email, "phone": "+1234567892"},
        ]
        
        contact_ids = []
        for contact_data in test_contacts_data:
            contact = db.query(Contact).filter(
                Contact.email == contact_data["email"],
                Contact.full_name == contact_data["full_name"]
            ).first()
            
            if contact:
                print_info(f"Using existing contact: {contact.full_name}")
                contact_ids.append(contact.id)
            else:
                contact = Contact(
                    full_name=contact_data["full_name"],
                    email=contact_data["email"],
                    phone=contact_data["phone"],
                    status="active",
                    is_suppressed=False
                )
                db.add(contact)
                db.flush()
                contact_ids.append(contact.id)
                print_success(f"Created contact: {contact.full_name}")
        
        db.commit()
        
        # ============================================================
        # STEP 4: Add Contacts to Audience List
        # ============================================================
        print_step(4, "Adding Contacts to Audience List")
        
        for contact_id in contact_ids:
            # Check if already in list
            existing = db.query(ListContact).filter(
                ListContact.list_id == audience_list_id,
                ListContact.contact_id == contact_id
            ).first()
            
            if not existing:
                list_contact = ListContact(
                    list_id=audience_list_id,
                    contact_id=contact_id
                )
                db.add(list_contact)
        
        db.commit()
        print_success(f"Added {len(contact_ids)} contacts to audience list")
        
        # ============================================================
        # STEP 5: Create Test Template
        # ============================================================
        print_step(5, "Creating Test Template")
        
        test_template = db.query(Template).filter(
            Template.name == "Test Campaign Template"
        ).first()
        
        if test_template:
            print_info(f"Using existing test template (ID: {test_template.id})")
            template_id = test_template.id
        else:
            test_template = Template(
                name="Test Campaign Template",
                subject="🎉 Test Campaign Email",
                html_content="""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                    <div style="background: linear-gradient(135deg, #4F46E5, #7C3AED); color: white; padding: 40px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
                        <h1 style="margin: 0;">🎉 WynReach Campaign Test</h1>
                        <p style="margin: 10px 0 0 0; opacity: 0.9;">This is a test email from the WynReach campaign system</p>
                    </div>
                    
                    <div style="padding: 20px; background: #f5f5f5; border-radius: 8px; margin-bottom: 20px;">
                        <h2 style="color: #1f2937;">Welcome to WynReach! 👋</h2>
                        <p>This test email demonstrates the campaign email system is working correctly.</p>
                        
                        <div style="background: white; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #4F46E5;">
                            <p><strong>✅ What's working:</strong></p>
                            <ul style="margin: 10px 0;">
                                <li>Email sending via SMTP</li>
                                <li>Template rendering</li>
                                <li>Campaign finalization</li>
                                <li>Contact database integration</li>
                            </ul>
                        </div>
                        
                        <p style="color: #666; font-size: 14px;">
                            <strong>Send Time:</strong> {timestamp}
                        </p>
                    </div>
                    
                    <div style="text-align: center; padding: 20px; color: #999; font-size: 12px; border-top: 1px solid #ddd;">
                        <p>© 2026 WynReach. All rights reserved.</p>
                        <p>This is an automated test email.</p>
                    </div>
                </div>
                """.replace("{timestamp}", datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"))
            )
            db.add(test_template)
            db.commit()
            db.refresh(test_template)
            print_success(f"Created test template (ID: {test_template.id})")
            template_id = test_template.id
        
        # ============================================================
        # STEP 6: Create Test Campaign
        # ============================================================
        print_step(6, "Creating Test Campaign")
        
        campaign = Campaign(
            campaign_name="Test Campaign Email Verification",
            channel="email",
            goal_label="testing",
            status="draft",
            current_step=1,
            audience_list_ids=[audience_list_id],
            template_id=template_id,
            subject_line="🎉 WynReach Campaign Test",
            send_mode="immediate"
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        print_success(f"Created campaign (ID: {campaign.id})")
        campaign_id = campaign.id
        
        # ============================================================
        # STEP 7: Send Test Email
        # ============================================================
        print_step(7, "Sending Test Email Preview")
        
        try:
            test_request = TestEmailRequest(email=test_email)
            result = await send_test_email(db, campaign_id, test_request)
            print_success(f"Test email sent to: {test_email}")
            print_info(f"Response: {result['message']}")
            await asyncio.sleep(2)  # Brief pause
        except Exception as e:
            print_error(f"Failed to send test email: {e}")
            return False
        
        # ============================================================
        # STEP 8: Finalize and Send Campaign
        # ============================================================
        print_step(8, "Finalizing and Sending Campaign")
        
        try:
            finalize_request = CampaignFinalize(status="sending")
            result = await finalize_campaign(db, campaign_id, finalize_request)
            print_success(f"Campaign finalized successfully")
            print_info(f"Recipients sent: {result.get('recipients_count', 'N/A')}")
            print_info(f"Campaign status: {result['campaign'].status}")
        except Exception as e:
            print_error(f"Failed to finalize campaign: {e}")
            return False
        
        # ============================================================
        # STEP 9: Verify Campaign Status
        # ============================================================
        print_step(9, "Verifying Campaign Status")
        
        updated_campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
        
        if updated_campaign:
            print_success(f"Campaign status: {updated_campaign.status}")
            print_info(f"Email sent at: {updated_campaign.email_sent_at}")
            print_info(f"Current step: {updated_campaign.current_step}")
            
            if updated_campaign.status == "sent":
                print_success("✅ Campaign successfully sent!")
            else:
                print_error(f"Campaign status is '{updated_campaign.status}', expected 'sent'")
        else:
            print_error("Campaign not found after finalization")
            return False
        
        # ============================================================
        # FINAL SUMMARY
        # ============================================================
        print_section("✅ TEST COMPLETE - ALL SYSTEMS WORKING")
        
        print_info(f"Campaign ID: {campaign_id}")
        print_info(f"Test Email: {test_email}")
        print_info(f"Recipients: {len(contact_ids)}")
        print_info(f"Template: {test_template.name}")
        print_info(f"\n📧 Check your email inbox ({test_email}) for the test emails!")
        print_info(f"📊 Check backend console for detailed logs")
        
        return True
        
    except Exception as e:
        print_section("❌ TEST FAILED")
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        db.close()


if __name__ == "__main__":
    """
    Run test from command line:
    
    python test_campaign_email.py
    Or with custom email:
    python test_campaign_email.py --email your-email@example.com
    """
    
    test_email = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--email" and len(sys.argv) > 2:
            test_email = sys.argv[2]
    
    # Run async test
    success = asyncio.run(run_email_test(test_email))
    
    sys.exit(0 if success else 1)

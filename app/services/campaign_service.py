# # # # # from backend.app.schemas import campaign
# # # # from sqlalchemy import text, func
# # # # from sqlalchemy.orm import Session
# # # # from fastapi import HTTPException

# # # # from app.models.campaign import Campaign
# # # # from app.schemas.campaign import CampaignCreate

# # # # from app.utils.notification_service import create_notification

# # # # from fastapi import HTTPException
# # # # from app.services.whatsapp_service import send_bulk_whatsapp
# # # # from copy import deepcopy
# # # # from app.services.email_service import send_campaign_emails, send_email
# # # # from datetime import datetime, timezone
# # # # from types import SimpleNamespace
# # # # import os
# # # # import json as _json

# # # # FALLBACK_EMAIL = os.getenv("CAMPAIGN_FALLBACK_EMAIL", "sathish.wynsync@gmail.com")


# # # # def fallback_contact():
# # # #     return SimpleNamespace(
# # # #         id=None,
# # # #         full_name="Fallback Recipient",
# # # #         email=FALLBACK_EMAIL,
# # # #         phone=None,
# # # #     )


# # # # def create_campaign(db, campaign: CampaignCreate):
# # # #     try:
# # # #         print("🔥 CREATE CAMPAIGN STARTED")
# # # #         print(campaign.model_dump())
# # # #         from app.models.campaign import Campaign

# # # #         new_campaign = Campaign(
# # # #             campaign_name=campaign.campaign_name,
# # # #             channel=campaign.channel,
# # # #             goal_label=campaign.goal_label,
# # # #             status="draft",
# # # #             current_step=1,
# # # #         )
# # # #         db.add(new_campaign)
# # # #         db.commit()
# # # #         db.refresh(new_campaign)
# # # #         print("✅ CAMPAIGN CREATED")
# # # #         return new_campaign
# # # #     except Exception as e:
# # # #         print("❌ CREATE CAMPAIGN ERROR")
# # # #         print(str(e))
# # # #         db.rollback()
# # # #         raise e


# # # # def update_campaign_content(db, campaign_id, content_data):
# # # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # # #     if not campaign:
# # # #         raise HTTPException(status_code=404, detail="Campaign not found")
# # # #     campaign.subject_line = content_data.subject_line
# # # #     campaign.preview_text = content_data.preview_text
# # # #     campaign.template_id = content_data.template_id
# # # #     campaign.sender_identity_id = content_data.sender_identity_id
# # # #     campaign.current_step = 3
# # # #     db.commit()
# # # #     db.refresh(campaign)
# # # #     return campaign


# # # # def update_campaign_schedule(db, campaign_id, schedule_data):
# # # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # # #     if not campaign:
# # # #         return None
# # # #     campaign.send_mode = schedule_data.send_mode
# # # #     campaign.scheduled_at = schedule_data.scheduled_at
# # # #     campaign.timezone = schedule_data.timezone
# # # #     campaign.current_step = 4
# # # #     db.commit()
# # # #     db.refresh(campaign)
# # # #     return campaign


# # # # import asyncio


# # # # def _blocks_to_html(content, campaign_name):
# # # #     try:
# # # #         blocks = _json.loads(content)
# # # #         html_parts = []
# # # #         for block in blocks:
# # # #             btype = block.get("type", "")
# # # #             props = block.get("props", {})
# # # #             if btype == "text":
# # # #                 html_parts.append(
# # # #                     f'<p style="color:{props.get("color","#000")};font-size:{props.get("fontSize","14px")}">{props.get("text","")}</p>'
# # # #                 )
# # # #             elif btype == "image":
# # # #                 html_parts.append(
# # # #                     f'<img src="{props.get("url","")}" alt="{props.get("alt","")}" style="max-width:100%"/>'
# # # #                 )
# # # #             elif btype == "button":
# # # #                 html_parts.append(
# # # #                     f'<a href="{props.get("url","#")}" style="background:{props.get("bgColor","#4f46e5")};color:{props.get("textColor","#fff")};padding:10px 20px;border-radius:6px;text-decoration:none;display:inline-block">{props.get("label","Click")}</a>'
# # # #                 )
# # # #             elif btype == "footer":
# # # #                 html_parts.append(
# # # #                     f'<p style="color:{props.get("color","#999")};font-size:12px">{props.get("text","")}</p>'
# # # #                 )
# # # #             elif btype == "divider":
# # # #                 html_parts.append(
# # # #                     f'<hr style="border:none;border-top:1px solid {props.get("color","#e2e8f0")};margin:16px 0"/>'
# # # #                 )
# # # #         return f'<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">{"".join(html_parts)}</div>'
# # # #     except:
# # # #         return content or f"<h2>{campaign_name}</h2>"


# # # # async def finalize_campaign(db, log_db, campaign_id, finalize_data):
# # # #     from app.models.template import Template
# # # #     from app.models.lists import ListContact
# # # #     from app.models.contact import Contact

# # # #     print(f"\n{'='*60}")
# # # #     print(f"🚀 FINALIZING CAMPAIGN {campaign_id}")
# # # #     print(f"{'='*60}\n")

# # # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # # #     if not campaign:
# # # #         raise Exception("Campaign not found")

# # # #     campaign.current_step = 6
# # # #     channel = campaign.channel
# # # #     print(f"   📡 Channel: {channel}")

# # # #     if campaign.send_mode == "immediate":

# # # #         print("📍 STEP 1: Fetching audience contacts...")
# # # #         audience_list_ids = campaign.audience_list_ids or []
# # # #         exclude_list_ids = campaign.exclude_list_ids or []
# # # #         print(f"   Audience lists: {audience_list_ids}")
# # # #         print(f"   Exclude lists: {exclude_list_ids}")

# # # #         if not audience_list_ids:
# # # #             raise HTTPException(status_code=400, detail="No audience lists selected")

# # # #         audience_list_ids = [int(x) for x in audience_list_ids]
# # # #         exclude_list_ids = (
# # # #             [int(x) for x in exclude_list_ids] if exclude_list_ids else []
# # # #         )

# # # #         contact_ids_query = db.query(ListContact.contact_id).filter(
# # # #             ListContact.list_id.in_(audience_list_ids)
# # # #         )
# # # #         if exclude_list_ids:
# # # #             excluded_ids = (
# # # #                 db.query(ListContact.contact_id)
# # # #                 .filter(ListContact.list_id.in_(exclude_list_ids))
# # # #                 .subquery()
# # # #             )
# # # #             contact_ids_query = contact_ids_query.filter(
# # # #                 ListContact.contact_id.notin_(excluded_ids)
# # # #             )

# # # #         contact_ids = [row.contact_id for row in contact_ids_query.all()]
# # # #         print(f"   ✅ Found {len(contact_ids)} contacts")

# # # #         print(
# # # #             f"\n📍 STEP 2: Fetching {'phone numbers' if channel == 'whatsapp' else 'email addresses'}..."
# # # #         )

# # # #         contacts = []
# # # #         if contact_ids:
# # # #             contacts = (
# # # #                 db.query(Contact)
# # # #                 .filter(Contact.id.in_(contact_ids), Contact.is_suppressed == False)
# # # #                 .all()
# # # #             )

# # # #         print("\n📍 STEP 3: Fetching template...")
# # # #         if not campaign.template_id:
# # # #             raise HTTPException(status_code=400, detail="No template selected")

# # # #         template = (
# # # #             log_db.query(Template)
# # # #             .filter(Template.id == int(campaign.template_id))
# # # #             .first()
# # # #         )
# # # #         if not template:
# # # #             raise HTTPException(status_code=404, detail="Template not found")
# # # #         print(f"   ✅ Using template: {template.name}")

# # # #         if channel == "whatsapp":
# # # #             print(f"\n📍 STEP 4: Sending WhatsApp messages...")
# # # #             # recipients = [{"phone": c.phone} for c in contacts if c.phone]
# # # #             recipients = [
# # # #                 {"phone": c.phone, "name": c.full_name or c.phone}
# # # #                 for c in contacts
# # # #                 if c.phone
# # # #             ]
# # # #             print(f"   ✅ Found {len(recipients)} recipients with valid phone numbers")
# # # #             if not recipients:
# # # #                 raise HTTPException(
# # # #                     status_code=400, detail="No contacts with phone numbers found"
# # # #                 )
# # # #             send_result = await send_bulk_whatsapp(
# # # #                 recipients=recipients,
# # # #                 template_name=template.name,
# # # #                 language_code="en",
# # # #             )
# # # #             print(f"   ✅ WhatsApp messages sent!")


# # # #             success_count = len(send_result.get("success", []))

# # # # campaign.total_sent = success_count
# # # # campaign.total_delivered = success_count

# # # # campaign.total_opened = 0
# # # # campaign.total_clicked = 0
# # # # campaign.total_bounced = 0
# # # # campaign.total_unsubscribed = 0

# # # # campaign.delivery_rate = 100 if success_count > 0 else 0
# # # # campaign.open_rate = 0
# # # # campaign.click_rate = 0
# # # # campaign.bounce_rate = 0

# # # #             from app.models.message_log import MessageLog
# # # #             for item in send_result.get("success", []):
# # # #                 log = MessageLog(
# # # #                     recipient_phone=item["phone"],
# # # #                     recipient_name=item.get("name", item["phone"]),
# # # #                     message=f"Template: {template.name}",
# # # #                     template_name=template.name,
# # # #                     campaign_id=str(campaign_id),
# # # #                     campaign_name=campaign.campaign_name,
# # # #                     status="sent",
# # # #                     wamid=item.get("message_id"),
# # # #                     sent_at=datetime.now(timezone.utc),
# # # #                     direction="outgoing",
# # # #                     source="campaign",
# # # #                 )
# # # #                 db.add(log)

# # # #             for item in send_result.get("failed", []):
# # # #                 log = MessageLog(
# # # #                     recipient_phone=item["phone"],
# # # #                     recipient_name=item.get("name", item["phone"]),
# # # #                     message=f"Template: {template.name}",
# # # #                     template_name=template.name,
# # # #                     campaign_id=str(campaign_id),
# # # #                     campaign_name=campaign.campaign_name,
# # # #                     status="failed",
# # # #                     error_reason=item.get("error"),
# # # #                     sent_at=datetime.now(timezone.utc),
# # # #                     direction="outgoing",
# # # #                     source="campaign",
# # # #                 )
# # # #                 db.add(log)

# # # #             db.commit()

# # # #         else:
# # # #             print(f"\n📍 STEP 4: Sending emails...")
# # # #             recipients_email = [c.email for c in contacts if c.email]
# # # #             print(f"   ✅ Found {len(recipients_email)} recipients with valid emails")

# # # #             if not recipients_email:
# # # #                 contacts = [fallback_contact()]
# # # #                 recipients_email = [FALLBACK_EMAIL]
# # # #                 print(f"   No valid contact emails. Using fallback: {FALLBACK_EMAIL}")

# # # #             html_body = _blocks_to_html(template.content, campaign.campaign_name)

# # # #             send_result = await send_campaign_emails(
# # # #                 log_db=log_db,
# # # #                 campaign=campaign,
# # # #                 contacts=contacts,
# # # #                 subject=campaign.subject_line or "Campaign Email",
# # # #                 html_body=html_body,
# # # #                 template_name=template.name,
# # # #             )
# # # #             print(f"   ✅ Emails sent!")

# # # # total_sent = len(recipients_email)

# # # # campaign.total_sent = total_sent
# # # # campaign.total_delivered = total_sent

# # # # campaign.total_opened = 0
# # # # campaign.total_clicked = 0
# # # # campaign.total_bounced = 0
# # # # campaign.total_unsubscribed = 0

# # # # campaign.delivery_rate = 100 if total_sent > 0 else 0
# # # # campaign.open_rate = 0
# # # # campaign.click_rate = 0
# # # # campaign.bounce_rate = 0
# # # #         print("\n📍 STEP 5: Updating campaign status...")
# # # #         campaign.status = "sent"
# # # #         campaign.email_sent_at = datetime.now(timezone.utc)
# # # #         campaign.sent_at = datetime.now(timezone.utc)
# # # #         create_notification(
# # # #             db=db,
# # # #             notification_type="campaignSent",
# # # #             title="Campaign Sent",
# # # #             message=f'Campaign "{campaign.campaign_name}" sent successfully',
# # # #         )
# # # #         print(f"   ✅ Campaign marked as sent")

# # # #     else:
# # # #         print(f"\n📅 Scheduling campaign for {campaign.scheduled_at}")
# # # #         campaign.status = "scheduled"
# # # #         create_notification(
# # # #             db=db,
# # # #             notification_type="campaignScheduled",
# # # #             title="Campaign Scheduled",
# # # #             message=f'Campaign "{campaign.campaign_name}" scheduled successfully',
# # # #         )

# # # #     db.commit()
# # # #     db.refresh(campaign)

# # # #     print(f"\n{'='*60}")
# # # #     print(f"✅ CAMPAIGN FINALIZED SUCCESSFULLY")
# # # #     print(f"{'='*60}\n")

# # # #     return {
# # # #         "message": "Campaign finalized",
# # # #         "campaign": campaign,
# # # #         "channel": channel,
# # # #         "status": campaign.status,
# # # #     }


# # # # async def send_test_email(db, log_db, campaign_id, email_data):
# # # #     from app.models.template import Template

# # # #     print(f"\n{'='*60}")
# # # #     print(f"📧 SENDING TEST EMAIL")
# # # #     print(f"{'='*60}\n")

# # # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # # #     if not campaign:
# # # #         raise HTTPException(status_code=404, detail="Campaign not found")

# # # #     email = email_data.email or FALLBACK_EMAIL
# # # #     print(f"   To: {email}")

# # # #     html_body = f"""
# # # #     <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
# # # #         <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
# # # #             <strong>📊 TEST EMAIL PREVIEW</strong>
# # # #             <p style="color: #666; font-size: 12px; margin: 10px 0 0 0;">
# # # #                 This is a test email for: <strong>{campaign.campaign_name}</strong>
# # # #             </p>
# # # #         </div>
# # # #         <h2 style="margin-top: 0;">{campaign.campaign_name}</h2>
# # # #     """

# # # #     if campaign.template_id:
# # # #         template = (
# # # #             log_db.query(Template)
# # # #             .filter(Template.id == int(campaign.template_id))
# # # #             .first()
# # # #         )
# # # #         if template and template.content:
# # # #             html_body += _blocks_to_html(template.content, campaign.campaign_name)
# # # #             print(f"   Template: {template.name}")
# # # #         else:
# # # #             html_body += f"<p>This email will use the selected template.</p>"
# # # #     else:
# # # #         html_body += f"<p>⚠️ No template selected for campaign</p>"

# # # #     html_body += f"""
# # # #         <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
# # # #         <p style="color: #999; font-size: 12px;">
# # # #             This is a test email. When sent, this campaign will reach
# # # #             {len([x for x in (campaign.audience_list_ids or [])]) or 0} audience lists.
# # # #         </p>
# # # #     </div>
# # # #     """

# # # #     try:
# # # #         await send_email(
# # # #             recipients=[email],
# # # #             subject=campaign.subject_line or "Test Campaign Email",
# # # #             html_body=html_body,
# # # #         )
# # # #         print(f"   ✅ Test email sent successfully!\n")
# # # #         return {
# # # #             "message": "Test email sent successfully",
# # # #             "sent_to": email,
# # # #             "delivery_status": "sent",
# # # #         }
# # # #     except Exception as e:
# # # #         create_notification(
# # # #             db=db,
# # # #             notification_type="campaignFailed",
# # # #             title="Campaign Failed",
# # # #             message=f'Campaign "{campaign.campaign_name}" failed to send',
# # # #         )
# # # #         print(f"   ❌ Failed: {str(e)}\n")
# # # #         return {
# # # #             "message": "Test email attempted, but AWS SES rejected it",
# # # #             "sent_to": email,
# # # #             "delivery_status": "failed",
# # # #             "error": str(e),
# # # #         }


# # # # def get_all_campaigns(db: Session):
# # # #     campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
# # # #     return campaigns


# # # # def get_campaign_by_id(db, campaign_id: str):
# # # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # # #     if not campaign:
# # # #         raise HTTPException(status_code=404, detail="Campaign not found")
# # # #     return campaign


# # # # def duplicate_campaign(db: Session, campaign_id: str):
# # # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # # #     if not campaign:
# # # #         return {"error": "Campaign not found"}
# # # #     duplicated = Campaign(
# # # #         campaign_name=f"Copy of {campaign.campaign_name}",
# # # #         channel=campaign.channel,
# # # #         goal_label=campaign.goal_label,
# # # #         status="draft",
# # # #     )
# # # #     db.add(duplicated)
# # # #     db.commit()
# # # #     db.refresh(duplicated)
# # # #     return duplicated


# # # # def update_campaign_audience(db, campaign_id, audience):
# # # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # # #     if not campaign:
# # # #         raise Exception("Campaign not found")
# # # #     campaign.audience_list_ids = audience.audience_list_ids
# # # #     campaign.exclude_list_ids = audience.exclude_list_ids
# # # #     campaign.estimated_recipients = audience.estimated_recipients
# # # #     campaign.suppressed_count = audience.suppressed_count
# # # #     campaign.current_step = max(campaign.current_step, 2)
# # # #     db.commit()
# # # #     db.refresh(campaign)
# # # #     return {"success": True}


# # # # def update_campaign(db: Session, campaign_id: int, payload):
# # # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # # #     if not campaign:
# # # #         raise HTTPException(status_code=404, detail="Campaign not found")
# # # #     campaign.campaign_name = payload.campaign_name
# # # #     campaign.channel = payload.channel
# # # #     campaign.goal_label = payload.goal_label
# # # #     db.commit()
# # # #     db.refresh(campaign)
# # # #     return campaign


# # # # def get_campaign_logs(main_db: Session, log_db: Session, campaign_id: str):
# # # #     from app.models.log import EmailLog

# # # #     campaign = main_db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # # #     if not campaign:
# # # #         raise HTTPException(status_code=404, detail="Campaign not found")

# # # #     logs = (
# # # #         log_db.query(EmailLog)
# # # #         .filter(EmailLog.campaign_id == campaign_id)
# # # #         .order_by(EmailLog.created_at.desc())
# # # #         .all()
# # # #     )

# # # #     summary_rows = (
# # # #         log_db.query(EmailLog.status, func.count(EmailLog.id))
# # # #         .filter(EmailLog.campaign_id == campaign_id)
# # # #         .group_by(EmailLog.status)
# # # #         .all()
# # # #     )
# # # #     counts = {status: count for status, count in summary_rows}

# # # #     return {
# # # #         "campaign": campaign,
# # # #         "logs": [
# # # #             {
# # # #                 "id": log.id,
# # # #                 "contactName": log.recipient_name,
# # # #                 "email": log.recipient_email,
# # # #                 "phone": log.recipient_phone,
# # # #                 "status": log.status,
# # # #                 "failureReason": log.bounce_reason or log.error_message,
# # # #                 "sentAt": log.sent_at,
# # # #                 "deliveredAt": log.delivered_at,
# # # #                 "openedAt": log.opened_at,
# # # #                 "clickedAt": log.clicked_at,
# # # #                 "openCount": log.opens,
# # # #                 "device": None,
# # # #                 "browser": None,
# # # #                 "country": None,
# # # #                 "recipient_name": log.recipient_name,
# # # #                 "recipient_email": log.recipient_email,
# # # #                 "recipient_phone": log.recipient_phone,
# # # #                 "subject": log.subject,
# # # #                 "template_name": log.template_name,
# # # #                 "campaign_name": log.campaign_name,
# # # #                 "opens": log.opens,
# # # #                 "clicks": log.clicks,
# # # #                 "sent_at": log.sent_at,
# # # #                 "bounce_reason": log.bounce_reason or log.error_message,
# # # #             }
# # # #             for log in logs
# # # #         ],
# # # #         "summary": {
# # # #             "total": len(logs),
# # # #             "sent": counts.get("sent", 0),
# # # #             "delivered": counts.get("delivered", 0),
# # # #             "opened": counts.get("opened", 0),
# # # #             "clicked": counts.get("clicked", 0),
# # # #             "failed": counts.get("failed", 0),
# # # #             "bounced": counts.get("bounced", 0),
# # # #             "unsubscribed": counts.get("unsubscribed", 0),
# # # #         },
# # # #     }


# # # from sqlalchemy import text, func
# # # from sqlalchemy.orm import Session
# # # from fastapi import HTTPException

# # # from app.models.campaign import Campaign
# # # from app.schemas.campaign import CampaignCreate

# # # from app.utils.notification_service import create_notification

# # # from fastapi import HTTPException
# # # from app.services.whatsapp_service import send_bulk_whatsapp
# # # from copy import deepcopy
# # # from app.services.email_service import send_campaign_emails, send_email
# # # from datetime import datetime, timezone
# # # from types import SimpleNamespace
# # # import os
# # # import json as _json

# # # FALLBACK_EMAIL = os.getenv("CAMPAIGN_FALLBACK_EMAIL", "sathish.wynsync@gmail.com")


# # # def fallback_contact():
# # #     return SimpleNamespace(
# # #         id=None,
# # #         full_name="Fallback Recipient",
# # #         email=FALLBACK_EMAIL,
# # #         phone=None,
# # #     )


# # # def create_campaign(db, campaign: CampaignCreate):
# # #     try:
# # #         print("🔥 CREATE CAMPAIGN STARTED")
# # #         print(campaign.model_dump())
# # #         from app.models.campaign import Campaign

# # #         new_campaign = Campaign(
# # #             campaign_name=campaign.campaign_name,
# # #             channel=campaign.channel,
# # #             goal_label=campaign.goal_label,
# # #             status="draft",
# # #             current_step=1,
# # #         )
# # #         db.add(new_campaign)
# # #         db.commit()
# # #         db.refresh(new_campaign)
# # #         print("✅ CAMPAIGN CREATED")
# # #         return new_campaign
# # #     except Exception as e:
# # #         print("❌ CREATE CAMPAIGN ERROR")
# # #         print(str(e))
# # #         db.rollback()
# # #         raise e


# # # def update_campaign_content(db, campaign_id, content_data):
# # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # #     if not campaign:
# # #         raise HTTPException(status_code=404, detail="Campaign not found")
# # #     campaign.subject_line = content_data.subject_line
# # #     campaign.preview_text = content_data.preview_text
# # #     campaign.template_id = content_data.template_id
# # #     campaign.sender_identity_id = content_data.sender_identity_id
# # #     campaign.current_step = 3
# # #     db.commit()
# # #     db.refresh(campaign)
# # #     return campaign


# # # def update_campaign_schedule(db, campaign_id, schedule_data):
# # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # #     if not campaign:
# # #         return None
# # #     campaign.send_mode = schedule_data.send_mode
# # #     campaign.scheduled_at = schedule_data.scheduled_at
# # #     campaign.timezone = schedule_data.timezone
# # #     campaign.current_step = 4
# # #     db.commit()
# # #     db.refresh(campaign)
# # #     return campaign


# # # import asyncio


# # # def _blocks_to_html(content, campaign_name):
# # #     try:
# # #         blocks = _json.loads(content)
# # #         html_parts = []
# # #         for block in blocks:
# # #             btype = block.get("type", "")
# # #             props = block.get("props", {})
# # #             if btype == "text":
# # #                 html_parts.append(
# # #                     f'<p style="color:{props.get("color","#000")};font-size:{props.get("fontSize","14px")}">{props.get("text","")}</p>'
# # #                 )
# # #             elif btype == "image":
# # #                 html_parts.append(
# # #                     f'<img src="{props.get("url","")}" alt="{props.get("alt","")}" style="max-width:100%"/>'
# # #                 )
# # #             elif btype == "button":
# # #                 html_parts.append(
# # #                     f'<a href="{props.get("url","#")}" style="background:{props.get("bgColor","#4f46e5")};color:{props.get("textColor","#fff")};padding:10px 20px;border-radius:6px;text-decoration:none;display:inline-block">{props.get("label","Click")}</a>'
# # #                 )
# # #             elif btype == "footer":
# # #                 html_parts.append(
# # #                     f'<p style="color:{props.get("color","#999")};font-size:12px">{props.get("text","")}</p>'
# # #                 )
# # #             elif btype == "divider":
# # #                 html_parts.append(
# # #                     f'<hr style="border:none;border-top:1px solid {props.get("color","#e2e8f0")};margin:16px 0"/>'
# # #                 )
# # #         return f'<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">{"".join(html_parts)}</div>'
# # #     except:
# # #         return content or f"<h2>{campaign_name}</h2>"


# # # async def finalize_campaign(db, log_db, campaign_id, finalize_data):
# # #     from app.models.template import Template
# # #     from app.models.lists import ListContact
# # #     from app.models.contact import Contact

# # #     print(f"\n{'='*60}")
# # #     print(f"🚀 FINALIZING CAMPAIGN {campaign_id}")
# # #     print(f"{'='*60}\n")

# # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # #     if not campaign:
# # #         raise Exception("Campaign not found")

# # #     campaign.current_step = 6
# # #     channel = campaign.channel
# # #     print(f"   📡 Channel: {channel}")

# # #     if campaign.send_mode == "immediate":

# # #         print("📍 STEP 1: Fetching audience contacts...")
# # #         audience_list_ids = campaign.audience_list_ids or []
# # #         exclude_list_ids = campaign.exclude_list_ids or []
# # #         print(f"   Audience lists: {audience_list_ids}")
# # #         print(f"   Exclude lists: {exclude_list_ids}")

# # #         if not audience_list_ids:
# # #             raise HTTPException(status_code=400, detail="No audience lists selected")

# # #         audience_list_ids = [int(x) for x in audience_list_ids]
# # #         exclude_list_ids = (
# # #             [int(x) for x in exclude_list_ids] if exclude_list_ids else []
# # #         )

# # #         contact_ids_query = db.query(ListContact.contact_id).filter(
# # #             ListContact.list_id.in_(audience_list_ids)
# # #         )
# # #         if exclude_list_ids:
# # #             excluded_ids = (
# # #                 db.query(ListContact.contact_id)
# # #                 .filter(ListContact.list_id.in_(exclude_list_ids))
# # #                 .subquery()
# # #             )
# # #             contact_ids_query = contact_ids_query.filter(
# # #                 ListContact.contact_id.notin_(excluded_ids)
# # #             )

# # #         contact_ids = [row.contact_id for row in contact_ids_query.all()]
# # #         print(f"   ✅ Found {len(contact_ids)} contacts")

# # #         print(
# # #             f"\n📍 STEP 2: Fetching {'phone numbers' if channel == 'whatsapp' else 'email addresses'}..."
# # #         )

# # #         contacts = []
# # #         if contact_ids:
# # #             contacts = (
# # #                 db.query(Contact)
# # #                 .filter(Contact.id.in_(contact_ids), Contact.is_suppressed == False)
# # #                 .all()
# # #             )

# # #         print("\n📍 STEP 3: Fetching template...")
# # #         if not campaign.template_id:
# # #             raise HTTPException(status_code=400, detail="No template selected")

# # #         template = (
# # #             log_db.query(Template)
# # #             .filter(Template.id == int(campaign.template_id))
# # #             .first()
# # #         )
# # #         if not template:
# # #             raise HTTPException(status_code=404, detail="Template not found")
# # #         print(f"   ✅ Using template: {template.name}")

# # #         if channel == "whatsapp":
# # #             print(f"\n📍 STEP 4: Sending WhatsApp messages...")
# # #             recipients = [
# # #                 {"phone": c.phone, "name": c.full_name or c.phone}
# # #                 for c in contacts
# # #                 if c.phone
# # #             ]
# # #             print(f"   ✅ Found {len(recipients)} recipients with valid phone numbers")
# # #             if not recipients:
# # #                 raise HTTPException(
# # #                     status_code=400, detail="No contacts with phone numbers found"
# # #                 )
# # #             send_result = await send_bulk_whatsapp(
# # #                 recipients=recipients,
# # #                 template_name=template.name,
# # #                 language_code="en",
# # #             )
# # #             print(f"   ✅ WhatsApp messages sent!")

# # #             success_count = len(send_result.get("success", []))

# # #             # CORRECTED INDENTATION (12 spaces relative to the if block)
# # #             campaign.total_sent = success_count
# # #             campaign.total_delivered = success_count

# # #             campaign.total_opened = 0
# # #             campaign.total_clicked = 0
# # #             campaign.total_bounced = 0
# # #             campaign.total_unsubscribed = 0

# # #             campaign.delivery_rate = 100 if success_count > 0 else 0
# # #             campaign.open_rate = 0
# # #             campaign.click_rate = 0
# # #             campaign.bounce_rate = 0

# # #             from app.models.message_log import MessageLog
# # #             for item in send_result.get("success", []):
# # #                 log = MessageLog(
# # #                     recipient_phone=item["phone"],
# # #                     recipient_name=item.get("name", item["phone"]),
# # #                     message=f"Template: {template.name}",
# # #                     template_name=template.name,
# # #                     campaign_id=str(campaign_id),
# # #                     campaign_name=campaign.campaign_name,
# # #                     status="sent",
# # #                     wamid=item.get("message_id"),
# # #                     sent_at=datetime.now(timezone.utc),
# # #                     direction="outgoing",
# # #                     source="campaign",
# # #                 )
# # #                 db.add(log)

# # #             for item in send_result.get("failed", []):
# # #                 log = MessageLog(
# # #                     recipient_phone=item["phone"],
# # #                     recipient_name=item.get("name", item["phone"]),
# # #                     message=f"Template: {template.name}",
# # #                     template_name=template.name,
# # #                     campaign_id=str(campaign_id),
# # #                     campaign_name=campaign.campaign_name,
# # #                     status="failed",
# # #                     error_reason=item.get("error"),
# # #                     sent_at=datetime.now(timezone.utc),
# # #                     direction="outgoing",
# # #                     source="campaign",
# # #                 )
# # #                 db.add(log)

# # #             db.commit()

# # #         else:
# # #             print(f"\n📍 STEP 4: Sending emails...")
# # #             recipients_email = [c.email for c in contacts if c.email]
# # #             print(f"   ✅ Found {len(recipients_email)} recipients with valid emails")

# # #             if not recipients_email:
# # #                 contacts = [fallback_contact()]
# # #                 recipients_email = [FALLBACK_EMAIL]
# # #                 print(f"   No valid contact emails. Using fallback: {FALLBACK_EMAIL}")

# # #             html_body = _blocks_to_html(template.content, campaign.campaign_name)

# # #             send_result = await send_campaign_emails(
# # #                 log_db=log_db,
# # #                 campaign=campaign,
# # #                 contacts=contacts,
# # #                 subject=campaign.subject_line or "Campaign Email",
# # #                 html_body=html_body,
# # #                 template_name=template.name,
# # #             )
# # #             print(f"   ✅ Emails sent!")

# # #             total_sent = len(recipients_email)

# # #             # CORRECTED INDENTATION (12 spaces relative to the else block)
# # #             campaign.total_sent = total_sent
# # #             campaign.total_delivered = total_sent

# # #             campaign.total_opened = 0
# # #             campaign.total_clicked = 0
# # #             campaign.total_bounced = 0
# # #             campaign.total_unsubscribed = 0

# # #             campaign.delivery_rate = 100 if total_sent > 0 else 0
# # #             campaign.open_rate = 0
# # #             campaign.click_rate = 0
# # #             campaign.bounce_rate = 0

# # #         print("\n📍 STEP 5: Updating campaign status...")
# # #         campaign.status = "sent"
# # #         campaign.email_sent_at = datetime.now(timezone.utc)
# # #         campaign.sent_at = datetime.now(timezone.utc)
# # #         create_notification(
# # #             db=db,
# # #             notification_type="campaignSent",
# # #             title="Campaign Sent",
# # #             message=f'Campaign "{campaign.campaign_name}" sent successfully',
# # #         )
# # #         print(f"   ✅ Campaign marked as sent")

# # #     else:
# # #         print(f"\n📅 Scheduling campaign for {campaign.scheduled_at}")
# # #         campaign.status = "scheduled"
# # #         create_notification(
# # #             db=db,
# # #             notification_type="campaignScheduled",
# # #             title="Campaign Scheduled",
# # #             message=f'Campaign "{campaign.campaign_name}" scheduled successfully',
# # #         )

# # #     db.commit()
# # #     db.refresh(campaign)

# # #     print(f"\n{'='*60}")
# # #     print(f"✅ CAMPAIGN FINALIZED SUCCESSFULLY")
# # #     print(f"{'='*60}\n")

# # #     return {
# # #         "message": "Campaign finalized",
# # #         "campaign": campaign,
# # #         "channel": channel,
# # #         "status": campaign.status,
# # #     }


# # # async def send_test_email(db, log_db, campaign_id, email_data):
# # #     from app.models.template import Template

# # #     print(f"\n{'='*60}")
# # #     print(f"📧 SENDING TEST EMAIL")
# # #     print(f"{'='*60}\n")

# # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # #     if not campaign:
# # #         raise HTTPException(status_code=404, detail="Campaign not found")

# # #     email = email_data.email or FALLBACK_EMAIL
# # #     print(f"   To: {email}")

# # #     html_body = f"""
# # #     <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
# # #         <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
# # #             <strong>📊 TEST EMAIL PREVIEW</strong>
# # #             <p style="color: #666; font-size: 12px; margin: 10px 0 0 0;">
# # #                 This is a test email for: <strong>{campaign.campaign_name}</strong>
# # #             </p>
# # #         </div>
# # #         <h2 style="margin-top: 0;">{campaign.campaign_name}</h2>
# # #     """

# # #     if campaign.template_id:
# # #         template = (
# # #             log_db.query(Template)
# # #             .filter(Template.id == int(campaign.template_id))
# # #             .first()
# # #         )
# # #         if template and template.content:
# # #             html_body += _blocks_to_html(template.content, campaign.campaign_name)
# # #             print(f"   Template: {template.name}")
# # #         else:
# # #             html_body += f"<p>This email will use the selected template.</p>"
# # #     else:
# # #         html_body += f"<p>⚠️ No template selected for campaign</p>"

# # #     html_body += f"""
# # #         <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
# # #         <p style="color: #999; font-size: 12px;">
# # #             This is a test email. When sent, this campaign will reach
# # #             {len([x for x in (campaign.audience_list_ids or [])]) or 0} audience lists.
# # #         </p>
# # #     </div>
# # #     """

# # #     try:
# # #         await send_email(
# # #             recipients=[email],
# # #             subject=campaign.subject_line or "Test Campaign Email",
# # #             html_body=html_body,
# # #         )
# # #         print(f"   ✅ Test email sent successfully!\n")
# # #         return {
# # #             "message": "Test email sent successfully",
# # #             "sent_to": email,
# # #             "delivery_status": "sent",
# # #         }
# # #     except Exception as e:
# # #         create_notification(
# # #             db=db,
# # #             notification_type="campaignFailed",
# # #             title="Campaign Failed",
# # #             message=f'Campaign "{campaign.campaign_name}" failed to send',
# # #         )
# # #         print(f"   ❌ Failed: {str(e)}\n")
# # #         return {
# # #             "message": "Test email attempted, but AWS SES rejected it",
# # #             "sent_to": email,
# # #             "delivery_status": "failed",
# # #             "error": str(e),
# # #         }


# # # def get_all_campaigns(db: Session):
# # #     campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
# # #     return campaigns


# # # def get_campaign_by_id(db, campaign_id: str):
# # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # #     if not campaign:
# # #         raise HTTPException(status_code=404, detail="Campaign not found")
# # #     return campaign


# # # def duplicate_campaign(db: Session, campaign_id: str):
# # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # #     if not campaign:
# # #         return {"error": "Campaign not found"}
# # #     duplicated = Campaign(
# # #         campaign_name=f"Copy of {campaign.campaign_name}",
# # #         channel=campaign.channel,
# # #         goal_label=campaign.goal_label,
# # #         status="draft",
# # #     )
# # #     db.add(duplicated)
# # #     db.commit()
# # #     db.refresh(duplicated)
# # #     return duplicated


# # # def update_campaign_audience(db, campaign_id, audience):
# # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # #     if not campaign:
# # #         raise Exception("Campaign not found")
# # #     campaign.audience_list_ids = audience.audience_list_ids
# # #     campaign.exclude_list_ids = audience.exclude_list_ids
# # #     campaign.estimated_recipients = audience.estimated_recipients
# # #     campaign.suppressed_count = audience.suppressed_count
# # #     campaign.current_step = max(campaign.current_step, 2)
# # #     db.commit()
# # #     db.refresh(campaign)
# # #     return {"success": True}


# # # def update_campaign(db: Session, campaign_id: int, payload):
# # #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # #     if not campaign:
# # #         raise HTTPException(status_code=404, detail="Campaign not found")
# # #     campaign.campaign_name = payload.campaign_name
# # #     campaign.channel = payload.channel
# # #     campaign.goal_label = payload.goal_label
# # #     db.commit()
# # #     db.refresh(campaign)
# # #     return campaign


# # # def get_campaign_logs(main_db: Session, log_db: Session, campaign_id: str):
# # #     from app.models.log import EmailLog

# # #     campaign = main_db.query(Campaign).filter(Campaign.id == campaign_id).first()
# # #     if not campaign:
# # #         raise HTTPException(status_code=404, detail="Campaign not found")

# # #     logs = (
# # #         log_db.query(EmailLog)
# # #         .filter(EmailLog.campaign_id == campaign_id)
# # #         .order_by(EmailLog.created_at.desc())
# # #         .all()
# # #     )

# # #     summary_rows = (
# # #         log_db.query(EmailLog.status, func.count(EmailLog.id))
# # #         .filter(EmailLog.campaign_id == campaign_id)
# # #         .group_by(EmailLog.status)
# # #         .all()
# # #     )
# # #     counts = {status: count for status, count in summary_rows}

# # #     return {
# # #         "campaign": campaign,
# # #         "logs": [
# # #             {
# # #                 "id": log.id,
# # #                 "contactName": log.recipient_name,
# # #                 "email": log.recipient_email,
# # #                 "phone": log.recipient_phone,
# # #                 "status": log.status,
# # #                 "failureReason": log.bounce_reason or log.error_message,
# # #                 "sentAt": log.sent_at,
# # #                 "deliveredAt": log.delivered_at,
# # #                 "openedAt": log.opened_at,
# # #                 "clickedAt": log.clicked_at,
# # #                 "openCount": log.opens,
# # #                 "device": None,
# # #                 "browser": None,
# # #                 "country": None,
# # #                 "recipient_name": log.recipient_name,
# # #                 "recipient_email": log.recipient_email,
# # #                 "recipient_phone": log.recipient_phone,
# # #                 "subject": log.subject,
# # #                 "template_name": log.template_name,
# # #                 "campaign_name": log.campaign_name,
# # #                 "opens": log.opens,
# # #                 "clicks": log.clicks,
# # #                 "sent_at": log.sent_at,
# # #                 "bounce_reason": log.bounce_reason or log.error_message,
# # #             }
# # #             for log in logs
# # #         ],
# # #         "summary": {
# # #             "total": len(logs),
# # #             "sent": counts.get("sent", 0),
# # #             "delivered": counts.get("delivered", 0),
# # #             "opened": counts.get("opened", 0),
# # #             "clicked": counts.get("clicked", 0),
# # #             "failed": counts.get("failed", 0),
# # #             "bounced": counts.get("bounced", 0),
# # #             "unsubscribed": counts.get("unsubscribed", 0),
# # #         },
# # #     }


# # from sqlalchemy import text, func
# # from sqlalchemy.orm import Session
# # from fastapi import HTTPException

# # from app.models.campaign import Campaign
# # from app.schemas.campaign import CampaignCreate

# # from app.utils.notification_service import create_notification

# # from fastapi import HTTPException
# # from app.services.whatsapp_service import send_bulk_whatsapp
# # from copy import deepcopy
# # from app.services.email_service import send_campaign_emails, send_email
# # from datetime import datetime, timezone
# # from types import SimpleNamespace
# # import os
# # import json as _json

# # FALLBACK_EMAIL = os.getenv("CAMPAIGN_FALLBACK_EMAIL", "sathish.wynsync@gmail.com")


# # def fallback_contact():
# #     return SimpleNamespace(
# #         id=None,
# #         full_name="Fallback Recipient",
# #         email=FALLBACK_EMAIL,
# #         phone=None,
# #     )


# # def create_campaign(db, campaign: CampaignCreate):
# #     try:
# #         print("🔥 CREATE CAMPAIGN STARTED")
# #         print(campaign.model_dump())
# #         from app.models.campaign import Campaign

# #         new_campaign = Campaign(
# #             campaign_name=campaign.campaign_name,
# #             channel=campaign.channel,
# #             goal_label=campaign.goal_label,
# #             status="draft",
# #             current_step=1,
# #         )
# #         db.add(new_campaign)
# #         db.commit()
# #         db.refresh(new_campaign)
# #         print("✅ CAMPAIGN CREATED")
# #         return new_campaign
# #     except Exception as e:
# #         print("❌ CREATE CAMPAIGN ERROR")
# #         print(str(e))
# #         db.rollback()
# #         raise e


# # def update_campaign_content(db, campaign_id, content_data):
# #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         raise HTTPException(status_code=404, detail="Campaign not found")
# #     campaign.subject_line = content_data.subject_line
# #     campaign.preview_text = content_data.preview_text
# #     campaign.template_id = content_data.template_id
# #     campaign.sender_identity_id = content_data.sender_identity_id
# #     campaign.current_step = 3
# #     db.commit()
# #     db.refresh(campaign)
# #     return campaign


# # def update_campaign_schedule(db, campaign_id, schedule_data):
# #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         return None
# #     campaign.send_mode = schedule_data.send_mode
# #     campaign.scheduled_at = schedule_data.scheduled_at
# #     campaign.timezone = schedule_data.timezone
# #     campaign.current_step = 4
# #     db.commit()
# #     db.refresh(campaign)
# #     return campaign


# # import asyncio


# # def _blocks_to_html(content, campaign_name):
# #     try:
# #         blocks = _json.loads(content)
# #         html_parts = []
# #         for block in blocks:
# #             btype = block.get("type", "")
# #             props = block.get("props", {})
# #             if btype == "text":
# #                 html_parts.append(
# #                     f'<p style="color:{props.get("color","#000")};font-size:{props.get("fontSize","14px")}">{props.get("text","")}</p>'
# #                 )
# #             elif btype == "image":
# #                 html_parts.append(
# #                     f'<img src="{props.get("url","")}" alt="{props.get("alt","")}" style="max-width:100%"/>'
# #                 )
# #             elif btype == "button":
# #                 html_parts.append(
# #                     f'<a href="{props.get("url","#")}" style="background:{props.get("bgColor","#4f46e5")};color:{props.get("textColor","#fff")};padding:10px 20px;border-radius:6px;text-decoration:none;display:inline-block">{props.get("label","Click")}</a>'
# #                 )
# #             elif btype == "footer":
# #                 html_parts.append(
# #                     f'<p style="color:{props.get("color","#999")};font-size:12px">{props.get("text","")}</p>'
# #                 )
# #             elif btype == "divider":
# #                 html_parts.append(
# #                     f'<hr style="border:none;border-top:1px solid {props.get("color","#e2e8f0")};margin:16px 0"/>'
# #                 )
# #         return f'<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">{"".join(html_parts)}</div>'
# #     except:
# #         return content or f"<h2>{campaign_name}</h2>"


# # async def finalize_campaign(db, log_db, campaign_id, finalize_data):
# #     print("🔥 FINALIZE CAMPAIGN CALLED 🔥")
# #     from app.models.template import Template
# #     from app.models.lists import ListContact
# #     from app.models.contact import Contact

# #     print(f"\n{'='*60}")
# #     print(f"🚀 FINALIZING CAMPAIGN {campaign_id}")
# #     print(f"{'='*60}\n")

# #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         raise Exception("Campaign not found")

# #     campaign.current_step = 6
# #     channel = campaign.channel
# #     print(f"   📡 Channel: {channel}")

# #     if campaign.send_mode == "immediate":

# #         print("📍 STEP 1: Fetching audience contacts...")
# #         audience_list_ids = campaign.audience_list_ids or []
# #         exclude_list_ids = campaign.exclude_list_ids or []
# #         print(f"   Audience lists: {audience_list_ids}")
# #         print(f"   Exclude lists: {exclude_list_ids}")

# #         if not audience_list_ids:
# #             raise HTTPException(status_code=400, detail="No audience lists selected")

# #         audience_list_ids = [int(x) for x in audience_list_ids]
# #         exclude_list_ids = (
# #             [int(x) for x in exclude_list_ids] if exclude_list_ids else []
# #         )

# #         contact_ids_query = db.query(ListContact.contact_id).filter(
# #             ListContact.list_id.in_(audience_list_ids)
# #         )
# #         if exclude_list_ids:
# #             excluded_ids = (
# #                 db.query(ListContact.contact_id)
# #                 .filter(ListContact.list_id.in_(exclude_list_ids))
# #                 .subquery()
# #             )
# #             contact_ids_query = contact_ids_query.filter(
# #                 ListContact.contact_id.notin_(excluded_ids)
# #             )

# #         contact_ids = [row.contact_id for row in contact_ids_query.all()]
# #         print(f"   ✅ Found {len(contact_ids)} contacts")

# #         print(
# #             f"\n📍 STEP 2: Fetching {'phone numbers' if channel == 'whatsapp' else 'email addresses'}..."
# #         )

# #         contacts = []
# #         if contact_ids:
# #             contacts = (
# #                 db.query(Contact)
# #                 .filter(Contact.id.in_(contact_ids), Contact.is_suppressed == False)
# #                 .all()
# #             )

# #         print("\n📍 STEP 3: Fetching template...")
# #         if not campaign.template_id:
# #             raise HTTPException(status_code=400, detail="No template selected")

# #         template = (
# #             log_db.query(Template)
# #             .filter(Template.id == int(campaign.template_id))
# #             .first()
# #         )
# #         if not template:
# #             raise HTTPException(status_code=404, detail="Template not found")
# #         print(f"   ✅ Using template: {template.name}")

# #         if channel == "whatsapp":
# #             print(f"\n📍 STEP 4: Sending WhatsApp messages...")
# #             recipients = [
# #                 {"phone": c.phone, "name": c.full_name or c.phone}
# #                 for c in contacts
# #                 if c.phone
# #             ]
# #             print(f"   ✅ Found {len(recipients)} recipients with valid phone numbers")
# #             if not recipients:
# #                 raise HTTPException(
# #                     status_code=400, detail="No contacts with phone numbers found"
# #                 )
# #             send_result = await send_bulk_whatsapp(
# #                 recipients=recipients,
# #                 template_name=template.name,
# #                 language_code="en",
# #             )
# #             print(f"   ✅ WhatsApp messages sent!")

# #             success_count = len(send_result.get("success", []))

# #             # CORRECTLY INDENTED (12 spaces relative to the if block)
# #             campaign.total_sent = success_count
# #             campaign.total_delivered = success_count

# #             campaign.total_opened = 0
# #             campaign.total_clicked = 0
# #             campaign.total_bounced = 0
# #             campaign.total_unsubscribed = 0

# #             campaign.delivery_rate = 100 if success_count > 0 else 0
# #             campaign.open_rate = 0
# #             campaign.click_rate = 0
# #             campaign.bounce_rate = 0

# #             # Additional debug prints
# #             print("ANALYTICS UPDATED (WhatsApp)")
# #             print("Campaign:", campaign.campaign_name)
# #             print("Success Count:", success_count)

# #             from app.models.message_log import MessageLog
# #             for item in send_result.get("success", []):
# #                 log = MessageLog(
# #                     recipient_phone=item["phone"],
# #                     recipient_name=item.get("name", item["phone"]),
# #                     message=f"Template: {template.name}",
# #                     template_name=template.name,
# #                     campaign_id=str(campaign_id),
# #                     campaign_name=campaign.campaign_name,
# #                     status="sent",
# #                     wamid=item.get("message_id"),
# #                     sent_at=datetime.now(timezone.utc),
# #                     direction="outgoing",
# #                     source="campaign",
# #                 )
# #                 db.add(log)

# #             for item in send_result.get("failed", []):
# #                 log = MessageLog(
# #                     recipient_phone=item["phone"],
# #                     recipient_name=item.get("name", item["phone"]),
# #                     message=f"Template: {template.name}",
# #                     template_name=template.name,
# #                     campaign_id=str(campaign_id),
# #                     campaign_name=campaign.campaign_name,
# #                     status="failed",
# #                     error_reason=item.get("error"),
# #                     sent_at=datetime.now(timezone.utc),
# #                     direction="outgoing",
# #                     source="campaign",
# #                 )
# #                 db.add(log)

# #             db.commit()
# #             db.refresh(campaign)

# #         else:
# #             print(f"\n📍 STEP 4: Sending emails...")
# #             recipients_email = [c.email for c in contacts if c.email]
# #             print(f"   ✅ Found {len(recipients_email)} recipients with valid emails")

# #             if not recipients_email:
# #                 contacts = [fallback_contact()]
# #                 recipients_email = [FALLBACK_EMAIL]
# #                 print(f"   No valid contact emails. Using fallback: {FALLBACK_EMAIL}")

# #             html_body = _blocks_to_html(template.content, campaign.campaign_name)

# #             send_result = await send_campaign_emails(
# #                 log_db=log_db,
# #                 campaign=campaign,
# #                 contacts=contacts,
# #                 subject=campaign.subject_line or "Campaign Email",
# #                 html_body=html_body,
# #                 template_name=template.name,
# #             )
# #             print(f"   ✅ Emails sent!")

# #             total_sent = len(recipients_email)

# #             # CORRECTLY INDENTED (12 spaces relative to the else block)
# #             campaign.total_sent = total_sent
# #             campaign.total_delivered = total_sent
# #             print("BEFORE COMMIT")
# #             print("total_sent =", campaign.total_sent)
# #             print("total_delivered =", campaign.total_delivered)

# #             campaign.total_opened = 0
# #             campaign.total_clicked = 0
# #             campaign.total_bounced = 0
# #             campaign.total_unsubscribed = 0

# #             campaign.delivery_rate = 100 if total_sent > 0 else 0
# #             campaign.open_rate = 0
# #             campaign.click_rate = 0
# #             campaign.bounce_rate = 0

# #             # Additional debug prints
# #             print("EMAIL ANALYTICS UPDATED")
# #             print("Campaign:", campaign.campaign_name)
# #             print("Total Sent:", total_sent)

# #             db.commit()
# #             db.refresh(campaign)
# #             print("AFTER COMMIT")
# #             print("total_sent =", campaign.total_sent)
# #             print("total_delivered =", campaign.total_delivered)

# #         print("\n📍 STEP 5: Updating campaign status...")
# #         print("================================")
# #         print("UPDATING ANALYTICS")
# #         print("Recipients:", total_recipients)

# #         campaign.total_sent = total_recipients
# #         campaign.total_delivered = total_recipients
# #         campaign.total_opened = 0
# #         campaign.total_clicked = 0
# #         campaign.total_bounced = 0
# #         campaign.total_unsubscribed = 0

# #         db.add(campaign)
# #         db.commit()
# #         db.refresh(campaign)

# #         print("SAVED")
# #         print("total_sent =", campaign.total_sent)
# #         print("total_delivered =", campaign.total_delivered)
# #         print("================================")
# #         campaign.status = "sent"
# #         campaign.email_sent_at = datetime.now(timezone.utc)
# #         campaign.sent_at = datetime.now(timezone.utc)
# #         create_notification(
# #             db=db,
# #             notification_type="campaignSent",
# #             title="Campaign Sent",
# #             message=f'Campaign "{campaign.campaign_name}" sent successfully',
# #         )
# #         print(f"   ✅ Campaign marked as sent")

# #     else:
# #         print(f"\n📅 Scheduling campaign for {campaign.scheduled_at}")
# #         campaign.status = "scheduled"
# #         create_notification(
# #             db=db,
# #             notification_type="campaignScheduled",
# #             title="Campaign Scheduled",
# #             message=f'Campaign "{campaign.campaign_name}" scheduled successfully',
# #         )

# #     db.commit()
# #     db.refresh(campaign)

# #     print(f"\n{'='*60}")
# #     print(f"✅ CAMPAIGN FINALIZED SUCCESSFULLY")
# #     print(f"{'='*60}\n")

# #     return {
# #         "message": "Campaign finalized",
# #         "campaign": campaign,
# #         "channel": channel,
# #         "status": campaign.status,
# #     }


# # async def send_test_email(db, log_db, campaign_id, email_data):
# #     from app.models.template import Template

# #     print(f"\n{'='*60}")
# #     print(f"📧 SENDING TEST EMAIL")
# #     print(f"{'='*60}\n")

# #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         raise HTTPException(status_code=404, detail="Campaign not found")

# #     email = email_data.email or FALLBACK_EMAIL
# #     print(f"   To: {email}")

# #     html_body = f"""
# #     <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
# #         <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
# #             <strong>📊 TEST EMAIL PREVIEW</strong>
# #             <p style="color: #666; font-size: 12px; margin: 10px 0 0 0;">
# #                 This is a test email for: <strong>{campaign.campaign_name}</strong>
# #             </p>
# #         </div>
# #         <h2 style="margin-top: 0;">{campaign.campaign_name}</h2>
# #     """

# #     if campaign.template_id:
# #         template = (
# #             log_db.query(Template)
# #             .filter(Template.id == int(campaign.template_id))
# #             .first()
# #         )
# #         if template and template.content:
# #             html_body += _blocks_to_html(template.content, campaign.campaign_name)
# #             print(f"   Template: {template.name}")
# #         else:
# #             html_body += f"<p>This email will use the selected template.</p>"
# #     else:
# #         html_body += f"<p>⚠️ No template selected for campaign</p>"

# #     html_body += f"""
# #         <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
# #         <p style="color: #999; font-size: 12px;">
# #             This is a test email. When sent, this campaign will reach
# #             {len([x for x in (campaign.audience_list_ids or [])]) or 0} audience lists.
# #         </p>
# #     </div>
# #     """

# #     try:
# #         await send_email(
# #             recipients=[email],
# #             subject=campaign.subject_line or "Test Campaign Email",
# #             html_body=html_body,
# #         )
# #         print(f"   ✅ Test email sent successfully!\n")
# #         return {
# #             "message": "Test email sent successfully",
# #             "sent_to": email,
# #             "delivery_status": "sent",
# #         }
# #     except Exception as e:
# #         create_notification(
# #             db=db,
# #             notification_type="campaignFailed",
# #             title="Campaign Failed",
# #             message=f'Campaign "{campaign.campaign_name}" failed to send',
# #         )
# #         print(f"   ❌ Failed: {str(e)}\n")
# #         return {
# #             "message": "Test email attempted, but AWS SES rejected it",
# #             "sent_to": email,
# #             "delivery_status": "failed",
# #             "error": str(e),
# #         }


# # def get_all_campaigns(db: Session):
# #     campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
# #     return campaigns


# # def get_campaign_by_id(db, campaign_id: str):
# #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         raise HTTPException(status_code=404, detail="Campaign not found")
# #     return campaign


# # def duplicate_campaign(db: Session, campaign_id: str):
# #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         return {"error": "Campaign not found"}
# #     duplicated = Campaign(
# #         campaign_name=f"Copy of {campaign.campaign_name}",
# #         channel=campaign.channel,
# #         goal_label=campaign.goal_label,
# #         status="draft",
# #     )
# #     db.add(duplicated)
# #     db.commit()
# #     db.refresh(duplicated)
# #     return duplicated


# # def update_campaign_audience(db, campaign_id, audience):
# #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         raise Exception("Campaign not found")
# #     campaign.audience_list_ids = audience.audience_list_ids
# #     campaign.exclude_list_ids = audience.exclude_list_ids
# #     campaign.estimated_recipients = audience.estimated_recipients
# #     campaign.suppressed_count = audience.suppressed_count
# #     campaign.current_step = max(campaign.current_step, 2)
# #     db.commit()
# #     db.refresh(campaign)
# #     return {"success": True}


# # def update_campaign(db: Session, campaign_id: int, payload):
# #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         raise HTTPException(status_code=404, detail="Campaign not found")
# #     campaign.campaign_name = payload.campaign_name
# #     campaign.channel = payload.channel
# #     campaign.goal_label = payload.goal_label
# #     db.commit()
# #     db.refresh(campaign)
# #     return campaign


# # def get_campaign_logs(main_db: Session, log_db: Session, campaign_id: str):
# #     from app.models.log import EmailLog

# #     campaign = main_db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         raise HTTPException(status_code=404, detail="Campaign not found")

# #     logs = (
# #         log_db.query(EmailLog)
# #         .filter(EmailLog.campaign_id == campaign_id)
# #         .order_by(EmailLog.created_at.desc())
# #         .all()
# #     )

# #     summary_rows = (
# #         log_db.query(EmailLog.status, func.count(EmailLog.id))
# #         .filter(EmailLog.campaign_id == campaign_id)
# #         .group_by(EmailLog.status)
# #         .all()
# #     )
# #     counts = {status: count for status, count in summary_rows}

# #     return {
# #         "campaign": campaign,
# #         "logs": [
# #             {
# #                 "id": log.id,
# #                 "contactName": log.recipient_name,
# #                 "email": log.recipient_email,
# #                 "phone": log.recipient_phone,
# #                 "status": log.status,
# #                 "failureReason": log.bounce_reason or log.error_message,
# #                 "sentAt": log.sent_at,
# #                 "deliveredAt": log.delivered_at,
# #                 "openedAt": log.opened_at,
# #                 "clickedAt": log.clicked_at,
# #                 "openCount": log.opens,
# #                 "device": None,
# #                 "browser": None,
# #                 "country": None,
# #                 "recipient_name": log.recipient_name,
# #                 "recipient_email": log.recipient_email,
# #                 "recipient_phone": log.recipient_phone,
# #                 "subject": log.subject,
# #                 "template_name": log.template_name,
# #                 "campaign_name": log.campaign_name,
# #                 "opens": log.opens,
# #                 "clicks": log.clicks,
# #                 "sent_at": log.sent_at,
# #                 "bounce_reason": log.bounce_reason or log.error_message,
# #             }
# #             for log in logs
# #         ],
# #         "summary": {
# #             "total": len(logs),
# #             "sent": counts.get("sent", 0),
# #             "delivered": counts.get("delivered", 0),
# #             "opened": counts.get("opened", 0),
# #             "clicked": counts.get("clicked", 0),
# #             "failed": counts.get("failed", 0),
# #             "bounced": counts.get("bounced", 0),
# #             "unsubscribed": counts.get("unsubscribed", 0),
# #         },
# #     }


# from sqlalchemy import text, func
# from sqlalchemy.orm import Session
# from fastapi import HTTPException

# from app.models.campaign import Campaign
# from app.schemas.campaign import CampaignCreate

# from app.utils.notification_service import create_notification
# from app.utils.render_email_template import render_blocks_to_html

# from fastapi import HTTPException
# from app.services.whatsapp_service import send_bulk_whatsapp
# from copy import deepcopy
# from app.services.email_service import send_campaign_emails, send_email
# from datetime import datetime, timezone
# from types import SimpleNamespace
# from zoneinfo import ZoneInfo
# from datetime import timezone
# import os
# import json as _json


# FALLBACK_EMAIL = os.getenv("CAMPAIGN_FALLBACK_EMAIL", "sathish.wynsync@gmail.com")


# def fallback_contact():
#     return SimpleNamespace(
#         id=None,
#         full_name="Fallback Recipient",
#         email=FALLBACK_EMAIL,
#         phone=None,
#     )


# def create_campaign(db, campaign: CampaignCreate):
#     try:
#         print("🔥 CREATE CAMPAIGN STARTED")
#         print(campaign.model_dump())
#         from app.models.campaign import Campaign

#         new_campaign = Campaign(
#             campaign_name=campaign.campaign_name,
#             channel=campaign.channel,
#             goal_label=campaign.goal_label,
#             status="draft",
#             current_step=1,
#         )
#         db.add(new_campaign)
#         db.commit()
#         db.refresh(new_campaign)
#         print("✅ CAMPAIGN CREATED")
#         return new_campaign
#     except Exception as e:
#         print("❌ CREATE CAMPAIGN ERROR")
#         print(str(e))
#         db.rollback()
#         raise e


# def update_campaign_content(db, campaign_id, content_data):
#     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
#     if not campaign:
#         raise HTTPException(status_code=404, detail="Campaign not found")
#     campaign.subject_line = content_data.subject_line
#     campaign.preview_text = content_data.preview_text
#     campaign.template_id = content_data.template_id
#     campaign.sender_identity_id = content_data.sender_identity_id
#     campaign.current_step = 3
#     db.commit()
#     db.refresh(campaign)
#     return campaign


# def update_campaign_schedule(db, campaign_id, schedule_data):
    
#     print("\n========== SCHEDULE UPDATE ==========")
#     print("send_mode =", schedule_data.send_mode)
#     print("scheduled_at =", schedule_data.scheduled_at)
#     print("timezone =", schedule_data.timezone)
#     print("=====================================\n")

#     campaign = db.query(Campaign).filter(
#         Campaign.id == campaign_id
#     ).first()

#     if not campaign:
#         return None

#     campaign.send_mode = schedule_data.send_mode

#     if (
#         schedule_data.send_mode == "scheduled"
#         and schedule_data.scheduled_at
#         and schedule_data.timezone
#     ):
#         local_dt = schedule_data.scheduled_at.replace(
#             tzinfo=ZoneInfo(schedule_data.timezone)
#         )

#         utc_dt = local_dt.astimezone(timezone.utc)

#         print("LOCAL TIME =", local_dt)
#         print("UTC TIME   =", utc_dt)

#         campaign.scheduled_at = utc_dt
#     else:
#         campaign.scheduled_at = None

#     campaign.timezone = schedule_data.timezone
#     campaign.current_step = 4

#     db.commit()
#     db.refresh(campaign)

#     return campaign


# import asyncio


# async def finalize_campaign(db, log_db, campaign_id, finalize_data):
#     print("🔥 FINALIZE CAMPAIGN CALLED 🔥")
#     from app.models.template import Template
#     from app.models.lists import ListContact
#     from app.models.contact import Contact

#     print(f"\n{'='*60}")
#     print(f"🚀 FINALIZING CAMPAIGN {campaign_id}")
#     print(f"{'='*60}\n")

#     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
#     if not campaign:
#         raise Exception("Campaign not found")

#     campaign.current_step = 6
#     channel = campaign.channel
#     print(f"   📡 Channel: {channel}")

#     if campaign.send_mode == "immediate":

#         print("📍 STEP 1: Fetching audience contacts...")
#         audience_list_ids = campaign.audience_list_ids or []
#         exclude_list_ids = campaign.exclude_list_ids or []
#         print(f"   Audience lists: {audience_list_ids}")
#         print(f"   Exclude lists: {exclude_list_ids}")

#         if not audience_list_ids:
#             raise HTTPException(status_code=400, detail="No audience lists selected")

#         audience_list_ids = [int(x) for x in audience_list_ids]
#         exclude_list_ids = (
#             [int(x) for x in exclude_list_ids] if exclude_list_ids else []
#         )

#         contact_ids_query = db.query(ListContact.contact_id).filter(
#             ListContact.list_id.in_(audience_list_ids)
#         )
#         if exclude_list_ids:
#             excluded_ids = (
#                 db.query(ListContact.contact_id)
#                 .filter(ListContact.list_id.in_(exclude_list_ids))
#                 .subquery()
#             )
#             contact_ids_query = contact_ids_query.filter(
#                 ListContact.contact_id.notin_(excluded_ids)
#             )

#         contact_ids = [row.contact_id for row in contact_ids_query.all()]
#         print(f"   ✅ Found {len(contact_ids)} contacts")

#         print(
#             f"\n📍 STEP 2: Fetching {'phone numbers' if channel == 'whatsapp' else 'email addresses'}..."
#         )

#         contacts = []
#         if contact_ids:
#             contacts = (
#                 db.query(Contact)
#                 .filter(Contact.id.in_(contact_ids), Contact.is_suppressed == False)
#                 .all()
#             )

#         print("\n📍 STEP 3: Fetching template...")
#         if not campaign.template_id:
#             raise HTTPException(status_code=400, detail="No template selected")

#         template = (
#             log_db.query(Template)
#             .filter(Template.id == int(campaign.template_id))
#             .first()
#         )
#         if not template:
#             raise HTTPException(status_code=404, detail="Template not found")
#         print(f"   ✅ Using template: {template.name}")

#         if channel == "whatsapp":
#             print(f"\n📍 STEP 4: Sending WhatsApp messages...")
#             recipients = [
#                 {"phone": c.phone, "name": c.full_name or c.phone}
#                 for c in contacts
#                 if c.phone
#             ]
#             print(f"   ✅ Found {len(recipients)} recipients with valid phone numbers")
#             if not recipients:
#                 raise HTTPException(
#                     status_code=400, detail="No contacts with phone numbers found"
#                 )
#             send_result = await send_bulk_whatsapp(
#                 recipients=recipients,
#                 template_name=template.name,
#                 language_code="en",
#             )
#             print(f"   ✅ WhatsApp messages sent!")

#             success_count = len(send_result.get("success", []))

#             # Update campaign analytics
#             campaign.total_sent = success_count
#             campaign.total_delivered = success_count
#             campaign.total_opened = 0
#             campaign.total_clicked = 0
#             campaign.total_bounced = 0
#             campaign.total_unsubscribed = 0
#             campaign.delivery_rate = 100 if success_count > 0 else 0
#             campaign.open_rate = 0
#             campaign.click_rate = 0
#             campaign.bounce_rate = 0

#             print("ANALYTICS UPDATED (WhatsApp)")
#             print("Campaign:", campaign.campaign_name)
#             print("Success Count:", success_count)

#             from app.models.message_log import MessageLog

#             for item in send_result.get("success", []):
#                 log = MessageLog(
#                     recipient_phone=item["phone"],
#                     recipient_name=item.get("name", item["phone"]),
#                     message=f"Template: {template.name}",
#                     template_name=template.name,
#                     campaign_id=str(campaign_id),
#                     campaign_name=campaign.campaign_name,
#                     status="sent",
#                     wamid=item.get("message_id"),
#                     sent_at=datetime.now(timezone.utc),
#                     direction="outgoing",
#                     source="campaign",
#                 )
#                 db.add(log)

#             for item in send_result.get("failed", []):
#                 log = MessageLog(
#                     recipient_phone=item["phone"],
#                     recipient_name=item.get("name", item["phone"]),
#                     message=f"Template: {template.name}",
#                     template_name=template.name,
#                     campaign_id=str(campaign_id),
#                     campaign_name=campaign.campaign_name,
#                     status="failed",
#                     error_reason=item.get("error"),
#                     sent_at=datetime.now(timezone.utc),
#                     direction="outgoing",
#                     source="campaign",
#                 )
#                 db.add(log)

#             db.commit()
#             db.refresh(campaign)

#         else:  # Email channel
#             print(f"\n📍 STEP 4: Sending emails...")
#             recipients_email = [c.email for c in contacts if c.email]
#             print(f"   ✅ Found {len(recipients_email)} recipients with valid emails")

#             if not recipients_email:
#                 contacts = [fallback_contact()]
#                 recipients_email = [FALLBACK_EMAIL]
#                 print(f"   No valid contact emails. Using fallback: {FALLBACK_EMAIL}")

#             send_result = await send_campaign_emails(
#                 log_db=log_db,
#                 campaign=campaign,
#                 contacts=contacts,
#                 subject=campaign.subject_line or "Campaign Email",
#                 template_content=template.content,
#                 template_name=template.name,
#             )
#             print(f"   ✅ Emails sent!")

#             total_sent = len(recipients_email)

#             # Update campaign analytics
#             campaign.total_sent = total_sent
#             campaign.total_delivered = total_sent
#             campaign.total_opened = 0
#             campaign.total_clicked = 0
#             campaign.total_bounced = 0
#             campaign.total_unsubscribed = 0
#             campaign.delivery_rate = 100 if total_sent > 0 else 0
#             campaign.open_rate = 0
#             campaign.click_rate = 0
#             campaign.bounce_rate = 0

#             print("EMAIL ANALYTICS UPDATED")
#             print("Campaign:", campaign.campaign_name)
#             print("Total Sent:", total_sent)

#             db.commit()
#             db.refresh(campaign)

#         print("\n📍 STEP 5: Updating campaign status...")
#         # UPDATE LAST CAMPAIGN FOR CONTACTS

# for contact in contacts:
#     contact.campaign = campaign.campaign_name

# print(
#     f"Updated last campaign for {len(contacts)} contacts"
# )
#         campaign.status = "sent"
#         campaign.email_sent_at = datetime.now(timezone.utc)
#         campaign.sent_at = datetime.now(timezone.utc)
#         create_notification(
#             db=db,
#             notification_type="campaignSent",
#             title="Campaign Sent",
#             message=f'Campaign "{campaign.campaign_name}" sent successfully',
#         )
#         db.commit()
#         db.refresh(campaign)

#         print("FINAL VALUES")
#         print("total_sent =", campaign.total_sent)
#         print("total_delivered =", campaign.total_delivered)
#         print(f"   ✅ Campaign marked as sent")

#     else:  # Scheduled mode
#         print(f"\n📅 Scheduling campaign for {campaign.scheduled_at}")
#         campaign.status = "scheduled"
#         print("STATUS =", campaign.status)
#         print("SEND MODE =", campaign.send_mode)
#         print("SCHEDULED AT =", campaign.scheduled_at)
#         create_notification(
#             db=db,
#             notification_type="campaignScheduled",
#             title="Campaign Scheduled",
#             message=f'Campaign "{campaign.campaign_name}" scheduled successfully',
#         )
#         db.commit()
#         db.refresh(campaign)

#     print(f"\n{'='*60}")
#     print(f"✅ CAMPAIGN FINALIZED SUCCESSFULLY")
#     print(f"{'='*60}\n")

#     return {
#         "message": "Campaign finalized",
#         "campaign": campaign,
#         "channel": channel,
#         "status": campaign.status,
#     }


# async def send_test_email(db, log_db, campaign_id, email_data):
#     from app.models.template import Template

#     print(f"\n{'='*60}")
#     print(f"📧 SENDING TEST EMAIL")
#     print(f"{'='*60}\n")

#     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
#     if not campaign:
#         raise HTTPException(status_code=404, detail="Campaign not found")

#     email = email_data.email or FALLBACK_EMAIL
#     print(f"   To: {email}")

#     html_body = f"""
#     <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
#         <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
#             <strong>📊 TEST EMAIL PREVIEW</strong>
#             <p style="color: #666; font-size: 12px; margin: 10px 0 0 0;">
#                 This is a test email for: <strong>{campaign.campaign_name}</strong>
#             </p>
#         </div>
#         <h2 style="margin-top: 0;">{campaign.campaign_name}</h2>
#     """

#     if campaign.template_id:
#         template = (
#             log_db.query(Template)
#             .filter(Template.id == int(campaign.template_id))
#             .first()
#         )
#         if template and template.content:
#             html_body += _blocks_to_html(template.content, campaign.campaign_name)
#             print(f"   Template: {template.name}")
#         else:
#             html_body += f"<p>This email will use the selected template.</p>"
#     else:
#         html_body += f"<p>⚠️ No template selected for campaign</p>"

#     html_body += f"""
#         <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
#         <p style="color: #999; font-size: 12px;">
#             This is a test email. When sent, this campaign will reach
#             {len([x for x in (campaign.audience_list_ids or [])]) or 0} audience lists.
#         </p>
#     </div>
#     """

#     try:
#         await send_email(
#             recipients=[email],
#             subject=campaign.subject_line or "Test Campaign Email",
#             html_body=html_body,
#         )
#         print(f"   ✅ Test email sent successfully!\n")
#         return {
#             "message": "Test email sent successfully",
#             "sent_to": email,
#             "delivery_status": "sent",
#         }
#     except Exception as e:
#         create_notification(
#             db=db,
#             notification_type="campaignFailed",
#             title="Campaign Failed",
#             message=f'Campaign "{campaign.campaign_name}" failed to send',
#         )
#         print(f"   ❌ Failed: {str(e)}\n")
#         return {
#             "message": "Test email attempted, but AWS SES rejected it",
#             "sent_to": email,
#             "delivery_status": "failed",
#             "error": str(e),
#         }


# def get_all_campaigns(db: Session):
#     campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
#     return campaigns


# # def get_campaign_by_id(db, campaign_id: str):
# #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         raise HTTPException(status_code=404, detail="Campaign not found")
# #     return campaign


# # def get_campaign_by_id(db, campaign_id: str):
# #     from app.models.message_log import MessageLog
# #     from app.models.log import EmailLog

# #     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
# #     if not campaign:
# #         raise HTTPException(status_code=404, detail="Campaign not found")
# #     logs = db.query(MessageLog).filter(MessageLog.campaign_id == str(campaign_id)).all()

# #     total_sent = len(logs)
# #     total_delivered = len([l for l in logs if l.status in ("sent", "delivered")])
# #     total_failed = len([l for l in logs if l.status == "failed"])

# #     return {
# #         "id": str(campaign.id),
# #         "campaign_name": campaign.campaign_name,
# #         "channel": campaign.channel,
# #         "status": campaign.status,
# #         "goal_label": campaign.goal_label,
# #         "sender_identity": campaign.sender_identity_id,
# #         "created_at": str(campaign.created_at),
# #         "estimated_recipients": campaign.estimated_recipients,
# #         "total_sent": total_sent,
# #         "total_delivered": total_delivered,
# #         "total_opened": campaign.total_opened or 0,
# #         "total_clicked": campaign.total_clicked or 0,
# #         "total_bounced": total_failed,
# #         "total_unsubscribed": campaign.total_unsubscribed or 0,
# #         "open_rate": campaign.open_rate or 0,
# #         "click_rate": campaign.click_rate or 0,
# #         "delivery_rate": (
# #             round(total_delivered / total_sent, 4) if total_sent > 0 else 0
# #         ),
# #         "bounce_rate": round(total_failed / total_sent, 4) if total_sent > 0 else 0,
# #         "links": [],
# #         "recipients": [
# #             {
# #                 "recipientId": str(l.id),
# #                 "contactName": l.recipient_name or l.recipient_phone,
# #                 "lastEvent": l.status,
# #             }
# #             for l in logs[:10]
# #         ],
# #     }


# def get_campaign_by_id(db, campaign_id: str):
#     from app.models.message_log import MessageLog
#     from app.models.log import EmailLog

#     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
#     if not campaign:
#         raise HTTPException(status_code=404, detail="Campaign not found")

#     if campaign.channel == "email":
#         logs = db.query(EmailLog).filter(EmailLog.campaign_id == str(campaign_id)).all()
#         total_sent = len(logs)
#         total_delivered = len(
#             [l for l in logs if l.status in ("delivered", "opened", "clicked")]
#         )
#         total_failed = len([l for l in logs if l.status in ("failed", "bounced")])
#         total_opened = len([l for l in logs if l.status in ("opened", "clicked")])
#         total_clicked = len([l for l in logs if l.status == "clicked"])
#         recipients_data = [
#             {
#                 "recipientId": str(l.id),
#                 "contactName": l.recipient_name or l.recipient_email,
#                 "lastEvent": l.status,
#             }
#             for l in logs[:10]
#         ]
#     else:
#         logs = (
#             db.query(MessageLog)
#             .filter(MessageLog.campaign_id == str(campaign_id))
#             .all()
#         )
#         total_sent = len(logs)
#         total_delivered = len([l for l in logs if l.status in ("sent", "delivered")])
#         total_failed = len([l for l in logs if l.status == "failed"])
#         total_opened = len([l for l in logs if l.status == "read"])
#         total_clicked = 0
#         recipients_data = [
#             {
#                 "recipientId": str(l.id),
#                 "contactName": l.recipient_name or l.recipient_phone,
#                 "lastEvent": l.status,
#             }
#             for l in logs[:10]
#         ]

#     return {
#         "id": str(campaign.id),
#         "campaign_name": campaign.campaign_name,
#         "channel": campaign.channel,
#         "status": campaign.status,
#         "goal_label": campaign.goal_label,
#         "audience_list_ids": campaign.audience_list_ids,
#         "exclude_list_ids": campaign.exclude_list_ids,

#         "subject_line": campaign.subject_line,
#         "preview_text": campaign.preview_text,
#         "template_id": campaign.template_id,
#         "sender_identity_id": campaign.sender_identity_id,

#         "send_mode": campaign.send_mode,
#         "scheduled_at": campaign.scheduled_at,
#         "timezone": campaign.timezone,

#         "current_step": campaign.current_step,
#         "sender_identity": campaign.sender_identity_id,
#         "created_at": str(campaign.created_at),
#         "estimated_recipients": campaign.estimated_recipients,
#         "total_sent": total_sent,
#         "total_delivered": total_delivered,
#         "total_opened": total_opened,
#         "total_clicked": total_clicked,
#         "total_bounced": total_failed,
#         "total_unsubscribed": campaign.total_unsubscribed or 0,
#         "open_rate": round(total_opened / total_sent, 4) if total_sent > 0 else 0,
#         "click_rate": round(total_clicked / total_sent, 4) if total_sent > 0 else 0,
#         "delivery_rate": (
#             round(total_delivered / total_sent, 4) if total_sent > 0 else 0
#         ),
#         "bounce_rate": round(total_failed / total_sent, 4) if total_sent > 0 else 0,
#         "links": [],
#         "recipients": recipients_data,
#     }


# def duplicate_campaign(db: Session, campaign_id: str):
#     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
#     if not campaign:
#         return {"error": "Campaign not found"}
#     duplicated = Campaign(
#         campaign_name=f"Copy of {campaign.campaign_name}",
#         channel=campaign.channel,
#         goal_label=campaign.goal_label,
#         status="draft",
#     )
#     db.add(duplicated)
#     db.commit()
#     db.refresh(duplicated)
#     return duplicated


# def update_campaign_audience(db, campaign_id, audience):
#     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
#     if not campaign:
#         raise Exception("Campaign not found")
#     campaign.audience_list_ids = audience.audience_list_ids
#     campaign.exclude_list_ids = audience.exclude_list_ids
#     campaign.estimated_recipients = audience.estimated_recipients
#     campaign.suppressed_count = audience.suppressed_count
#     campaign.current_step = max(campaign.current_step, 2)
#     db.commit()
#     db.refresh(campaign)
#     return {"success": True}


# def update_campaign(db: Session, campaign_id: int, payload):
#     campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
#     if not campaign:
#         raise HTTPException(status_code=404, detail="Campaign not found")
#     campaign.campaign_name = payload.campaign_name
#     campaign.channel = payload.channel
#     campaign.goal_label = payload.goal_label
#     db.commit()
#     db.refresh(campaign)
#     return campaign


# def get_campaign_logs(main_db: Session, log_db: Session, campaign_id: str):
#     from app.models.log import EmailLog
#     from app.models.message_log import MessageLog

#     campaign = main_db.query(Campaign).filter(Campaign.id == campaign_id).first()
#     if not campaign:
#         raise HTTPException(status_code=404, detail="Campaign not found")

#     # WhatsApp campaign
#     if campaign.channel == "whatsapp":
#         logs = (
#             main_db.query(MessageLog)
#             .filter(MessageLog.campaign_id == str(campaign_id))
#             .order_by(MessageLog.sent_at.desc())
#             .all()
#         )

#         summary_rows = (
#             main_db.query(MessageLog.status, func.count(MessageLog.id))
#             .filter(MessageLog.campaign_id == str(campaign_id))
#             .group_by(MessageLog.status)
#             .all()
#         )
#         counts = {status: count for status, count in summary_rows}

#         return {
#             "campaign": campaign,
#             "logs": [
#                 {
#                     "id": log.id,
#                     "contactName": log.recipient_name,
#                     "email": None,
#                     "phone": log.recipient_phone,
#                     "status": log.status,
#                     "failureReason": log.error_reason,
#                     "sentAt": log.sent_at,
#                     "deliveredAt": log.delivered_at,
#                     "openedAt": None,
#                     "clickedAt": None,
#                     "openCount": 0,
#                     "device": None,
#                     "browser": None,
#                     "country": None,
#                 }
#                 for log in logs
#             ],
#             "summary": {
#                 "total": len(logs),
#                 "sent": counts.get("sent", 0),
#                 "delivered": counts.get("delivered", 0),
#                 "opened": counts.get("read", 0),
#                 "clicked": counts.get("clicked", 0),
#                 "failed": counts.get("failed", 0),
#                 "bounced": 0,
#                 "unsubscribed": counts.get("unsubscribed", 0),
#             },
#         }

#     logs = (
#         log_db.query(EmailLog)
#         .filter(EmailLog.campaign_id == campaign_id)
#         .order_by(EmailLog.created_at.desc())
#         .all()
#     )

#     summary_rows = (
#         log_db.query(EmailLog.status, func.count(EmailLog.id))
#         .filter(EmailLog.campaign_id == campaign_id)
#         .group_by(EmailLog.status)
#         .all()
#     )
#     counts = {status: count for status, count in summary_rows}

#     return {
#         "campaign": campaign,
#         "logs": [
#             {
#                 "id": log.id,
#                 "contactName": log.recipient_name,
#                 "email": log.recipient_email,
#                 "phone": log.recipient_phone,
#                 "status": log.status,
#                 "failureReason": log.bounce_reason or log.error_message,
#                 "sentAt": log.sent_at,
#                 "deliveredAt": log.delivered_at,
#                 "openedAt": log.opened_at,
#                 "clickedAt": log.clicked_at,
#                 "openCount": log.opens,
#                 "device": None,
#                 "browser": None,
#                 "country": None,
#                 "recipient_name": log.recipient_name,
#                 "recipient_email": log.recipient_email,
#                 "recipient_phone": log.recipient_phone,
#                 "subject": log.subject,
#                 "template_name": log.template_name,
#                 "campaign_name": log.campaign_name,
#                 "opens": log.opens,
#                 "clicks": log.clicks,
#                 "sent_at": log.sent_at,
#                 "bounce_reason": log.bounce_reason or log.error_message,
#             }
#             for log in logs
#         ],
#         "summary": {
#             "total": len(logs),
#             "sent": counts.get("sent", 0),
#             "delivered": counts.get("delivered", 0),
#             "opened": counts.get("opened", 0),
#             "clicked": counts.get("clicked", 0),
#             "failed": counts.get("failed", 0),
#             "bounced": counts.get("bounced", 0),
#             "unsubscribed": counts.get("unsubscribed", 0),
#         },
#     }

from sqlalchemy import text, func
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.campaign import Campaign
from app.schemas.campaign import CampaignCreate

from app.utils.notification_service import create_notification
from app.utils.render_email_template import render_blocks_to_html

from fastapi import HTTPException
from app.services.whatsapp_service import send_bulk_whatsapp
from copy import deepcopy
from app.services.email_service import send_campaign_emails, send_email
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import os
import json as _json


FALLBACK_EMAIL = os.getenv("CAMPAIGN_FALLBACK_EMAIL", "sathish.wynsync@gmail.com")


def fallback_contact():
    return SimpleNamespace(
        id=None,
        full_name="Fallback Recipient",
        email=FALLBACK_EMAIL,
        phone=None,
    )


def create_campaign(db, campaign: CampaignCreate):
    try:
        print("🔥 CREATE CAMPAIGN STARTED")
        print(campaign.model_dump())
        from app.models.campaign import Campaign

        new_campaign = Campaign(
            campaign_name=campaign.campaign_name,
            channel=campaign.channel,
            goal_label=campaign.goal_label,
            status="draft",
            current_step=1,
        )
        db.add(new_campaign)
        db.commit()
        db.refresh(new_campaign)
        print("✅ CAMPAIGN CREATED")
        return new_campaign
    except Exception as e:
        print("❌ CREATE CAMPAIGN ERROR")
        print(str(e))
        db.rollback()
        raise e


def update_campaign_content(db, campaign_id, content_data):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.subject_line = content_data.subject_line
    campaign.preview_text = content_data.preview_text
    campaign.template_id = content_data.template_id
    campaign.sender_identity_id = content_data.sender_identity_id
    campaign.current_step = 3
    db.commit()
    db.refresh(campaign)
    return campaign


def update_campaign_schedule(db, campaign_id, schedule_data):

    print("\n========== SCHEDULE UPDATE ==========")
    print("send_mode =", schedule_data.send_mode)
    print("scheduled_at =", schedule_data.scheduled_at)
    print("timezone =", schedule_data.timezone)
    print("=====================================\n")

    campaign = db.query(Campaign).filter(
        Campaign.id == campaign_id
    ).first()

    if not campaign:
        return None

    campaign.send_mode = schedule_data.send_mode

    if (
        schedule_data.send_mode == "scheduled"
        and schedule_data.scheduled_at
        and schedule_data.timezone
    ):
        local_dt = schedule_data.scheduled_at.replace(
            tzinfo=ZoneInfo(schedule_data.timezone)
        )
        utc_dt = local_dt.astimezone(timezone.utc)
        print("LOCAL TIME =", local_dt)
        print("UTC TIME   =", utc_dt)
        campaign.scheduled_at = utc_dt

    elif schedule_data.send_mode == "immediate":
        campaign.scheduled_at = None
    else:
        campaign.scheduled_at = None

    campaign.timezone = schedule_data.timezone
    campaign.current_step = 4

    db.commit()
    db.refresh(campaign)

    return campaign


import asyncio


async def finalize_campaign(db, log_db, campaign_id, finalize_data):
    print("🔥 FINALIZE CAMPAIGN CALLED 🔥")
    from app.models.template import Template
    from app.models.lists import ListContact
    from app.models.contact import Contact

    print(f"\n{'='*60}")
    print(f"🚀 FINALIZING CAMPAIGN {campaign_id}")
    print(f"{'='*60}\n")

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise Exception("Campaign not found")

    campaign.current_step = 6
    channel = campaign.channel
    print(f"   📡 Channel: {channel}")

    if campaign.send_mode == "immediate":

        print("📍 STEP 1: Fetching audience contacts...")
        audience_list_ids = campaign.audience_list_ids or []
        exclude_list_ids = campaign.exclude_list_ids or []
        print(f"   Audience lists: {audience_list_ids}")
        print(f"   Exclude lists: {exclude_list_ids}")

        if not audience_list_ids:
            raise HTTPException(status_code=400, detail="No audience lists selected")

        audience_list_ids = [int(x) for x in audience_list_ids]
        exclude_list_ids = (
            [int(x) for x in exclude_list_ids] if exclude_list_ids else []
        )

        contact_ids_query = db.query(ListContact.contact_id).filter(
            ListContact.list_id.in_(audience_list_ids)
        )
        if exclude_list_ids:
            excluded_ids = (
                db.query(ListContact.contact_id)
                .filter(ListContact.list_id.in_(exclude_list_ids))
                .subquery()
            )
            contact_ids_query = contact_ids_query.filter(
                ListContact.contact_id.notin_(excluded_ids)
            )

        contact_ids = [row.contact_id for row in contact_ids_query.all()]
        print(f"   ✅ Found {len(contact_ids)} contacts")

        print(
            f"\n📍 STEP 2: Fetching {'phone numbers' if channel == 'whatsapp' else 'email addresses'}..."
        )

        contacts = []
        if contact_ids:
            contacts = (
                db.query(Contact)
                .filter(
                    Contact.id.in_(contact_ids),
                    Contact.is_suppressed == False,
                    Contact.status != "suppressed",
                )
                .all()
            )

        print("\n📍 STEP 3: Fetching template...")
        if not campaign.template_id:
            raise HTTPException(status_code=400, detail="No template selected")

        template = (
            log_db.query(Template)
            .filter(Template.id == int(campaign.template_id))
            .first()
        )
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        print(f"   ✅ Using template: {template.name}")

        if channel == "whatsapp":
            print(f"\n📍 STEP 4: Sending WhatsApp messages...")
            recipients = [
                {"phone": c.phone, "name": c.full_name or c.phone}
                for c in contacts
                if c.phone
            ]
            print(f"   ✅ Found {len(recipients)} recipients with valid phone numbers")
            if not recipients:
                raise HTTPException(
                    status_code=400, detail="No contacts with phone numbers found"
                )
            send_result = await send_bulk_whatsapp(
                recipients=recipients,
                template_name=template.name,
                language_code="en",
            )
            print(f"   ✅ WhatsApp messages sent!")

            success_count = len(send_result.get("success", []))

            campaign.total_sent = success_count
            campaign.total_delivered = success_count
            campaign.total_opened = 0
            campaign.total_clicked = 0
            campaign.total_bounced = 0
            campaign.total_unsubscribed = 0
            campaign.delivery_rate = 100 if success_count > 0 else 0
            campaign.open_rate = 0
            campaign.click_rate = 0
            campaign.bounce_rate = 0

            print("ANALYTICS UPDATED (WhatsApp)")
            print("Campaign:", campaign.campaign_name)
            print("Success Count:", success_count)

            from app.models.message_log import MessageLog

            for item in send_result.get("success", []):
                log = MessageLog(
                    recipient_phone=item["phone"],
                    recipient_name=item.get("name", item["phone"]),
                    message=f"Template: {template.name}",
                    template_name=template.name,
                    campaign_id=str(campaign_id),
                    campaign_name=campaign.campaign_name,
                    status="sent",
                    wamid=item.get("message_id"),
                    sent_at=datetime.now(timezone.utc),
                    direction="outgoing",
                    source="campaign",
                )
                db.add(log)

            for item in send_result.get("failed", []):
                log = MessageLog(
                    recipient_phone=item["phone"],
                    recipient_name=item.get("name", item["phone"]),
                    message=f"Template: {template.name}",
                    template_name=template.name,
                    campaign_id=str(campaign_id),
                    campaign_name=campaign.campaign_name,
                    status="failed",
                    error_reason=item.get("error"),
                    sent_at=datetime.now(timezone.utc),
                    direction="outgoing",
                    source="campaign",
                )
                db.add(log)

            db.commit()
            db.refresh(campaign)

        else:  # Email channel
            print(f"\n📍 STEP 4: Sending emails...")
            recipients_email = [c.email for c in contacts if c.email]
            print(f"   ✅ Found {len(recipients_email)} recipients with valid emails")

            if not recipients_email:
                contacts = [fallback_contact()]
                recipients_email = [FALLBACK_EMAIL]
                print(f"   No valid contact emails. Using fallback: {FALLBACK_EMAIL}")

            send_result = await send_campaign_emails(
                log_db=log_db,
                main_db=db,
                campaign=campaign,
                contacts=contacts,
                subject=campaign.subject_line or "Campaign Email",
                template_content=template.content,
                template_name=template.name,
            )
            print(f"   ✅ Emails sent!")

            total_sent = send_result.get("sent", 0)
            total_failed = send_result.get("failed", 0)

            campaign.total_sent = total_sent
            campaign.total_delivered = 0
            campaign.total_opened = 0
            campaign.total_clicked = 0
            campaign.total_bounced = 0
            campaign.total_failed = total_failed
            campaign.total_complained = 0
            campaign.total_unsubscribed = 0
            campaign.delivery_rate = 0
            campaign.open_rate = 0
            campaign.click_rate = 0
            campaign.bounce_rate = 0
            campaign.complaint_rate = 0

            print("EMAIL ANALYTICS UPDATED")
            print("Campaign:", campaign.campaign_name)
            print("Total Sent:", total_sent)

            db.commit()
            db.refresh(campaign)

        # STEP 5: Update campaign status and last campaign for contacts
        print("\n📍 STEP 5: Updating campaign status...")

        # Update each contact's last campaign
        for contact in contacts:
            contact.campaign = campaign.campaign_name
        print(f"Updated last campaign for {len(contacts)} contacts")

        campaign.status = "sent"
        campaign.email_sent_at = datetime.now(timezone.utc)
        campaign.sent_at = datetime.now(timezone.utc)
        create_notification(
            db=db,
            notification_type="campaignSent",
            title="Campaign Sent",
            message=f'Campaign "{campaign.campaign_name}" sent successfully',
        )
        db.commit()
        db.refresh(campaign)

        print("FINAL VALUES")
        print("total_sent =", campaign.total_sent)
        print("total_delivered =", campaign.total_delivered)
        print(f"   ✅ Campaign marked as sent")

    else:  # Scheduled mode
        print(f"\n📅 Scheduling campaign for {campaign.scheduled_at}")
        campaign.status = "scheduled"
        create_notification(
            db=db,
            notification_type="campaignScheduled",
            title="Campaign Scheduled",
            message=f'Campaign "{campaign.campaign_name}" scheduled successfully',
        )
        db.commit()
        db.refresh(campaign)

    print(f"\n{'='*60}")
    print(f"✅ CAMPAIGN FINALIZED SUCCESSFULLY")
    print(f"{'='*60}\n")

    return {
        "message": "Campaign finalized",
        "campaign": campaign,
        "channel": channel,
        "status": campaign.status,
    }


async def send_test_email(db, log_db, campaign_id, email_data):
    from app.models.template import Template

    print(f"\n{'='*60}")
    print(f"📧 SENDING TEST EMAIL")
    print(f"{'='*60}\n")

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    email = email_data.email or FALLBACK_EMAIL
    print(f"   To: {email}")

    html_body = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: #f5f5f5; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
            <strong>📊 TEST EMAIL PREVIEW</strong>
            <p style="color: #666; font-size: 12px; margin: 10px 0 0 0;">
                This is a test email for: <strong>{campaign.campaign_name}</strong>
            </p>
        </div>
        <h2 style="margin-top: 0;">{campaign.campaign_name}</h2>
    """

    if campaign.template_id:
        template = (
            log_db.query(Template)
            .filter(Template.id == int(campaign.template_id))
            .first()
        )
        if template and template.content:
            html_body += render_blocks_to_html(
              template.content,
              campaign.campaign_name
           )
            print(f"   Template: {template.name}")
        else:
            html_body += f"<p>This email will use the selected template.</p>"
    else:
        html_body += f"<p>⚠️ No template selected for campaign</p>"

    html_body += f"""
        <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
        <p style="color: #999; font-size: 12px;">
            This is a test email. When sent, this campaign will reach
            {len([x for x in (campaign.audience_list_ids or [])]) or 0} audience lists.
        </p>
    </div>
    """

    try:
        await send_email(
            tenant_id=str(campaign.id),
            recipients=[email],
            subject=campaign.subject_line or "Test Campaign Email",
            html_body=html_body,
        )
        print(f"   ✅ Test email sent successfully!\n")
        return {
            "message": "Test email sent successfully",
            "sent_to": email,
            "delivery_status": "sent",
        }
    except Exception as e:
        create_notification(
            db=db,
            notification_type="campaignFailed",
            title="Campaign Failed",
            message=f'Campaign "{campaign.campaign_name}" failed to send',
        )
        print(f"   ❌ Failed: {str(e)}\n")
        return {
            "message": "Test email attempted, but AWS SES rejected it",
            "sent_to": email,
            "delivery_status": "failed",
            "error": str(e),
        }


def get_all_campaigns(db: Session):
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    return campaigns


def get_campaign_by_id(db, campaign_id: str):
    from app.models.message_log import MessageLog
    from app.models.log import EmailLog

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    if campaign.channel == "email":
        logs = db.query(EmailLog).filter(EmailLog.campaign_id == str(campaign_id)).all()
        total_sent = len(logs)
        total_delivered = len(
            [l for l in logs if l.status in ("delivered", "opened", "clicked")]
        )
        total_failed = len([l for l in logs if l.status in ("failed", "bounced")])
        total_opened = len([l for l in logs if l.status in ("opened", "clicked")])
        total_clicked = len([l for l in logs if l.status == "clicked"])
        recipients_data = [
            {
                "recipientId": str(l.id),
                "contactName": l.recipient_name or l.recipient_email,
                "lastEvent": l.status,
            }
            for l in logs[:10]
        ]
    else:
        logs = (
            db.query(MessageLog)
            .filter(MessageLog.campaign_id == str(campaign_id))
            .all()
        )
        total_sent = len(logs)
        total_delivered = len([l for l in logs if l.status in ("sent", "delivered")])
        total_failed = len([l for l in logs if l.status == "failed"])
        total_opened = len([l for l in logs if l.status == "read"])
        total_clicked = 0
        recipients_data = [
            {
                "recipientId": str(l.id),
                "contactName": l.recipient_name or l.recipient_phone,
                "lastEvent": l.status,
            }
            for l in logs[:10]
        ]

    return {
        "id": str(campaign.id),
        "campaign_name": campaign.campaign_name,
        "channel": campaign.channel,
        "status": campaign.status,
        "goal_label": campaign.goal_label,
        "audience_list_ids": campaign.audience_list_ids,
        "exclude_list_ids": campaign.exclude_list_ids,
        "subject_line": campaign.subject_line,
        "preview_text": campaign.preview_text,
        "template_id": campaign.template_id,
        "sender_identity_id": campaign.sender_identity_id,
        "send_mode": campaign.send_mode,
        "scheduled_at": campaign.scheduled_at,
        "timezone": campaign.timezone,
        "current_step": campaign.current_step,
        "sender_identity": campaign.sender_identity_id,
        "created_at": str(campaign.created_at),
        "estimated_recipients": campaign.estimated_recipients,
        "total_sent": total_sent,
        "total_delivered": total_delivered,
        "total_opened": total_opened,
        "total_clicked": total_clicked,
        "total_bounced": total_failed,
        "total_unsubscribed": campaign.total_unsubscribed or 0,
        "open_rate": round(total_opened / total_sent, 4) if total_sent > 0 else 0,
        "click_rate": round(total_clicked / total_sent, 4) if total_sent > 0 else 0,
        "delivery_rate": round(total_delivered / total_sent, 4) if total_sent > 0 else 0,
        "bounce_rate": round(total_failed / total_sent, 4) if total_sent > 0 else 0,
        "links": [],
        "recipients": recipients_data,
    }


def duplicate_campaign(db: Session, campaign_id: str):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        return {"error": "Campaign not found"}
    duplicated = Campaign(
        campaign_name=f"Copy of {campaign.campaign_name}",
        channel=campaign.channel,
        goal_label=campaign.goal_label,
        status="draft",
    )
    db.add(duplicated)
    db.commit()
    db.refresh(duplicated)
    return duplicated


def update_campaign_audience(db, campaign_id, audience):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise Exception("Campaign not found")
    campaign.audience_list_ids = audience.audience_list_ids
    campaign.exclude_list_ids = audience.exclude_list_ids
    campaign.estimated_recipients = audience.estimated_recipients
    campaign.suppressed_count = audience.suppressed_count
    campaign.current_step = max(campaign.current_step, 2)
    db.commit()
    db.refresh(campaign)
    return {"success": True}


def update_campaign(db: Session, campaign_id: int, payload):
    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    campaign.campaign_name = payload.campaign_name
    campaign.channel = payload.channel
    campaign.goal_label = payload.goal_label
    db.commit()
    db.refresh(campaign)
    return campaign


def get_campaign_logs(main_db: Session, log_db: Session, campaign_id: str, page: int = 1, per_page: int = 50, since_id: int = None):
    """
    Fetch campaign logs with pagination and lightweight timing.
    """
    import time
    import logging
    from app.models.log import EmailLog
    from app.models.message_log import MessageLog

    logger = logging.getLogger(__name__)

    campaign = main_db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # WhatsApp logs live on main DB (MessageLog)
    if campaign.channel == "whatsapp":
        q = main_db.query(MessageLog).filter(MessageLog.campaign_id == str(campaign_id))
        if since_id:
            q = q.filter(MessageLog.id > since_id)

        # Avoid running an expensive COUNT(*) on every page request. Only compute total on the first page.
        total = q.count() if page == 1 else None

        start = time.perf_counter()
        logs = (
            q.order_by(MessageLog.sent_at.desc())
            .limit(per_page)
            .offset((page - 1) * per_page)
            .all()
        )
        duration = time.perf_counter() - start
        logger.debug("Fetched %d whatsapp logs for campaign %s page=%s per_page=%s in %0.3fs", len(logs), campaign_id, page, per_page, duration)

        # Only compute summary counts on the first page (less frequent, expensive on large tables)
        if page == 1:
            summary_rows = (
                main_db.query(MessageLog.status, func.count(MessageLog.id))
                .filter(MessageLog.campaign_id == str(campaign_id))
                .group_by(MessageLog.status)
                .all()
            )
            counts = {status: count for status, count in summary_rows}
        else:
            counts = {}
        return {
            "campaign": campaign,
            "logs": [
                {
                    "id": log.id,
                    "contactName": log.recipient_name,
                    "email": None,
                    "phone": log.recipient_phone,
                    "status": log.status,
                    "failureReason": log.error_reason,
                    "sentAt": log.sent_at,
                    "deliveredAt": log.delivered_at,
                    "openedAt": None,
                    "clickedAt": None,
                    "openCount": 0,
                    "device": None,
                    "browser": None,
                    "country": None,
                }
                for log in logs
            ],
            "summary": {
                "total": total,
                "sent": counts.get("sent", 0),
                "delivered": counts.get("delivered", 0),
                "opened": counts.get("read", 0),
                "clicked": counts.get("clicked", 0),
                "failed": counts.get("failed", 0),
                "bounced": 0,
                "unsubscribed": counts.get("unsubscribed", 0),
            },
        }

    # Email logs live on log_db
    q = log_db.query(EmailLog).filter(EmailLog.campaign_id == campaign_id)
    if since_id:
        q = q.filter(EmailLog.id > since_id)

    # Only compute total on the first page to avoid expensive COUNT() on every page request
    total = q.count() if page == 1 else None

    start = time.perf_counter()
    logs = (
        q.order_by(EmailLog.created_at.desc())
        .limit(per_page)
        .offset((page - 1) * per_page)
        .all()
    )
    duration = time.perf_counter() - start
    logger.debug("Fetched %d email logs for campaign %s page=%s per_page=%s in %0.3fs", len(logs), campaign_id, page, per_page, duration)

    if page == 1:
        summary_rows = (
            log_db.query(EmailLog.status, func.count(EmailLog.id))
            .filter(EmailLog.campaign_id == campaign_id)
            .group_by(EmailLog.status)
            .all()
        )
        counts = {status: count for status, count in summary_rows}
    else:
        counts = {}

    return {
        "campaign": campaign,
        "logs": [
            {
                "id": log.id,
                "contactName": log.recipient_name,
                "email": log.recipient_email,
                "phone": log.recipient_phone,
                "status": log.status,
                "failureReason": log.bounce_reason or log.error_message,
                "sentAt": log.sent_at,
                "deliveredAt": log.delivered_at,
                "openedAt": log.opened_at,
                "clickedAt": log.clicked_at,
                "openCount": log.opens,
                "device": None,
                "browser": None,
                "country": None,
                "recipient_name": log.recipient_name,
                "recipient_email": log.recipient_email,
                "recipient_phone": log.recipient_phone,
                "subject": log.subject,
                "template_name": log.template_name,
                "campaign_name": log.campaign_name,
                "opens": log.opens,
                "clicks": log.clicks,
                "sent_at": log.sent_at,
                "bounce_reason": log.bounce_reason or log.error_message,
            }
            for log in logs
        ],
        "summary": {
            "total": total,
            "sent": counts.get("sent", 0),
            "delivered": counts.get("delivered", 0),
            "opened": counts.get("opened", 0),
            "clicked": counts.get("clicked", 0),
            "failed": counts.get("failed", 0),
            "bounced": counts.get("bounced", 0),
            "unsubscribed": counts.get("unsubscribed", 0),
        },
    }

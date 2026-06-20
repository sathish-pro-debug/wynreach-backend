from apscheduler.schedulers.asyncio import AsyncIOScheduler

from datetime import datetime, timezone

from app.database import MainSessionLocal

from app.models.campaign import Campaign

from app.services.email_service import send_email
from app.services.whatsapp_service import send_bulk_whatsapp
from app.services.email_service import (
    send_campaign_emails
)
from app.utils.render_email_template import render_blocks_to_html
import json as _json
from app.models.notification import Notification
scheduler = AsyncIOScheduler()


async def process_scheduled_campaigns():
    """
    Scheduled job that runs every 1 minute.
    Checks for campaigns scheduled to send NOW.
    """
    from app.models.lists import ListContact
    from app.models.contact import Contact
    from app.models.template import Template

    db = MainSessionLocal()

    try:

        now = datetime.now(timezone.utc)
        print("NOW UTC =", now)
        campaigns = db.query(Campaign).filter(
            Campaign.status == "scheduled",
            Campaign.scheduled_at <= now
        ).all()

        if campaigns:
            print(f"\n📅 Processing {len(campaigns)} scheduled campaigns at {now}")

        # DEBUG
        all_scheduled = db.query(Campaign).filter(
            Campaign.status == "scheduled"
        ).all()

        print("\n===== SCHEDULED CAMPAIGNS =====")

        for c in all_scheduled:
            print(
                c.id,
                c.campaign_name,
                c.status,
                c.scheduled_at,
                c.timezone
            )

        print("===============================\n")

        for campaign in campaigns:
            print("CHANNEL =", campaign.channel)
            # print(f"\n⏰ Sending scheduled campaign: {campaign.campaign_name}")

            try:
                # STEP 1: Fetch audience contacts
                audience_list_ids = campaign.audience_list_ids or []
                exclude_list_ids = campaign.exclude_list_ids or []

                if not audience_list_ids:
                    # print(
                    #     f"   ⚠️ Campaign {campaign.id}: No audience lists selected, skipping"
                    # )
                    continue

                audience_list_ids = [int(x) for x in audience_list_ids]
                exclude_list_ids = (
                    [int(x) for x in exclude_list_ids]
                    if exclude_list_ids else []
                )

                

                # Query contacts
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

                if not contact_ids:
                    # print(f"   ⚠️ Campaign {campaign.id}: No contacts found, skipping")
                    continue

                # STEP 2: Fetch emails
                contacts = db.query(Contact).filter(
                    Contact.id.in_(contact_ids),
                    Contact.email != None,
                    Contact.is_suppressed == False,
                    Contact.status != "suppressed"
                ).all()

                recipients = [c.email for c in contacts if c.email]

                if not recipients:
                    # print(f"   ⚠️ Campaign {campaign.id}: No valid email addresses, skipping")
                    continue

                # STEP 3: Fetch template
                html_body = f"<h2>{campaign.campaign_name}</h2>"
                if campaign.template_id:
                    template = db.query(Template).filter(
                        Template.id == int(campaign.template_id)
                    ).first()
                    if template:
                        try:
                            blocks = _json.loads(template.content)
                            html_body = render_blocks_to_html(blocks)
                        except:
                            html_body = f"<h2>{campaign.campaign_name}</h2>"

                
                # STEP 4: Send based on channel

                if campaign.channel == "email":

                #     await send_email(
                #     tenant_id=str(campaign.id),
                #     recipients=recipients,
                #     subject=campaign.subject_line or "Campaign Email",
                #     html_body=html_body
                # )
                     result = await send_campaign_emails(
                       log_db=db,
                       main_db=db,
                       campaign=campaign,
                       contacts=contacts,
                       subject=campaign.subject_line or "Campaign Email",
                       template_content=template.content if template else html_body,
                       template_name=template.name if template else None,
                       
    )

                    #  print("EMAIL RESULT =",result)

                elif campaign.channel == "whatsapp":
                    print("📱 WHATSAPP CAMPAIGN DETECTED")
                    print("CAMPAIGN ID =", campaign.id)
                    print("TEMPLATE ID =", campaign.template_id)
                    print("CONTACT IDS =", contact_ids) 

                    contacts = db.query(Contact).filter(
                          Contact.id.in_(contact_ids),
                          Contact.phone != None,
                          Contact.is_suppressed == False,
                          Contact.status != "suppressed"
                    ).all()
                    print("WHATSAPP CONTACTS FOUND =", len(contacts))
                    recipients = [
                      {
                        "phone": c.phone,
                        "name": c.full_name
                      }
                      for c in contacts
                      if c.phone
                     ]
                    print("WHATSAPP RECIPIENTS =", recipients)

                    if not recipients:
                       print(
                           f"   ⚠️ Campaign {campaign.id}: No WhatsApp recipients found"
                       )
                       continue

                    template = db.query(Template).filter(
                        Template.id == int(campaign.template_id)
                    ).first() 
                    print("TEMPLATE FOUND =", template)
                    if template:
                     print("TEMPLATE NAME =", template.name)

                    if not template:
                        print(
                             f"   ❌ Campaign {campaign.id}: Template not found"
                        )
                        continue
                    print("🚀 SENDING WHATSAPP...")
                    result = await send_bulk_whatsapp(
                        recipients=recipients,
                        template_name=template.name
                         )

                    print("📱 WhatsApp Result =", result)

                    

                # STEP 5: Update status
                campaign.status = "sent"
                campaign.email_sent_at = now
                notification = Notification(
                    notification_type="campaign",
                    title="Campaign Sent",
                    message=f"{campaign.campaign_name} sent successfully via {campaign.channel}"
)

                db.add(notification)
                print(f"   ✅ Campaign {campaign.id} sent to {len(recipients)} recipients")

            except Exception as e:
                print(f"   ❌ Error processing campaign {campaign.id}: {e}")
                continue

        db.commit()
    except Exception as e:
        print(f"❌ Error in scheduler: {e}")
    finally:
        db.close()


def start_scheduler():

    scheduler.add_job(
        process_scheduled_campaigns,
        "interval",
        minutes=1
    )

    scheduler.start()

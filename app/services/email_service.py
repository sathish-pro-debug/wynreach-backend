import boto3
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from botocore.exceptions import BotoCoreError, ClientError
from app.models.log import EmailLog
from app.services.email_tracking_service import (
    EVENT_FAILED,
    EVENT_SENT,
    create_email_event,
    recalculate_campaign_metrics,
)
from app.services.suppression_service import is_suppressed
from app.utils.render_email_template import (
    normalize_template_blocks,
    render_blocks_to_html,
    validate_template_images_for_send,
)

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent.parent / ".env")


def _get_ses_client():
    return boto3.client(
        "ses",
        region_name=os.getenv("AWS_REGION"),
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    )


async def send_email(
    tenant_id,
    recipients,
    subject,
    html_body,
    from_email=None,
    campaign_id=None,
    contact_id=None,
    message_id=None,
):

    print("FINAL EMAIL HTML")
    print(html_body)
    client = _get_ses_client()
    sender = from_email or os.getenv("SES_FROM_EMAIL")

    try:
        print("\n================================================")
        print("📧 AWS SES SEND EMAIL")
        print("================================================")
        print("FROM:", sender)
        print("TO:", recipients)
        print("SUBJECT:", subject)

        tags = [{"Name": "tenant_id", "Value": str(tenant_id)}]
        if campaign_id is not None:
            tags.append({"Name": "campaign_id", "Value": str(campaign_id)})
        if contact_id is not None:
            tags.append({"Name": "contact_id", "Value": str(contact_id)})
        if message_id is not None:
            tags.append({"Name": "message_id", "Value": str(message_id)})

        response = client.send_email(
            Source=sender,
            Destination={"ToAddresses": recipients},
            Message={
                "Subject": {"Data": subject},
                "Body": {"Html": {"Data": html_body}},
            },
            Tags=tags,
        )

        print("✅ EMAIL SENT SUCCESS")
        print("Message ID:", response.get("MessageId"))

        return {"success": True, "message_id": response.get("MessageId")}

    except ClientError as e:
        print("❌ AWS SES CLIENT ERROR")
        print(str(e))
        return {"success": False, "error": str(e)}

    except Exception as e:
        print("❌ UNKNOWN EMAIL ERROR")
        print(str(e))
        return {"success": False, "error": str(e)}


async def send_campaign_emails(
    log_db,
    main_db,
    campaign,
    contacts,
    subject,
    template_content,
    template_name=None,
):
    sent = 0
    failed = 0
    tenant_id = str(campaign.workspace_id or campaign.id)

    # Sender email lookup from email_addresses table using main_db
    from_email = os.getenv("SES_FROM_EMAIL")
    if campaign.sender_identity_id:
        try:
            from sqlalchemy import text

            result_row = main_db.execute(
                text("SELECT email FROM email_addresses WHERE id = :id"),
                {"id": str(campaign.sender_identity_id)},
            ).fetchone()
            if result_row:
                from_email = result_row[0]
                print(f"✅ Sender found in DB: {from_email}")
            else:
                print(
                    f"⚠️ Sender not found for id: {campaign.sender_identity_id}, using default: {from_email}"
                )
        except Exception as e:
            print(f"⚠️ Sender lookup failed: {e}, using default: {from_email}")

    print(f"📧 SENDING FROM: {from_email}")

    blocks = normalize_template_blocks(template_content)
    validate_template_images_for_send(blocks)
    print("\n========== TEMPLATE BLOCKS ==========")
    print(f"TOTAL BLOCKS: {len(blocks)}")

    for contact in contacts:
        email = (contact.email or "").strip()
        if not email:
            continue

        if is_suppressed(log_db, email):
            continue

        message_id = str(uuid.uuid4())

        log = EmailLog(
            tenant_id=tenant_id,
            campaign_id=str(campaign.id),
            contact_id=contact.id,
            message_id=message_id,
            recipient_name=contact.full_name,
            recipient_email=email,
            recipient_phone=contact.phone,
            subject=subject,
            template_name=template_name,
            campaign_name=campaign.campaign_name,
            status="pending",
        )

        log_db.add(log)
        log_db.commit()

        try:
            html_body = render_blocks_to_html(blocks, log_id=log.id)
            if 'src=""' in html_body or "src=''" in html_body:
                raise ValueError("Campaign contains invalid image URLs.")
            print(f"\n✅ RENDERED HTML FOR {email} (Log ID: {log.id})")
        except Exception as e:
            print(f"❌ Error rendering template: {e}")
            log.status = "failed"
            log.delivery_status = "failed"
            log.error_message = str(e)
            log.failed_at = datetime.now(timezone.utc)
            create_email_event(
                log_db,
                tenant_id=tenant_id,
                campaign_id=str(campaign.id),
                contact_id=contact.id,
                message_id=message_id,
                recipient_email=email,
                event_type=EVENT_FAILED,
                metadata={"error": str(e)},
            )
            failed += 1
            log_db.commit()
            continue

        try:
            result = await send_email(
                tenant_id=tenant_id,
                recipients=[email],
                subject=subject,
                html_body=html_body,
                from_email=from_email,
                campaign_id=str(campaign.id),
                contact_id=contact.id,
                message_id=message_id,
            )

            if result["success"]:
                log.status = "sent"
                log.delivery_status = "sent"
                log.ses_message_id = result["message_id"]
                log.sent_at = datetime.now(timezone.utc)
                create_email_event(
                    log_db,
                    tenant_id=tenant_id,
                    campaign_id=str(campaign.id),
                    contact_id=contact.id,
                    message_id=message_id,
                    recipient_email=email,
                    event_type=EVENT_SENT,
                    metadata={"ses_message_id": result["message_id"]},
                )
                sent += 1
            else:
                log.status = "failed"
                log.delivery_status = "failed"
                log.error_message = result["error"]
                log.bounce_reason = result["error"]
                log.failed_at = datetime.now(timezone.utc)
                create_email_event(
                    log_db,
                    tenant_id=tenant_id,
                    campaign_id=str(campaign.id),
                    contact_id=contact.id,
                    message_id=message_id,
                    recipient_email=email,
                    event_type=EVENT_FAILED,
                    metadata={"error": result["error"]},
                )
                failed += 1

        except (BotoCoreError, ClientError, Exception) as exc:
            print("EMAIL ERROR")
            print(type(exc))
            print(str(exc))
            log.status = "failed"
            log.delivery_status = "failed"
            log.error_message = str(exc)
            log.bounce_reason = str(exc)
            log.failed_at = datetime.now(timezone.utc)
            create_email_event(
                log_db,
                tenant_id=tenant_id,
                campaign_id=str(campaign.id),
                contact_id=contact.id,
                message_id=message_id,
                recipient_email=email,
                event_type=EVENT_FAILED,
                metadata={"error": str(exc)},
            )
            failed += 1

        log_db.commit()

    recalculate_campaign_metrics(log_db, str(campaign.id))
    log_db.commit()

    return {
        "sent": sent,
        "failed": failed,
        "total": sent + failed,
    }

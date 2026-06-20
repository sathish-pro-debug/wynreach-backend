import json

from fastapi import APIRouter, Request

from sqlalchemy import or_
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.database import MainSessionLocal

from app.models.email_tenant import Tenant
from app.models.log import EmailLog

from app.services.email_reputation import calculate_reputation

router = APIRouter()


def _first_tag(tags, name):
    value = tags.get(name)
    if isinstance(value, list):
        return value[0] if value else None
    return value


def _as_int(value):
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _bounce_recipients(message):
    return [
        item.get("emailAddress")
        for item in message.get("bounce", {}).get("bouncedRecipients", [])
        if item.get("emailAddress")
    ]


def _complaint_recipients(message):
    return [
        item.get("emailAddress")
        for item in message.get("complaint", {}).get("complainedRecipients", [])
        if item.get("emailAddress")
    ]


@router.post("/ses")
@router.post("/ses/webhook")
async def ses_webhook(request: Request):

    db: Session = MainSessionLocal()

    try:
        from app.services.email_tracking_service import (
            EVENT_BOUNCED,
            EVENT_COMPLAINED,
            EVENT_DELIVERED,
            EVENT_FAILED,
            EVENT_SENT,
            create_email_event,
            mark_contact_suppressed,
            recalculate_campaign_metrics,
        )

        body = await request.json()
        message_type = body.get("Type")

        if message_type == "SubscriptionConfirmation":

            print("SNS Subscription Confirmed")

            return {"success": True}

        message = json.loads(body["Message"]) if "Message" in body else body

        print(json.dumps(message, indent=2))

        notification_type = message.get("notificationType")
        mail = message.get("mail", {})
        tags = mail.get("tags", {})
        tenant_id = _first_tag(tags, "tenant_id")
        campaign_id = _first_tag(tags, "campaign_id")
        contact_id = _as_int(_first_tag(tags, "contact_id"))
        message_id = _first_tag(tags, "message_id")
        ses_message_id = mail.get("messageId")
        event_message_id = message_id or ses_message_id

        print("=" * 60)
        print("SES EVENT RECEIVED")
        print("TYPE:", notification_type)
        print("SES MESSAGE ID:", ses_message_id)
        print("TRACKING MESSAGE ID:", event_message_id)
        print("=" * 60)

        log = None
        filters = []
        if event_message_id:
            filters.append(EmailLog.message_id == event_message_id)
        if ses_message_id:
            filters.append(EmailLog.ses_message_id == ses_message_id)
        if filters:
            log = db.query(EmailLog).filter(or_(*filters)).first()

        if log:
            tenant_id = tenant_id or log.tenant_id
            campaign_id = campaign_id or log.campaign_id
            contact_id = contact_id or log.contact_id
            event_message_id = event_message_id or log.message_id or log.ses_message_id

        recipients = mail.get("destination", [])
        if notification_type == "Bounce":
            recipients = _bounce_recipients(message) or recipients
            event_type = EVENT_BOUNCED
        elif notification_type == "Complaint":
            recipients = _complaint_recipients(message) or recipients
            event_type = EVENT_COMPLAINED
        elif notification_type == "Delivery":
            event_type = EVENT_DELIVERED
        elif notification_type == "Send":
            event_type = EVENT_SENT
        elif notification_type in ("Reject", "Rendering Failure"):
            event_type = EVENT_FAILED
        else:
            print(f"Unhandled SES notification type: {notification_type}")
            return {"success": True}

        if not recipients and log:
            recipients = [log.recipient_email]

        for email in recipients:
            create_email_event(
                db,
                tenant_id=tenant_id,
                campaign_id=campaign_id,
                contact_id=contact_id,
                message_id=event_message_id,
                recipient_email=email,
                event_type=event_type,
                metadata={
                    "ses_message_id": ses_message_id,
                    "notification_type": notification_type,
                    "payload": message,
                },
            )

        if log:
            log.ses_event_data = message
            if notification_type == "Bounce":
                log.status = "bounced"
                log.delivery_status = "bounced"
                log.bounce_reason = str(message)
                log.bounced_at = func.now()
            elif notification_type == "Complaint":
                log.status = "complained"
                log.delivery_status = "complained"
                log.complaint_reason = str(message)
                log.complaint_at = func.now()
            elif notification_type == "Delivery":
                log.status = "delivered"
                log.delivery_status = "delivered"
                log.delivered_at = func.now()
            elif notification_type == "Send":
                log.status = "sent"
                log.delivery_status = "sent"
            else:
                log.status = "failed"
                log.delivery_status = "failed"
                log.error_message = str(message)
                log.failed_at = func.now()

        tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first() if tenant_id else None
        if tenant:
            if notification_type == "Bounce":
                tenant.total_bounces = (tenant.total_bounces or 0) + len(recipients)
            elif notification_type == "Complaint":
                tenant.total_complaints = (tenant.total_complaints or 0) + len(recipients)
            tenant.reputation_score = calculate_reputation(tenant)

            bounce_rate = (tenant.total_bounces / max(tenant.total_sent or 0, 1)) * 100
            complaint_rate = (tenant.total_complaints / max(tenant.total_sent or 0, 1)) * 100
            if bounce_rate > 5 or complaint_rate > 0.1:
                tenant.sending_enabled = False

        if notification_type == "Bounce" and message.get("bounce", {}).get("bounceType") == "Permanent":
            for email in recipients:
                mark_contact_suppressed(
                    db,
                    contact_id=contact_id,
                    email=email,
                    reason="Permanent Bounce",
                    source="AWS SES Bounce",
                    status="BOUNCED",
                )
        elif notification_type == "Complaint":
            for email in recipients:
                mark_contact_suppressed(
                    db,
                    contact_id=contact_id,
                    email=email,
                    reason="Complaint",
                    source="AWS SES Complaint",
                    status="COMPLAINED",
                )

        recalculate_campaign_metrics(db, campaign_id)
        db.commit()

        return {"success": True}

    finally:

        db.close()


# import json
# import uuid

# from fastapi import APIRouter, Request

# from sqlalchemy.orm import Session

# from app.database import MainSessionLocal

# from app.models.email_tenant import Tenant
# from app.models.email_event import EmailEvent
# from app.models.suppression import Suppression
# from sqlalchemy.sql import func
# from app.services.email_reputation import (
#     calculate_reputation
# )
# from app.models.log import EmailLog

# router = APIRouter()

# @router.post("/ses/webhook")
# async def ses_webhook(request: Request):

#     db: Session = MainSessionLocal()

#     body = await request.json()

#     message = json.loads(body["Message"])

#     notification_type = message["notificationType"]

#     mail = message["mail"]

#     tags = mail.get("tags", {})

#     tenant_id = tags.get(
#         "tenant_id",
#         [None]
#     )[0]

#     recipients = mail["destination"]

#     tenant = db.query(Tenant).filter(
#         Tenant.id == tenant_id
#     ).first()

#     if notification_type == "Bounce":

#         tenant.total_bounces += len(recipients)

#         for email in recipients:

#             suppression = Suppression(
#                 email=email
#             )

#             db.merge(suppression)

#             event = EmailEvent(
#                 id=str(uuid.uuid4()),
#                 tenant_id=tenant_id,
#                 recipient_email=email,
#                 event_type="bounced",
#                 event_metadata=message
#             )

#             db.add(event)

#         message_id = mail.get("messageId")

#     log = db.query(EmailLog).filter(
#         EmailLog.ses_message_id == message_id
#     ).first()

#     if log:

#         log.status = "bounced"

#         log.delivery_status = "bounced"

#         log.bounce_reason = str(message)

#         log.bounced_at = func.now()

#         log.ses_event_data = message

#     elif notification_type == "Complaint":

#         tenant.total_complaints += len(recipients)

#         for email in recipients:

#             suppression = Suppression(
#                 email=email
#             )

#             db.merge(suppression)

#             event = EmailEvent(
#                 id=str(uuid.uuid4()),
#                 tenant_id=tenant_id,
#                 recipient_email=email,
#                 event_type="complaint",
#                 event_metadata=message
#             )

#             db.add(event)

#         message_id = mail.get("messageId")

#     log = db.query(EmailLog).filter(
#         EmailLog.ses_message_id == message_id
#     ).first()

#     if log:

#         log.status = "complaint"

#         log.delivery_status = "complaint"

#         log.complaint_reason = str(message)

#         log.complaint_at = func.now()

#         log.ses_event_data = message

#     tenant.reputation_score = (
#         calculate_reputation(tenant)
#     )

#     bounce_rate = (
#         tenant.total_bounces / tenant.total_sent
#     ) * 100

#     complaint_rate = (
#         tenant.total_complaints / tenant.total_sent
#     ) * 100

#     if bounce_rate > 5:
#         tenant.sending_enabled = False

#     if complaint_rate > 0.1:
#         tenant.sending_enabled = False

#     db.commit()

#     return {
#         "success": True
#     }

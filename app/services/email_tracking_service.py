import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.contact import Contact
from app.models.email_event import EmailEvent
from app.models.suppression import Suppression

EVENT_SENT = "SENT"
EVENT_DELIVERED = "DELIVERED"
EVENT_OPENED = "OPENED"
EVENT_CLICKED = "CLICKED"
EVENT_BOUNCED = "BOUNCED"
EVENT_FAILED = "FAILED"
EVENT_COMPLAINED = "COMPLAINED"

LIFECYCLE_EVENTS = {
    EVENT_SENT,
    EVENT_DELIVERED,
    EVENT_OPENED,
    EVENT_CLICKED,
    EVENT_BOUNCED,
    EVENT_FAILED,
    EVENT_COMPLAINED,
}


def _clean_event_type(event_type: str) -> str:
    return (event_type or "").strip().upper()


def create_email_event(
    db: Session,
    *,
    tenant_id: Optional[str],
    campaign_id: Optional[str],
    contact_id: Optional[int],
    message_id: Optional[str],
    recipient_email: Optional[str],
    event_type: str,
    metadata: Optional[dict] = None,
    dedupe: bool = True,
) -> Optional[EmailEvent]:
    normalized_event = _clean_event_type(event_type)
    if normalized_event not in LIFECYCLE_EVENTS:
        return None

    query = db.query(EmailEvent).filter(
        func.upper(EmailEvent.event_type) == normalized_event
    )

    if dedupe:
        if message_id:
            query = query.filter(EmailEvent.message_id == str(message_id))
        elif campaign_id and contact_id:
            query = query.filter(
                EmailEvent.campaign_id == str(campaign_id),
                EmailEvent.contact_id == contact_id,
            )
        elif campaign_id and recipient_email:
            query = query.filter(
                EmailEvent.campaign_id == str(campaign_id),
                EmailEvent.recipient_email == recipient_email,
            )
        else:
            query = None

        if query is not None and query.first():
            return None

    event = EmailEvent(
        id=str(uuid.uuid4()),
        tenant_id=str(tenant_id) if tenant_id is not None else None,
        campaign_id=str(campaign_id) if campaign_id is not None else None,
        contact_id=contact_id,
        message_id=str(message_id) if message_id is not None else None,
        recipient_email=recipient_email or "",
        event_type=normalized_event,
        event_metadata=metadata or {},
    )
    db.add(event)
    return event


def recalculate_campaign_metrics(db: Session, campaign_id: Optional[str]) -> None:
    if not campaign_id:
        return

    campaign = db.query(Campaign).filter(Campaign.id == str(campaign_id)).first()
    if not campaign:
        return

    rows = (
        db.query(func.upper(EmailEvent.event_type), func.count(EmailEvent.id))
        .filter(EmailEvent.campaign_id == str(campaign_id))
        .group_by(func.upper(EmailEvent.event_type))
        .all()
    )
    counts = {event_type: count for event_type, count in rows}

    sent = counts.get(EVENT_SENT, 0)
    delivered = counts.get(EVENT_DELIVERED, 0)
    opened = counts.get(EVENT_OPENED, 0)
    clicked = counts.get(EVENT_CLICKED, 0)
    bounced = counts.get(EVENT_BOUNCED, 0)
    failed = counts.get(EVENT_FAILED, 0)
    complained = counts.get(EVENT_COMPLAINED, 0)

    campaign.total_sent = sent
    campaign.total_delivered = delivered
    campaign.total_opened = opened
    campaign.total_clicked = clicked
    campaign.total_bounced = bounced
    campaign.total_failed = failed
    campaign.total_complained = complained
    campaign.delivery_rate = round((delivered / sent * 100) if sent else 0, 2)
    campaign.open_rate = round((opened / sent * 100) if sent else 0, 2)
    campaign.click_rate = round((clicked / sent * 100) if sent else 0, 2)
    campaign.bounce_rate = round((bounced / sent * 100) if sent else 0, 2)
    campaign.complaint_rate = round((complained / sent * 100) if sent else 0, 2)


def mark_contact_suppressed(
    db: Session,
    *,
    contact_id: Optional[int] = None,
    email: Optional[str] = None,
    reason: str,
    source: str,
    channel: str = "Email",
    status: str = "suppressed",
) -> Optional[Contact]:
    contact = None
    if contact_id is not None:
        contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None and email:
        contact = db.query(Contact).filter(func.lower(Contact.email) == email.lower()).first()
    if contact is None:
        return None

    contact.is_suppressed = True
    contact.status = status
    contact.suppression_channel = channel
    contact.suppression_reason = reason
    contact.suppressed_at = datetime.utcnow()

    suppression = (
        db.query(Suppression)
        .filter(
            Suppression.contact_id == contact.id,
            Suppression.channel == channel,
        )
        .first()
    )
    if suppression is None:
        suppression = Suppression(
            contact_id=contact.id,
            channel=channel,
        )
        db.add(suppression)

    suppression.reason = reason
    suppression.source = source
    return contact

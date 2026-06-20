from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Text,
    JSON,
    Index,
)

from sqlalchemy.sql import func

from app.database import Base


class EmailLog(Base):

    __tablename__ = "email_logs"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    tenant_id = Column(
        String,
        nullable=True,
        index=True
    )

    campaign_id = Column(
        String,
        nullable=True,
        index=True
    )

    contact_id = Column(
        Integer,
        nullable=True
    )

    recipient_name = Column(
        String,
        nullable=True
    )

    recipient_email = Column(
        String,
        nullable=False,
        index=True
    )

    recipient_phone = Column(
        String,
        nullable=True
    )

    subject = Column(
        String,
        nullable=True
    )

    template_name = Column(
        String,
        nullable=True
    )

    campaign_name = Column(
        String,
        nullable=True
    )

    status = Column(
        String,
        nullable=False,
        default="queued",
        index=True
    )

    delivery_status = Column(
        String,
        nullable=True
    )

    opens = Column(
        Integer,
        nullable=False,
        default=0
    )

    clicks = Column(
        Integer,
        nullable=False,
        default=0
    )

    retry_count = Column(
        Integer,
        nullable=False,
        default=0
    )

    provider = Column(
        String,
        nullable=True,
        default="aws_ses"
    )

    ses_message_id = Column(
        String,
        nullable=True,
        index=True
    )

    message_id = Column(
        String,
        nullable=True,
        index=True
    )

    smtp_response = Column(
        Text,
        nullable=True
    )

    bounce_reason = Column(
        Text,
        nullable=True
    )

    complaint_reason = Column(
        Text,
        nullable=True
    )

    error_message = Column(
        Text,
        nullable=True
    )

    unsubscribe_reason = Column(
        Text,
        nullable=True
    )

    ip_address = Column(
        String,
        nullable=True
    )

    user_agent = Column(
        Text,
        nullable=True
    )

    country = Column(
        String,
        nullable=True
    )

    city = Column(
        String,
        nullable=True
    )

    ses_event_data = Column(
        JSON,
        nullable=True
    )

    sent_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    delivered_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    opened_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    clicked_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    bounced_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    complaint_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    failed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    unsubscribed_at = Column(
        DateTime(timezone=True),
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
    )


# Composite index to speed up queries filtered by campaign_id and ordered by created_at
Index("ix_email_logs_campaign_created_at", EmailLog.__tablename__ + ":campaign_id", "campaign_id", "created_at")

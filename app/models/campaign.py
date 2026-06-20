from sqlalchemy import Column, Integer, String, DateTime, Text, text, Float
from sqlalchemy.sql import func

from app.database import Base
from sqlalchemy import JSON

class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(
        String,
        primary_key=True,
        index=True,
        server_default=text("gen_random_uuid()"),
    )

    workspace_id = Column(String, nullable=True)
    created_by_user_id = Column(String, nullable=True)
    campaign_name = Column(String, nullable=False)
    channel = Column(String, nullable=False)
    goal_label = Column(String, nullable=True)
    status = Column(String, nullable=False, default="draft")
    current_step = Column(Integer, default=1)
    subject_line = Column(String, nullable=True)
    preview_text = Column(String, nullable=True)
    template_id = Column(String, nullable=True)
    sender_identity_id = Column(String, nullable=True)
    audience_list_ids = Column(JSON, nullable=True)
    exclude_list_ids = Column(JSON, nullable=True)
    estimated_recipients = Column(Integer, default=0)
    suppressed_count = Column(Integer, default=0)
    send_mode = Column(String, nullable=True)
    scheduled_at = Column(DateTime(timezone=True), nullable=True)
    timezone = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    sent_at = Column(DateTime(timezone=True), nullable=True)
    credits_used = Column(Integer, nullable=True)
    approved_by_user_id = Column(String, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    email_sent_at = Column(DateTime(timezone=True), nullable=True)

    # Analytics Stats
    total_sent = Column(Integer, default=0)
    total_delivered = Column(Integer, default=0)
    total_opened = Column(Integer, default=0)
    total_clicked = Column(Integer, default=0)
    total_bounced = Column(Integer, default=0)
    total_failed = Column(Integer, default=0)
    total_complained = Column(Integer, default=0)
    total_unsubscribed = Column(Integer, default=0)
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    delivery_rate = Column(Float, default=0.0)
    bounce_rate = Column(Float, default=0.0)
    complaint_rate = Column(Float, default=0.0)
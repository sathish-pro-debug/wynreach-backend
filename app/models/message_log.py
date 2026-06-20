from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean

from sqlalchemy.sql import func

from app.database import Base


class MessageLog(Base):

    __tablename__ = "message_logs"

    id = Column(Integer, primary_key=True, index=True)

    campaign_id = Column(String, nullable=True)

    campaign_name = Column(String, nullable=True)

    template_name = Column(String, nullable=True)

    recipient_name = Column(String, nullable=True)

    recipient_phone = Column(String, nullable=False)

    recipient_email = Column(String, nullable=True)

    message = Column(Text, nullable=True)

    status = Column(String, default="sent")

    wamid = Column(String, nullable=True)

    delivered = Column(Boolean, default=False)

    is_read = Column(Boolean, default=False)

    error_reason = Column(Text, nullable=True)

    engagement_score = Column(Float, default=0)

    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    delivered_at = Column(DateTime(timezone=True), nullable=True)

    read_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    source = Column(String, nullable=True, default="campaign")
    
    direction = Column(String, nullable=True, default="outgoing")

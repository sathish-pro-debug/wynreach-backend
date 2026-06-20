from sqlalchemy import Column, String, JSON, Integer, DateTime
from sqlalchemy.sql import func
from app.database import Base

class EmailEvent(Base):

    __tablename__ = "email_events"

    id = Column(String, primary_key=True)

    tenant_id = Column(String)

    campaign_id = Column(String, nullable=True)

    contact_id = Column(Integer, nullable=True)

    message_id = Column(String, nullable=True)

    recipient_email = Column(String)

    event_type = Column(String)

    event_metadata = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
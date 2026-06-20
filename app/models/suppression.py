from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

from datetime import datetime

from app.database import Base


class Suppression(Base):

    __tablename__ = "suppressions"

    id = Column(Integer, primary_key=True, index=True)

    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)

    channel = Column(String(50), nullable=False)

    reason = Column(String(255), nullable=True)

    source = Column(String(255), nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

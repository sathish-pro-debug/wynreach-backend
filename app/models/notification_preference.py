# =====================================================
# app/models/notification_preference.py
# =====================================================

from sqlalchemy import (
    Column,
    Integer,
    Boolean,
    String,
    DateTime
)

from datetime import datetime

from app.database import Base


class NotificationPreference(Base):

    __tablename__ = "notification_preferences"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    notification_type = Column(
        String(100),
        nullable=False,
        unique=True
    )

    in_app = Column(
        Boolean,
        default=True
    )

    email = Column(
        Boolean,
        default=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     DateTime,
#     Boolean,
#     JSON
# )

# from datetime import datetime

# from app.database import Base


# class Contact(Base):

#     __tablename__ = "contacts"

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True
#     )

#     # ==========================================
#     # BASIC DETAILS
#     # ==========================================

#     full_name = Column(
#         String(255),
#         nullable=False
#     )

#     email = Column(
#         String(255),
#         nullable=True
#     )

#     phone = Column(
#         String(50),
#         nullable=True
#     )

#     status = Column(
#         String(50),
#         default="active"
#     )

#     # ==========================================
#     # SUPPRESSION
#     # ==========================================

#     is_suppressed = Column(
#         Boolean,
#         default=False
#     )

#     suppression_channel = Column(
#         String(50),
#         nullable=True
#     )

#     suppression_reason = Column(
#         String(255),
#         nullable=True
#     )

#     suppressed_at = Column(
#         DateTime,
#         nullable=True
#     )

#     # ==========================================
#     # EXTRA FIELDS
#     # ==========================================

#     tags = Column(
#         JSON,
#         nullable=True,
#         default=[]
#     )

#     score = Column(
#         Integer,
#         default=0
#     )

#     campaign = Column(
#         String(255),
#         nullable=True
#     )

#     # ==========================================
#     # TIMESTAMPS
#     # ==========================================

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

#     updated_at = Column(
#         DateTime,
#         default=datetime.utcnow,
#         onupdate=datetime.utcnow
#     )


from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON

from datetime import datetime

from sqlalchemy.orm import relationship

from app.database import Base


class Contact(Base):

    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)

    # ==========================================
    # BASIC DETAILS
    # ==========================================

    full_name = Column(String(255), nullable=False)

    email = Column(String(255), nullable=True, unique=True)

    phone = Column(String(50), nullable=True)

    status = Column(String(50), default="active")

    # ==========================================
    # SUPPRESSION
    # ==========================================

    is_suppressed = Column(Boolean, default=False)

    suppression_channel = Column(String(50), nullable=True)

    suppression_reason = Column(String(255), nullable=True)

    suppressed_at = Column(DateTime, nullable=True)

    # ==========================================
    # EXTRA FIELDS
    # ==========================================

    tags = Column(JSON, nullable=True, default=[])

    score = Column(Integer, default=0)

    campaign = Column(String(255), nullable=True)

    # ==========================================
    # ✅ NEW FIELD
    # ==========================================

    is_whatsapp = Column(Boolean, default=False)

    # ==========================================
    # TIMESTAMPS
    # ==========================================

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ==========================================
    # RELATIONSHIP
    # ==========================================

    lists = relationship("ListContact", back_populates="contact", cascade="all, delete")

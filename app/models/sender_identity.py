# app/models/sender_identity.py
from sqlalchemy import Column, String, Boolean, DateTime, Integer, Text, JSON
from sqlalchemy.sql import func
from app.database import Base
import uuid

class EmailDomain(Base):
    __tablename__ = "email_domains"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), nullable=False, index=True)
    domain = Column(String(255), unique=True, nullable=False, index=True)
    sender_name = Column(String(255), nullable=False)
    from_email = Column(String(255), nullable=False)
    reply_to_email = Column(String(255), nullable=True)
    
    # DNS Verification Status
    spf_status = Column(String(20), default='pending')
    dkim_status = Column(String(20), default='pending')
    dmarc_status = Column(String(20), default='pending')
    
    # AWS SES Specific Fields
    aws_verification_token = Column(String(255), nullable=True)
    aws_dkim_tokens = Column(JSON, nullable=True)
    aws_verification_status = Column(String(20), default='pending')
    
    # ✅ Active/Inactive Status (Simple toggle)
    is_active = Column(Boolean, default=True)  # True = Active, False = Inactive
    
    is_default = Column(Boolean, default=False)
    verification_details = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# app/models/sender_identity.py
class EmailAddress(Base):
    __tablename__ = "email_addresses"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), nullable=False, index=True)
    domain_id = Column(String(50), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    status = Column(String(20), default='pending')
    is_active = Column(Boolean, default=True)  # ✅ NEW: Active/Inactive status
    verification_code = Column(String(10), nullable=True)
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WhatsAppNumber(Base):
    __tablename__ = "whatsapp_numbers"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(50), nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    account_name = Column(String(255), nullable=False)
    status = Column(String(20), default='pending')
    templates_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
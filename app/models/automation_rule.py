# app/models/automation_rule.py
from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Integer
from sqlalchemy.sql import func
from app.database import Base
import uuid

class AutomationRule(Base):
    __tablename__ = "automation_rules"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    # Remove user_id or make it nullable
    # user_id = Column(String(50), nullable=True, index=True)  # ← Make nullable
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Campaign association
    campaign_id = Column(String(50), nullable=False, index=True)
    campaign_name = Column(String(255), nullable=True)
    campaign_channel = Column(String(20), nullable=False)
    
    # Trigger configuration
    trigger_type = Column(String(50), nullable=False)
    trigger_config = Column(JSON, nullable=True)
    
    # Condition configuration
    condition_type = Column(String(50), default="always")
    condition_config = Column(JSON, nullable=True)
    
    # Action configuration
    action_type = Column(String(50), nullable=False)
    action_config = Column(JSON, nullable=True)
    
    is_active = Column(Boolean, default=True)
    execution_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
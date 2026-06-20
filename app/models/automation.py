# backend/app/models/automation.py
from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.sql import func
from app.database import Base
import uuid

# ============ EXISTING RULE MODELS ============
class AutomationRule(Base):
    __tablename__ = "automation_rules"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="paused")
    
    trigger_type = Column(String(50), nullable=False)
    trigger_config = Column(JSON, default={})
    
    condition_type = Column(String(50), default="always")
    condition_config = Column(JSON, default={})
    
    action_type = Column(String(50), nullable=False)
    action_config = Column(JSON, default={})
    
    total_triggered = Column(Integer, default=0)
    last_triggered_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class RuleExecution(Base):
    __tablename__ = "rule_executions"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    rule_id = Column(String(50), nullable=False)
    contact_id = Column(Integer, nullable=True)
    triggered_at = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="success")
    details = Column(JSON, default={})


# ============ SEQUENCE MODELS ============

class AutomationSequence(Base):
    __tablename__ = "automation_sequences"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    workspace_id = Column(Integer, nullable=True, default=1)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default="active")
    
    # Campaign association
    campaign_id = Column(String(50), nullable=True)
    campaign_name = Column(String(255), nullable=True)
    campaign_channel = Column(String(20), nullable=True)
    
    # Pause/Resume tracking
    last_resume_at = Column(DateTime, nullable=True)
    paused_at = Column(DateTime, nullable=True)
    
    # Steps configuration
    steps = Column(JSON, default=[])
    
    # Analytics
    total_triggered = Column(Integer, default=0)
    completed_count = Column(Integer, default=0)
    last_triggered_at = Column(DateTime, nullable=True)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def to_dict(self):
        """Convert model to dictionary for API responses"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "campaign_id": self.campaign_id,
            "campaign_name": self.campaign_name,
            "campaign_channel": self.campaign_channel,
            "steps": self.steps if self.steps else [],
            "status": self.status,
            "total_triggered": self.total_triggered or 0,
            "completed_count": self.completed_count or 0,
            "last_resume_at": self.last_resume_at.isoformat() if self.last_resume_at else None,
            "paused_at": self.paused_at.isoformat() if self.paused_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SequenceExecution(Base):
    __tablename__ = "sequence_executions"
    
    id = Column(String(50), primary_key=True, default=lambda: str(uuid.uuid4()))
    sequence_id = Column(String(50), nullable=False)
    contact_id = Column(Integer, nullable=True)
    current_step = Column(Integer, default=0)
    started_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)
    status = Column(String(20), default="in_progress")
    last_message_sent_at = Column(DateTime, nullable=True)
    details = Column(JSON, default={})
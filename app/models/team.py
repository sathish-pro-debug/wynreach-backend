from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.database import Base

import uuid
class TeamMember(Base):
    __tablename__ = "team_members"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), nullable=True)
    workspace_id = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default='member')
    status = Column(String(20), nullable=False, default='pending')
    invited_by_user_id = Column(String(50), nullable=True)
    invite_token = Column(String(255), unique=True, nullable=True)
    last_active_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
class Invitation(Base):
    __tablename__ = "invitations"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), nullable=False, index=True)
    workspace_id = Column(String(50), nullable=False)
    workspace_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False)
    invited_by = Column(String(50), nullable=False)
    invited_by_name = Column(String(255), nullable=True)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

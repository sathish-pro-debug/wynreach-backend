# backend/app/schemas/team.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TeamRole(str, Enum):
    OWNER = "Owner"
    ADMIN = "Admin"
    EDITOR = "Editor"
    APPROVER = "Approver"
    VIEWER = "Viewer"

class MemberStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"

# Request Models
class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: TeamRole = TeamRole.VIEWER

class UpdateRoleRequest(BaseModel):
    member_id: str
    role: TeamRole

class RemoveMemberRequest(BaseModel):
    member_id: str

class ResendInviteRequest(BaseModel):
    email: str

# Response Models
class TeamMemberResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    status: str
    last_active: Optional[datetime]
    invited_at: datetime
    accepted_at: Optional[datetime]
    color: Optional[str] = None  # For frontend avatar

class InvitationResponse(BaseModel):
    id: str
    email: str
    role: str
    expires_at: datetime
    invited_at: datetime

class WorkspaceResponse(BaseModel):
    id: str
    name: str
    owner_id: str
    created_at: datetime
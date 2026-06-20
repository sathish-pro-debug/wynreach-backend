# backend/app/schemas/user_profile.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# ============ PROFILE SCHEMAS ============

class UserProfileUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    timezone: Optional[str] = None
    language: Optional[str] = None
    bio: Optional[str] = None
    avatar: Optional[str] = None


class UserProfileResponse(BaseModel):
    """Schema for user profile response with Integer ID"""
    id: int  # Changed from str to int to match your model
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    timezone: Optional[str] = "Asia/Kolkata"
    language: Optional[str] = "English"
    bio: Optional[str] = None
    avatar: Optional[str] = None
    role: str
    workspace_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """Schema for password change request"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)
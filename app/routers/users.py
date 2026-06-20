# backend/app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime
from jose import jwt, JWTError
from typing import Any

from app.database import get_main_db
from app.models.user import User
from app.services.auth_service import get_password_hash, verify_password
from app.core.config import settings

router = APIRouter(prefix="/users", tags=["Users"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_main_db)
):
    """Get current user from JWT token"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Get user by ID from token
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user


# ============ GET USER PROFILE ============
@router.get("/me")
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> Any:
    """Get current user profile"""
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": getattr(current_user, 'phone', ''),
        "company": getattr(current_user, 'company', ''),
        "job_title": getattr(current_user, 'job_title', ''),
        "timezone": getattr(current_user, 'timezone', 'Asia/Kolkata'),
        "language": getattr(current_user, 'language', 'English'),
        "bio": getattr(current_user, 'bio', ''),
        "avatar": getattr(current_user, 'avatar', None),
        "role": current_user.role,
        "workspace_id": current_user.workspace_id,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }


# ============ UPDATE USER PROFILE ============
@router.put("/me")
async def update_current_user_profile(
    profile_data: dict,
    db: Session = Depends(get_main_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Update current user profile"""
    
    allowed_fields = ['full_name', 'phone', 'company', 'job_title', 
                      'timezone', 'language', 'bio', 'avatar']
    
    for field in allowed_fields:
        if field in profile_data and profile_data[field] is not None:
            setattr(current_user, field, profile_data[field])
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone": getattr(current_user, 'phone', ''),
        "company": getattr(current_user, 'company', ''),
        "job_title": getattr(current_user, 'job_title', ''),
        "timezone": getattr(current_user, 'timezone', 'Asia/Kolkata'),
        "language": getattr(current_user, 'language', 'English'),
        "bio": getattr(current_user, 'bio', ''),
        "avatar": getattr(current_user, 'avatar', None),
        "role": current_user.role,
        "workspace_id": current_user.workspace_id,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at
    }


# ============ CHANGE PASSWORD ============
@router.post("/me/change-password")
async def change_password(
    request: dict,
    db: Session = Depends(get_main_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Change user password"""
    
    current_password = request.get('current_password')
    new_password = request.get('new_password')
    
    if not current_password or not new_password:
        raise HTTPException(status_code=400, detail="Current password and new password are required")
    
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="New password must be at least 8 characters")
    
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    current_user.password_hash = get_password_hash(new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Password changed successfully"}


# ============ DELETE ACCOUNT ============
@router.delete("/me")
async def delete_account(
    db: Session = Depends(get_main_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    """Delete user account"""
    db.delete(current_user)
    db.commit()
    return {"message": "Account deleted successfully"}
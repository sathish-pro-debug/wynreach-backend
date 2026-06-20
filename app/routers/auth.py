# from fastapi import APIRouter, Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.orm import Session
# from datetime import datetime, timedelta
# from jose import jwt, JWTError
# import uuid
# import os

# from app.database import get_main_db
# from app.models.user import User
# from app.schemas.auth import (
#     SignupRequest,
#     LoginRequest,
#     AuthResponse,
#     ResetPasswordRequest
# )
# from app.services.auth_service import (
#     authenticate_user,
#     create_access_token,
#     create_refresh_token,
#     create_user_and_workspace,
#     get_password_hash,
#     verify_password
# )
# from app.utils.email import send_email
# from app.core.config import settings

# router = APIRouter()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


# # =====================================================
# # GET CURRENT USER HELPER
# # =====================================================

# def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: Session = Depends(get_main_db)
# ):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     if not token:
#         raise credentials_exception
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#     except JWTError:
#         raise credentials_exception
#     user = db.query(User).filter(User.id == int(user_id)).first()
#     if user is None:
#         raise credentials_exception
#     return user


# # =====================================================
# # SIGNUP
# # =====================================================

# @router.post("/signup")
# async def signup(
#     req: SignupRequest,
#     db: Session = Depends(get_main_db)
# ):
#     existing = db.query(User).filter(User.email == req.email).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Email already registered")

#     user, workspace = create_user_and_workspace(
#         db,
#         req.full_name,
#         req.email,
#         getattr(req, "phone", ""),
#         getattr(req, "company", "")
#     )

#     setup_token = str(uuid.uuid4())
#     user.setup_token = setup_token
#     user.setup_token_expiry = datetime.utcnow() + timedelta(hours=24)
#     db.commit()

#     frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
#     setup_link = f"{frontend_url}/set-password/{setup_token}"

#     await send_email(
#         to_email=user.email,
#         subject="Set Your Password",
#         body=f"""Welcome to WynReach!\n\nClick below link to set your password:\n\n{setup_link}\n\nThis link expires in 24 hours."""
#     )

#     print("\n✅ PASSWORD SETUP LINK")
#     print(setup_link)

#     return {"success": True, "message": "Password setup link sent to email"}


# # =====================================================
# # SET PASSWORD
# # =====================================================

# @router.post("/set-password")
# def set_password(
#     request: ResetPasswordRequest,
#     db: Session = Depends(get_main_db)
# ):
#     user = db.query(User).filter(User.setup_token == request.token).first()

#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid token")

#     if user.setup_token_expiry and user.setup_token_expiry < datetime.utcnow():
#         raise HTTPException(status_code=400, detail="Token expired")

#     user.password_hash = get_password_hash(request.new_password)
#     user.is_active = True
#     user.setup_token = None
#     user.setup_token_expiry = None
#     db.commit()

#     return {"success": True, "message": "Password set successfully"}


# # =====================================================
# # LOGIN
# # =====================================================

# @router.post("/login", response_model=AuthResponse)
# def login(
#     req: LoginRequest,
#     db: Session = Depends(get_main_db)
# ):
#     user = authenticate_user(db, req.email, req.password)

#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password"
#         )

#     if not user.is_active:
#         raise HTTPException(status_code=401, detail="Please setup password first")

#     access_token = create_access_token({"sub": str(user.id)})
#     refresh_token = create_refresh_token(db, user.id)

#     return {
#         "user": user,
#         "workspace": user.workspace,
#         "access_token": access_token,
#         "refresh_token": refresh_token
#     }


# # =====================================================
# # FORGOT PASSWORD
# # =====================================================

# @router.post("/forgot-password")
# async def forgot_password(
#     payload: dict,
#     db: Session = Depends(get_main_db)
# ):
#     email = payload.get("email")
#     user = db.query(User).filter(User.email == email).first()

#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     reset_token = str(uuid.uuid4())
#     user.setup_token = reset_token
#     user.setup_token_expiry = datetime.utcnow() + timedelta(hours=1)
#     db.commit()

#     frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
#     reset_link = f"{frontend_url}/reset-password/{reset_token}"

#     await send_email(
#         to_email=user.email,
#         subject="Reset Password",
#         body=f"""Click below link to reset password:\n\n{reset_link}\n\nThis link expires in 1 hour."""
#     )

#     return {"success": True, "message": "Reset link sent to email"}


# # =====================================================
# # GET MY PROFILE
# # =====================================================

# @router.get("/me")
# def get_me(current_user: User = Depends(get_current_user)):
#     return {
#         "user": {
#             "id": current_user.id,
#             "full_name": current_user.full_name,
#             "email": current_user.email,
#             "phone": getattr(current_user, 'phone', '') or '',
#             "company": getattr(current_user, 'company', '') or '',
#             "role": current_user.role,
#             "created_at": str(current_user.created_at) if hasattr(current_user, 'created_at') else '',
#             "timezone": getattr(current_user, 'timezone', 'Asia/Kolkata') or 'Asia/Kolkata',
#             "language": getattr(current_user, 'language', 'English') or 'English',
#             "job_title": getattr(current_user, 'job_title', '') or '',
#             "bio": getattr(current_user, 'bio', '') or '',
#         }
#     }


# # =====================================================
# # UPDATE MY PROFILE
# # =====================================================

# @router.put("/me")
# def update_me(
#     payload: dict,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_main_db)
# ):
#     updatable = ['full_name', 'phone', 'company', 'job_title', 'timezone', 'language', 'bio']
#     for field in updatable:
#         if field in payload and hasattr(current_user, field):
#             setattr(current_user, field, payload[field])
#     db.commit()
#     db.refresh(current_user)
#     return {"success": True, "message": "Profile updated"}


# # =====================================================
# # CHANGE PASSWORD
# # =====================================================

# @router.post("/change-password")
# def change_password(
#     payload: dict,
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_main_db)
# ):
#     current_password = payload.get("current_password")
#     new_password = payload.get("new_password")

#     if not verify_password(current_password, current_user.password_hash):
#         raise HTTPException(status_code=400, detail="Current password is incorrect")

#     current_user.password_hash = get_password_hash(new_password)
#     db.commit()

#     return {"success": True, "message": "Password changed successfully"}

from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import authenticate_team_member
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone 
from jose import jwt, JWTError
import uuid
import os
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.database import get_main_db
from app.models.user import User, Workspace
from app.models.team import TeamMember # ← ADD THIS IMPORT
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    ResetPasswordRequest
)
from app.services.auth_service import (
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_user_and_workspace,
    get_password_hash,
    verify_password,
    validate_password_strength
)
from app.utils.email import send_email
from app.core.config import settings

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    auto_error=False
)


# =====================================================
# CREATE DEMO ADMIN
# =====================================================

def create_demo_admin(db: Session):

    existing = (
        db.query(User)
        .filter(User.email == "admin@gmail.com")
        .first()
    )

    # ALREADY EXISTS
    if existing:
        return

    # =================================================
    # CREATE WORKSPACE
    # =================================================

    workspace = Workspace(
        name="Demo Workspace",
        slug="demo-workspace",
        plan="free"
    )

    db.add(workspace)

    db.commit()

    db.refresh(workspace)

    # =================================================
    # CREATE ADMIN USER
    # =================================================

    admin_user = User(
        full_name="Admin User",

        email="admin@gmail.com",

        password_hash=get_password_hash("Admin@123"),

        role="owner",

        workspace_id=workspace.id,

        phone="+911234567890",

        company="WynReach",

        is_active=True
    )

    db.add(admin_user)

    db.commit()

    db.refresh(admin_user)

    print("✅ Demo Admin Created")


# =====================================================
# GET CURRENT USER
# =====================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_main_db)
):

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token:
        raise credentials_exception

    try:

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    user = (
        db.query(User)
        .filter(User.id == int(user_id))
        .first()
    )

    if user is None:
        raise credentials_exception

    return user


@router.post("/signup")
def signup(req: SignupRequest, db: Session = Depends(get_main_db)):
    """Create a new user account"""
    
    create_demo_admin(db)
    
    # Check if user exists
    existing = db.query(User).filter(User.email == req.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate password strength
    validate_password_strength(req.password)
    
    # Create user and workspace
    user, workspace = create_user_and_workspace(
        db,
        req.full_name,
        req.email,
        req.password,
        req.phone,
        req.company
    )
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(db, user.id)
    
    # ✅ Return COMPLETE user data including phone and company
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "phone": user.phone or "",
            "company": user.company or "",
            "workspace_id": user.workspace_id,
            "role": "owner",
            "created_at": str(user.created_at),
            "timezone": getattr(user, "timezone", "Asia/Kolkata"),
            "language": getattr(user, "language", "English"),
            "job_title": getattr(user, "job_title", ""),
            "bio": getattr(user, "bio", ""),
            "avatar": getattr(user, "avatar", "")
        },
        "workspace": {
            "id": workspace.id,
            "name": workspace.name,
            "slug": workspace.slug
        }
    }

# =====================================================
# SET PASSWORD
# =====================================================

@router.post("/set-password")
def set_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_main_db)
):

    user = (
        db.query(User)
        .filter(User.setup_token == request.token)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid token"
        )

    if (
        user.setup_token_expiry
        and user.setup_token_expiry < datetime.utcnow()
    ):
        raise HTTPException(
            status_code=400,
            detail="Token expired"
        )

    # UPDATE PASSWORD
    user.password_hash = get_password_hash(
        request.new_password
    )

    user.is_active = True

    user.setup_token = None

    user.setup_token_expiry = None

    db.commit()

    return {
        "success": True,
        "message": "Password set successfully"
    }


# =====================================================
# LOGIN
# =====================================================
@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_main_db)):
    """Login for workspace members"""
    
    print(f"🔐 Login attempt: {login_data.email}")
    
    user = authenticate_team_member(db, login_data.email, login_data.password)
    
    if not user:
        print(f"❌ Login failed for: {login_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    print(f"✅ Login successful: {user.email}")
    
    # Create tokens
    access_token = create_access_token(data={"sub": str(user.id), "user_id": user.id})
    refresh_token = create_refresh_token(db, user.id)
    
    # Get team member info
    team_member = db.query(TeamMember).filter(
        TeamMember.user_id == str(user.id)
    ).first()
    
    # Determine role
    role = "owner"
    if team_member:
        role = team_member.role
    elif user.role == "owner":
        role = "owner"
    
    # ✅ Handle null created_at
    created_at_str = None
    if user.created_at:
        created_at_str = str(user.created_at)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "workspace_id": user.workspace_id,
            "role": role,
            "phone": getattr(user, "phone", "") or "",
            "company": getattr(user, "company", "") or "",
            "created_at": created_at_str,  # ✅ Handle null
            "timezone": getattr(user, "timezone", "Asia/Kolkata"),
            "language": getattr(user, "language", "English"),
            "job_title": getattr(user, "job_title", ""),
            "bio": getattr(user, "bio", ""),
            "avatar": getattr(user, "avatar", "")
        }
    }

# =====================================================
# FORGOT PASSWORD
# =====================================================

@router.post("/forgot-password")
async def forgot_password(
    payload: dict,
    db: Session = Depends(get_main_db)
):

    email = payload.get("email")

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    reset_token = str(uuid.uuid4())

    user.setup_token = reset_token

    user.setup_token_expiry = (
        datetime.utcnow()
        + timedelta(hours=1)
    )

    db.commit()

    frontend_url = os.getenv(
        "FRONTEND_URL",
        "http://localhost:5173"
    )

    reset_link = (
        f"{frontend_url}/reset-password/{reset_token}"
    )

    await send_email(
        to_email=user.email,
        subject="Reset Password",
        body=f"""
Click below link to reset password:

{reset_link}

This link expires in 1 hour.
"""
    )

    return {
        "success": True,
        "message": "Reset link sent to email"
    }


# =====================================================
# GET PROFILE
# =====================================================

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_main_db)):
    """Get current user profile"""
    
    # Get team member role
    team_member = db.query(TeamMember).filter(
        TeamMember.user_id == str(current_user.id),
        TeamMember.workspace_id == str(current_user.workspace_id)
    ).first()
    
    role = team_member.role if team_member else current_user.role
    
    return {
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "phone": getattr(current_user, "phone", "") or "",
            "company": getattr(current_user, "company", "") or "",
            "avatar": getattr(current_user, "avatar", "") or "",
            "role": role,
            "created_at": str(current_user.created_at),
            "timezone": getattr(current_user, "timezone", "Asia/Kolkata"),
            "language": getattr(current_user, "language", "English"),
            "job_title": getattr(current_user, "job_title", ""),
            "bio": getattr(current_user, "bio", ""),
        }
    }

@router.put("/me")
def update_me(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_main_db)):
    """Update current user profile"""
    
    updatable = ["full_name", "phone", "company", "job_title", "timezone", "language", "bio", "avatar"]
    
    for field in updatable:
        if field in payload and hasattr(current_user, field):
            setattr(current_user, field, payload[field])
    
    db.commit()
    db.refresh(current_user)
    
    # Get updated team member role
    team_member = db.query(TeamMember).filter(
        TeamMember.user_id == str(current_user.id),
        TeamMember.workspace_id == str(current_user.workspace_id)
    ).first()
    
    role = team_member.role if team_member else current_user.role
    
    return {
        "success": True,
        "message": "Profile updated",
        "user": {
            "id": current_user.id,
            "full_name": current_user.full_name,
            "email": current_user.email,
            "phone": current_user.phone or "",
            "company": current_user.company or "",
            "avatar": current_user.avatar or "",
            "role": role,
            "timezone": current_user.timezone or "Asia/Kolkata",
            "language": current_user.language or "English",
            "job_title": current_user.job_title or "",
            "bio": current_user.bio or "",
        }
    }


@router.post("/change-password")
def change_password(payload: dict, current_user: User = Depends(get_current_user), db: Session = Depends(get_main_db)):
    """Change user password"""
    
    if not verify_password(payload.get("current_password"), current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    
    new_password = payload.get("new_password")
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    
    return {"success": True, "message": "Password changed successfully"}
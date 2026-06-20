from datetime import datetime, timedelta
import secrets
import re
from fastapi import HTTPException, Depends, Request
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User, Workspace, RefreshToken
from app.models.team import TeamMember
from app.core.config import settings
from app.database import get_main_db
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not hashed_password:
        return False
    return pwd_context.verify(plain_password, hashed_password)
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
def validate_password_strength(password: str) -> bool:
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    if not re.search(r"[A-Z]", password):
        raise HTTPException(status_code=400, detail="Password must contain an uppercase letter")
    if not re.search(r"[a-z]", password):
        raise HTTPException(status_code=400, detail="Password must contain a lowercase letter")
    if not re.search(r"\d", password):
        raise HTTPException(status_code=400, detail="Password must contain a number")
    return True
def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
def create_refresh_token(db: Session, user_id: int) -> str:
    token = secrets.token_urlsafe(64)
    expires_at = datetime.utcnow() + timedelta(days=7)
    db_refresh = RefreshToken(token=token, user_id=user_id, expires_at=expires_at)
    db.add(db_refresh)
    db.commit()
    return token
def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        return None
    if not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user
def authenticate_team_member(db: Session, email: str, password: str):
    return authenticate_user(db, email, password)
def create_user_and_workspace(db: Session, full_name: str, email: str, password: str, phone: str = "", company: str = ""):
    # Generate unique slug
    base_slug = full_name.lower().replace(" ", "-")
    slug = base_slug
    counter = 1
    while db.query(Workspace).filter(Workspace.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
    workspace = Workspace(
        name=f"{full_name}'s Workspace",
        slug=slug,
        plan="free"
    )
    db.add(workspace)
    db.flush()
    hashed_password = get_password_hash(password)
    new_user = User(
        full_name=full_name,
        email=email,
        password_hash=hashed_password,
        workspace_id=workspace.id,
        phone=phone,
        company=company,
        is_active=True
    )
    db.add(new_user)
    db.flush()
    team_member = TeamMember(
        user_id=str(new_user.id),
        workspace_id=str(workspace.id),
        email=email,
        full_name=full_name,
        role="owner",
        status="active",
        invited_by_user_id=str(new_user.id)
    )
    db.add(team_member)
    db.commit()
    db.refresh(new_user)
    db.refresh(workspace)
    return new_user, workspace
async def get_current_user(
    request: Request,
    db: Session = Depends(get_main_db)
):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Not authenticated")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    token = auth_header.replace("Bearer ", "")
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        if not user.is_active:
            raise HTTPException(status_code=401, detail="User inactive")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

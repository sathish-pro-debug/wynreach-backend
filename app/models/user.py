# # ## backend/app/models/user.py
# # from sqlalchemy import (
# #     Column,
# #     Integer,
# #     String,
# #     DateTime,
# #     Boolean,
# #     ForeignKey,
# #     Text
# # )
# # from sqlalchemy.sql import func
# # from sqlalchemy.orm import relationship
# # from app.database import Base


# # # =========================
# # # Workspace Model
# # # =========================
# # class Workspace(Base):
# #     __tablename__ = "workspaces"

# #     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
# #     name = Column(String, nullable=False)
# #     slug = Column(String, unique=True, nullable=False)
# #     plan = Column(String, default="free")
# #     created_at = Column(DateTime, server_default=func.now())
# #     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# #     users = relationship("User", back_populates="workspace", cascade="all, delete")
# #     email_settings = relationship("WorkspaceEmailSettings", back_populates="workspace", uselist=False)
    
# #     # ✅ If you want automation rules, add it here (NOT in RefreshToken)
# #     # automation_rules = relationship("AutomationRule", back_populates="workspace", cascade="all, delete")


# # # =========================
# # # Workspace Email Settings Model
# # # =========================
# # class WorkspaceEmailSettings(Base):
# #     __tablename__ = "workspace_email_settings"
    
# #     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
# #     workspace_id = Column(Integer, ForeignKey("workspaces.id"), unique=True, nullable=False)
    
# #     smtp_host = Column(String, default="smtp.gmail.com")
# #     smtp_port = Column(Integer, default=587)
# #     smtp_user = Column(String, nullable=False)
# #     smtp_password = Column(String, nullable=False)
# #     from_email = Column(String, nullable=False)
# #     from_name = Column(String, default="Support")
# #     is_configured = Column(Boolean, default=False)
    
# #     created_at = Column(DateTime, server_default=func.now())
# #     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
# #     workspace = relationship("Workspace", back_populates="email_settings")


# # # =========================
# # # User Model
# # # =========================
# # class User(Base):
# #     __tablename__ = "users"

# #     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
# #     full_name = Column(String, nullable=False)
# #     email = Column(String, unique=True, nullable=False, index=True)
# #     password_hash = Column(String, nullable=False)
# #     role = Column(String, default="owner")
# #     is_active = Column(Boolean, default=True)
# #     workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=False)
# #     created_at = Column(DateTime, server_default=func.now())
# #     updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

# #     workspace = relationship("Workspace", back_populates="users")
# #     refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete")

# #     # Profile columns
# #     phone = Column(String(20), nullable=True)
# #     company = Column(String(255), nullable=True)
# #     job_title = Column(String(255), nullable=True)
# #     timezone = Column(String(50), default="Asia/Kolkata")
# #     language = Column(String(50), default="English")
# #     bio = Column(Text, nullable=True)
# #     avatar = Column(String(500), nullable=True)


# # # =========================
# # # Refresh Token Model
# # # =========================
# # class RefreshToken(Base):
# #     __tablename__ = "refresh_tokens"

# #     id = Column(Integer, primary_key=True, index=True, autoincrement=True)
# #     token = Column(String, unique=True, nullable=False)
# #     user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
# #     expires_at = Column(DateTime, nullable=False)
# #     created_at = Column(DateTime, server_default=func.now())

# #     user = relationship("User", back_populates="refresh_tokens")
    
# #     # ❌ REMOVED - This line should NOT be here
# #     # automation_rules = relationship("AutomationRule", back_populates="workspace", cascade="all, delete")

# # backend/app/models/user.py
# # backend/app/models/user.py
# from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
# from sqlalchemy.orm import relationship
# from datetime import datetime
# from app.database import Base

# class User(Base):
#     __tablename__ = "users"
    
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String(255), unique=True, index=True, nullable=False)
#     hashed_password = Column(String(255), nullable=False)
#     full_name = Column(String(255))
#     phone = Column(String(50))
#     company = Column(String(255))
#     role = Column(String(50), default="member")
#     is_active = Column(Boolean, default=True)
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships
#     workspace = relationship("Workspace", back_populates="users", uselist=False)
#     workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    
#     # Email settings relationship - FIXED
#     email_settings = relationship("WorkspaceEmailSettings", back_populates="user", uselist=False)

# class Workspace(Base):
#     __tablename__ = "workspaces"
    
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(255), nullable=False)
#     slug = Column(String(255), unique=True, index=True)
#     plan = Column(String(50), default="free")
#     created_at = Column(DateTime, default=datetime.utcnow)
    
#     # Relationships
#     users = relationship("User", back_populates="workspace")

# class WorkspaceEmailSettings(Base):
#     __tablename__ = "workspace_email_settings"
    
#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # ← Fixed: Added ForeignKey
#     from_email = Column(String(255))
#     from_name = Column(String(255))
#     smtp_host = Column(String(255))
#     smtp_port = Column(Integer)
#     smtp_username = Column(String(255))
#     smtp_password = Column(String(255))
#     created_at = Column(DateTime, default=datetime.utcnow)
#     updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
#     # Relationships - FIXED
#     user = relationship("User", back_populates="email_settings")

# class RefreshToken(Base):
#     __tablename__ = "refresh_tokens"
    
#     id = Column(Integer, primary_key=True, index=True)
#     token = Column(String(500), unique=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     expires_at = Column(DateTime)
#     created_at = Column(DateTime, default=datetime.utcnow)




from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text
)

from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


# =====================================================
# WORKSPACE MODEL
# =====================================================

class Workspace(Base):

    __tablename__ = "workspaces"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String, nullable=False)

    slug = Column(String, unique=True, nullable=False)

    plan = Column(String, default="free")

    created_at = Column(DateTime, default=datetime.utcnow)

    users = relationship("User", back_populates="workspace")


# =====================================================
# USER MODEL
# =====================================================

class User(Base):

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    full_name = Column(String, nullable=False)

    email = Column(String, unique=True, index=True, nullable=False)

    # IMPORTANT FIX
    password_hash = Column(String, nullable=True)

    role = Column(String, default="owner")

    workspace_id = Column(
        Integer,
        ForeignKey("workspaces.id")
    )

    phone = Column(String, nullable=True)

    company = Column(String, nullable=True)

    job_title = Column(String, nullable=True)

    timezone = Column(String, default="Asia/Kolkata")

    language = Column(String, default="English")

    bio = Column(Text, nullable=True)

    avatar = Column(String, nullable=True)

    is_active = Column(Boolean, default=False)

    setup_token = Column(String, nullable=True)

    setup_token_expiry = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    workspace = relationship(
        "Workspace",
        back_populates="users"
    )


# =====================================================
# REFRESH TOKEN MODEL
# =====================================================

class RefreshToken(Base):

    __tablename__ = "refresh_tokens"

    id = Column(Integer, primary_key=True, index=True)

    token = Column(String, unique=True, nullable=False)

    user_id = Column(Integer, ForeignKey("users.id"))

    expires_at = Column(DateTime, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
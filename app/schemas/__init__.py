# backend/app/schemas/__init__.py
from .auth import (
    UserResponse, WorkspaceResponse, LoginRequest,
    SignupRequest, AuthResponse, RefreshTokenRequest,
    TokenResponse, ForgotPasswordRequest, ResetPasswordRequest
)
from .chatbot import (
    ButtonSchema, FAQSchema, ChatbotCreate, ChatbotUpdate,
    ChatbotResponse, ChatRequest, ChatResponse
)

# ✅ ADD THESE NEW IMPORTS (don't modify existing above)
from .user_profile import (
    UserProfileUpdate,
    UserProfileResponse,
    ChangePasswordRequest,
)

__all__ = [
    # Existing exports
    "UserResponse", "WorkspaceResponse", "LoginRequest", "SignupRequest",
    "AuthResponse", "RefreshTokenRequest", "TokenResponse",
    "ForgotPasswordRequest", "ResetPasswordRequest",
    "ButtonSchema", "FAQSchema", "ChatbotCreate", "ChatbotUpdate",
    "ChatbotResponse", "ChatRequest", "ChatResponse",
    
    # ✅ ADD NEW exports
    "UserProfileUpdate",
    "UserProfileResponse",
    "ChangePasswordRequest",
]
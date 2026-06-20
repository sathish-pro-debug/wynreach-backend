# # # backend/app/schemas/auth.py
# # from pydantic import BaseModel, EmailStr
# # from typing import Optional
# # from datetime import datetime

# # class UserResponse(BaseModel):
# #     id: int
# #     email: EmailStr
# #     full_name: str
# #     role: str
# #     is_active: bool
# #     workspace_id: int
# #     created_at: datetime
# #     # Add these optional fields for profile
# #     phone: Optional[str] = ""
# #     company: Optional[str] = ""
# #     job_title: Optional[str] = ""
# #     timezone: Optional[str] = "Asia/Kolkata"
# #     language: Optional[str] = "English"
# #     bio: Optional[str] = ""
# #     avatar: Optional[str] = None
    
# #     class Config:
# #         from_attributes = True

# # class WorkspaceResponse(BaseModel):
# #     id: int
# #     name: str
# #     slug: str
# #     plan: str
# #     class Config:
# #         from_attributes = True

# # class LoginRequest(BaseModel):
# #     email: EmailStr
# #     password: str

# # # ✅ UPDATE SignupRequest to include phone and company
# # class SignupRequest(BaseModel):
# #     full_name: str
# #     email: EmailStr
# #     password: str
# #     phone: Optional[str] = ""      # ✅ Add this
# #     company: Optional[str] = ""     # ✅ Add this

# # class AuthResponse(BaseModel):
# #     user: UserResponse
# #     workspace: WorkspaceResponse
# #     access_token: str
# #     refresh_token: str

# # class RefreshTokenRequest(BaseModel):
# #     refresh_token: str

# # class TokenResponse(BaseModel):
# #     access_token: str
# #     refresh_token: str
# #     token_type: str = "bearer"

# # class ForgotPasswordRequest(BaseModel):
# #     email: EmailStr

# # class ResetPasswordRequest(BaseModel):
# #     token: str
# #     new_password: str




# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from datetime import datetime


# class UserResponse(BaseModel):

#     id: int

#     email: EmailStr

#     full_name: str

#     role: str

#     is_active: bool

#     workspace_id: int

#     created_at: datetime

#     phone: Optional[str] = ""

#     company: Optional[str] = ""

#     job_title: Optional[str] = ""

#     timezone: Optional[str] = "Asia/Kolkata"

#     language: Optional[str] = "English"

#     bio: Optional[str] = ""

#     avatar: Optional[str] = None

#     class Config:

#         from_attributes = True


# class WorkspaceResponse(BaseModel):

#     id: int

#     name: str

#     slug: str

#     plan: str

#     class Config:

#         from_attributes = True


# class LoginRequest(BaseModel):

#     email: EmailStr

#     password: str


# # =====================================================
# # UPDATED SIGNUP
# # =====================================================

# class SignupRequest(BaseModel):

#     full_name: str

#     email: EmailStr

#     phone: Optional[str] = ""

#     company: Optional[str] = ""


# class AuthResponse(BaseModel):

#     user: UserResponse

#     workspace: WorkspaceResponse

#     access_token: str

#     refresh_token: str


# class RefreshTokenRequest(BaseModel):

#     refresh_token: str


# class TokenResponse(BaseModel):

#     access_token: str

#     refresh_token: str

#     token_type: str = "bearer"


# class ForgotPasswordRequest(BaseModel):

#     email: EmailStr


# class ResetPasswordRequest(BaseModel):

#     token: str

#     new_password: str



from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# =====================================================
# USER RESPONSE
# =====================================================

class UserResponse(BaseModel):

    id: int
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    workspace_id: int
    created_at: datetime

    phone: Optional[str] = ""
    company: Optional[str] = ""
    job_title: Optional[str] = ""
    timezone: Optional[str] = "Asia/Kolkata"
    language: Optional[str] = "English"
    bio: Optional[str] = ""
    avatar: Optional[str] = None

    class Config:
        from_attributes = True


# =====================================================
# WORKSPACE RESPONSE
# =====================================================

class WorkspaceResponse(BaseModel):

    id: int
    name: str
    slug: str
    plan: str

    class Config:
        from_attributes = True


# =====================================================
# LOGIN REQUEST
# =====================================================

class LoginRequest(BaseModel):

    email: EmailStr
    password: str


# =====================================================
# SIGNUP REQUEST
# =====================================================

class SignupRequest(BaseModel):

    full_name: str
    email: EmailStr

    phone: Optional[str] = ""

    company: Optional[str] = ""


# =====================================================
# AUTH RESPONSE
# =====================================================

class AuthResponse(BaseModel):

    user: UserResponse

    workspace: WorkspaceResponse

    access_token: str

    refresh_token: str


# =====================================================
# REFRESH TOKEN REQUEST
# =====================================================

class RefreshTokenRequest(BaseModel):

    refresh_token: str


# =====================================================
# TOKEN RESPONSE
# =====================================================

class TokenResponse(BaseModel):

    access_token: str

    refresh_token: str

    token_type: str = "bearer"


# =====================================================
# FORGOT PASSWORD
# =====================================================

class ForgotPasswordRequest(BaseModel):

    email: EmailStr


# =====================================================
# RESET PASSWORD
# =====================================================

class ResetPasswordRequest(BaseModel):

    token: str

    new_password: str
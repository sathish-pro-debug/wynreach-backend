# =====================================================
# app/schemas/notification.py
# =====================================================

from pydantic import BaseModel


# =====================================================
# RESPONSE
# =====================================================

class NotificationPreferenceResponse(BaseModel):

    id: int

    notification_type: str

    in_app: bool

    email: bool

    class Config:
        from_attributes = True


# =====================================================
# UPDATE
# =====================================================

class NotificationPreferenceUpdate(BaseModel):

    in_app: bool

    email: bool
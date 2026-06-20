from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime

# Reuse your existing ContactResponse if you have one, or define a minimal one here
class ContactSimpleResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Optional[str]
    status: str

    class Config:
        from_attributes = True

class ListBase(BaseModel):
    name: str
    description: Optional[str] = None

class ListCreate(ListBase):
    pass

class ListUpdate(ListBase):
    name: Optional[str] = None

class ListResponse(ListBase):
    id: int
    is_archived: bool
    archived_at: Optional[datetime]
    contact_count: int          # computed
    email_eligible: int         # computed
    wa_eligible: int            # computed
    campaigns: int              # optional, default 0
    last_updated: datetime
    contacts: List[ContactSimpleResponse] = []

    class Config:
        from_attributes = True

class AddContactRequest(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
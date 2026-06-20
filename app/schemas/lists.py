from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class ContactBase(BaseModel):

    name: str
    email: EmailStr
    phone: Optional[str] = None
    status: Optional[str] = "active"


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):

    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ListBase(BaseModel):

    list_name: str
    description: Optional[str] = None


class ListCreate(ListBase):

    is_archived: Optional[bool] = False


class ListUpdate(BaseModel):

    list_name: Optional[str] = None
    description: Optional[str] = None


class ListResponse(ListBase):

    id: int

    contact_count: int

    email_eligible: int

    wa_eligible: int

    campaigns: int

    is_archived: bool

    archived_at: Optional[datetime]

    created_at: datetime

    updated_at: Optional[datetime]

    contacts: List[ContactResponse] = []

    class Config:
        from_attributes = True
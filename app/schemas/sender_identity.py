from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class EmailDomainCreate(BaseModel):
    domain: str = Field(..., example="mycompany.com")
    sender_name: str = Field(..., example="My Company")
    email_address: EmailStr = Field(..., example="hello@mycompany.com")

class EmailDomainResponse(BaseModel):
    id: str
    domain: str
    sender_name: str
    from_email: str
    reply_to_email: Optional[str]
    dkim_status: str
    spf_status: str
    is_default: bool
    created_at: datetime

class DNSRecordResponse(BaseModel):
    type: str
    name: str
    value: str
    description: str

class WhatsAppCreate(BaseModel):
    phone_number: str = Field(..., example="+919840012345")
    account_name: str = Field(..., example="My Business")

class WhatsAppResponse(BaseModel):
    id: str
    phone_number: str
    account_name: str
    status: str
    templates_count: int
    created_at: datetime

class VerifyDomainRequest(BaseModel):
    domain_id: str

class SetDefaultDomainRequest(BaseModel):
    domain_id: str
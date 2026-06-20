from pydantic import BaseModel, EmailStr


class TestEmailRequest(BaseModel):
    email: EmailStr
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ButtonSchema(BaseModel):
    label: str
    action: str

class FAQSchema(BaseModel):
    question: str
    answer: str

class ChatbotBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: Optional[str] = "active"
    welcome_message: str = "Hi! Welcome to our service. How can I help you today?"
    buttons: List[ButtonSchema] = []
    faqs: List[FAQSchema] = []

class ChatbotCreate(ChatbotBase):
    pass

class ChatbotUpdate(ChatbotBase):
    name: Optional[str] = None
    status: Optional[str] = None
    welcome_message: Optional[str] = None

class ChatbotResponse(ChatbotBase):
    id: int
    conversations: int
    satisfaction: float
    responses: int
    last_active: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True   # ✅ Pydantic v2

class ChatRequest(BaseModel):
    message: str
    chatbot_id: int

class ChatResponse(BaseModel):
    reply: str
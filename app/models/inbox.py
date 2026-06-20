from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
)
from sqlalchemy.sql import func
from app.database import Base


class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    contact_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    last_message = Column(Text, nullable=True)
    status = Column(String, default="unread")
    tag = Column(String, nullable=True)
    assigned_agent = Column(String, nullable=True)
    is_closed = Column(Boolean, default=False)
    template_messages = Column(Integer, default=0)
    session_messages = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    from_type = Column(String, nullable=False)
    text = Column(Text, nullable=True)
    msg_type = Column(String, default="text")
    content = Column(JSON, nullable=True)
    wamid = Column(String, nullable=True)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

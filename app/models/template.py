from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON
from sqlalchemy.sql import func
from app.database import LogBase

class Template(LogBase):
    __tablename__ = "templates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)
    category = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    content = Column(Text, nullable=False)
    variables = Column(JSON, nullable=True)
    status = Column(String, default="active")
    meta_approved = Column(Boolean, default=False)
    times_used = Column(Integer, default=0)
    created_by = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

from sqlalchemy import Column, String, Integer, Float, Boolean
from app.database import Base

class Tenant(Base):

    __tablename__ = "tenants"

    id = Column(String, primary_key=True)

    name = Column(String)

    domain = Column(String)

    sending_enabled = Column(Boolean, default=True)

    total_sent = Column(Integer, default=0)

    total_bounces = Column(Integer, default=0)

    total_complaints = Column(Integer, default=0)

    reputation_score = Column(Float, default=100)
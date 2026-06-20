from pydantic import BaseModel
from typing import Optional, Union
from datetime import datetime
from uuid import UUID


class CampaignCreate(BaseModel):
    campaign_name: str
    channel: str
    goal_label: Optional[str] = None


class CampaignResponse(BaseModel):
    id: Union[int, str, UUID]
    campaign_name: str
    channel: str
    goal_label: Optional[str]
    status: str
    created_at: datetime
    estimated_recipients: Optional[int] = 0

    class Config:
        from_attributes = True

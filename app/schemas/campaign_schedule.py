from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CampaignScheduleUpdate(BaseModel):
    send_mode: str
    scheduled_at: Optional[datetime] = None
    timezone: Optional[str] = None
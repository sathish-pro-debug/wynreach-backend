from pydantic import BaseModel
from typing import Optional


class CampaignContentUpdate(BaseModel):
    subject_line: Optional[str] = None
    preview_text: Optional[str] = None
    template_id: str
    sender_identity_id: str
from pydantic import BaseModel
from typing import List


class CampaignAudienceUpdate(BaseModel):

    audience_list_ids: List[str]

    exclude_list_ids: List[str] = []

    estimated_recipients: int = 0

    suppressed_count: int = 0
from pydantic import BaseModel


class CampaignFinalize(BaseModel):
    status: str
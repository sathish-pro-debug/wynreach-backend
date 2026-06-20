from typing import Optional
from fastapi import Query

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_log_db, get_main_db

from app.schemas.campaign import (
    CampaignCreate,
    CampaignResponse
)

from app.services.campaign_service import create_campaign

from app.schemas.campaign_content import CampaignContentUpdate
from app.services.campaign_service import update_campaign_content

from app.schemas.campaign_schedule import CampaignScheduleUpdate

from app.services.campaign_service import update_campaign_schedule

from app.schemas.campaign_finalize import CampaignFinalize
from app.services.campaign_service import finalize_campaign

from app.schemas.campaign_test_email import TestEmailRequest
from app.services.campaign_service import send_test_email

from app.services.campaign_service import get_all_campaigns
from app.services.campaign_service import update_campaign
from app.services.campaign_service import get_campaign_logs

from app.services.campaign_service import duplicate_campaign
from app.schemas.campaign_audience import (
    CampaignAudienceUpdate
)
from app.services.campaign_service import (
    update_campaign_audience
)

router = APIRouter()


@router.post("/", response_model=CampaignResponse)
def create_new_campaign(
    campaign: CampaignCreate,
    db: Session = Depends(get_main_db)
):
    return create_campaign(db, campaign)

@router.put("/{campaign_id}/audience")
def update_campaign_step2(
    campaign_id: str,
    audience: CampaignAudienceUpdate,
    db: Session = Depends(get_main_db)
):
    return update_campaign_audience(
        db,
        campaign_id,
        audience
    )
@router.put("/{campaign_id}")
def update_existing_campaign(
    campaign_id: str,
    campaign: CampaignCreate,
    db: Session = Depends(get_main_db)
):
    return update_campaign(
        db,
        campaign_id,
        campaign
    )

@router.put("/{campaign_id}/content")
def update_campaign_step3(
    campaign_id: str,
    content: CampaignContentUpdate,
    db: Session = Depends(get_main_db)
):
    return update_campaign_content(
        db,
        campaign_id,
        content
    )

@router.put("/{campaign_id}/schedule")
def update_campaign_step4(
    campaign_id: str,
    schedule: CampaignScheduleUpdate,
    db: Session = Depends(get_main_db)
):
    return update_campaign_schedule(
        db,
        campaign_id,
        schedule
    )

@router.put("/{campaign_id}/finalize")
async def finalize_campaign_step5(
    campaign_id: str,
    finalize: CampaignFinalize,
    db: Session = Depends(get_main_db),
    log_db: Session = Depends(get_log_db)
):
    return await finalize_campaign(
        db,
        log_db,
        campaign_id,
        finalize
    )

@router.post("/{campaign_id}/test-email")
async def send_campaign_test_email(
    campaign_id: str,
    email: TestEmailRequest,
    db: Session = Depends(get_main_db),
    log_db: Session = Depends(get_log_db)
):
    return await send_test_email(
        db,
        log_db,
        campaign_id,
        email
    )

# app/routers/campaigns.py - Update the GET endpoint
@router.get("/")
def get_campaigns(
    status: Optional[str] = Query(None, description="Filter by campaign status"),
    db: Session = Depends(get_main_db)
):
    from app.models.campaign import Campaign

    normalized_status = status.lower() if status else None

    query = db.query(
        Campaign.id,
        Campaign.campaign_name,
        Campaign.channel,
        Campaign.status,
        Campaign.estimated_recipients,
        Campaign.scheduled_at,
        Campaign.created_at,
        Campaign.total_sent,
        Campaign.total_opened,
        Campaign.total_clicked,
        Campaign.open_rate,
        Campaign.click_rate,
    )

    if normalized_status:
        query = query.filter(Campaign.status == normalized_status)

    if normalized_status == 'sent':
        query = query.filter(Campaign.sent_at.isnot(None))

    result = query.order_by(Campaign.created_at.desc()).all()

    return [
        {
            "id": row.id,
            "campaign_name": row.campaign_name,
            "channel": row.channel,
            "status": row.status,
            "estimated_recipients": row.estimated_recipients,
            "scheduled_at": row.scheduled_at.isoformat() if row.scheduled_at else None,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "total_sent": row.total_sent,
            "total_opened": row.total_opened,
            "total_clicked": row.total_clicked,
            "open_rate": row.open_rate,
            "click_rate": row.click_rate,
        }
        for row in result
    ]


@router.get("/{campaign_id}/logs")
def get_campaign_logs_route(
    campaign_id: str,
    page: int = Query(1, ge=1, description="Page number for logs"),
    per_page: int = Query(50, ge=1, le=500, description="Logs per page"),
    since_id: Optional[int] = Query(None, description="Only logs with id > since_id"),
    db: Session = Depends(get_main_db),
    log_db: Session = Depends(get_log_db)
):
    print(f"Campaign Logs API Called: {campaign_id}")
    return get_campaign_logs(db, log_db, campaign_id, page=page, per_page=per_page, since_id=since_id)

@router.get("/{campaign_id}/analytics")
def get_campaign_analytics(
    campaign_id: str,
    db: Session = Depends(get_main_db)
):
    from sqlalchemy import func

    from app.models.campaign import Campaign
    from app.models.email_event import EmailEvent

    campaign = db.query(Campaign).filter(Campaign.id == campaign_id).first()
    if not campaign:
        return {
            "sent": 0,
            "delivered": 0,
            "opened": 0,
            "clicked": 0,
            "bounced": 0,
            "failed": 0,
            "complained": 0,
            "delivery_rate": 0,
            "open_rate": 0,
            "click_rate": 0,
            "bounce_rate": 0,
            "complaint_rate": 0,
        }

    rows = (
        db.query(func.upper(EmailEvent.event_type), func.count(EmailEvent.id))
        .filter(EmailEvent.campaign_id == campaign_id)
        .group_by(func.upper(EmailEvent.event_type))
        .all()
    )
    counts = {event_type: count for event_type, count in rows}

    sent = counts.get("SENT", 0) or getattr(campaign, "total_sent", 0) or 0
    delivered = counts.get("DELIVERED", 0) or getattr(campaign, "total_delivered", 0) or 0
    opened = counts.get("OPENED", 0) or getattr(campaign, "total_opened", 0) or 0
    clicked = counts.get("CLICKED", 0) or getattr(campaign, "total_clicked", 0) or 0
    bounced = counts.get("BOUNCED", 0) or getattr(campaign, "total_bounced", 0) or 0
    failed = counts.get("FAILED", 0) or getattr(campaign, "total_failed", 0) or 0
    complained = counts.get("COMPLAINED", 0) or getattr(campaign, "total_complained", 0) or 0

    return {
        "sent": sent,
        "delivered": delivered,
        "opened": opened,
        "clicked": clicked,
        "bounced": bounced,
        "failed": failed,
        "complained": complained,
        "delivery_rate": round((delivered / sent * 100) if sent else 0, 2),
        "open_rate": round((opened / sent * 100) if sent else 0, 2),
        "click_rate": round((clicked / sent * 100) if sent else 0, 2),
        "bounce_rate": round((bounced / sent * 100) if sent else 0, 2),
        "complaint_rate": round((complained / sent * 100) if sent else 0, 2),
    }

@router.get("/{campaign_id}")
def get_campaign(
    campaign_id: str,
    db: Session = Depends(get_main_db)
):
    from app.services.campaign_service import get_campaign_by_id

    return get_campaign_by_id(
        db,
        campaign_id
    )

@router.post("/{campaign_id}/duplicate")
def duplicate_campaign_route(
    campaign_id: str,
    db: Session = Depends(get_main_db)
):
    return duplicate_campaign(db, campaign_id)

@router.get("/all")
def get_all_campaigns_simple(
    db: Session = Depends(get_main_db)
):
    """Simple endpoint to get all campaigns without filters"""
    from app.models.campaign import Campaign
    
    campaigns = db.query(Campaign).order_by(Campaign.created_at.desc()).all()
    
    # Convert to list of dicts with simple fields for automation
    result = []
    for campaign in campaigns:
        result.append({
            "id": campaign.id,
            "campaign_name": campaign.campaign_name,
            "channel": campaign.channel,
            "status": campaign.status,
            "sent_at": campaign.sent_at.isoformat() if campaign.sent_at else None,
            "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
        })
    
    return result

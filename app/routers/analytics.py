# # # from fastapi import APIRouter, Depends
# # # from sqlalchemy.orm import Session
# # # from datetime import datetime, timedelta

# # # from app.database import get_main_db
# # # from app.models.campaign import Campaign
# # # from app.routers.auth import get_current_user
# # # from app.models.user import User

# # # router = APIRouter()


# # # @router.get("/overview")
# # # def get_analytics_overview(
# # #     period: str = "30",
# # #     current_user: User = Depends(get_current_user),
# # #     db: Session = Depends(get_main_db)
# # # ):
# # #     campaigns = db.query(Campaign).filter(
# # #         Campaign.status == "sent"
# # #     ).all()

# # #     total_sent = sum(c.total_sent or c.credits_used or 0 for c in campaigns)
# # #     total_delivered = sum(c.total_delivered or 0 for c in campaigns)
# # #     total_opened = sum(c.total_opened or 0 for c in campaigns)
# # #     total_clicked = sum(c.total_clicked or 0 for c in campaigns)
# # #     total_bounced = sum(c.total_bounced or 0 for c in campaigns)
# # #     total_unsubscribed = sum(c.total_unsubscribed or 0 for c in campaigns)

# # #     email_campaigns = [c for c in campaigns if c.channel == "email"]
# # #     whatsapp_campaigns = [c for c in campaigns if c.channel == "whatsapp"]

# # #     email_sent = sum(c.total_sent or c.credits_used or 0 for c in email_campaigns)
# # #     whatsapp_sent = sum(c.total_sent or c.credits_used or 0 for c in whatsapp_campaigns)

# # #     avg_delivery_rate = round((total_delivered / total_sent * 100) if total_sent > 0 else 0, 1)
# # #     avg_open_rate = round((total_opened / total_sent * 100) if total_sent > 0 else 0, 1)
# # #     avg_click_rate = round((total_clicked / total_sent * 100) if total_sent > 0 else 0, 1)

# # #     return {
# # #         "totalSent": total_sent,
# # #         "totalSentDelta": 0,
# # #         "avgDeliveryRate": avg_delivery_rate,
# # #         "avgDeliveryRateDelta": 0,
# # #         "avgOpenRate": avg_open_rate,
# # #         "avgOpenRateDelta": 0,
# # #         "avgClickRate": avg_click_rate,
# # #         "avgClickRateDelta": 0,
# # #         "emailSent": email_sent,
# # #         "whatsappSent": whatsapp_sent,
# # #         "emailAvgOpenRate": avg_open_rate,
# # #         "whatsappAvgReadRate": 0,
# # #         "whatsappAvgCtr": 0,
# # #         "hardBounces": total_bounced,
# # #         "unsubscribes": total_unsubscribed,
# # #     }


# # # @router.get("/campaigns")
# # # def get_analytics_campaigns(
# # #     period: str = "30",
# # #     current_user: User = Depends(get_current_user),
# # #     db: Session = Depends(get_main_db)
# # # ):
# # #     campaigns = db.query(Campaign).filter(
# # #         Campaign.status == "sent"
# # #     ).order_by(Campaign.created_at.desc()).all()

# # #     result = []
# # #     for c in campaigns:
# # #         sent = c.total_sent or c.credits_used or 0
# # #         delivered = c.total_delivered or 0
# # #         opened = c.total_opened or 0
# # #         clicked = c.total_clicked or 0
# # #         bounced = c.total_bounced or 0
# # #         unsubs = c.total_unsubscribed or 0

# # #         result.append({
# # #             "id": c.id,
# # #             "campaignName": c.campaign_name,
# # #             "channel": c.channel,
# # #             "sent": sent,
# # #             "delivered": delivered,
# # #             "deliveryRate": round((delivered / sent * 100) if sent > 0 else 0, 1),
# # #             "openRate": round((opened / sent * 100) if sent > 0 else 0, 1),
# # #             "ctr": round((clicked / sent * 100) if sent > 0 else 0, 1),
# # #             "bounce": round((bounced / sent * 100) if sent > 0 else 0, 1),
# # #             "unsubs": round((unsubs / sent * 100) if sent > 0 else 0, 1),
# # #             "date": c.sent_at.strftime("%Y-%m-%d") if c.sent_at else "",
# # #         })

# # #     return result




# # from fastapi import APIRouter, Depends
# # from sqlalchemy.orm import Session

# # from app.database import get_main_db
# # from app.models.campaign import Campaign

# # router = APIRouter()


# # @router.get("/overview")
# # def get_analytics_overview(
# #     period: str = "30",
# #     db: Session = Depends(get_main_db)
# # ):

# #     campaigns = db.query(Campaign).all()

# #     total_sent = sum(
# #         (c.total_sent or c.credits_used or 0)
# #         for c in campaigns
# #     )

# #     total_delivered = sum(
# #         (c.total_delivered or 0)
# #         for c in campaigns
# #     )

# #     total_opened = sum(
# #         (c.total_opened or 0)
# #         for c in campaigns
# #     )

# #     total_clicked = sum(
# #         (c.total_clicked or 0)
# #         for c in campaigns
# #     )

# #     return {
# #         "totalSent": total_sent,
# #         "avgDeliveryRate": round(
# #             (total_delivered / total_sent * 100)
# #             if total_sent else 0,
# #             1
# #         ),
# #         "avgOpenRate": round(
# #             (total_opened / total_sent * 100)
# #             if total_sent else 0,
# #             1
# #         ),
# #         "avgClickRate": round(
# #             (total_clicked / total_sent * 100)
# #             if total_sent else 0,
# #             1
# #         ),
# #         "emailSent": total_sent,
# #         "whatsappSent": 0,
# #         "campaignCount": len(campaigns)
# #     }


# # @router.get("/campaigns")
# # def get_analytics_campaigns(
# #     period: str = "30",
# #     db: Session = Depends(get_main_db)
# # ):

# #     campaigns = (
# #         db.query(Campaign)
# #         .order_by(Campaign.created_at.desc())
# #         .all()
# #     )

# #     result = []

# #     for c in campaigns:

# #         sent = c.total_sent or c.credits_used or 0
# #         delivered = c.total_delivered or 0
# #         opened = c.total_opened or 0
# #         clicked = c.total_clicked or 0

# #         result.append({
# #             "id": c.id,
# #             "campaignName": c.campaign_name,
# #             "channel": c.channel,
# #             "status": c.status,
# #             "sent": sent,
# #             "delivered": delivered,
# #             "deliveryRate": round(
# #                 (delivered / sent * 100)
# #                 if sent else 0,
# #                 1
# #             ),
# #             "openRate": round(
# #                 (opened / sent * 100)
# #                 if sent else 0,
# #                 1
# #             ),
# #             "ctr": round(
# #                 (clicked / sent * 100)
# #                 if sent else 0,
# #                 1
# #             ),
# #             "date": (
# #                 c.sent_at.strftime("%Y-%m-%d")
# #                 if c.sent_at
# #                 else ""
# #             )
# #         })

# #     return result

    

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from app.database import get_main_db
# from app.models.campaign import Campaign

# router = APIRouter()


# # =====================================================
# # ANALYTICS OVERVIEW
# # =====================================================

# @router.get("/overview")
# def get_analytics_overview(
#     period: str = "30",
#     db: Session = Depends(get_main_db)
# ):

#     campaigns = db.query(Campaign).all()

#     total_sent = sum(
#         (getattr(c, "total_sent", 0) or getattr(c, "credits_used", 0) or 0)
#         for c in campaigns
#     )

#     total_delivered = sum(
#         (getattr(c, "total_delivered", 0) or 0)
#         for c in campaigns
#     )

#     total_opened = sum(
#         (getattr(c, "total_opened", 0) or 0)
#         for c in campaigns
#     )

#     total_clicked = sum(
#         (getattr(c, "total_clicked", 0) or 0)
#         for c in campaigns
#     )

#     avg_delivery_rate = round(
#         (total_delivered / total_sent * 100)
#         if total_sent > 0 else 0,
#         1
#     )

#     avg_open_rate = round(
#         (total_opened / total_sent * 100)
#         if total_sent > 0 else 0,
#         1
#     )

#     avg_click_rate = round(
#         (total_clicked / total_sent * 100)
#         if total_sent > 0 else 0,
#         1
#     )

#     return {
#         "totalSent": total_sent,
#         "avgDeliveryRate": avg_delivery_rate,
#         "avgOpenRate": avg_open_rate,
#         "avgClickRate": avg_click_rate,
#         "campaignCount": len(campaigns),
#     }


# # =====================================================
# # ANALYTICS CAMPAIGNS
# # =====================================================

# @router.get("/campaigns")
# def get_analytics_campaigns(
#     period: str = "30",
#     db: Session = Depends(get_main_db)
# ):

#     campaigns = (
#         db.query(Campaign)
#         .order_by(Campaign.id.desc())
#         .all()
#     )

#     result = []

#     for c in campaigns:

#         sent = (
#             getattr(c, "total_sent", 0)
#             or getattr(c, "credits_used", 0)
#             or 0
#         )

#         delivered = getattr(c, "total_delivered", 0) or 0
#         opened = getattr(c, "total_opened", 0) or 0
#         clicked = getattr(c, "total_clicked", 0) or 0

#         result.append({
#             "id": c.id,
#             "campaignName": getattr(c, "campaign_name", ""),
#             "channel": getattr(c, "channel", ""),
#             "status": getattr(c, "status", ""),
#             "sent": sent,
#             "delivered": delivered,
#             "deliveryRate": round(
#                 (delivered / sent * 100)
#                 if sent > 0 else 0,
#                 1
#             ),
#             "openRate": round(
#                 (opened / sent * 100)
#                 if sent > 0 else 0,
#                 1
#             ),
#             "ctr": round(
#                 (clicked / sent * 100)
#                 if sent > 0 else 0,
#                 1
#             ),
#         })

#     return result



from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_main_db
from app.models.campaign import Campaign

router = APIRouter()


# =====================================================
# ANALYTICS OVERVIEW
# =====================================================

@router.get("/overview")
def get_analytics_overview(
    period: str = "30",
    db: Session = Depends(get_main_db)
):

    campaigns = db.query(Campaign).all()

    total_sent = sum(
        (
            getattr(c, "total_sent", 0)
            or getattr(c, "credits_used", 0)
            or 0
        )
        for c in campaigns
    )

    total_delivered = sum(
        getattr(c, "total_delivered", 0) or 0
        for c in campaigns
    )

    total_opened = sum(
        getattr(c, "total_opened", 0) or 0
        for c in campaigns
    )

    total_clicked = sum(
        getattr(c, "total_clicked", 0) or 0
        for c in campaigns
    )

    total_bounced = sum(
        getattr(c, "total_bounced", 0) or 0
        for c in campaigns
    )

    total_failed = sum(
        getattr(c, "total_failed", 0) or 0
        for c in campaigns
    )

    total_complained = sum(
        getattr(c, "total_complained", 0) or 0
        for c in campaigns
    )

    total_unsubscribed = sum(
        getattr(c, "total_unsubscribed", 0) or 0
        for c in campaigns
    )

    avg_delivery_rate = round(
        (total_delivered / total_sent * 100)
        if total_sent > 0 else 0,
        1
    )

    avg_open_rate = round(
        (total_opened / total_sent * 100)
        if total_sent > 0 else 0,
        1
    )

    avg_click_rate = round(
        (total_clicked / total_sent * 100)
        if total_sent > 0 else 0,
        1
    )

    email_campaigns = [
        c for c in campaigns
        if getattr(c, "channel", "").lower() == "email"
    ]

    whatsapp_campaigns = [
        c for c in campaigns
        if getattr(c, "channel", "").lower() == "whatsapp"
    ]

    email_sent = sum(
        (
            getattr(c, "total_sent", 0)
            or getattr(c, "credits_used", 0)
            or 0
        )
        for c in email_campaigns
    )

    whatsapp_sent = sum(
        (
            getattr(c, "total_sent", 0)
            or getattr(c, "credits_used", 0)
            or 0
        )
        for c in whatsapp_campaigns
    )

    return {
        "totalSent": total_sent,
        "avgDeliveryRate": avg_delivery_rate,
        "avgOpenRate": avg_open_rate,
        "avgClickRate": avg_click_rate,
        "campaignCount": len(campaigns),
        "emailSent": email_sent,
        "whatsappSent": whatsapp_sent,
        "hardBounces": total_bounced,
        "failed": total_failed,
        "complaints": total_complained,
        "unsubscribes": total_unsubscribed,
    }


# =====================================================
# ANALYTICS CAMPAIGNS
# =====================================================

@router.get("/campaigns")
def get_analytics_campaigns(
    page: int = 1,
    limit: int = 15,
    period: str = "30",
    db: Session = Depends(get_main_db)
):

    query = db.query(Campaign)

    total = query.count()

    campaigns = (
        query
        .order_by(Campaign.created_at.asc())   # oldest first, latest at bottom
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    result = []

    for c in campaigns:

        sent = (
            getattr(c, "total_sent", 0)
            or getattr(c, "credits_used", 0)
            or 0
        )

        delivered = (
            getattr(c, "total_delivered", 0)
            or 0
        )

        opened = (
            getattr(c, "total_opened", 0)
            or 0
        )

        clicked = (
            getattr(c, "total_clicked", 0)
            or 0
        )

        bounced_count = (
            getattr(c, "total_bounced", 0)
            or 0
        )

        failed = (
            getattr(c, "total_failed", 0)
            or 0
        )

        complained = (
            getattr(c, "total_complained", 0)
            or 0
        )

        bounce = (
            getattr(c, "bounce_rate", 0)
            or 0
        )

        unsubs = (
            getattr(c, "unsubscribe_rate", 0)
            or 0
        )

        result.append({
            "id": c.id,

            "campaignName":
                getattr(c, "campaign_name", ""),

            "channel":
                getattr(c, "channel", ""),

            "status":
                getattr(c, "status", ""),

            "sent":
                sent,

            "delivered":
                delivered,

            "deliveryRate":
                round(
                    (delivered / sent * 100)
                    if sent > 0 else 0,
                    1
                ),

            "openRate":
                round(
                    (opened / sent * 100)
                    if sent > 0 else 0,
                    1
                ),

            "ctr":
                round(
                    (clicked / sent * 100)
                    if sent > 0 else 0,
                    1
                ),

            "opened":
                opened,

            "clicked":
                clicked,

            "bounced":
                bounced_count,

            "failed":
                failed,

            "complained":
                complained,

            "bounce":
                bounce,

            "unsubs":
                unsubs,

            "date":
                (
                    c.created_at.strftime("%d-%m-%Y")
                    if getattr(c, "created_at", None)
                    else ""
                ),
        })

    return {
        "data": result,
        "page": page,
        "limit": limit,
        "total": total,
        "totalPages": (
            (total + limit - 1) // limit
        )
    }

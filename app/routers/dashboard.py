# # # # from fastapi import APIRouter, Depends
# # # # from sqlalchemy.orm import Session
# # # # from sqlalchemy import func

# # # # from app.database import get_main_db
# # # # from app.models.campaign import Campaign

# # # # router = APIRouter(
# # # #     prefix="/dashboard",
# # # #     tags=["Dashboard"]
# # # # )


# # # # @router.get("/overview")
# # # # def get_dashboard_overview(
# # # #     db: Session = Depends(get_main_db)
# # # # ):

# # # #     # TOTAL CAMPAIGNS
# # # #     total_campaigns = (
# # # #         db.query(func.count(Campaign.id))
# # # #         .scalar()
# # # #     )

# # # #     # ACTIVE CAMPAIGNS
# # # #     active_campaigns = (
# # # #         db.query(func.count(Campaign.id))
# # # #         .filter(
# # # #             func.lower(Campaign.status).in_([
# # # #                 "scheduled",
# # # #                 "sent",
# # # #                 "completed"
# # # #             ])
# # # #         )
# # # #         .scalar()
# # # #     )

# # # #     # SENT CAMPAIGNS
# # # #     sent_campaigns = (
# # # #         db.query(func.count(Campaign.id))
# # # #         .filter(
# # # #             func.lower(Campaign.status) == "sent"
# # # #         )
# # # #         .scalar()
# # # #     )

# # # #     # DRAFT CAMPAIGNS
# # # #     draft_campaigns = (
# # # #         db.query(func.count(Campaign.id))
# # # #         .filter(
# # # #             func.lower(Campaign.status) == "draft"
# # # #         )
# # # #         .scalar()
# # # #     )

# # # #     # RECENT CAMPAIGNS
# # # #     campaigns = (
# # # #         db.query(Campaign)
# # # #         .order_by(Campaign.created_at.desc())
# # # #         .limit(5)
# # # #         .all()
# # # #     )

# # # #     active_campaign_list = []

# # # #     for campaign in campaigns:

# # # #         active_campaign_list.append({

# # # #             "id": campaign.id,

# # # #             "campaignName": campaign.campaign_name,

# # # #             "channel": campaign.channel,

# # # #             "status": campaign.status,

# # # #             "totalRecipients": (
# # # #                 campaign.estimated_recipients or 0
# # # #             ),

# # # #             "openRate": (
# # # #                 campaign.open_rate or 0
# # # #             ),

# # # #             "createdAt": campaign.created_at
# # # #         })

# # # #     recent_activity = []

# # # #     for campaign in campaigns:

# # # #         recent_activity.append({

# # # #             "icon": (
# # # #                 "✉️"
# # # #                 if campaign.channel == "email"
# # # #                 else "💬"
# # # #             ),

# # # #             "bg": (
# # # #                 "bg-violet-50"
# # # #                 if campaign.channel == "email"
# # # #                 else "bg-emerald-50"
# # # #             ),

# # # #             "message": (
# # # #                 f"{campaign.campaign_name} "
# # # #                 f"({campaign.status})"
# # # #             ),

# # # #             "time": "Recently"
# # # #         })

# # # #     return {

# # # #         "success": True,

# # # #         "kpis": {

# # # #             "totalCampaigns": total_campaigns,

# # # #             "activeCampaigns": active_campaigns,

# # # #             "sentCampaigns": sent_campaigns,

# # # #             "draftCampaigns": draft_campaigns
# # # #         },

# # # #         "activeCampaigns": active_campaign_list,

# # # #         "recentActivity": recent_activity,

# # # #         "engagement": {

# # # #             "labels": [
# # # #                 "Week 1",
# # # #                 "Week 2",
# # # #                 "Week 3",
# # # #                 "Week 4"
# # # #             ],

# # # #             "sends": [
# # # #                 120,
# # # #                 180,
# # # #                 240,
# # # #                 300
# # # #             ],

# # # #             "opens": [
# # # #                 80,
# # # #                 130,
# # # #                 170,
# # # #                 220
# # # #             ]
# # # #         }
# # # #     }




# # # from fastapi import APIRouter, Depends
# # # from sqlalchemy.orm import Session
# # # from sqlalchemy import (
# # #     func,
# # #     cast,
# # #     String
# # # )

# # # from app.database import get_main_db
# # # from app.models.campaign import Campaign

# # # router = APIRouter(
# # #     prefix="/dashboard",
# # #     tags=["Dashboard"]
# # # )


# # # # =====================================================
# # # # DASHBOARD OVERVIEW
# # # # =====================================================

# # # @router.get("/overview")
# # # def get_dashboard_overview(
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     # =================================================
# # #     # TOTAL CAMPAIGNS
# # #     # =================================================

# # #     total_campaigns = (
# # #         db.query(func.count(Campaign.id))
# # #         .scalar()
# # #     )

# # #     # =================================================
# # #     # ACTIVE CAMPAIGNS
# # #     # =================================================

# # #     active_campaigns = (

# # #         db.query(func.count(Campaign.id))

# # #         .filter(

# # #             func.lower(

# # #                 cast(
# # #                     Campaign.status,
# # #                     String
# # #                 )

# # #             ).in_([

# # #                 "scheduled",
# # #                 "sent",
# # #                 "completed"

# # #             ])

# # #         )

# # #         .scalar()
# # #     )

# # #     # =================================================
# # #     # SENT CAMPAIGNS
# # #     # =================================================

# # #     sent_campaigns = (

# # #         db.query(func.count(Campaign.id))

# # #         .filter(

# # #             func.lower(

# # #                 cast(
# # #                     Campaign.status,
# # #                     String
# # #                 )

# # #             ) == "sent"

# # #         )

# # #         .scalar()
# # #     )

# # #     # =================================================
# # #     # DRAFT CAMPAIGNS
# # #     # =================================================

# # #     draft_campaigns = (

# # #         db.query(func.count(Campaign.id))

# # #         .filter(

# # #             func.lower(

# # #                 cast(
# # #                     Campaign.status,
# # #                     String
# # #                 )

# # #             ) == "draft"

# # #         )

# # #         .scalar()
# # #     )

# # #     # =================================================
# # #     # RECENT CAMPAIGNS
# # #     # =================================================

# # #     campaigns = (

# # #         db.query(Campaign)

# # #         .order_by(
# # #             Campaign.created_at.desc()
# # #         )

# # #         .limit(5)

# # #         .all()
# # #     )

# # #     # =================================================
# # #     # ACTIVE CAMPAIGN LIST
# # #     # =================================================

# # #     active_campaign_list = []

# # #     for campaign in campaigns:

# # #         recipients = (
# # #             campaign.estimated_recipients
# # #             or 0
# # #         )

# # #         open_rate = (
# # #             campaign.open_rate
# # #             or 0
# # #         )

# # #         active_campaign_list.append({

# # #             "id": campaign.id,

# # #             "campaignName": (
# # #                 campaign.campaign_name
# # #             ),

# # #             "channel": (
# # #                 campaign.channel
# # #             ),

# # #             "status": (
# # #                 campaign.status
# # #             ),

# # #             "totalRecipients": (
# # #                 recipients
# # #             ),

# # #             "openRate": (
# # #                 open_rate
# # #             ),

# # #             "createdAt": (
# # #                 campaign.created_at
# # #             )
# # #         })

# # #     # =================================================
# # #     # RECENT ACTIVITY
# # #     # =================================================

# # #     recent_activity = []

# # #     for campaign in campaigns:

# # #         recent_activity.append({

# # #             "icon": (

# # #                 "✉️"

# # #                 if campaign.channel == "email"

# # #                 else "💬"
# # #             ),

# # #             "bg": (

# # #                 "bg-violet-50"

# # #                 if campaign.channel == "email"

# # #                 else "bg-emerald-50"
# # #             ),

# # #             "message": (

# # #                 f"{campaign.campaign_name} "
# # #                 f"({campaign.status})"
# # #             ),

# # #             "time": "Recently"
# # #         })

# # #     # =================================================
# # #     # RESPONSE
# # #     # =================================================

# # #     return {

# # #         "success": True,

# # #         "kpis": {

# # #             "totalCampaigns": (
# # #                 total_campaigns
# # #             ),

# # #             "activeCampaigns": (
# # #                 active_campaigns
# # #             ),

# # #             "sentCampaigns": (
# # #                 sent_campaigns
# # #             ),

# # #             "draftCampaigns": (
# # #                 draft_campaigns
# # #             )
# # #         },

# # #         "activeCampaigns": (
# # #             active_campaign_list
# # #         ),

# # #         "recentActivity": (
# # #             recent_activity
# # #         ),

# # #         "engagement": {

# # #             "labels": [

# # #                 "Week 1",
# # #                 "Week 2",
# # #                 "Week 3",
# # #                 "Week 4"
# # #             ],

# # #             "sends": [

# # #                 120,
# # #                 180,
# # #                 240,
# # #                 300
# # #             ],

# # #             "opens": [

# # #                 80,
# # #                 130,
# # #                 170,
# # #                 220
# # #             ]
# # #         }
# # #     }



# # from fastapi import APIRouter, Depends
# # from sqlalchemy.orm import Session
# # from sqlalchemy import (
# #     func,
# #     cast,
# #     String
# # )

# # from app.database import get_main_db
# # from app.models.campaign import Campaign

# # router = APIRouter(
# #     prefix="/dashboard",
# #     tags=["Dashboard"]
# # )


# # # =====================================================
# # # DASHBOARD OVERVIEW
# # # =====================================================

# # @router.get("/overview")
# # def get_dashboard_overview(
# #     db: Session = Depends(get_main_db)
# # ):

# #     # =================================================
# #     # TOTAL CAMPAIGNS
# #     # =================================================

# #     total_campaigns = (
# #         db.query(func.count(Campaign.id))
# #         .scalar()
# #     )

# #     # =================================================
# #     # ACTIVE CAMPAIGNS
# #     # =================================================

# #     active_campaigns = (

# #         db.query(func.count(Campaign.id))

# #         .filter(

# #             func.lower(

# #                 cast(
# #                     Campaign.status,
# #                     String
# #                 )

# #             ).in_([

# #                 "scheduled",
# #                 "sent",
# #                 "completed"

# #             ])

# #         )

# #         .scalar()
# #     )

# #     # =================================================
# #     # SENT CAMPAIGNS
# #     # =================================================

# #     sent_campaigns = (

# #         db.query(func.count(Campaign.id))

# #         .filter(

# #             func.lower(

# #                 cast(
# #                     Campaign.status,
# #                     String
# #                 )

# #             ) == "sent"

# #         )

# #         .scalar()
# #     )

# #     # =================================================
# #     # DRAFT CAMPAIGNS
# #     # =================================================

# #     draft_campaigns = (

# #         db.query(func.count(Campaign.id))

# #         .filter(

# #             func.lower(

# #                 cast(
# #                     Campaign.status,
# #                     String
# #                 )

# #             ) == "draft"

# #         )

# #         .scalar()
# #     )

# #     # =================================================
# #     # RECENT CAMPAIGNS
# #     # =================================================

# #     campaigns = (

# #         db.query(Campaign)

# #         .order_by(
# #             Campaign.created_at.desc()
# #         )

# #         .limit(5)

# #         .all()
# #     )

# #     # =================================================
# #     # UPCOMING SCHEDULED CAMPAIGNS
# #     # =================================================

# #     scheduled_campaigns = (

# #         db.query(Campaign)

# #         .filter(

# #             func.lower(

# #                 cast(
# #                     Campaign.status,
# #                     String
# #                 )

# #             ) == "scheduled"

# #         )

# #         .order_by(
# #             Campaign.scheduled_at.asc()
# #         )

# #         .limit(5)

# #         .all()
# #     )

# #     # =================================================
# #     # ACTIVE CAMPAIGN LIST
# #     # =================================================

# #     active_campaign_list = []

# #     for campaign in campaigns:

# #         recipients = (
# #             campaign.estimated_recipients
# #             or 0
# #         )

# #         open_rate = (
# #             campaign.open_rate
# #             or 0
# #         )

# #         active_campaign_list.append({

# #             "id": campaign.id,

# #             "campaignName": (
# #                 campaign.campaign_name
# #             ),

# #             "channel": (
# #                 campaign.channel
# #             ),

# #             "status": (
# #                 campaign.status
# #             ),

# #             "totalRecipients": (
# #                 recipients
# #             ),

# #             "openRate": (
# #                 open_rate
# #             ),

# #             "createdAt": (
# #                 campaign.created_at
# #             )
# #         })

# #     # =================================================
# #     # RECENT ACTIVITY
# #     # =================================================

# #     recent_activity = []

# #     for campaign in campaigns:

# #         recent_activity.append({

# #             "icon": (

# #                 "✉️"

# #                 if campaign.channel == "email"

# #                 else "💬"
# #             ),

# #             "bg": (

# #                 "bg-violet-50"

# #                 if campaign.channel == "email"

# #                 else "bg-emerald-50"
# #             ),

# #             "message": (

# #                 f"{campaign.campaign_name} "
# #                 f"({campaign.status})"
# #             ),

# #             "time": "Recently"
# #         })

# #     # =================================================
# #     # UPCOMING SCHEDULE LIST
# #     # =================================================

# #     upcoming_scheduled = []

# #     for campaign in scheduled_campaigns:

# #         upcoming_scheduled.append({

# #             "id": campaign.id,

# #             "campaignName": (
# #                 campaign.campaign_name
# #             ),

# #             "channel": (
# #                 campaign.channel
# #             ),

# #             "recipients": (
# #                 campaign.estimated_recipients or 0
# #             ),

# #             "scheduledAt": (
# #                 campaign.scheduled_at
# #             )
# #         })

# #     # =================================================
# #     # RESPONSE
# #     # =================================================

# #     return {

# #         "success": True,

# #         "kpis": {

# #             "totalCampaigns": (
# #                 total_campaigns
# #             ),

# #             "activeCampaigns": (
# #                 active_campaigns
# #             ),

# #             "sentCampaigns": (
# #                 sent_campaigns
# #             ),

# #             "draftCampaigns": (
# #                 draft_campaigns
# #             )
# #         },

# #         "activeCampaigns": (
# #             active_campaign_list
# #         ),

# #         "recentActivity": (
# #             recent_activity
# #         ),

# #         "upcomingScheduled": (
# #             upcoming_scheduled
# #         ),

# #         "engagement": {

# #             "labels": [

# #                 "Week 1",
# #                 "Week 2",
# #                 "Week 3",
# #                 "Week 4"
# #             ],

# #             "sends": [

# #                 120,
# #                 180,
# #                 240,
# #                 300
# #             ],

# #             "opens": [

# #                 80,
# #                 130,
# #                 170,
# #                 220
# #             ]
# #         }
# #     }




# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from sqlalchemy import func, cast, String

# from app.database import get_main_db
# from app.models.campaign import Campaign

# router = APIRouter(
#     prefix="/dashboard",
#     tags=["Dashboard"]
# )


# @router.get("/overview")
# def get_dashboard_overview(
#     db: Session = Depends(get_main_db)
# ):

#     # ==========================================
#     # KPI COUNTS
#     # ==========================================

#     order_total = (
#         db.query(func.count(Campaign.id))
#         .scalar()
#     )

#     sent_campaigns_count = (
#         db.query(func.count(Campaign.id))
#         .filter(
#             func.lower(
#                 cast(Campaign.status, String)
#             ) == "sent"
#         )
#         .scalar()
#     )

#     scheduled_campaigns_count = (
#         db.query(func.count(Campaign.id))
#         .filter(
#             func.lower(
#                 cast(Campaign.status, String)
#             ) == "scheduled"
#         )
#         .scalar()
#     )

#     draft_campaigns_count = (
#         db.query(func.count(Campaign.id))
#         .filter(
#             func.lower(
#                 cast(Campaign.status, String)
#             ) == "draft"
#         )
#         .scalar()
#     )

#     # ==========================================
#     # LAST 4 SENT CAMPAIGNS
#     # ==========================================

#     sent_campaigns = (
#         db.query(Campaign)
#         .filter(
#             func.lower(
#                 cast(Campaign.status, String)
#             ) == "sent"
#         )
#         .order_by(
#             Campaign.created_at.desc()
#         )
#         .limit(4)
#         .all()
#     )

#     sent_campaigns_preview = []

#     for campaign in sent_campaigns:

#         sent_campaigns_preview.append({

#             "id": campaign.id,

#             "campaignName":
#                 campaign.campaign_name,

#             "channel":
#                 campaign.channel,

#             "status":
#                 campaign.status,

#             "totalRecipients":
#                 campaign.estimated_recipients or 0,

#             "openRate":
#                 campaign.open_rate or 0,

#             "createdAt":
#                 campaign.created_at
#         })

#     # ==========================================
#     # RECENT ACTIVITY
#     # ==========================================

#     recent_campaigns = (
#         db.query(Campaign)
#         .order_by(
#             Campaign.created_at.desc()
#         )
#         .limit(5)
#         .all()
#     )

#     recent_activity = []

#     for campaign in recent_campaigns:

#         recent_activity.append({

#             "icon":
#                 "✉️"
#                 if campaign.channel == "email"
#                 else "💬",

#             "bg":
#                 "bg-violet-50"
#                 if campaign.channel == "email"
#                 else "bg-emerald-50",

#             "message":
#                 f"{campaign.campaign_name} ({campaign.status})",

#             "time":
#                 "Recently"
#         })

#     # ==========================================
#     # UPCOMING SCHEDULED CAMPAIGNS
#     # ==========================================

#     scheduled_campaigns = (
#         db.query(Campaign)
#         .filter(
#             func.lower(
#                 cast(Campaign.status, String)
#             ) == "scheduled"
#         )
#         .order_by(
#             Campaign.scheduled_at.asc()
#         )
#         .limit(5)
#         .all()
#     )

#     upcoming_scheduled = []

#     for campaign in scheduled_campaigns:

#         upcoming_scheduled.append({

#             "id":
#                 campaign.id,

#             "campaignName":
#                 campaign.campaign_name,

#             "channel":
#                 campaign.channel,

#             "recipients":
#                 campaign.estimated_recipients or 0,

#             "scheduledAt":
#                 campaign.scheduled_at
#         })

#     # ==========================================
#     # RESPONSE
#     # ==========================================

#     return {

#         "success": True,

#         "kpis": {

#             "orderTotal":
#                 order_total,

#             "sentCampaigns":
#                 sent_campaigns_count,

#             "scheduledCampaigns":
#                 scheduled_campaigns_count,

#             "draftCampaigns":
#                 draft_campaigns_count
#         },

#         # LAST 4 SENT CAMPAIGNS
#         "sentCampaignsPreview":
#             sent_campaigns_preview,

#         # UPCOMING SCHEDULED
#         "upcomingScheduled":
#             upcoming_scheduled,

#         # RECENT ACTIVITY
#         "recentActivity":
#             recent_activity,

#         # CHART
#         "engagement": {

#             "labels": [
#                 "Week 1",
#                 "Week 2",
#                 "Week 3",
#                 "Week 4"
#             ],

#             "sends": [
#                 120,
#                 180,
#                 240,
#                 300
#             ],

#             "opens": [
#                 80,
#                 130,
#                 170,
#                 220
#             ]
#         }
#     }



from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, cast, String
from datetime import datetime, timedelta

from app.database import get_main_db
from app.models.campaign import Campaign

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get("/overview")
def get_dashboard_overview(
    db: Session = Depends(get_main_db)
):

    # ==========================================
    # KPI COUNTS
    # ==========================================

    order_total = (
        db.query(func.count(Campaign.id))
        .scalar()
    )

    sent_campaigns_count = (
        db.query(func.count(Campaign.id))
        .filter(
            func.lower(
                cast(Campaign.status, String)
            ) == "sent"
        )
        .scalar()
    )

    scheduled_campaigns_count = (
        db.query(func.count(Campaign.id))
        .filter(
            func.lower(
                cast(Campaign.status, String)
            ) == "scheduled"
        )
        .scalar()
    )

    draft_campaigns_count = (
        db.query(func.count(Campaign.id))
        .filter(
            func.lower(
                cast(Campaign.status, String)
            ) == "draft"
        )
        .scalar()
    )

    # ==========================================
    # LAST 4 SENT CAMPAIGNS
    # ==========================================

    sent_campaigns = (
        db.query(Campaign)
        .filter(
            func.lower(
                cast(Campaign.status, String)
            ) == "sent"
        )
        .order_by(
            Campaign.created_at.desc()
        )
        .limit(4)
        .all()
    )

    sent_campaigns_preview = []

    for campaign in sent_campaigns:

        sent_campaigns_preview.append({

            "id": campaign.id,

            "campaignName":
                campaign.campaign_name,

            "channel":
                campaign.channel,

            "status":
                campaign.status,

            "totalRecipients":
                campaign.estimated_recipients or 0,

            "openRate":
                campaign.open_rate or 0,

            "createdAt":
                campaign.created_at
        })

    # ==========================================
    # RECENT ACTIVITY
    # ==========================================

    recent_campaigns = (
        db.query(Campaign)
        .order_by(
            Campaign.created_at.desc()
        )
        .limit(5)
        .all()
    )

    recent_activity = []

    for campaign in recent_campaigns:

        recent_activity.append({

            "icon":
                "✉️"
                if campaign.channel == "email"
                else "💬",

            "bg":
                "bg-violet-50"
                if campaign.channel == "email"
                else "bg-emerald-50",

            "message":
                f"{campaign.campaign_name} ({campaign.status})",

            "time":
                campaign.created_at.strftime("%d %b %Y")
                if campaign.created_at
                else "Recently"
        })

    # ==========================================
    # UPCOMING SCHEDULED CAMPAIGNS
    # ==========================================

    scheduled_campaigns = (
        db.query(Campaign)
        .filter(
            func.lower(
                cast(Campaign.status, String)
            ) == "scheduled"
        )
        .order_by(
            Campaign.scheduled_at.asc()
        )
        .limit(5)
        .all()
    )

    upcoming_scheduled = []

    for campaign in scheduled_campaigns:

        upcoming_scheduled.append({

            "id":
                campaign.id,

            "campaignName":
                campaign.campaign_name,

            "channel":
                campaign.channel,

            "recipients":
                campaign.estimated_recipients or 0,

            "scheduledAt":
                campaign.scheduled_at
        })

    # ==========================================
    # EMAIL VS WHATSAPP TREND (30 DAYS)
    # ==========================================

    labels = []
    email_data = []
    whatsapp_data = []

    start_date = datetime.utcnow().date() - timedelta(days=29)

    trend_rows = (
        db.query(
        func.date(Campaign.created_at).label("day"),
        func.lower(cast(Campaign.channel, String)).label("channel"),
        func.count(Campaign.id).label("count")
    )
    .filter(
        func.lower(cast(Campaign.status, String)) == "sent"
    )
    .filter(
        Campaign.created_at >= start_date
    )
    .group_by(
        func.date(Campaign.created_at),
        func.lower(cast(Campaign.channel, String))
    )
    .all()
    )

    # for i in range(29, -1, -1):

    #     day = datetime.utcnow().date() - timedelta(days=i)

    #     labels.append(
    #         day.strftime("%d %b")
    #     )

    #     email_count = (
    #         db.query(func.count(Campaign.id))
    #         .filter(
    #             func.lower(
    #                 cast(Campaign.status, String)
    #             ) == "sent"
    #         )
    #         .filter(
    #             func.lower(
    #                 cast(Campaign.channel, String)
    #             ) == "email"
    #         )
    #         .filter(
    #             func.date(Campaign.created_at) == day
    #         )
    #         .scalar()
    #     )

    #     whatsapp_count = (
    #         db.query(func.count(Campaign.id))
    #         .filter(
    #             func.lower(
    #                 cast(Campaign.status, String)
    #             ) == "sent"
    #         )
    #         .filter(
    #             func.lower(
    #                 cast(Campaign.channel, String)
    #             ) == "whatsapp"
    #         )
    #         .filter(
    #             func.date(Campaign.created_at) == day
    #         )
    #         .scalar()
    #     )

    #     email_data.append(email_count)
    #     whatsapp_data.append(whatsapp_count)

    # ==========================================
    # RESPONSE
    # ==========================================

    return {

        "success": True,

        "kpis": {

            "orderTotal":
                order_total,

            "sentCampaigns":
                sent_campaigns_count,

            "scheduledCampaigns":
                scheduled_campaigns_count,

            "draftCampaigns":
                draft_campaigns_count
        },

        "sentCampaignsPreview":
            sent_campaigns_preview,

        "upcomingScheduled":
            upcoming_scheduled,

        "recentActivity":
            recent_activity,

        "engagement": {

            "labels":
                labels,

            "email":
                email_data,

            "whatsapp":
                whatsapp_data
        }
    }
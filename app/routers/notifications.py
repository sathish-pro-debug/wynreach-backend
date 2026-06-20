# =====================================================
# app/routers/notifications.py
# =====================================================

from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from datetime import datetime

from app.database import get_main_db

from app.models.notification_preference import (
    NotificationPreference
)

from app.schemas.notification import (
    NotificationPreferenceUpdate
)

router = APIRouter()


# =====================================================
# DEFAULT NOTIFICATIONS
# =====================================================

DEFAULT_NOTIFICATIONS = [

    {
        "notification_type": "campaignSent",
        "in_app": True,
        "email": True
    },

    {
        "notification_type": "approvalRequested",
        "in_app": True,
        "email": True
    },

    {
        "notification_type": "campaignFailed",
        "in_app": True,
        "email": True
    },

    {
        "notification_type": "highBounceAlert",
        "in_app": True,
        "email": True
    },

    {
        "notification_type": "automationError",
        "in_app": True,
        "email": True
    },

    {
        "notification_type": "contactImportDone",
        "in_app": True,
        "email": True
    }
]


# =====================================================
# INITIALIZE DEFAULT SETTINGS
# =====================================================

def initialize_notifications(db: Session):

    existing = db.query(
        NotificationPreference
    ).count()

    if existing == 0:

        for item in DEFAULT_NOTIFICATIONS:

            new_item = NotificationPreference(

                notification_type=item[
                    "notification_type"
                ],

                in_app=item["in_app"],

                email=item["email"]
            )

            db.add(new_item)

        db.commit()


# =====================================================
# GET NOTIFICATION PREFERENCES
# =====================================================

@router.get("/")
def get_notification_preferences(
    db: Session = Depends(get_main_db)
):

    initialize_notifications(db)

    preferences = (
        db.query(NotificationPreference)
        .all()
    )

    return preferences


# =====================================================
# UPDATE NOTIFICATION
# =====================================================

@router.put("/{notification_type}")
def update_notification_preference(
    notification_type: str,
    payload: NotificationPreferenceUpdate,
    db: Session = Depends(get_main_db)
):

    preference = (
        db.query(NotificationPreference)
        .filter(
            NotificationPreference.notification_type
            == notification_type
        )
        .first()
    )

    if not preference:

        raise HTTPException(
            status_code=404,
            detail="Notification preference not found"
        )

    preference.in_app = payload.in_app

    preference.email = payload.email

    preference.updated_at = datetime.utcnow()

    db.commit()

    db.refresh(preference)

    return {
        "message": "Notification preference updated",
        "data": preference
    }
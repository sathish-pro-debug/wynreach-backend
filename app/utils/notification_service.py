from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference


def create_notification(
    db: Session,
    notification_type: str,
    title: str,
    message: str
):
    preference = (
    db.query(NotificationPreference)
    .filter(
        NotificationPreference.notification_type == notification_type
    )
    .first()
)

    if preference is not None and not preference.in_app:
       return None

    notification = Notification(
        notification_type=notification_type,
        title=title,
        message=message,
        is_read=False
    )

    db.add(notification)
    db.commit()
    db.refresh(notification)

    return notification
from fastapi import APIRouter

from sqlalchemy.orm import Session

from app.database import MainSessionLocal

from app.models.notification import Notification

router = APIRouter()


@router.get("/list")
def get_notifications():

    db: Session = MainSessionLocal()

    try:

        notifications = (
            db.query(Notification)
            .order_by(Notification.created_at.desc())
            .all()
        )

        result = []

        for item in notifications:

            result.append({
                "id": item.id,
                "notification_type": item.notification_type,
                "title": item.title,
                "message": item.message,
                "is_read": item.is_read,
                "created_at":
                    item.created_at.isoformat()
                    if item.created_at
                    else None
            })

        return result

    finally:

        db.close()

@router.post("/test")
def create_test_notification():

    db: Session = MainSessionLocal()

    try:

        notification = Notification(
            notification_type="campaignSent",
            title="Campaign Sent",
            message="Summer Sale campaign sent successfully"
        )

        db.add(notification)

        db.commit()

        db.refresh(notification)

        return {
            "message": "Test notification created",
            "id": notification.id
        }

    finally:

        db.close()

@router.put("/read/{notification_id}")
def mark_notification_read(notification_id: int):

    db: Session = MainSessionLocal()

    try:

        notification = (
            db.query(Notification)
            .filter(Notification.id == notification_id)
            .first()
        )

        if not notification:
            return {
                "message": "Notification not found"
            }

        notification.is_read = True

        db.commit()

        return {
            "message": "Notification marked as read"
        }

    finally:

        db.close()

@router.put("/read-all")
def mark_all_notifications_read():

    db: Session = MainSessionLocal()

    try:

        notifications = (
            db.query(Notification)
            .filter(Notification.is_read == False)
            .all()
        )

        for item in notifications:
            item.is_read = True

        db.commit()

        return {
            "message": "All notifications marked as read"
        }

    finally:

        db.close()

@router.get("/unread-count")
def get_unread_count():

    db: Session = MainSessionLocal()

    try:

        count = (
            db.query(Notification)
            .filter(Notification.is_read == False)
            .count()
        )

        return {
            "count": count
        }

    finally:

        db.close()
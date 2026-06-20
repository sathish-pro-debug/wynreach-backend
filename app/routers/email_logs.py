from fastapi import APIRouter

from sqlalchemy.orm import Session

from app.database import MainSessionLocal

from app.models.log import EmailLog

router = APIRouter()


@router.get("/")
def get_email_logs():

    db: Session = MainSessionLocal()

    try:

        logs = db.query(EmailLog).order_by(EmailLog.sent_at.desc()).all()

        result = []

        for log in logs:

            result.append(
                {
                    "id": log.id,
                    "recipient_name": log.recipient_name,
                    "recipient_email": log.recipient_email,
                    "subject": log.subject,
                    "template_name": log.template_name,
                    "status": log.status,
                    "opens": log.opens,
                    "clicks": log.clicks,
                    "sent_at": log.sent_at.isoformat() if log.sent_at else None,
                    "opened_at": log.opened_at.isoformat() if log.opened_at else None,
                    "clicked_at": (
                        log.clicked_at.isoformat() if log.clicked_at else None
                    ),
                }
            )

        return result

    finally:

        db.close()

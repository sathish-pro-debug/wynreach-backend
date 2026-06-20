from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_main_db
from app.models.message_log import MessageLog

router = APIRouter()


@router.get("/")
def get_message_logs(db: Session = Depends(get_main_db)):

    logs = db.query(MessageLog).order_by(desc(MessageLog.created_at)).all()

    # total_sent = len(logs)
    outgoing = [x for x in logs if x.direction != "incoming"]
    total_sent = len(outgoing)
    delivered = len([x for x in outgoing if x.status in ["delivered", "read"]])
    read = len([x for x in outgoing if x.status == "read"])
    failed = len([x for x in outgoing if x.status == "failed"])
    received = len([x for x in logs if x.direction == "incoming"])

    delivered = len([x for x in logs if x.status in ["delivered", "read"]])

    read = len([x for x in logs if x.status == "read"])

    failed = len([x for x in logs if x.status == "failed"])

    formatted_logs = []

    for log in logs:

        formatted_logs.append(
            {
                "id": log.id,
                "campaign_id": log.campaign_id,
                "campaign_name": log.campaign_name,
                "template_name": log.template_name,
                "recipient_name": log.recipient_name,
                "recipient_phone": log.recipient_phone,
                "recipient_email": log.recipient_email,
                "message": log.message,
                "status": log.status,
                "wamid": log.wamid,
                "engagement_score": log.engagement_score,
                "error_reason": log.error_reason,
                "sent_at": log.sent_at,
                "delivered_at": log.delivered_at,
                "read_at": log.read_at,
                "direction": log.direction or "outgoing",
            }
        )

    return {
        "success": True,
        "stats": {
            "total_sent": total_sent,
            "delivered": delivered,
            "read": read,
            "failed": failed,
            "received": received,
        },
        "messages": formatted_logs,
    }

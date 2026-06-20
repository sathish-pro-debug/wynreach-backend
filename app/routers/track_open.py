from fastapi import APIRouter, Request

from sqlalchemy.orm import Session

from sqlalchemy.sql import func

from app.database import MainSessionLocal

from app.models.log import EmailLog

from fastapi.responses import Response

from app.services.email_tracking_service import (
    EVENT_OPENED,
    create_email_event,
    recalculate_campaign_metrics,
)

router = APIRouter()


@router.get("/track/open/{log_id}")
async def track_open(log_id: int, request: Request):
    

    db: Session = MainSessionLocal()
    print("=" * 60)
    print("OPEN TRACKED")
    print("LOG ID:", log_id)
    print("=" * 60)

    try:

        log = db.query(EmailLog).filter(EmailLog.id == log_id).first()

        if log:

            log.opens = (log.opens or 0) + 1

            if not log.opened_at:

                log.opened_at = func.now()
                if log.status in ("sent", "delivered"):
                    log.status = "opened"
                create_email_event(
                    db,
                    tenant_id=log.tenant_id or log.campaign_id,
                    campaign_id=log.campaign_id,
                    contact_id=log.contact_id,
                    message_id=log.message_id or log.ses_message_id or f"log:{log.id}",
                    recipient_email=log.recipient_email,
                    event_type=EVENT_OPENED,
                    metadata={
                        "log_id": log.id,
                        "user_agent": request.headers.get("user-agent"),
                    },
                )
                recalculate_campaign_metrics(db, log.campaign_id)

            db.commit()

        pixel = (
            b"GIF89a\x01\x00\x01\x00\x80\x00\x00"
            b"\x00\x00\x00\xff\xff\xff!"
            b"\xf9\x04\x01\x00\x00\x00\x00,"
            b"\x00\x00\x00\x00\x01\x00\x01\x00"
            b"\x00\x02\x02D\x01\x00;"
        )

        return Response(content=pixel, media_type="image/gif")

    finally:

        db.close()

from fastapi import APIRouter, Request

from sqlalchemy.orm import Session

from sqlalchemy.sql import func

from app.database import MainSessionLocal

from app.models.log import EmailLog

from fastapi.responses import Response
from fastapi.responses import RedirectResponse

from app.services.email_tracking_service import (
    EVENT_CLICKED,
    EVENT_OPENED,
    create_email_event,
    recalculate_campaign_metrics,
)

router = APIRouter()


@router.get("/track/click/{log_id}")
async def track_click(log_id: int, url: str, request: Request):

    print("=" * 60)
    print("🔥 CLICK ROUTE HIT 🔥")
    print("LOG ID:", log_id)
    print("URL:", url)

    db = MainSessionLocal()

    try:

        print("DB URL:", db.bind.url)

        log = db.query(EmailLog).filter(
            EmailLog.id == log_id
        ).first()

        print("LOG FOUND:", log)

        if not log:
            print("❌ LOG NOT FOUND")
            return RedirectResponse(url=url)

        print("BEFORE CLICKS:", log.clicks)

        log.clicks = (log.clicks or 0) + 1

        print("AFTER CLICKS:", log.clicks)

        first_click = log.clicked_at is None
        if not log.clicked_at:
            log.clicked_at = func.now()
        if not log.opened_at:
            log.opened_at = func.now()
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
                    "source": "click_implied_open",
                    "user_agent": request.headers.get("user-agent"),
                },
            )

        if first_click:
            log.status = "clicked"
            create_email_event(
                db,
                tenant_id=log.tenant_id or log.campaign_id,
                campaign_id=log.campaign_id,
                contact_id=log.contact_id,
                message_id=log.message_id or log.ses_message_id or f"log:{log.id}",
                recipient_email=log.recipient_email,
                event_type=EVENT_CLICKED,
                metadata={
                    "log_id": log.id,
                    "url": url,
                    "user_agent": request.headers.get("user-agent"),
                },
            )
            recalculate_campaign_metrics(db, log.campaign_id)

        db.commit()

        print("✅ COMMIT SUCCESS")

        db.refresh(log)

        print("DB VALUE AFTER COMMIT:", log.clicks)

        return RedirectResponse(
            url=url,
            status_code=302
        )

    except Exception as e:

        db.rollback()

        print("❌ ERROR")
        print(type(e))
        print(str(e))

        raise

    finally:
        db.close()

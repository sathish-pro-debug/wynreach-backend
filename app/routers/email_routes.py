from fastapi import APIRouter

from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from app.database import MainSessionLocal

from app.models.email_tenant import Tenant
from app.models.log import EmailLog

from app.services.email_service import send_email

from app.services.email_limiter import (
    check_rate_limit
)

from app.services.suppression_service import (
    is_suppressed
)

router = APIRouter()


@router.post("/send-email")
async def send_email_api(data: dict):

    db: Session = MainSessionLocal()

    try:

        tenant_id = data["tenant_id"]

        tenant = db.query(Tenant).filter(
            Tenant.id == tenant_id
        ).first()

        if not tenant:
            return {
                "error": "Tenant not found"
            }

        if not tenant.sending_enabled:
            return {
                "error": "Tenant suspended"
            }

        check_rate_limit(tenant_id)

        to_email = data["to_email"]

        if is_suppressed(db, to_email):

            return {
                "error": "Suppressed email"
            }

        # CREATE EMAIL LOG
        log = EmailLog(
            tenant_id=tenant_id,

            recipient_name=data.get(
                "recipient_name"
            ),

            recipient_email=to_email,

            subject=data["subject"],

            template_name=data.get(
                "template_name"
            ),

            status="sending",

            delivery_status="sending"
        )

        db.add(log)

        db.commit()

        db.refresh(log)

        # SEND EMAIL
        response = await send_email(
            tenant_id=tenant_id,

            recipients=[to_email],

            subject=data["subject"],

            html_body=data["html"],

            from_email=data["from_email"]
        )

        # SUCCESS
        if response["success"]:

            log.status = "sent"

            log.delivery_status = "sent"

            log.ses_message_id = response[
                "message_id"
            ]

            log.smtp_response = str(response)

            log.sent_at = func.now()

            tenant.total_sent += 1

        # FAILED
        else:

            log.status = "failed"

            log.delivery_status = "failed"

            log.error_message = response[
                "error"
            ]

            log.failed_at = func.now()

            log.retry_count += 1

        db.commit()

        return {
            "success": response["success"],
            "message": response
        }

    finally:

        db.close()
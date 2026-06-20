# app/routers/automation_webhook.py
from fastapi import APIRouter, Request, HTTPException
from fastapi import Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import logging

from app.database import main_engine
from app.models.message_log import MessageLog
from app.services.automation_service import AutomationService

router = APIRouter(prefix="/api/automation", tags=["Automation"])
logger = logging.getLogger(__name__)


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    """Verify webhook for automation - uses same verify token"""
    if hub_verify_token == "wynreach123":
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Invalid verify token")


@router.post("/webhook")
async def receive_webhook(request: Request):
    """
    Automation webhook listener.
    This endpoint receives the same webhook data as whatsapp.py
    but only processes automation rules.
    """
    MainSession = sessionmaker(bind=main_engine)
    db = MainSession()
    
    data = await request.json()
    
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        
        print("🤖 AUTOMATION WEBHOOK DATA:")
        print(json.dumps(data, indent=2))
        
        # ✅ Process status updates (delivered, read, sent)
        statuses = value.get("statuses", [])
        for status in statuses:
            wamid = status.get("id")
            status_val = status.get("status")
            recipient_phone = status.get("recipient_id") or status.get("to")
            
            if not recipient_phone or not wamid:
                continue
            
            # Find original message to get campaign_id
            original_msg = db.query(MessageLog).filter(MessageLog.wamid == wamid).first()
            
            if original_msg and original_msg.campaign_id:
                campaign_id = original_msg.campaign_id
                trigger_data = {
                    "phone": recipient_phone,
                    "message_id": wamid,
                    "status": status_val,
                    "campaign_id": campaign_id
                }
                
                # Trigger automation based on status
                if status_val == "delivered":
                    await AutomationService.check_and_execute_rules(
                        db, campaign_id, "message_delivered", recipient_phone, trigger_data
                    )
                elif status_val == "read":
                    await AutomationService.check_and_execute_rules(
                        db, campaign_id, "message_read", recipient_phone, trigger_data
                    )
                elif status_val == "sent":
                    await AutomationService.check_and_execute_rules(
                        db, campaign_id, "message_sent", recipient_phone, trigger_data
                    )
        
        # ✅ Process incoming messages (replies and button clicks)
        messages = value.get("messages", [])
        for msg in messages:
            phone = msg.get("from")
            msg_type = msg.get("type", "")
            text = msg.get("text", {}).get("body", "")
            
            if not phone:
                continue
            
            # Find last sent message to this phone
            last_sent = db.query(MessageLog).filter(
                MessageLog.recipient_phone == phone,
                MessageLog.direction == "outgoing"
            ).order_by(MessageLog.sent_at.desc()).first()
            
            if last_sent and last_sent.campaign_id:
                campaign_id = last_sent.campaign_id
                
                # Text reply
                if msg_type == "text" and text:
                    trigger_data = {
                        "phone": phone,
                        "message_text": text,
                        "campaign_id": campaign_id
                    }
                    await AutomationService.check_and_execute_rules(
                        db, campaign_id, "message_replied", phone, trigger_data
                    )
                
                # Button click
                elif msg_type == "interactive":
                    interactive = msg.get("interactive", {})
                    button_reply = interactive.get("button_reply", {})
                    button_id = button_reply.get("id", "").lower()
                    button_title = button_reply.get("title", "")
                    
                    trigger_data = {
                        "phone": phone,
                        "button_id": button_id,
                        "button_title": button_title,
                        "campaign_id": campaign_id
                    }
                    await AutomationService.check_and_execute_rules(
                        db, campaign_id, "button_clicked", phone, trigger_data
                    )
        
    except Exception as e:
        logger.error(f"Automation webhook error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()
    
    return {"status": "ok"}
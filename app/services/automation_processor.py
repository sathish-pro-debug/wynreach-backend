# app/services/automation_processor.py
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import asyncio
import logging

from app.database import main_engine
from app.models.message_log import MessageLog
from app.services.automation_service import AutomationService

logger = logging.getLogger(__name__)


class AutomationProcessor:
    """
    Process webhook events from the database.
    This can be called as a background task or via API.
    """
    
    @staticmethod
    async def process_status_update(wamid: str, status_val: str, recipient_phone: str):
        """Process a status update for automation"""
        MainSession = sessionmaker(bind=main_engine)
        db = MainSession()
        
        try:
            original_msg = db.query(MessageLog).filter(MessageLog.wamid == wamid).first()
            
            if original_msg and original_msg.campaign_id:
                campaign_id = original_msg.campaign_id
                
                trigger_data = {
                    "phone": recipient_phone,
                    "message_id": wamid,
                    "status": status_val,
                    "campaign_id": campaign_id
                }
                
                if status_val == "delivered":
                    await AutomationService.check_and_execute_rules(
                        db, campaign_id, "message_delivered", recipient_phone, trigger_data
                    )
                elif status_val == "read":
                    await AutomationService.check_and_execute_rules(
                        db, campaign_id, "message_read", recipient_phone, trigger_data
                    )
        finally:
            db.close()
    
    @staticmethod
    async def process_reply(phone: str, message_text: str):
        """Process a reply for automation"""
        MainSession = sessionmaker(bind=main_engine)
        db = MainSession()
        
        try:
            last_sent = db.query(MessageLog).filter(
                MessageLog.recipient_phone == phone,
                MessageLog.direction == "outgoing"
            ).order_by(MessageLog.sent_at.desc()).first()
            
            if last_sent and last_sent.campaign_id:
                campaign_id = last_sent.campaign_id
                trigger_data = {
                    "phone": phone,
                    "message_text": message_text,
                    "reply_to": last_sent.wamid,
                    "campaign_id": campaign_id
                }
                
                await AutomationService.check_and_execute_rules(
                    db, campaign_id, "message_replied", phone, trigger_data
                )
        finally:
            db.close()
# backend/app/services/campaign_engagement_service.py
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.message_log import MessageLog
from app.models.email_log import EmailLog
from app.models.campaign import Campaign
from app.models.contact import Contact
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class CampaignEngagementService:
    """Service to track and check campaign engagement"""
    
    def __init__(self, db: Session, log_db: Session):
        self.db = db
        self.log_db = log_db
    
    def check_engagement(self, campaign_id: str, contact_id: int) -> Dict:
        """
        Check if a contact engaged with a campaign
        Returns: {
            'opened': bool,
            'replied': bool,
            'clicked': bool,
            'engaged': bool,
            'engagement_type': str
        }
        """
        result = {
            'opened': False,
            'replied': False,
            'clicked': False,
            'engaged': False,
            'engagement_type': None
        }
        
        # Get campaign to know channel
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return result
        
        if campaign.channel == 'whatsapp':
            # Check WhatsApp engagement from message_logs
            logs = self.db.query(MessageLog).filter(
                MessageLog.campaign_id == campaign_id,
                MessageLog.contact_id == contact_id
            ).all()
            
            for log in logs:
                if log.status == 'read':
                    result['opened'] = True
                if log.status == 'replied':
                    result['replied'] = True
                # WhatsApp doesn't have clicks in same way
        
        else:  # Email
            # Check Email engagement from email_logs
            logs = self.log_db.query(EmailLog).filter(
                EmailLog.campaign_id == campaign_id,
                EmailLog.contact_id == contact_id
            ).all()
            
            for log in logs:
                if log.opens > 0:
                    result['opened'] = True
                if log.clicks > 0:
                    result['clicked'] = True
        
        # Determine if engaged
        result['engaged'] = result['opened'] or result['replied'] or result['clicked']
        
        # Determine engagement type
        if result['clicked']:
            result['engagement_type'] = 'clicked'
        elif result['replied']:
            result['engagement_type'] = 'replied'
        elif result['opened']:
            result['engagement_type'] = 'opened'
        
        return result
    
    def get_engaged_contacts(self, campaign_id: str, engagement_type: str = 'all') -> List[int]:
        """
        Get all contacts who engaged with a campaign
        engagement_type: 'all', 'opened', 'replied', 'clicked'
        """
        campaign = self.db.query(Campaign).filter(Campaign.id == campaign_id).first()
        if not campaign:
            return []
        
        contact_ids = set()
        
        if campaign.channel == 'whatsapp':
            logs = self.db.query(MessageLog).filter(
                MessageLog.campaign_id == campaign_id
            ).all()
            
            for log in logs:
                if engagement_type == 'all':
                    contact_ids.add(log.contact_id)
                elif engagement_type == 'opened' and log.status == 'read':
                    contact_ids.add(log.contact_id)
                elif engagement_type == 'replied' and log.status == 'replied':
                    contact_ids.add(log.contact_id)
        
        else:  # Email
            logs = self.log_db.query(EmailLog).filter(
                EmailLog.campaign_id == campaign_id
            ).all()
            
            for log in logs:
                if engagement_type == 'all':
                    contact_ids.add(log.contact_id)
                elif engagement_type == 'opened' and log.opens > 0:
                    contact_ids.add(log.contact_id)
                elif engagement_type == 'clicked' and log.clicks > 0:
                    contact_ids.add(log.contact_id)
        
        return list(contact_ids)
    
    def get_engagement_count(self, campaign_id: str, engagement_type: str = 'all') -> int:
        """Get count of engaged contacts"""
        return len(self.get_engaged_contacts(campaign_id, engagement_type))
# app/services/domain_service.py
from sqlalchemy.orm import Session
from app.models.sender_identity import EmailDomain
from fastapi import HTTPException

class DomainService:
    
    @staticmethod
    def check_domain_access(db: Session, domain_id: str, user_id: str) -> EmailDomain:
        """Check if domain exists, belongs to user, and is not paused"""
        
        domain = db.query(EmailDomain).filter(
            EmailDomain.id == domain_id,
            EmailDomain.user_id == user_id
        ).first()
        
        if not domain:
            raise HTTPException(status_code=404, detail="Domain not found")
        
        if domain.is_paused:
            raise HTTPException(
                status_code=403, 
                detail=f"Domain '{domain.domain}' is paused. Please unpause to use this domain."
            )
        
        return domain
    
    @staticmethod
    def check_domain_access_by_name(db: Session, domain_name: str, user_id: str) -> EmailDomain:
        """Check if domain exists, belongs to user, and is not paused"""
        
        domain = db.query(EmailDomain).filter(
            EmailDomain.domain == domain_name,
            EmailDomain.user_id == user_id
        ).first()
        
        if not domain:
            raise HTTPException(status_code=404, detail="Domain not found")
        
        if domain.is_paused:
            raise HTTPException(
                status_code=403, 
                detail=f"Domain '{domain.domain}' is paused. Please unpause to use this domain."
            )
        
        return domain
    
    @staticmethod
    def get_active_domains(db: Session, user_id: str):
        """Get all active (non-paused) domains for a user"""
        
        return db.query(EmailDomain).filter(
            EmailDomain.user_id == user_id,
            EmailDomain.aws_verification_status == "success",
            EmailDomain.is_paused == False
        ).all()
from sqlalchemy.orm import Session
from app.models.contact import Contact
from app.models.suppression import Suppression

def is_suppressed(
    db: Session,
    email: str
) -> bool:
    if not email:
        return False
    
    # 1. Check contact table
    contact = db.query(Contact).filter(Contact.email == email).first()
    if contact:
        suppression_reason = (contact.suppression_reason or "").lower()
        blocked_reasons = ("hard bounce", "permanent bounce", "complaint", "unsubscribe")
        if (
            contact.is_suppressed
            or contact.status == "suppressed"
            or any(reason in suppression_reason for reason in blocked_reasons)
        ):
            return True
            
        # 2. Check suppressions table
        supp = db.query(Suppression).filter(Suppression.contact_id == contact.id).first()
        if supp:
            return True
            
    return False

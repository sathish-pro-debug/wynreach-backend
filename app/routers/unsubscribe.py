from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_main_db
from app.services.email_tracking_service import mark_contact_suppressed

router = APIRouter()

@router.get("/unsubscribe")
def unsubscribe(email: str, db: Session = Depends(get_main_db)):
    contact = mark_contact_suppressed(
        db,
        email=email,
        reason="Unsubscribe",
        source="Unsubscribe Link",
    )
    db.commit()

    return {
        "message": f"{email} unsubscribed",
        "suppressed": contact is not None,
    }


@router.get("/")
def unsubscribe_root(email: str, db: Session = Depends(get_main_db)):
    return unsubscribe(email=email, db=db)

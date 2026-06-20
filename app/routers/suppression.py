# # # # # # # # # from fastapi import APIRouter, Depends
# # # # # # # # # from sqlalchemy.orm import Session
# # # # # # # # # from sqlalchemy import or_
# # # # # # # # # from datetime import datetime

# # # # # # # # # from app.database import get_main_db

# # # # # # # # # from app.models.lists import (
# # # # # # # # #     AudienceList,
# # # # # # # # #     ListContact
# # # # # # # # # )

# # # # # # # # # from app.models.contact import Contact

# # # # # # # # # router = APIRouter()


# # # # # # # # # # =====================================================
# # # # # # # # # # GET ALL SUPPRESSED CONTACTS
# # # # # # # # # # =====================================================

# # # # # # # # # @router.get("/")
# # # # # # # # # def get_suppressed_contacts(
# # # # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # # # ):

# # # # # # # # #     contacts = (
# # # # # # # # #         db.query(
# # # # # # # # #             ListContact.id,
# # # # # # # # #             ListContact.name,
# # # # # # # # #             ListContact.email,
# # # # # # # # #             ListContact.phone,
# # # # # # # # #             ListContact.status,
# # # # # # # # #             ListContact.suppression_reason,
# # # # # # # # #             ListContact.suppressed_at,
# # # # # # # # #             ListContact.suppression_channel,
# # # # # # # # #             AudienceList.list_name
# # # # # # # # #         )
# # # # # # # # #         .join(
# # # # # # # # #             AudienceList,
# # # # # # # # #             AudienceList.id == ListContact.list_id
# # # # # # # # #         )
# # # # # # # # #         .filter(
# # # # # # # # #             ListContact.is_suppressed == True
# # # # # # # # #         )
# # # # # # # # #         .all()
# # # # # # # # #     )

# # # # # # # # #     result = []

# # # # # # # # #     for item in contacts:

# # # # # # # # #         # CONTACT VALUE
# # # # # # # # #         contact_value = (
# # # # # # # # #             item.email
# # # # # # # # #             if item.suppression_channel == "Email"
# # # # # # # # #             else item.phone
# # # # # # # # #         )

# # # # # # # # #         # CHANNEL
# # # # # # # # #         channel = (
# # # # # # # # #             item.suppression_channel
# # # # # # # # #             if item.suppression_channel
# # # # # # # # #             else "Email"
# # # # # # # # #         )

# # # # # # # # #         result.append({
# # # # # # # # #             "id": item.id,
# # # # # # # # #             "name": item.name,
# # # # # # # # #             "contact": contact_value,
# # # # # # # # #             "channel": channel,
# # # # # # # # #             "reason": item.suppression_reason or "Manual Blacklist",
# # # # # # # # #             "source": item.list_name,
# # # # # # # # #             "since": item.suppressed_at,
# # # # # # # # #             "status": item.status
# # # # # # # # #         })

# # # # # # # # #     return result


# # # # # # # # # # =====================================================
# # # # # # # # # # SUPPRESS CONTACT
# # # # # # # # # # =====================================================

# # # # # # # # # @router.patch("/{contact_id}/suppress")
# # # # # # # # # def suppress_contact(
# # # # # # # # #     contact_id: int,
# # # # # # # # #     payload: dict,
# # # # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # # # ):

# # # # # # # # #     contact = (
# # # # # # # # #         db.query(ListContact)
# # # # # # # # #         .filter(
# # # # # # # # #             ListContact.id == contact_id
# # # # # # # # #         )
# # # # # # # # #         .first()
# # # # # # # # #     )

# # # # # # # # #     if not contact:

# # # # # # # # #         return {
# # # # # # # # #             "success": False,
# # # # # # # # #             "message": "Contact not found"
# # # # # # # # #         }

# # # # # # # # #     # =================================================
# # # # # # # # #     # UPDATE LIST CONTACT
# # # # # # # # #     # =================================================


# # # # # # # # #     contact.is_suppressed = True
# # # # # # # # # contact.status = "suppressed"

# # # # # # # # # print("LIST CONTACT UPDATED:", contact.id)
# # # # # # # # # print("STATUS:", contact.status)
# # # # # # # # # print("SUPPRESSED:", contact.is_suppressed)

# # # # # # # # #     contact.suppression_channel = payload.get(
# # # # # # # # #         "channel",
# # # # # # # # #         "Email"
# # # # # # # # #     )

# # # # # # # # #     contact.suppression_reason = payload.get(
# # # # # # # # #         "reason",
# # # # # # # # #         "Manual Blacklist"
# # # # # # # # #     )

# # # # # # # # #     contact.suppressed_at = datetime.utcnow()

# # # # # # # # #     # =================================================
# # # # # # # # #     # UPDATE MAIN CONTACT TABLE
# # # # # # # # #     # =================================================

# # # # # # # # #     main_contact = (
# # # # # # # # #         db.query(Contact)
# # # # # # # # #         .filter(
# # # # # # # # #             or_(
# # # # # # # # #                 Contact.email == contact.email,
# # # # # # # # #                 Contact.phone == contact.phone
# # # # # # # # #             )
# # # # # # # # #         )
# # # # # # # # #         .first()
# # # # # # # # #     )

# # # # # # # # #     if main_contact:

# # # # # # # # #         main_contact.status = "suppressed"

# # # # # # # # #         main_contact.updated_at = datetime.utcnow()

# # # # # # # # #         print("UPDATED CONTACT:", main_contact.id)

# # # # # # # # #     else:

# # # # # # # # #         print("CONTACT NOT FOUND")

# # # # # # # # #     db.commit()

# # # # # # # # #     return {
# # # # # # # # #         "success": True,
# # # # # # # # #         "message": "Contact suppressed successfully"
# # # # # # # # #     }


# # # # # # # # # # =====================================================
# # # # # # # # # # RESTORE CONTACT
# # # # # # # # # # =====================================================

# # # # # # # # # @router.patch("/{contact_id}/restore")
# # # # # # # # # def restore_contact(
# # # # # # # # #     contact_id: int,
# # # # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # # # ):

# # # # # # # # #     contact = (
# # # # # # # # #         db.query(ListContact)
# # # # # # # # #         .filter(
# # # # # # # # #             ListContact.id == contact_id
# # # # # # # # #         )
# # # # # # # # #         .first()
# # # # # # # # #     )

# # # # # # # # #     if not contact:

# # # # # # # # #         return {
# # # # # # # # #             "success": False,
# # # # # # # # #             "message": "Contact not found"
# # # # # # # # #         }

# # # # # # # # #     # =================================================
# # # # # # # # #     # RESTORE LIST CONTACT
# # # # # # # # #     # =================================================

# # # # # # # # #    contact.is_suppressed = False
# # # # # # # # #    contact.status = "active"

# # # # # # # # #    print("RESTORED LIST CONTACT:", contact.id)
# # # # # # # # #    print("STATUS:", contact.status)

# # # # # # # # #     contact.suppression_reason = None

# # # # # # # # #     contact.suppression_channel = None

# # # # # # # # #     contact.suppressed_at = None

# # # # # # # # #     # =================================================
# # # # # # # # #     # RESTORE MAIN CONTACT TABLE
# # # # # # # # #     # =================================================

# # # # # # # # #     main_contact = (
# # # # # # # # #         db.query(Contact)
# # # # # # # # #         .filter(
# # # # # # # # #             or_(
# # # # # # # # #                 Contact.email == contact.email,
# # # # # # # # #                 Contact.phone == contact.phone
# # # # # # # # #             )
# # # # # # # # #         )
# # # # # # # # #         .first()
# # # # # # # # #     )

# # # # # # # # #     if main_contact:

# # # # # # # # #         main_contact.status = "active"

# # # # # # # # #         main_contact.updated_at = datetime.utcnow()

# # # # # # # # #         print("RESTORED CONTACT:", main_contact.id)

# # # # # # # # #     else:

# # # # # # # # #         print("CONTACT NOT FOUND")

# # # # # # # # #     db.commit()

# # # # # # # # #     return {
# # # # # # # # #         "success": True,
# # # # # # # # #         "message": "Contact restored successfully"
# # # # # # # # #     }


# # # # # # # # # # =====================================================
# # # # # # # # # # COUNT BY LIST
# # # # # # # # # # =====================================================

# # # # # # # # # @router.get("/count-by-list/{list_id}")
# # # # # # # # # def get_suppression_count_by_list(
# # # # # # # # #     list_id: int,
# # # # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # # # ):

# # # # # # # # #     count = (
# # # # # # # # #         db.query(ListContact)
# # # # # # # # #         .filter(
# # # # # # # # #             ListContact.list_id == list_id,
# # # # # # # # #             ListContact.is_suppressed == True
# # # # # # # # #         )
# # # # # # # # #         .count()
# # # # # # # # #     )

# # # # # # # # #     return {
# # # # # # # # #         "list_id": list_id,
# # # # # # # # #         "suppressed_count": count
# # # # # # # # #     }


# # # # # # # # # # =====================================================
# # # # # # # # # # ESTIMATE SUPPRESSION
# # # # # # # # # # =====================================================

# # # # # # # # # @router.post("/estimate")
# # # # # # # # # def estimate_suppression(
# # # # # # # # #     payload: dict,
# # # # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # # # ):

# # # # # # # # #     list_ids = payload.get("list_ids", [])

# # # # # # # # #     if not list_ids:

# # # # # # # # #         return {
# # # # # # # # #             "suppressed_count": 0
# # # # # # # # #         }

# # # # # # # # #     count = (
# # # # # # # # #         db.query(ListContact)
# # # # # # # # #         .filter(
# # # # # # # # #             ListContact.list_id.in_(list_ids),
# # # # # # # # #             ListContact.is_suppressed == True
# # # # # # # # #         )
# # # # # # # # #         .count()
# # # # # # # # #     )

# # # # # # # # #     return {
# # # # # # # # #         "suppressed_count": count
# # # # # # # # #     }


# # # # # # # # from fastapi import APIRouter, Depends
# # # # # # # # from sqlalchemy.orm import Session
# # # # # # # # from datetime import datetime

# # # # # # # # from app.database import get_main_db

# # # # # # # # from app.models.lists import (
# # # # # # # #     AudienceList,
# # # # # # # #     ListContact
# # # # # # # # )

# # # # # # # # router = APIRouter()


# # # # # # # # # =====================================================
# # # # # # # # # GET ALL SUPPRESSED CONTACTS
# # # # # # # # # =====================================================

# # # # # # # # @router.get("/")
# # # # # # # # def get_suppressed_contacts(
# # # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # # ):

# # # # # # # #     contacts = (
# # # # # # # #         db.query(
# # # # # # # #             ListContact.id,
# # # # # # # #             ListContact.name,
# # # # # # # #             ListContact.email,
# # # # # # # #             ListContact.phone,
# # # # # # # #             ListContact.status,
# # # # # # # #             ListContact.suppression_reason,
# # # # # # # #             ListContact.suppressed_at,
# # # # # # # #             ListContact.suppression_channel,
# # # # # # # #             AudienceList.list_name
# # # # # # # #         )
# # # # # # # #         .join(
# # # # # # # #             AudienceList,
# # # # # # # #             AudienceList.id == ListContact.list_id
# # # # # # # #         )
# # # # # # # #         .filter(
# # # # # # # #             ListContact.is_suppressed == True
# # # # # # # #         )
# # # # # # # #         .all()
# # # # # # # #     )

# # # # # # # #     result = []

# # # # # # # #     for item in contacts:

# # # # # # # #         contact_value = (
# # # # # # # #             item.email
# # # # # # # #             if item.suppression_channel == "Email"
# # # # # # # #             else item.phone
# # # # # # # #         )

# # # # # # # #         channel = (
# # # # # # # #             item.suppression_channel
# # # # # # # #             if item.suppression_channel
# # # # # # # #             else "Email"
# # # # # # # #         )

# # # # # # # #         result.append({
# # # # # # # #             "id": item.id,
# # # # # # # #             "name": item.name,
# # # # # # # #             "contact": contact_value,
# # # # # # # #             "channel": channel,
# # # # # # # #             "reason": item.suppression_reason or "Manual Blacklist",
# # # # # # # #             "source": item.list_name,
# # # # # # # #             "since": item.suppressed_at,
# # # # # # # #             "status": item.status
# # # # # # # #         })

# # # # # # # #     return result


# # # # # # # # # =====================================================
# # # # # # # # # SUPPRESS CONTACT
# # # # # # # # # =====================================================

# # # # # # # # @router.patch("/{contact_id}/suppress")
# # # # # # # # def suppress_contact(
# # # # # # # #     contact_id: int,
# # # # # # # #     payload: dict,
# # # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # # ):

# # # # # # # #     contact = (
# # # # # # # #         db.query(ListContact)
# # # # # # # #         .filter(
# # # # # # # #             ListContact.id == contact_id
# # # # # # # #         )
# # # # # # # #         .first()
# # # # # # # #     )

# # # # # # # #     if not contact:

# # # # # # # #         return {
# # # # # # # #             "success": False,
# # # # # # # #             "message": "Contact not found"
# # # # # # # #         }

# # # # # # # #     # UPDATE STATUS
# # # # # # # #     contact.is_suppressed = True

# # # # # # # #     contact.status = "suppressed"

# # # # # # # #     contact.suppression_channel = payload.get(
# # # # # # # #         "channel",
# # # # # # # #         "Email"
# # # # # # # #     )

# # # # # # # #     contact.suppression_reason = payload.get(
# # # # # # # #         "reason",
# # # # # # # #         "Manual Blacklist"
# # # # # # # #     )

# # # # # # # #     contact.suppressed_at = datetime.utcnow()

# # # # # # # #     contact.updated_at = datetime.utcnow()

# # # # # # # #     db.commit()

# # # # # # # #     return {
# # # # # # # #         "success": True,
# # # # # # # #         "message": "Contact suppressed successfully"
# # # # # # # #     }


# # # # # # # # # =====================================================
# # # # # # # # # RESTORE CONTACT
# # # # # # # # # =====================================================

# # # # # # # # @router.patch("/{contact_id}/restore")
# # # # # # # # def restore_contact(
# # # # # # # #     contact_id: int,
# # # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # # ):

# # # # # # # #     contact = (
# # # # # # # #         db.query(ListContact)
# # # # # # # #         .filter(
# # # # # # # #             ListContact.id == contact_id
# # # # # # # #         )
# # # # # # # #         .first()
# # # # # # # #     )

# # # # # # # #     if not contact:

# # # # # # # #         return {
# # # # # # # #             "success": False,
# # # # # # # #             "message": "Contact not found"
# # # # # # # #         }

# # # # # # # #     # RESTORE STATUS
# # # # # # # #     contact.is_suppressed = False

# # # # # # # #     contact.status = "active"

# # # # # # # #     contact.suppression_reason = None

# # # # # # # #     contact.suppression_channel = None

# # # # # # # #     contact.suppressed_at = None

# # # # # # # #     contact.updated_at = datetime.utcnow()

# # # # # # # #     db.commit()

# # # # # # # #     return {
# # # # # # # #         "success": True,
# # # # # # # #         "message": "Contact restored successfully"
# # # # # # # #     }


# # # # # # # # # =====================================================
# # # # # # # # # COUNT BY LIST
# # # # # # # # # =====================================================

# # # # # # # # @router.get("/count-by-list/{list_id}")
# # # # # # # # def get_suppression_count_by_list(
# # # # # # # #     list_id: int,
# # # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # # ):

# # # # # # # #     count = (
# # # # # # # #         db.query(ListContact)
# # # # # # # #         .filter(
# # # # # # # #             ListContact.list_id == list_id,
# # # # # # # #             ListContact.is_suppressed == True
# # # # # # # #         )
# # # # # # # #         .count()
# # # # # # # #     )

# # # # # # # #     return {
# # # # # # # #         "list_id": list_id,
# # # # # # # #         "suppressed_count": count
# # # # # # # #     }


# # # # # # # # # =====================================================
# # # # # # # # # ESTIMATE SUPPRESSION
# # # # # # # # # =====================================================

# # # # # # # # @router.post("/estimate")
# # # # # # # # def estimate_suppression(
# # # # # # # #     payload: dict,
# # # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # # ):

# # # # # # # #     list_ids = payload.get("list_ids", [])

# # # # # # # #     if not list_ids:

# # # # # # # #         return {
# # # # # # # #             "suppressed_count": 0
# # # # # # # #         }

# # # # # # # #     count = (
# # # # # # # #         db.query(ListContact)
# # # # # # # #         .filter(
# # # # # # # #             ListContact.list_id.in_(list_ids),
# # # # # # # #             ListContact.is_suppressed == True
# # # # # # # #         )
# # # # # # # #         .count()
# # # # # # # #     )

# # # # # # # #     return {
# # # # # # # #         "suppressed_count": count
# # # # # # # #     }


# # # # # # # from fastapi import APIRouter, Depends
# # # # # # # from sqlalchemy.orm import Session
# # # # # # # from datetime import datetime

# # # # # # # from app.database import get_main_db

# # # # # # # from app.models.lists import (
# # # # # # #     AudienceList,
# # # # # # #     ListContact
# # # # # # # )

# # # # # # # # IMPORTANT
# # # # # # # from app.models.contact import Contact

# # # # # # # router = APIRouter()


# # # # # # # # =====================================================
# # # # # # # # GET ALL SUPPRESSED CONTACTS
# # # # # # # # =====================================================

# # # # # # # @router.get("/")
# # # # # # # def get_suppressed_contacts(
# # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # ):

# # # # # # #     contacts = (
# # # # # # #         db.query(
# # # # # # #             ListContact.id,
# # # # # # #             ListContact.contact_id,
# # # # # # #             ListContact.name,
# # # # # # #             ListContact.email,
# # # # # # #             ListContact.phone,
# # # # # # #             ListContact.status,
# # # # # # #             ListContact.suppression_reason,
# # # # # # #             ListContact.suppressed_at,
# # # # # # #             ListContact.suppression_channel,
# # # # # # #             AudienceList.list_name
# # # # # # #         )
# # # # # # #         .join(
# # # # # # #             AudienceList,
# # # # # # #             AudienceList.id == ListContact.list_id
# # # # # # #         )
# # # # # # #         .filter(
# # # # # # #             ListContact.is_suppressed == True
# # # # # # #         )
# # # # # # #         .all()
# # # # # # #     )

# # # # # # #     result = []

# # # # # # #     for item in contacts:

# # # # # # #         # CONTACT VALUE
# # # # # # #         contact_value = (
# # # # # # #             item.email
# # # # # # #             if item.suppression_channel == "Email"
# # # # # # #             else item.phone
# # # # # # #         )

# # # # # # #         # CHANNEL
# # # # # # #         channel = (
# # # # # # #             item.suppression_channel
# # # # # # #             if item.suppression_channel
# # # # # # #             else "Email"
# # # # # # #         )

# # # # # # #         result.append({
# # # # # # #             "id": item.id,
# # # # # # #             "contact_id": item.contact_id,
# # # # # # #             "name": item.name,
# # # # # # #             "contact": contact_value,
# # # # # # #             "channel": channel,
# # # # # # #             "reason": item.suppression_reason or "Manual Blacklist",
# # # # # # #             "source": item.list_name,
# # # # # # #             "since": item.suppressed_at,
# # # # # # #             "status": item.status
# # # # # # #         })

# # # # # # #     return result


# # # # # # # # =====================================================
# # # # # # # # SUPPRESS CONTACT
# # # # # # # # =====================================================

# # # # # # # @router.patch("/{contact_id}/suppress")
# # # # # # # def suppress_contact(
# # # # # # #     contact_id: int,
# # # # # # #     payload: dict,
# # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # ):

# # # # # # #     # =================================================
# # # # # # #     # FIND LIST CONTACT
# # # # # # #     # =================================================

# # # # # # #     contact = (
# # # # # # #         db.query(ListContact)
# # # # # # #        .filter(
# # # # # # #     ListContact.contact_id == contact_id
# # # # # # # )
# # # # # # #         .first()
# # # # # # #     )

# # # # # # #     if not contact:

# # # # # # #         return {
# # # # # # #             "success": False,
# # # # # # #             "message": "Contact not found"
# # # # # # #         }

# # # # # # #     # =================================================
# # # # # # #     # UPDATE LIST CONTACT
# # # # # # #     # =================================================

# # # # # # #     contact.is_suppressed = True

# # # # # # #     contact.status = "suppressed"

# # # # # # #     contact.suppression_channel = payload.get(
# # # # # # #         "channel",
# # # # # # #         "Email"
# # # # # # #     )

# # # # # # #     contact.suppression_reason = payload.get(
# # # # # # #         "reason",
# # # # # # #         "Manual Blacklist"
# # # # # # #     )

# # # # # # #     contact.suppressed_at = datetime.utcnow()

# # # # # # #     contact.updated_at = datetime.utcnow()

# # # # # # #     # =================================================
# # # # # # #     # UPDATE MAIN CONTACT TABLE
# # # # # # #     # =================================================

# # # # # # #     if contact.contact_id:

# # # # # # #         main_contact = (
# # # # # # #             db.query(Contact)
# # # # # # #             .filter(
# # # # # # #                 Contact.id == contact.contact_id
# # # # # # #             )
# # # # # # #             .first()
# # # # # # #         )

# # # # # # #         if main_contact:

# # # # # # #             main_contact.status = "suppressed"

# # # # # # #             main_contact.updated_at = datetime.utcnow()

# # # # # # #             print(
# # # # # # #                 "MAIN CONTACT SUPPRESSED:",
# # # # # # #                 main_contact.id
# # # # # # #             )

# # # # # # #         else:

# # # # # # #             print("MAIN CONTACT NOT FOUND")

# # # # # # #     else:

# # # # # # #         print("CONTACT_ID IS NULL")

# # # # # # #     db.commit()

# # # # # # #     return {
# # # # # # #         "success": True,
# # # # # # #         "message": "Contact suppressed successfully"
# # # # # # #     }


# # # # # # # # =====================================================
# # # # # # # # RESTORE CONTACT
# # # # # # # # =====================================================

# # # # # # # @router.patch("/{contact_id}/restore")
# # # # # # # def restore_contact(
# # # # # # #     contact_id: int,
# # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # ):

# # # # # # #     # =================================================
# # # # # # #     # FIND LIST CONTACT
# # # # # # #     # =================================================

# # # # # # #     contact = (
# # # # # # #         db.query(ListContact)
# # # # # # #         .filter(
# # # # # # #            ListContact.contact_id == contact_id
# # # # # # #         )
# # # # # # #         .first()
# # # # # # #     )

# # # # # # #     if not contact:

# # # # # # #         return {
# # # # # # #             "success": False,
# # # # # # #             "message": "Contact not found"
# # # # # # #         }

# # # # # # #     # =================================================
# # # # # # #     # RESTORE LIST CONTACT
# # # # # # #     # =================================================

# # # # # # #     contact.is_suppressed = False

# # # # # # #     contact.status = "active"

# # # # # # #     contact.suppression_reason = None

# # # # # # #     contact.suppression_channel = None

# # # # # # #     contact.suppressed_at = None

# # # # # # #     contact.updated_at = datetime.utcnow()

# # # # # # #     # =================================================
# # # # # # #     # RESTORE MAIN CONTACT TABLE
# # # # # # #     # =================================================

# # # # # # #     if contact.contact_id:

# # # # # # #         main_contact = (
# # # # # # #             db.query(Contact)
# # # # # # #             .filter(
# # # # # # #                 Contact.id == contact.contact_id
# # # # # # #             )
# # # # # # #             .first()
# # # # # # #         )

# # # # # # #         if main_contact:

# # # # # # #             main_contact.status = "active"

# # # # # # #             main_contact.updated_at = datetime.utcnow()

# # # # # # #             print(
# # # # # # #                 "MAIN CONTACT RESTORED:",
# # # # # # #                 main_contact.id
# # # # # # #             )

# # # # # # #         else:

# # # # # # #             print("MAIN CONTACT NOT FOUND")

# # # # # # #     else:

# # # # # # #         print("CONTACT_ID IS NULL")

# # # # # # #     db.commit()

# # # # # # #     return {
# # # # # # #         "success": True,
# # # # # # #         "message": "Contact restored successfully"
# # # # # # #     }


# # # # # # # # =====================================================
# # # # # # # # COUNT BY LIST
# # # # # # # # =====================================================

# # # # # # # @router.get("/count-by-list/{list_id}")
# # # # # # # def get_suppression_count_by_list(
# # # # # # #     list_id: int,
# # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # ):

# # # # # # #     count = (
# # # # # # #         db.query(ListContact)
# # # # # # #         .filter(
# # # # # # #             ListContact.list_id == list_id,
# # # # # # #             ListContact.is_suppressed == True
# # # # # # #         )
# # # # # # #         .count()
# # # # # # #     )

# # # # # # #     return {
# # # # # # #         "list_id": list_id,
# # # # # # #         "suppressed_count": count
# # # # # # #     }


# # # # # # # # =====================================================
# # # # # # # # ESTIMATE SUPPRESSION
# # # # # # # # =====================================================

# # # # # # # @router.post("/estimate")
# # # # # # # def estimate_suppression(
# # # # # # #     payload: dict,
# # # # # # #     db: Session = Depends(get_main_db)
# # # # # # # ):

# # # # # # #     list_ids = payload.get("list_ids", [])

# # # # # # #     if not list_ids:

# # # # # # #         return {
# # # # # # #             "suppressed_count": 0
# # # # # # #         }

# # # # # # #     count = (
# # # # # # #         db.query(ListContact)
# # # # # # #         .filter(
# # # # # # #             ListContact.list_id.in_(list_ids),
# # # # # # #             ListContact.is_suppressed == True
# # # # # # #         )
# # # # # # #         .count()
# # # # # # #     )

# # # # # # #     return {
# # # # # # #         "suppressed_count": count
# # # # # # #     }


# # # # # # from fastapi import APIRouter, Depends
# # # # # # from sqlalchemy.orm import Session
# # # # # # from datetime import datetime

# # # # # # from app.database import get_main_db

# # # # # # from app.models.contact import Contact

# # # # # # router = APIRouter()


# # # # # # # =====================================================
# # # # # # # GET SUPPRESSED CONTACTS
# # # # # # # =====================================================

# # # # # # @router.get("/")
# # # # # # def get_suppressed_contacts(
# # # # # #     db: Session = Depends(get_main_db)
# # # # # # ):

# # # # # #     contacts = (
# # # # # #         db.query(Contact)
# # # # # #         .filter(Contact.status == "suppressed")
# # # # # #         .all()
# # # # # #     )

# # # # # #     result = []

# # # # # #     for contact in contacts:

# # # # # #         channel = (
# # # # # #             "Email"
# # # # # #             if contact.email
# # # # # #             else "WhatsApp"
# # # # # #         )

# # # # # #         contact_value = (
# # # # # #             contact.email
# # # # # #             if contact.email
# # # # # #             else contact.phone
# # # # # #         )

# # # # # #         result.append({
# # # # # #             "id": contact.id,
# # # # # #             "name": contact.full_name,
# # # # # #             "contact": contact_value,
# # # # # #             "channel": channel,
# # # # # #             "status": contact.status
# # # # # #         })

# # # # # #     return result


# # # # # # # =====================================================
# # # # # # # SUPPRESS CONTACT
# # # # # # # =====================================================

# # # # # # @router.patch("/{contact_id}/suppress")
# # # # # # def suppress_contact(
# # # # # #     contact_id: int,
# # # # # #     payload: dict,
# # # # # #     db: Session = Depends(get_main_db)
# # # # # # ):

# # # # # #     contact = (
# # # # # #         db.query(Contact)
# # # # # #         .filter(Contact.id == contact_id)
# # # # # #         .first()
# # # # # #     )

# # # # # #     if not contact:

# # # # # #         return {
# # # # # #             "success": False,
# # # # # #             "message": "Contact not found"
# # # # # #         }

# # # # # #     contact.status = "suppressed"

# # # # # #     contact.updated_at = datetime.utcnow()

# # # # # #     db.commit()

# # # # # #     return {
# # # # # #         "success": True,
# # # # # #         "message": "Contact suppressed successfully"
# # # # # #     }


# # # # # # # =====================================================
# # # # # # # RESTORE CONTACT
# # # # # # # =====================================================

# # # # # # @router.patch("/{contact_id}/restore")
# # # # # # def restore_contact(
# # # # # #     contact_id: int,
# # # # # #     db: Session = Depends(get_main_db)
# # # # # # ):

# # # # # #     contact = (
# # # # # #         db.query(Contact)
# # # # # #         .filter(Contact.id == contact_id)
# # # # # #         .first()
# # # # # #     )

# # # # # #     if not contact:

# # # # # #         return {
# # # # # #             "success": False,
# # # # # #             "message": "Contact not found"
# # # # # #         }

# # # # # #     contact.status = "active"

# # # # # #     contact.updated_at = datetime.utcnow()

# # # # # #     db.commit()

# # # # # #     return {
# # # # # #         "success": True,
# # # # # #         "message": "Contact restored successfully"
# # # # # #     }


# # # # # from fastapi import APIRouter, Depends
# # # # # from sqlalchemy.orm import Session
# # # # # from datetime import datetime

# # # # # from app.database import get_main_db

# # # # # from app.models.contact import Contact

# # # # # router = APIRouter()


# # # # # # =====================================================
# # # # # # GET SUPPRESSED CONTACTS
# # # # # # =====================================================

# # # # # @router.get("/")
# # # # # def get_suppressed_contacts(
# # # # #     db: Session = Depends(get_main_db)
# # # # # ):

# # # # #     contacts = (
# # # # #         db.query(Contact)
# # # # #         .filter(Contact.is_suppressed == True)
# # # # #         .all()
# # # # #     )

# # # # #     result = []

# # # # #     for contact in contacts:

# # # # #         contact_value = (
# # # # #             contact.email
# # # # #             if contact.suppression_channel == "Email"
# # # # #             else contact.phone
# # # # #         )

# # # # #         result.append({
# # # # #             "id": contact.id,
# # # # #             "name": contact.full_name,
# # # # #             "contact": contact_value,
# # # # #             "channel": contact.suppression_channel,
# # # # #             "reason": contact.suppression_reason,
# # # # #             "since": contact.suppressed_at,
# # # # #             "status": contact.status
# # # # #         })

# # # # #     return result


# # # # # # =====================================================
# # # # # # SUPPRESS CONTACT
# # # # # # =====================================================

# # # # # @router.patch("/{contact_id}/suppress")
# # # # # def suppress_contact(
# # # # #     contact_id: int,
# # # # #     payload: dict,
# # # # #     db: Session = Depends(get_main_db)
# # # # # ):

# # # # #     contact = (
# # # # #         db.query(Contact)
# # # # #         .filter(Contact.id == contact_id)
# # # # #         .first()
# # # # #     )

# # # # #     if not contact:

# # # # #         return {
# # # # #             "success": False,
# # # # #             "message": "Contact not found"
# # # # #         }

# # # # #     # =================================================
# # # # #     # UPDATE CONTACT
# # # # #     # =================================================

# # # # #     contact.status = "suppressed"

# # # # #     contact.is_suppressed = True

# # # # #     contact.suppression_channel = payload.get(
# # # # #         "channel",
# # # # #         "Email"
# # # # #     )

# # # # #     contact.suppression_reason = payload.get(
# # # # #         "reason",
# # # # #         "Manual Blacklist"
# # # # #     )

# # # # #     contact.suppressed_at = datetime.utcnow()

# # # # #     contact.updated_at = datetime.utcnow()

# # # # #     db.commit()

# # # # #     return {
# # # # #         "success": True,
# # # # #         "message": "Contact suppressed successfully"
# # # # #     }


# # # # # # =====================================================
# # # # # # RESTORE CONTACT
# # # # # # =====================================================

# # # # # @router.patch("/{contact_id}/restore")
# # # # # def restore_contact(
# # # # #     contact_id: int,
# # # # #     db: Session = Depends(get_main_db)
# # # # # ):

# # # # #     contact = (
# # # # #         db.query(Contact)
# # # # #         .filter(Contact.id == contact_id)
# # # # #         .first()
# # # # #     )

# # # # #     if not contact:

# # # # #         return {
# # # # #             "success": False,
# # # # #             "message": "Contact not found"
# # # # #         }

# # # # #     # =================================================
# # # # #     # RESTORE
# # # # #     # =================================================

# # # # #     contact.status = "active"

# # # # #     contact.is_suppressed = False

# # # # #     contact.suppression_channel = None

# # # # #     contact.suppression_reason = None

# # # # #     contact.suppressed_at = None

# # # # #     contact.updated_at = datetime.utcnow()

# # # # #     db.commit()

# # # # #     return {
# # # # #         "success": True,
# # # # #         "message": "Contact restored successfully"
# # # # #     }


# # # # from fastapi import APIRouter, Depends
# # # # from sqlalchemy.orm import Session
# # # # from datetime import datetime

# # # # from app.database import get_main_db

# # # # # CONTACT MODEL
# # # # from app.models.contact import Contact

# # # # # LIST MODELS
# # # # from app.models.lists import (
# # # #     ListContact,
# # # #     AudienceList
# # # # )

# # # # router = APIRouter()


# # # # # =====================================================
# # # # # GET SUPPRESSED CONTACTS
# # # # # =====================================================

# # # # @router.get("/")
# # # # def get_suppressed_contacts(
# # # #     db: Session = Depends(get_main_db)
# # # # ):

# # # #     contacts = (
# # # #         db.query(
# # # #             Contact,
# # # #             AudienceList.list_name
# # # #         )
# # # #         .join(
# # # #             ListContact,
# # # #             ListContact.contact_id == Contact.id
# # # #         )
# # # #         .join(
# # # #             AudienceList,
# # # #             AudienceList.id == ListContact.list_id
# # # #         )
# # # #         .filter(
# # # #             Contact.is_suppressed == True
# # # #         )
# # # #         .all()
# # # #     )

# # # #     result = []

# # # #     for contact, list_name in contacts:

# # # #         # =================================================
# # # #         # CONTACT VALUE
# # # #         # =================================================

# # # #         contact_value = (
# # # #             contact.email
# # # #             if contact.suppression_channel == "Email"
# # # #             else contact.phone
# # # #         )

# # # #         # =================================================
# # # #         # RESULT
# # # #         # =================================================

# # # #         result.append({
# # # #             "id": contact.id,
# # # #             "name": contact.full_name,
# # # #             "contact": contact_value,
# # # #             "channel": contact.suppression_channel,
# # # #             "reason": contact.suppression_reason,
# # # #             "source": list_name,
# # # #             "since": contact.suppressed_at,
# # # #             "status": contact.status
# # # #         })

# # # #     return result


# # # # # =====================================================
# # # # # SUPPRESS CONTACT
# # # # # =====================================================

# # # # @router.patch("/{contact_id}/suppress")
# # # # def suppress_contact(
# # # #     contact_id: int,
# # # #     payload: dict,
# # # #     db: Session = Depends(get_main_db)
# # # # ):

# # # #     contact = (
# # # #         db.query(Contact)
# # # #         .filter(Contact.id == contact_id)
# # # #         .first()
# # # #     )

# # # #     if not contact:

# # # #         return {
# # # #             "success": False,
# # # #             "message": "Contact not found"
# # # #         }

# # # #     # =================================================
# # # #     # UPDATE CONTACT
# # # #     # =================================================

# # # #     contact.status = "suppressed"

# # # #     contact.is_suppressed = True

# # # #     contact.suppression_channel = payload.get(
# # # #         "channel",
# # # #         "Email"
# # # #     )

# # # #     contact.suppression_reason = payload.get(
# # # #         "reason",
# # # #         "Manual Blacklist"
# # # #     )

# # # #     contact.suppressed_at = datetime.utcnow()

# # # #     contact.updated_at = datetime.utcnow()

# # # #     db.commit()

# # # #     return {
# # # #         "success": True,
# # # #         "message": "Contact suppressed successfully"
# # # #     }


# # # # # =====================================================
# # # # # RESTORE CONTACT
# # # # # =====================================================

# # # # @router.patch("/{contact_id}/restore")
# # # # def restore_contact(
# # # #     contact_id: int,
# # # #     db: Session = Depends(get_main_db)
# # # # ):

# # # #     contact = (
# # # #         db.query(Contact)
# # # #         .filter(Contact.id == contact_id)
# # # #         .first()
# # # #     )

# # # #     if not contact:

# # # #         return {
# # # #             "success": False,
# # # #             "message": "Contact not found"
# # # #         }

# # # #     # =================================================
# # # #     # RESTORE CONTACT
# # # #     # =================================================

# # # #     contact.status = "active"

# # # #     contact.is_suppressed = False

# # # #     contact.suppression_channel = None

# # # #     contact.suppression_reason = None

# # # #     contact.suppressed_at = None

# # # #     contact.updated_at = datetime.utcnow()

# # # #     db.commit()

# # # #     return {
# # # #         "success": True,
# # # #         "message": "Contact restored successfully"
# # # #     }


# # # # # =====================================================
# # # # # COUNT BY LIST
# # # # # =====================================================

# # # # @router.get("/count-by-list/{list_id}")
# # # # def get_suppression_count_by_list(
# # # #     list_id: int,
# # # #     db: Session = Depends(get_main_db)
# # # # ):

# # # #     count = (
# # # #         db.query(Contact)
# # # #         .join(
# # # #             ListContact,
# # # #             ListContact.contact_id == Contact.id
# # # #         )
# # # #         .filter(
# # # #             ListContact.list_id == list_id,
# # # #             Contact.is_suppressed == True
# # # #         )
# # # #         .count()
# # # #     )

# # # #     return {
# # # #         "list_id": list_id,
# # # #         "suppressed_count": count
# # # #     }


# # # # # =====================================================
# # # # # ESTIMATE SUPPRESSION
# # # # # =====================================================

# # # # @router.post("/estimate")
# # # # def estimate_suppression(
# # # #     payload: dict,
# # # #     db: Session = Depends(get_main_db)
# # # # ):

# # # #     list_ids = payload.get("list_ids", [])

# # # #     if not list_ids:

# # # #         return {
# # # #             "suppressed_count": 0
# # # #         }

# # # #     count = (
# # # #         db.query(Contact)
# # # #         .join(
# # # #             ListContact,
# # # #             ListContact.contact_id == Contact.id
# # # #         )
# # # #         .filter(
# # # #             ListContact.list_id.in_(list_ids),
# # # #             Contact.is_suppressed == True
# # # #         )
# # # #         .count()
# # # #     )

# # # #     return {
# # # #         "suppressed_count": count
# # # #     }


# # # from fastapi import APIRouter, Depends
# # # from sqlalchemy.orm import Session
# # # from datetime import datetime

# # # from app.database import get_main_db

# # # # CONTACT MODEL
# # # from app.models.contact import Contact

# # # # LIST MODELS
# # # from app.models.lists import (
# # #     ListContact,
# # #     AudienceList
# # # )

# # # router = APIRouter()


# # # # =====================================================
# # # # GET SUPPRESSED CONTACTS
# # # # =====================================================

# # # @router.get("/")
# # # def get_suppressed_contacts(
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     contacts = (
# # #         db.query(
# # #             Contact,
# # #             AudienceList.list_name
# # #         )
# # #         .outerjoin(
# # #             ListContact,
# # #             ListContact.contact_id == Contact.id
# # #         )
# # #         .outerjoin(
# # #             AudienceList,
# # #             AudienceList.id == ListContact.list_id
# # #         )
# # #         .filter(
# # #             Contact.is_suppressed == True
# # #         )
# # #         .all()
# # #     )

# # #     result = []

# # #     for contact, list_name in contacts:

# # #         # =================================================
# # #         # CONTACT VALUE
# # #         # =================================================

# # #         contact_value = (
# # #             contact.email
# # #             if contact.suppression_channel == "Email"
# # #             else contact.phone
# # #         )

# # #         # =================================================
# # #         # CHANNEL
# # #         # =================================================

# # #         channel = (
# # #             contact.suppression_channel
# # #             if contact.suppression_channel
# # #             else "Email"
# # #         )

# # #         # =================================================
# # #         # RESULT
# # #         # =================================================

# # #         result.append({
# # #             "id": contact.id,
# # #             "name": contact.full_name,
# # #             "contact": contact_value,
# # #             "channel": channel,
# # #             "reason": (
# # #                 contact.suppression_reason
# # #                 if contact.suppression_reason
# # #                 else "Manual Blacklist"
# # #             ),
# # #             "source": (
# # #                 list_name
# # #                 if list_name
# # #                 else "No List"
# # #             ),
# # #             "since": contact.suppressed_at,
# # #             "status": contact.status
# # #         })

# # #     return result


# # # # =====================================================
# # # # SUPPRESS CONTACT
# # # # =====================================================

# # # @router.patch("/{contact_id}/suppress")
# # # def suppress_contact(
# # #     contact_id: int,
# # #     payload: dict,
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     contact = (
# # #         db.query(Contact)
# # #         .filter(Contact.id == contact_id)
# # #         .first()
# # #     )

# # #     if not contact:

# # #         return {
# # #             "success": False,
# # #             "message": "Contact not found"
# # #         }

# # #     # =================================================
# # #     # UPDATE CONTACT
# # #     # =================================================

# # #     contact.status = "suppressed"

# # #     contact.is_suppressed = True

# # #     contact.suppression_channel = payload.get(
# # #         "channel",
# # #         "Email"
# # #     )

# # #     contact.suppression_reason = payload.get(
# # #         "reason",
# # #         "Manual Blacklist"
# # #     )

# # #     contact.suppressed_at = datetime.utcnow()

# # #     contact.updated_at = datetime.utcnow()

# # #     db.commit()

# # #     return {
# # #         "success": True,
# # #         "message": "Contact suppressed successfully"
# # #     }


# # # # =====================================================
# # # # RESTORE CONTACT
# # # # =====================================================

# # # @router.patch("/{contact_id}/restore")
# # # def restore_contact(
# # #     contact_id: int,
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     contact = (
# # #         db.query(Contact)
# # #         .filter(Contact.id == contact_id)
# # #         .first()
# # #     )

# # #     if not contact:

# # #         return {
# # #             "success": False,
# # #             "message": "Contact not found"
# # #         }

# # #     # =================================================
# # #     # RESTORE CONTACT
# # #     # =================================================

# # #     contact.status = "active"

# # #     contact.is_suppressed = False

# # #     contact.suppression_channel = None

# # #     contact.suppression_reason = None

# # #     contact.suppressed_at = None

# # #     contact.updated_at = datetime.utcnow()

# # #     db.commit()

# # #     return {
# # #         "success": True,
# # #         "message": "Contact restored successfully"
# # #     }


# # # # =====================================================
# # # # COUNT BY LIST
# # # # =====================================================

# # # @router.get("/count-by-list/{list_id}")
# # # def get_suppression_count_by_list(
# # #     list_id: int,
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     count = (
# # #         db.query(Contact)
# # #         .join(
# # #             ListContact,
# # #             ListContact.contact_id == Contact.id
# # #         )
# # #         .filter(
# # #             ListContact.list_id == list_id,
# # #             Contact.is_suppressed == True
# # #         )
# # #         .count()
# # #     )

# # #     return {
# # #         "list_id": list_id,
# # #         "suppressed_count": count
# # #     }


# # # # =====================================================
# # # # ESTIMATE SUPPRESSION
# # # # =====================================================

# # # @router.post("/estimate")
# # # def estimate_suppression(
# # #     payload: dict,
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     list_ids = payload.get("list_ids", [])

# # #     if not list_ids:

# # #         return {
# # #             "suppressed_count": 0
# # #         }

# # #     count = (
# # #         db.query(Contact)
# # #         .join(
# # #             ListContact,
# # #             ListContact.contact_id == Contact.id
# # #         )
# # #         .filter(
# # #             ListContact.list_id.in_(list_ids),
# # #             Contact.is_suppressed == True
# # #         )
# # #         .count()
# # #     )

# # #     return {
# # #         "suppressed_count": count
# # #     }


# # from fastapi import APIRouter, Depends
# # from sqlalchemy.orm import Session
# # from datetime import datetime

# # from app.database import get_main_db

# # from app.models.contact import Contact
# # from app.models.suppression import Suppression

# # from app.models.lists import (
# #     ListContact,
# #     AudienceList
# # )

# # router = APIRouter()


# # # =====================================================
# # # GET SUPPRESSED CONTACTS
# # # =====================================================

# # @router.get("/")
# # def get_suppressed_contacts(
# #     db: Session = Depends(get_main_db)
# # ):

# #     contacts = (
# #         db.query(
# #             ListContact.id,
# #             ListContact.contact_id,
# #             ListContact.name,
# #             ListContact.email,
# #             ListContact.phone,
# #             ListContact.status,
# #             ListContact.suppression_reason,
# #             ListContact.suppressed_at,
# #             ListContact.suppression_channel,
# #             AudienceList.list_name
# #         )
# #         .join(
# #             AudienceList,
# #             AudienceList.id == ListContact.list_id
# #         )
# #         .filter(
# #             ListContact.is_suppressed == True
# #         )
# #         .all()
# #     )

# #     result = []

# #     for item in contacts:

# #         result.append({
# #             "id": item.id,
# #             "contact_id": item.contact_id,

# #             # NEW
# #             "name": item.name,
# #             "email": item.email,
# #             "phone": item.phone,

# #             "channel": item.suppression_channel or "Email",
# #             "reason": item.suppression_reason or "Manual Blacklist",
# #             "source": item.list_name,
# #             "since": item.suppressed_at,
# #             "status": item.status
# #         })

# #     return result

# #     contacts = (
# #         db.query(
# #             Contact,
# #             Suppression,
# #             AudienceList.list_name
# #         )
# #         .join(
# #             Suppression,
# #             Suppression.contact_id == Contact.id
# #         )
# #         .outerjoin(
# #             ListContact,
# #             ListContact.contact_id == Contact.id
# #         )
# #         .outerjoin(
# #             AudienceList,
# #             AudienceList.id == ListContact.list_id
# #         )
# #         .all()
# #     )

# #     result = []

# #     for contact, suppression, list_name in contacts:

# #         contact_value = (
# #             contact.email
# #             if suppression.channel == "Email"
# #             else contact.phone
# #         )

# #         result.append({
# #             "id": contact.id,
# #             "name": contact.full_name,
# #             "contact": contact_value,
# #             "channel": suppression.channel,
# #             "reason": suppression.reason,
# #             "source": (
# #                 list_name
# #                 if list_name
# #                 else "No List"
# #             ),
# #             "since": suppression.created_at,
# #             "status": contact.status
# #         })

# #     return result


# # # =====================================================
# # # SUPPRESS CONTACT
# # # =====================================================

# # @router.patch("/{contact_id}/suppress")
# # def suppress_contact(
# #     contact_id: int,
# #     payload: dict,
# #     db: Session = Depends(get_main_db)
# # ):

# #     # =================================================
# #     # FIND CONTACT
# #     # =================================================

# #     contact = (
# #         db.query(Contact)
# #         .filter(Contact.id == contact_id)
# #         .first()
# #     )

# #     if not contact:

# #         return {
# #             "success": False,
# #             "message": "Contact not found"
# #         }

# #     # =================================================
# #     # UPDATE CONTACT STATUS
# #     # =================================================

# #     contact.status = "suppressed"

# #     contact.updated_at = datetime.utcnow()

# #     # =================================================
# #     # CHECK EXISTING SUPPRESSION
# #     # =================================================

# #     existing = (
# #         db.query(Suppression)
# #         .filter(
# #             Suppression.contact_id == contact_id
# #         )
# #         .first()
# #     )

# #     if not existing:

# #         suppression = Suppression(
# #             contact_id=contact_id,
# #             channel=payload.get(
# #                 "channel",
# #                 "Email"
# #             ),
# #             reason=payload.get(
# #                 "reason",
# #                 "Manual Blacklist"
# #             ),
# #             created_at=datetime.utcnow()
# #         )

# #         db.add(suppression)

# #     db.commit()

# #     return {
# #         "success": True,
# #         "message": "Contact suppressed successfully"
# #     }


# # # =====================================================
# # # RESTORE CONTACT
# # # =====================================================

# # @router.patch("/{contact_id}/restore")
# # def restore_contact(
# #     contact_id: int,
# #     db: Session = Depends(get_main_db)
# # ):

# #     # =================================================
# #     # FIND CONTACT
# #     # =================================================

# #     contact = (
# #         db.query(Contact)
# #         .filter(Contact.id == contact_id)
# #         .first()
# #     )

# #     if not contact:

# #         return {
# #             "success": False,
# #             "message": "Contact not found"
# #         }

# #     # =================================================
# #     # RESTORE CONTACT
# #     # =================================================

# #     contact.status = "active"

# #     contact.updated_at = datetime.utcnow()

# #     # =================================================
# #     # DELETE SUPPRESSION
# #     # =================================================

# #     suppression = (
# #         db.query(Suppression)
# #         .filter(
# #             Suppression.contact_id == contact_id
# #         )
# #         .first()
# #     )

# #     if suppression:

# #         db.delete(suppression)

# #     db.commit()

# #     return {
# #         "success": True,
# #         "message": "Contact restored successfully"
# #     }


# # # =====================================================
# # # COUNT BY LIST
# # # =====================================================

# # @router.get("/count-by-list/{list_id}")
# # def get_suppression_count_by_list(
# #     list_id: int,
# #     db: Session = Depends(get_main_db)
# # ):

# #     count = (
# #         db.query(Suppression)
# #         .join(
# #             Contact,
# #             Contact.id == Suppression.contact_id
# #         )
# #         .join(
# #             ListContact,
# #             ListContact.contact_id == Contact.id
# #         )
# #         .filter(
# #             ListContact.list_id == list_id
# #         )
# #         .count()
# #     )

# #     return {
# #         "list_id": list_id,
# #         "suppressed_count": count
# #     }


# # # =====================================================
# # # ESTIMATE SUPPRESSION
# # # =====================================================

# # @router.post("/estimate")
# # def estimate_suppression(
# #     payload: dict,
# #     db: Session = Depends(get_main_db)
# # ):

# #     list_ids = payload.get("list_ids", [])

# #     if not list_ids:

# #         return {
# #             "suppressed_count": 0
# #         }

# #     count = (
# #         db.query(Suppression)
# #         .join(
# #             Contact,
# #             Contact.id == Suppression.contact_id
# #         )
# #         .join(
# #             ListContact,
# #             ListContact.contact_id == Contact.id
# #         )
# #         .filter(
# #             ListContact.list_id.in_(list_ids)
# #         )
# #         .count()
# #     )

# #     return {
# #         "suppressed_count": count
# #     }


# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from datetime import datetime

# from app.database import get_main_db
# from app.models.contact import Contact

# router = APIRouter()


# # =====================================================
# # GET SUPPRESSED CONTACTS
# # =====================================================

# @router.get("/")
# def get_suppressed_contacts(
#     db: Session = Depends(get_main_db)
# ):

#     suppressed_contacts = (
#         db.query(Contact)
#         .filter(
#             Contact.status == "suppressed"
#         )
#         .all()
#     )

#     result = []

#     for contact in suppressed_contacts:

#         result.append({
#             "id": contact.id,
#             "contact_id": contact.id,
#             "name": contact.full_name,
#             "email": contact.email,
#             "phone": contact.phone,
#             "channel": (
#                 "WhatsApp"
#                 if getattr(contact, "is_whatsapp", False)
#                 else "Email"
#             ),
#             "reason": (
#                 getattr(contact, "suppression_reason", None)
#                 or "Manual Blacklist"
#             ),
#             "source": "-",
#             "since": getattr(contact, "suppressed_at", None),
#             "status": contact.status
#         })

#     return result


# # =====================================================
# # SUPPRESS CONTACT
# # =====================================================

# @router.patch("/{contact_id}/suppress")
# def suppress_contact(
#     contact_id: int,
#     payload: dict,
#     db: Session = Depends(get_main_db)
# ):

#     contact = (
#         db.query(Contact)
#         .filter(Contact.id == contact_id)
#         .first()
#     )

#     if not contact:
#         return {
#             "success": False,
#             "message": "Contact not found"
#         }

#     contact.status = "suppressed"

#     if hasattr(contact, "is_suppressed"):
#         contact.is_suppressed = True

#     if hasattr(contact, "suppression_reason"):
#         contact.suppression_reason = payload.get(
#             "reason",
#             "Manual Blacklist"
#         )

#     if hasattr(contact, "suppressed_at"):
#         contact.suppressed_at = datetime.utcnow()

#     if hasattr(contact, "updated_at"):
#         contact.updated_at = datetime.utcnow()

#     db.commit()

#     return {
#         "success": True,
#         "message": "Contact suppressed successfully"
#     }


# # =====================================================
# # RESTORE CONTACT
# # =====================================================

# @router.patch("/{contact_id}/restore")
# def restore_contact(
#     contact_id: int,
#     db: Session = Depends(get_main_db)
# ):

#     contact = (
#         db.query(Contact)
#         .filter(Contact.id == contact_id)
#         .first()
#     )

#     if not contact:
#         return {
#             "success": False,
#             "message": "Contact not found"
#         }

#     contact.status = "active"

#     if hasattr(contact, "is_suppressed"):
#         contact.is_suppressed = False

#     if hasattr(contact, "suppression_reason"):
#         contact.suppression_reason = None

#     if hasattr(contact, "suppressed_at"):
#         contact.suppressed_at = None

#     if hasattr(contact, "updated_at"):
#         contact.updated_at = datetime.utcnow()

#     db.commit()

#     return {
#         "success": True,
#         "message": "Contact restored successfully"
#     }


# # =====================================================
# # COUNT BY LIST
# # =====================================================

# @router.get("/count-by-list/{list_id}")
# def get_suppression_count_by_list(
#     list_id: int,
#     db: Session = Depends(get_main_db)
# ):

#     count = (
#         db.query(Contact)
#         .filter(Contact.status == "suppressed")
#         .count()
#     )

#     return {
#         "list_id": list_id,
#         "suppressed_count": count
#     }


# # =====================================================
# # ESTIMATE SUPPRESSION
# # =====================================================

# @router.post("/estimate")
# def estimate_suppression(
#     payload: dict,
#     db: Session = Depends(get_main_db)
# ):

#     count = (
#         db.query(Contact)
#         .filter(Contact.status == "suppressed")
#         .count()
#     )

#     return {
#         "suppressed_count": count
#     }


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_main_db

from app.models.contact import Contact

from app.models.lists import AudienceList, ListContact

router = APIRouter()


# =====================================================
# GET SUPPRESSED CONTACTS
# =====================================================


@router.get("/")
def get_suppressed_contacts(db: Session = Depends(get_main_db)):

    contacts = db.query(Contact).filter(Contact.status == "suppressed").all()

    result = []

    for contact in contacts:

        # ==========================================
        # GET CONTACT LISTS
        # ==========================================

     

        # ==========================================
        # CHANNEL
        # ==========================================

        # channel = "Email"

        # if getattr(contact, "phone", None):
        #     channel = "WhatsApp"

        channel = getattr(contact, "suppression_channel", None) or "Email"

        # ==========================================
        # RESPONSE
        # ==========================================

        result.append(
            {
                "id": contact.id,
                "contact_id": contact.id,
                "name": contact.full_name,
                "email": contact.email,
                "phone": contact.phone,
                "channel": channel,
                "reason": getattr(contact, "suppression_reason", None)
                or "Manual Blacklist",
                # ✅ SOURCE COLUMN
                "source": getattr(contact, "suppression_source", None) or "Admin",
                "since": getattr(contact, "suppressed_at", None),
                "status": contact.status,
            }
        )

    return result


# =====================================================
# SUPPRESS CONTACT
# =====================================================


@router.patch("/{contact_id}/suppress")
def suppress_contact(
    contact_id: int, payload: dict, db: Session = Depends(get_main_db)
):

    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if not contact:

        return {"success": False, "message": "Contact not found"}

    contact.status = "suppressed"

    if hasattr(contact, "is_suppressed"):
        contact.is_suppressed = True

    if hasattr(contact, "suppression_reason"):
        contact.suppression_reason = payload.get("reason", "Manual Blacklist")

    if hasattr(contact, "suppression_channel"):
        contact.suppression_channel = payload.get("channel", "Email")

    if hasattr(contact, "suppressed_at"):
        contact.suppressed_at = datetime.utcnow()

    if hasattr(contact, "updated_at"):
        contact.updated_at = datetime.utcnow()

    db.commit()

    return {"success": True, "message": "Contact suppressed successfully"}


# =====================================================
# RESTORE CONTACT
# =====================================================


@router.patch("/{contact_id}/restore")
def restore_contact(contact_id: int, db: Session = Depends(get_main_db)):

    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if not contact:

        return {"success": False, "message": "Contact not found"}

    contact.status = "active"

    if hasattr(contact, "is_suppressed"):
        contact.is_suppressed = False

    if hasattr(contact, "suppression_reason"):
        contact.suppression_reason = None

    if hasattr(contact, "suppressed_at"):
        contact.suppressed_at = None

    if hasattr(contact, "suppression_channel"):
        contact.suppression_channel = None

    if hasattr(contact, "updated_at"):
        contact.updated_at = datetime.utcnow()

    db.commit()

    return {"success": True, "message": "Contact restored successfully"}


# =====================================================
# COUNT BY LIST
# =====================================================


@router.get("/count-by-list/{list_id}")
def get_suppression_count_by_list(list_id: int, db: Session = Depends(get_main_db)):

    count = db.query(Contact).filter(Contact.status == "suppressed").count()

    return {"list_id": list_id, "suppressed_count": count}


# =====================================================
# ESTIMATE SUPPRESSION
# =====================================================


@router.post("/estimate")
def estimate_suppression(payload: dict, db: Session = Depends(get_main_db)):

    count = db.query(Contact).filter(Contact.status == "suppressed").count()

    return {"suppressed_count": count}

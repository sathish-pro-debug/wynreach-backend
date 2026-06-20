# # # # # =====================================================
# # # # # app/routers/contact.py
# # # # # =====================================================

# # # # from fastapi import APIRouter, Depends
# # # # from sqlalchemy.orm import Session
# # # # from datetime import datetime

# # # # from app.database import get_main_db

# # # # from app.models.contact import Contact

# # # # from app.models.lists import (
# # # #     AudienceList,
# # # #     ListContact
# # # # )

# # # # from app.schemas.contact import (
# # # #     ContactCreate,
# # # #     ContactUpdate
# # # # )

# # # # router = APIRouter()


# # # # # =====================================================
# # # # # GET CONTACTS
# # # # # =====================================================

# # # # @router.get("/")
# # # # def get_contacts(
# # # #     db: Session = Depends(get_main_db)
# # # # ):

# # # #     contacts = db.query(Contact).all()

# # # #     result = []

# # # #     for contact in contacts:

# # # #         # ==========================================
# # # #         # GET LIST MAPPING
# # # #         # ==========================================

# # # #         list_mapping = (
# # # #             db.query(ListContact)
# # # #             .filter(
# # # #                 ListContact.contact_id == contact.id
# # # #             )
# # # #             .first()
# # # #         )

# # # #         list_name = "—"

# # # #         if list_mapping:

# # # #             list_data = (
# # # #                 db.query(AudienceList)
# # # #                 .filter(
# # # #                     AudienceList.id == list_mapping.list_id
# # # #                 )
# # # #                 .first()
# # # #             )

# # # #             if list_data:
# # # #                 list_name = list_data.list_name

# # # #         # ==========================================
# # # #         # TAGS SAFE HANDLING
# # # #         # ==========================================

# # # #         tags_value = []

# # # #         if contact.tags:

# # # #             if isinstance(contact.tags, list):

# # # #                 tags_value = contact.tags

# # # #             else:

# # # #                 tags_value = [contact.tags]

# # # #         # ==========================================
# # # #         # RESPONSE
# # # #         # ==========================================

# # # #         result.append({

# # # #             "id": contact.id,

# # # #             "name": contact.full_name,

# # # #             "email": contact.email,

# # # #             "phone": contact.phone,

# # # #             "status": contact.status,

# # # #             "tags": tags_value,

# # # #             "score": contact.score,

# # # #             "list_name": list_name,

# # # #             "last_campaign": contact.campaign,

# # # #             "is_suppressed": contact.is_suppressed,

# # # #             "suppression_reason": contact.suppression_reason,

# # # #             "suppressed_at": contact.suppressed_at
# # # #         })

# # # #     return result


# # # # # =====================================================
# # # # # CREATE CONTACT
# # # # # =====================================================

# # # # @router.post("/")
# # # # def create_contact(
# # # #     payload: ContactCreate,
# # # #     db: Session = Depends(get_main_db)
# # # # ):

# # # #     # ==========================================
# # # #     # TAGS SAFE HANDLING
# # # #     # ==========================================

# # # #     tags_value = []

# # # #     if payload.tags:

# # # #         if isinstance(payload.tags, list):

# # # #             tags_value = payload.tags

# # # #         else:

# # # #             tags_value = [payload.tags]

# # # #     # ==========================================
# # # #     # CREATE CONTACT
# # # #     # ==========================================

# # # #     new_contact = Contact(

# # # #         full_name=payload.full_name,

# # # #         email=payload.email,

# # # #         phone=payload.phone,

# # # #         status=payload.status,

# # # #         tags=tags_value,

# # # #         score=payload.score,

# # # #         campaign=payload.campaign,

# # # #         created_at=datetime.utcnow(),

# # # #         updated_at=datetime.utcnow()
# # # #     )

# # # #     db.add(new_contact)

# # # #     db.commit()

# # # #     db.refresh(new_contact)

# # # #     # ==========================================
# # # #     # CREATE LIST MAPPING
# # # #     # ==========================================

# # # #     list_contact = ListContact(

# # # #         contact_id=new_contact.id,

# # # #         list_id=payload.list_id
# # # #     )

# # # #     db.add(list_contact)

# # # #     db.commit()

# # # #     return {
# # # #         "message": "Contact created successfully"
# # # #     }


# # # # # =====================================================
# # # # # UPDATE CONTACT
# # # # # =====================================================

# # # # @router.put("/{contact_id}")
# # # # def update_contact(
# # # #     contact_id: int,
# # # #     payload: ContactUpdate,
# # # #     db: Session = Depends(get_main_db)
# # # # ):

# # # #     contact = (
# # # #         db.query(Contact)
# # # #         .filter(Contact.id == contact_id)
# # # #         .first()
# # # #     )

# # # #     if not contact:

# # # #         return {
# # # #             "message": "Contact not found"
# # # #         }

# # # #     # ==========================================
# # # #     # UPDATE FIELDS
# # # #     # ==========================================

# # # #     if payload.full_name is not None:

# # # #         contact.full_name = payload.full_name

# # # #     if payload.email is not None:

# # # #         contact.email = payload.email

# # # #     if payload.phone is not None:

# # # #         contact.phone = payload.phone

# # # #     if payload.status is not None:

# # # #         contact.status = payload.status

# # # #     # ==========================================
# # # #     # TAGS SAFE UPDATE
# # # #     # ==========================================

# # # #     if payload.tags is not None:

# # # #         if isinstance(payload.tags, list):

# # # #             contact.tags = payload.tags

# # # #         else:

# # # #             contact.tags = [payload.tags]

# # # #     if payload.score is not None:

# # # #         contact.score = payload.score

# # # #     if payload.campaign is not None:

# # # #         contact.campaign = payload.campaign

# # # #     contact.updated_at = datetime.utcnow()

# # # #     db.commit()

# # # #     return {
# # # #         "message": "Contact updated successfully"
# # # #     }


# # # # # =====================================================
# # # # # DELETE CONTACT
# # # # # =====================================================

# # # # @router.delete("/{contact_id}")
# # # # def delete_contact(
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
# # # #             "message": "Contact not found"
# # # #         }

# # # #     # ==========================================
# # # #     # DELETE LIST MAPPINGS
# # # #     # ==========================================

# # # #     db.query(ListContact).filter(
# # # #         ListContact.contact_id == contact_id
# # # #     ).delete()

# # # #     # ==========================================
# # # #     # DELETE CONTACT
# # # #     # ==========================================

# # # #     db.delete(contact)

# # # #     db.commit()

# # # #     return {
# # # #         "message": "Contact deleted successfully"
# # # #     }


# # # # =====================================================
# # # # app/routers/contact.py
# # # # =====================================================

# # # from fastapi import (
# # #     APIRouter,
# # #     Depends,
# # #     HTTPException
# # # )

# # # from sqlalchemy.orm import Session

# # # from datetime import datetime

# # # from app.database import get_main_db

# # # from app.models.contact import Contact

# # # from app.models.lists import (
# # #     AudienceList,
# # #     ListContact
# # # )

# # # from app.schemas.contact import (
# # #     ContactCreate,
# # #     ContactUpdate
# # # )

# # # router = APIRouter()


# # # # =====================================================
# # # # GET CONTACTS
# # # # =====================================================

# # # @router.get("/")
# # # def get_contacts(
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     contacts = db.query(Contact).all()

# # #     result = []

# # #     for contact in contacts:

# # #         # ==========================================
# # #         # GET ALL LISTS OF CONTACT
# # #         # ==========================================

# # #         mappings = (
# # #             db.query(ListContact)
# # #             .filter(
# # #                 ListContact.contact_id == contact.id
# # #             )
# # #             .all()
# # #         )

# # #         lists = []

# # #         for mapping in mappings:

# # #             audience_list = (
# # #                 db.query(AudienceList)
# # #                 .filter(
# # #                     AudienceList.id == mapping.list_id
# # #                 )
# # #                 .first()
# # #             )

# # #             if audience_list:

# # #                 lists.append({

# # #                     "id": audience_list.id,

# # #                     "name": audience_list.list_name
# # #                 })

# # #         # ==========================================
# # #         # TAGS SAFE HANDLING
# # #         # ==========================================

# # #         tags_value = []

# # #         if contact.tags:

# # #             if isinstance(contact.tags, list):

# # #                 tags_value = contact.tags

# # #             else:

# # #                 tags_value = [contact.tags]

# # #         # ==========================================
# # #         # RESPONSE
# # #         # ==========================================

# # #         result.append({

# # #             "id": contact.id,

# # #             "name": contact.full_name,

# # #             "email": contact.email,

# # #             "phone": contact.phone,

# # #             "status": contact.status,

# # #             "tags": tags_value,

# # #             "score": contact.score,

# # #             "lists": lists,

# # #             "last_campaign": contact.campaign,

# # #             "is_suppressed": contact.is_suppressed,

# # #             "suppression_reason": contact.suppression_reason,

# # #             "suppressed_at": contact.suppressed_at
# # #         })

# # #     return result


# # # # =====================================================
# # # # CREATE CONTACT
# # # # =====================================================

# # # @router.post("/")
# # # def create_contact(
# # #     payload: ContactCreate,
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     # ==========================================
# # #     # CHECK LIST EXISTS
# # #     # ==========================================

# # #     audience_list = (
# # #         db.query(AudienceList)
# # #         .filter(
# # #             AudienceList.id == payload.list_id
# # #         )
# # #         .first()
# # #     )

# # #     if not audience_list:

# # #         raise HTTPException(
# # #             status_code=404,
# # #             detail="List not found"
# # #         )

# # #     # ==========================================
# # #     # TAGS SAFE HANDLING
# # #     # ==========================================

# # #     tags_value = []

# # #     if payload.tags:

# # #         if isinstance(payload.tags, list):

# # #             tags_value = payload.tags

# # #         else:

# # #             tags_value = [payload.tags]

# # #     # ==========================================
# # #     # CHECK EXISTING CONTACT
# # #     # ==========================================

# # #     existing_contact = (
# # #         db.query(Contact)
# # #         .filter(
# # #             Contact.email == payload.email
# # #         )
# # #         .first()
# # #     )

# # #     # ==========================================
# # #     # USE EXISTING CONTACT
# # #     # ==========================================

# # #     if existing_contact:

# # #         contact = existing_contact

# # #     else:

# # #         # ======================================
# # #         # CREATE NEW CONTACT
# # #         # ======================================

# # #         contact = Contact(

# # #             full_name=payload.full_name,

# # #             email=payload.email,

# # #             phone=payload.phone,

# # #             status=payload.status,

# # #             tags=tags_value,

# # #             score=payload.score,

# # #             campaign=payload.campaign,

# # #             created_at=datetime.utcnow(),

# # #             updated_at=datetime.utcnow()
# # #         )

# # #         db.add(contact)

# # #         db.commit()

# # #         db.refresh(contact)

# # #     # ==========================================
# # #     # CHECK SAME LIST DUPLICATE
# # #     # ==========================================

# # #     existing_mapping = (
# # #         db.query(ListContact)
# # #         .filter(
# # #             ListContact.contact_id == contact.id,
# # #             ListContact.list_id == payload.list_id
# # #         )
# # #         .first()
# # #     )

# # #     if existing_mapping:

# # #         raise HTTPException(
# # #             status_code=400,
# # #             detail="Contact already exists in this list"
# # #         )

# # #     # ==========================================
# # #     # CREATE LIST MAPPING
# # #     # ==========================================

# # #     list_contact = ListContact(

# # #         contact_id=contact.id,

# # #         list_id=payload.list_id
# # #     )

# # #     db.add(list_contact)

# # #     db.commit()

# # #     return {
# # #         "message": "Contact created successfully"
# # #     }


# # # # =====================================================
# # # # UPDATE CONTACT
# # # # =====================================================

# # # @router.put("/{contact_id}")
# # # def update_contact(
# # #     contact_id: int,
# # #     payload: ContactUpdate,
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     contact = (
# # #         db.query(Contact)
# # #         .filter(
# # #             Contact.id == contact_id
# # #         )
# # #         .first()
# # #     )

# # #     if not contact:

# # #         raise HTTPException(
# # #             status_code=404,
# # #             detail="Contact not found"
# # #         )

# # #     # ==========================================
# # #     # UPDATE FIELDS
# # #     # ==========================================

# # #     if payload.full_name is not None:

# # #         contact.full_name = payload.full_name

# # #     if payload.email is not None:

# # #         # ======================================
# # #         # CHECK EMAIL DUPLICATE
# # #         # ======================================

# # #         existing_email = (
# # #             db.query(Contact)
# # #             .filter(
# # #                 Contact.email == payload.email,
# # #                 Contact.id != contact_id
# # #             )
# # #             .first()
# # #         )

# # #         if existing_email:

# # #             raise HTTPException(
# # #                 status_code=400,
# # #                 detail="Email already exists"
# # #             )

# # #         contact.email = payload.email

# # #     if payload.phone is not None:

# # #         contact.phone = payload.phone

# # #     if payload.status is not None:

# # #         contact.status = payload.status

# # #     # ==========================================
# # #     # TAGS UPDATE
# # #     # ==========================================

# # #     if payload.tags is not None:

# # #         if isinstance(payload.tags, list):

# # #             contact.tags = payload.tags

# # #         else:

# # #             contact.tags = [payload.tags]

# # #     if payload.score is not None:

# # #         contact.score = payload.score

# # #     if payload.campaign is not None:

# # #         contact.campaign = payload.campaign

# # #     # ==========================================
# # #     # UPDATE TIMESTAMP
# # #     # ==========================================

# # #     contact.updated_at = datetime.utcnow()

# # #     db.commit()

# # #     db.refresh(contact)

# # #     return {
# # #         "message": "Contact updated successfully"
# # #     }


# # # # =====================================================
# # # # DELETE CONTACT
# # # # =====================================================

# # # @router.delete("/{contact_id}")
# # # def delete_contact(
# # #     contact_id: int,
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     contact = (
# # #         db.query(Contact)
# # #         .filter(
# # #             Contact.id == contact_id
# # #         )
# # #         .first()
# # #     )

# # #     if not contact:

# # #         raise HTTPException(
# # #             status_code=404,
# # #             detail="Contact not found"
# # #         )

# # #     # ==========================================
# # #     # DELETE ALL LIST MAPPINGS
# # #     # ==========================================

# # #     db.query(ListContact).filter(
# # #         ListContact.contact_id == contact_id
# # #     ).delete()

# # #     # ==========================================
# # #     # DELETE CONTACT
# # #     # ==========================================

# # #     db.delete(contact)

# # #     db.commit()

# # #     return {
# # #         "message": "Contact deleted successfully"
# # #     }


# # # # =====================================================
# # # # ADD EXISTING CONTACT TO ANOTHER LIST
# # # # =====================================================

# # # @router.post("/{contact_id}/add-to-list/{list_id}")
# # # def add_contact_to_list(
# # #     contact_id: int,
# # #     list_id: int,
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     # ==========================================
# # #     # CHECK CONTACT EXISTS
# # #     # ==========================================

# # #     contact = (
# # #         db.query(Contact)
# # #         .filter(
# # #             Contact.id == contact_id
# # #         )
# # #         .first()
# # #     )

# # #     if not contact:

# # #         raise HTTPException(
# # #             status_code=404,
# # #             detail="Contact not found"
# # #         )

# # #     # ==========================================
# # #     # CHECK LIST EXISTS
# # #     # ==========================================

# # #     audience_list = (
# # #         db.query(AudienceList)
# # #         .filter(
# # #             AudienceList.id == list_id
# # #         )
# # #         .first()
# # #     )

# # #     if not audience_list:

# # #         raise HTTPException(
# # #             status_code=404,
# # #             detail="List not found"
# # #         )

# # #     # ==========================================
# # #     # CHECK EXISTING MAPPING
# # #     # ==========================================

# # #     existing_mapping = (
# # #         db.query(ListContact)
# # #         .filter(
# # #             ListContact.contact_id == contact_id,
# # #             ListContact.list_id == list_id
# # #         )
# # #         .first()
# # #     )

# # #     if existing_mapping:

# # #         raise HTTPException(
# # #             status_code=400,
# # #             detail="Contact already exists in this list"
# # #         )

# # #     # ==========================================
# # #     # CREATE NEW MAPPING
# # #     # ==========================================

# # #     new_mapping = ListContact(

# # #         contact_id=contact_id,

# # #         list_id=list_id
# # #     )

# # #     db.add(new_mapping)

# # #     db.commit()

# # #     return {
# # #         "message": "Contact added to list successfully"
# # #     }


# # # # =====================================================
# # # # REMOVE CONTACT FROM LIST
# # # # =====================================================

# # # @router.delete("/{contact_id}/remove-from-list/{list_id}")
# # # def remove_contact_from_list(
# # #     contact_id: int,
# # #     list_id: int,
# # #     db: Session = Depends(get_main_db)
# # # ):

# # #     mapping = (
# # #         db.query(ListContact)
# # #         .filter(
# # #             ListContact.contact_id == contact_id,
# # #             ListContact.list_id == list_id
# # #         )
# # #         .first()
# # #     )

# # #     if not mapping:

# # #         raise HTTPException(
# # #             status_code=404,
# # #             detail="Contact mapping not found"
# # #         )

# # #     db.delete(mapping)

# # #     db.commit()

# # #     return {
# # #         "message": "Contact removed from list successfully"
# # #     }


# # # =====================================================
# # # app/routers/contact.py
# # # =====================================================

# # from fastapi import (
# #     APIRouter,
# #     Depends,
# #     HTTPException
# # )

# # from sqlalchemy.orm import Session

# # from datetime import datetime

# # from app.database import get_main_db

# # from app.models.contact import Contact

# # from app.models.lists import (
# #     AudienceList,
# #     ListContact
# # )

# # from app.schemas.contact import (
# #     ContactCreate,
# #     ContactUpdate
# # )

# # router = APIRouter()


# # # =====================================================
# # # GET CONTACTS
# # # =====================================================

# # @router.get("/")
# # def get_contacts(
# #     db: Session = Depends(get_main_db)
# # ):

# #     # ==========================================
# #     # GET ALL CONTACTS
# #     # ==========================================

# #     contacts = (
# #         db.query(Contact)
# #         .all()
# #     )

# #     # ==========================================
# #     # GET ALL LIST MAPPINGS ONLY ONCE
# #     # ==========================================

# #     mappings = (
# #         db.query(
# #             ListContact.contact_id,
# #             AudienceList.id,
# #             AudienceList.list_name
# #         )
# #         .join(
# #             AudienceList,
# #             AudienceList.id == ListContact.list_id
# #         )
# #         .all()
# #     )

# #     # ==========================================
# #     # GROUP LISTS BY CONTACT
# #     # ==========================================

# #     contact_lists = {}

# #     for mapping in mappings:

# #         if mapping.contact_id not in contact_lists:

# #             contact_lists[mapping.contact_id] = []

# #         contact_lists[mapping.contact_id].append({

# #             "id": mapping.id,

# #             "name": mapping.list_name
# #         })

# #     # ==========================================
# #     # FINAL RESPONSE
# #     # ==========================================

# #     result = []

# #     for contact in contacts:

# #         tags_value = []

# #         if contact.tags:

# #             if isinstance(contact.tags, list):

# #                 tags_value = contact.tags

# #             else:

# #                 tags_value = [contact.tags]

# #         result.append({

# #             "id": contact.id,

# #             "name": contact.full_name,

# #             "email": contact.email,

# #             "phone": contact.phone,

# #             "status": contact.status,

# #             "tags": tags_value,

# #             "score": contact.score,

# #             "lists": contact_lists.get(
# #                 contact.id,
# #                 []
# #             ),

# #             "last_campaign": contact.campaign,

# #             "is_suppressed": contact.is_suppressed,

# #             "suppression_reason": contact.suppression_reason,

# #             "suppressed_at": contact.suppressed_at
# #         })

# #     return result


# # # =====================================================
# # # CREATE CONTACT
# # # =====================================================

# # @router.post("/")
# # def create_contact(
# #     payload: ContactCreate,
# #     db: Session = Depends(get_main_db)
# # ):

# #     # ==========================================
# #     # CHECK LIST EXISTS
# #     # ==========================================

# #     audience_list = (
# #         db.query(AudienceList)
# #         .filter(
# #             AudienceList.id == payload.list_id
# #         )
# #         .first()
# #     )

# #     if not audience_list:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="List not found"
# #         )

# #     # ==========================================
# #     # TAGS SAFE HANDLING
# #     # ==========================================

# #     tags_value = []

# #     if payload.tags:

# #         if isinstance(payload.tags, list):

# #             tags_value = payload.tags

# #         else:

# #             tags_value = [payload.tags]

# #     # ==========================================
# #     # CHECK EXISTING CONTACT
# #     # ==========================================

# #     existing_contact = (
# #         db.query(Contact)
# #         .filter(
# #             Contact.email == payload.email
# #         )
# #         .first()
# #     )

# #     # ==========================================
# #     # USE EXISTING CONTACT
# #     # ==========================================

# #     if existing_contact:

# #         contact = existing_contact

# #     else:

# #         # ======================================
# #         # CREATE NEW CONTACT
# #         # ======================================

# #         contact = Contact(

# #             full_name=payload.full_name,

# #             email=payload.email,

# #             phone=payload.phone,

# #             status=payload.status,

# #             tags=tags_value,

# #             score=payload.score,

# #             campaign=payload.campaign,

# #             created_at=datetime.utcnow(),

# #             updated_at=datetime.utcnow()
# #         )

# #         db.add(contact)

# #         db.commit()

# #         db.refresh(contact)

# #     # ==========================================
# #     # CHECK SAME LIST DUPLICATE
# #     # ==========================================

# #     existing_mapping = (
# #         db.query(ListContact)
# #         .filter(
# #             ListContact.contact_id == contact.id,
# #             ListContact.list_id == payload.list_id
# #         )
# #         .first()
# #     )

# #     if existing_mapping:

# #         raise HTTPException(
# #             status_code=400,
# #             detail="Contact already exists in this list"
# #         )

# #     # ==========================================
# #     # CREATE LIST MAPPING
# #     # ==========================================

# #     list_contact = ListContact(

# #         contact_id=contact.id,

# #         list_id=payload.list_id
# #     )

# #     db.add(list_contact)

# #     db.commit()

# #     return {
# #         "message": "Contact created successfully"
# #     }


# # # =====================================================
# # # UPDATE CONTACT
# # # =====================================================

# # @router.put("/{contact_id}")
# # def update_contact(
# #     contact_id: int,
# #     payload: ContactUpdate,
# #     db: Session = Depends(get_main_db)
# # ):

# #     contact = (
# #         db.query(Contact)
# #         .filter(
# #             Contact.id == contact_id
# #         )
# #         .first()
# #     )

# #     if not contact:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="Contact not found"
# #         )

# #     # ==========================================
# #     # UPDATE FIELDS
# #     # ==========================================

# #     if payload.full_name is not None:

# #         contact.full_name = payload.full_name

# #     if payload.email is not None:

# #         existing_email = (
# #             db.query(Contact)
# #             .filter(
# #                 Contact.email == payload.email,
# #                 Contact.id != contact_id
# #             )
# #             .first()
# #         )

# #         if existing_email:

# #             raise HTTPException(
# #                 status_code=400,
# #                 detail="Email already exists"
# #             )

# #         contact.email = payload.email

# #     if payload.phone is not None:

# #         contact.phone = payload.phone

# #     if payload.status is not None:

# #         contact.status = payload.status

# #     # ==========================================
# #     # TAGS UPDATE
# #     # ==========================================

# #     if payload.tags is not None:

# #         if isinstance(payload.tags, list):

# #             contact.tags = payload.tags

# #         else:

# #             contact.tags = [payload.tags]

# #     if payload.score is not None:

# #         contact.score = payload.score

# #     if payload.campaign is not None:

# #         contact.campaign = payload.campaign

# #     # ==========================================
# #     # UPDATE TIMESTAMP
# #     # ==========================================

# #     contact.updated_at = datetime.utcnow()

# #     db.commit()

# #     db.refresh(contact)

# #     return {
# #         "message": "Contact updated successfully"
# #     }


# # # =====================================================
# # # DELETE CONTACT
# # # =====================================================

# # @router.delete("/{contact_id}")
# # def delete_contact(
# #     contact_id: int,
# #     db: Session = Depends(get_main_db)
# # ):

# #     contact = (
# #         db.query(Contact)
# #         .filter(
# #             Contact.id == contact_id
# #         )
# #         .first()
# #     )

# #     if not contact:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="Contact not found"
# #         )

# #     # ==========================================
# #     # DELETE ALL LIST MAPPINGS
# #     # ==========================================

# #     db.query(ListContact).filter(
# #         ListContact.contact_id == contact_id
# #     ).delete()

# #     # ==========================================
# #     # DELETE CONTACT
# #     # ==========================================

# #     db.delete(contact)

# #     db.commit()

# #     return {
# #         "message": "Contact deleted successfully"
# #     }


# # # =====================================================
# # # ADD EXISTING CONTACT TO ANOTHER LIST
# # # =====================================================

# # @router.post("/{contact_id}/add-to-list/{list_id}")
# # def add_contact_to_list(
# #     contact_id: int,
# #     list_id: int,
# #     db: Session = Depends(get_main_db)
# # ):

# #     # ==========================================
# #     # CHECK CONTACT EXISTS
# #     # ==========================================

# #     contact = (
# #         db.query(Contact)
# #         .filter(
# #             Contact.id == contact_id
# #         )
# #         .first()
# #     )

# #     if not contact:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="Contact not found"
# #         )

# #     # ==========================================
# #     # CHECK LIST EXISTS
# #     # ==========================================

# #     audience_list = (
# #         db.query(AudienceList)
# #         .filter(
# #             AudienceList.id == list_id
# #         )
# #         .first()
# #     )

# #     if not audience_list:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="List not found"
# #         )

# #     # ==========================================
# #     # CHECK EXISTING MAPPING
# #     # ==========================================

# #     existing_mapping = (
# #         db.query(ListContact)
# #         .filter(
# #             ListContact.contact_id == contact_id,
# #             ListContact.list_id == list_id
# #         )
# #         .first()
# #     )

# #     if existing_mapping:

# #         raise HTTPException(
# #             status_code=400,
# #             detail="Contact already exists in this list"
# #         )

# #     # ==========================================
# #     # CREATE NEW MAPPING
# #     # ==========================================

# #     new_mapping = ListContact(

# #         contact_id=contact_id,

# #         list_id=list_id
# #     )

# #     db.add(new_mapping)

# #     db.commit()

# #     return {
# #         "message": "Contact added to list successfully"
# #     }


# # # =====================================================
# # # REMOVE CONTACT FROM LIST
# # # =====================================================

# # @router.delete("/{contact_id}/remove-from-list/{list_id}")
# # def remove_contact_from_list(
# #     contact_id: int,
# #     list_id: int,
# #     db: Session = Depends(get_main_db)
# # ):

# #     mapping = (
# #         db.query(ListContact)
# #         .filter(
# #             ListContact.contact_id == contact_id,
# #             ListContact.list_id == list_id
# #         )
# #         .first()
# #     )

# #     if not mapping:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="Contact mapping not found"
# #         )

# #     db.delete(mapping)

# #     db.commit()

# #     return {
# #         "message": "Contact removed from list successfully"
# #     }


# # =====================================================
# # app/routers/contact.py
# # =====================================================

# from fastapi import APIRouter, Depends, HTTPException

# from sqlalchemy.orm import Session

# from datetime import datetime

# from app.database import get_main_db

# from app.models.contact import Contact

# from app.models.lists import AudienceList, ListContact

# from app.models.suppression import Suppression
# from app.utils.notification_service import create_notification

# from app.schemas.contact import ContactCreate, ContactUpdate

# router = APIRouter()


# # =====================================================
# # GET CONTACTS
# # =====================================================


# @router.get("/")
# def get_contacts(db: Session = Depends(get_main_db)):

#     contacts = db.query(Contact).all()

#     mappings = (
#         db.query(ListContact.contact_id, AudienceList.id, AudienceList.list_name)
#         .join(AudienceList, AudienceList.id == ListContact.list_id)
#         .all()
#     )

#     contact_lists = {}

#     for mapping in mappings:

#         if mapping.contact_id not in contact_lists:

#             contact_lists[mapping.contact_id] = []

#         contact_lists[mapping.contact_id].append(
#             {"id": mapping.id, "name": mapping.list_name}
#         )

#     result = []

#     for contact in contacts:

#         tags_value = []

#         if contact.tags:

#             if isinstance(contact.tags, list):

#                 tags_value = contact.tags

#             else:

#                 tags_value = [contact.tags]

#         result.append(
#             {
#                 "id": contact.id,
#                 "name": contact.full_name,
#                 "email": contact.email,
#                 "phone": contact.phone,
#                 "status": contact.status,
#                 "tags": tags_value,
#                 "score": contact.score,
#                 "lists": contact_lists.get(contact.id, []),
#                 "last_campaign": contact.campaign,
#                 "is_suppressed": contact.is_suppressed,
#                 "suppression_reason": contact.suppression_reason,
#                 "suppressed_at": contact.suppressed_at,
#                 "is_whatsapp": contact.is_whatsapp or False,
#             }
#         )

#     return result


# # =====================================================
# # CREATE CONTACT
# # =====================================================


# @router.post("/")
# def create_contact(payload: ContactCreate, db: Session = Depends(get_main_db)):

#     audience_list = (
#         db.query(AudienceList).filter(AudienceList.id == payload.list_id).first()
#     )

#     if not audience_list:

#         raise HTTPException(status_code=404, detail="List not found")

#     tags_value = []

#     if payload.tags:

#         if isinstance(payload.tags, list):

#             tags_value = payload.tags

#         else:

#             tags_value = [payload.tags]

#     existing_contact = db.query(Contact).filter(Contact.email == payload.email).first()

#     if existing_contact:

#         contact = existing_contact

#     else:

#         contact = Contact(
#             full_name=payload.full_name,
#             email=payload.email,
#             phone=payload.phone,
#             status=payload.status,
#             tags=tags_value,
#             score=payload.score,
#             campaign=payload.campaign,
#             is_whatsapp=payload.is_whatsapp or False,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow(),
#         )

#         db.add(contact)

#         db.commit()

#         db.refresh(contact)

#         create_notification(
#             db=db,
#             notification_type="contactImported",
#             title="Contact Added",
#             message=f'Contact "{contact.full_name}" added successfully',
#         )

#     existing_mapping = (
#         db.query(ListContact)
#         .filter(
#             ListContact.contact_id == contact.id, ListContact.list_id == payload.list_id
#         )
#         .first()
#     )

#     if existing_mapping:

#         raise HTTPException(
#             status_code=400, detail="Contact already exists in this list"
#         )

#     list_contact = ListContact(contact_id=contact.id, list_id=payload.list_id)

#     db.add(list_contact)

#     db.commit()

#     return {"message": "Contact created successfully"}


# # =====================================================
# # UPDATE CONTACT
# # =====================================================


# @router.put("/{contact_id}")
# def update_contact(
#     contact_id: int, payload: ContactUpdate, db: Session = Depends(get_main_db)
# ):

#     contact = db.query(Contact).filter(Contact.id == contact_id).first()

#     if not contact:

#         raise HTTPException(status_code=404, detail="Contact not found")

#     if payload.full_name is not None:

#         contact.full_name = payload.full_name

#     if payload.email is not None:

#         existing_email = (
#             db.query(Contact)
#             .filter(Contact.email == payload.email, Contact.id != contact_id)
#             .first()
#         )

#         if existing_email:

#             raise HTTPException(status_code=400, detail="Email already exists")

#         contact.email = payload.email

#     if payload.phone is not None:

#         contact.phone = payload.phone

#     if payload.status is not None:

#         contact.status = payload.status

#     if payload.tags is not None:

#         if isinstance(payload.tags, list):

#             contact.tags = payload.tags

#         else:

#             contact.tags = [payload.tags]

#     if payload.score is not None:

#         contact.score = payload.score

#     if payload.campaign is not None:

#         contact.campaign = payload.campaign

#     if payload.is_whatsapp is not None:
#         contact.is_whatsapp = payload.is_whatsapp

#     contact.updated_at = datetime.utcnow()

#     db.commit()

#     db.refresh(contact)

#     return {"message": "Contact updated successfully"}


# # =====================================================
# # DELETE CONTACT
# # =====================================================


# @router.delete("/{contact_id}")
# def delete_contact(contact_id: int, db: Session = Depends(get_main_db)):

#     contact = db.query(Contact).filter(Contact.id == contact_id).first()

#     if not contact:

#         raise HTTPException(status_code=404, detail="Contact not found")

#     try:

#         # ==========================================
#         # DELETE SUPPRESSION RECORDS
#         # ==========================================

#         db.query(Suppression).filter(Suppression.contact_id == contact_id).delete(
#             synchronize_session=False
#         )

#         # ==========================================
#         # DELETE LIST MAPPINGS
#         # ==========================================

#         db.query(ListContact).filter(ListContact.contact_id == contact_id).delete(
#             synchronize_session=False
#         )

#         # ==========================================
#         # DELETE CONTACT
#         # ==========================================

#         db.delete(contact)

#         db.commit()

#         return {"success": True, "message": "Contact deleted successfully"}

#     except Exception as e:

#         db.rollback()

#         raise HTTPException(status_code=500, detail=str(e))


# # =====================================================
# # ADD CONTACT TO LIST
# # =====================================================


# @router.post("/{contact_id}/add-to-list/{list_id}")
# def add_contact_to_list(
#     contact_id: int, list_id: int, db: Session = Depends(get_main_db)
# ):

#     contact = db.query(Contact).filter(Contact.id == contact_id).first()

#     if not contact:

#         raise HTTPException(status_code=404, detail="Contact not found")

#     audience_list = db.query(AudienceList).filter(AudienceList.id == list_id).first()

#     if not audience_list:

#         raise HTTPException(status_code=404, detail="List not found")

#     existing_mapping = (
#         db.query(ListContact)
#         .filter(ListContact.contact_id == contact_id, ListContact.list_id == list_id)
#         .first()
#     )

#     if existing_mapping:

#         raise HTTPException(
#             status_code=400, detail="Contact already exists in this list"
#         )

#     new_mapping = ListContact(contact_id=contact_id, list_id=list_id)

#     db.add(new_mapping)

#     db.commit()

#     return {"message": "Contact added to list successfully"}


# # =====================================================
# # REMOVE CONTACT FROM LIST
# # =====================================================


# @router.delete("/{contact_id}/remove-from-list/{list_id}")
# def remove_contact_from_list(
#     contact_id: int, list_id: int, db: Session = Depends(get_main_db)
# ):

#     mapping = (
#         db.query(ListContact)
#         .filter(ListContact.contact_id == contact_id, ListContact.list_id == list_id)
#         .first()
#     )

#     if not mapping:

#         raise HTTPException(status_code=404, detail="Contact mapping not found")

#     db.delete(mapping)

#     db.commit()

#     return {"message": "Contact removed from list successfully"}


# # =====================================================
# # BULK SET WHATSAPP - existing contacts update
# # =====================================================


# @router.post("/bulk-set-whatsapp")
# def bulk_set_whatsapp(db: Session = Depends(get_main_db)):
#     db.query(Contact).filter(Contact.phone.isnot(None), Contact.phone != "").update(
#         {"is_whatsapp": True}, synchronize_session=False
#     )
#     db.commit()
#     return {"message": "Done! All contacts with phone updated."}





# =====================================================
# app/routers/contact.py
# =====================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from app.database import get_main_db
from app.models.contact import Contact
from app.models.lists import AudienceList, ListContact
from app.models.suppression import Suppression
from app.utils.notification_service import create_notification
from app.schemas.contact import ContactCreate, ContactUpdate

router = APIRouter()


# =====================================================
# GET CONTACTS
# =====================================================
@router.get("/")
def get_contacts(db: Session = Depends(get_main_db)):
    contacts = db.query(Contact).all()

    mappings = (
        db.query(ListContact.contact_id, AudienceList.id, AudienceList.list_name)
        .join(AudienceList, AudienceList.id == ListContact.list_id)
        .all()
    )

    contact_lists = {}
    for mapping in mappings:
        if mapping.contact_id not in contact_lists:
            contact_lists[mapping.contact_id] = []
        contact_lists[mapping.contact_id].append(
            {"id": mapping.id, "name": mapping.list_name}
        )

    result = []
    for contact in contacts:
        tags_value = []
        if contact.tags:
            if isinstance(contact.tags, list):
                tags_value = contact.tags
            else:
                tags_value = [contact.tags]

        result.append(
            {
                "id": contact.id,
                "name": contact.full_name,
                "email": contact.email,
                "phone": contact.phone,
                "status": contact.status,
                "tags": tags_value,
                "score": contact.score,
                "lists": contact_lists.get(contact.id, []),
                "last_campaign": contact.campaign,
                "is_suppressed": contact.is_suppressed,
                "suppression_reason": contact.suppression_reason,
                "suppressed_at": contact.suppressed_at,
                "is_whatsapp": contact.is_whatsapp or False,
            }
        )

    return result


# =====================================================
# CREATE CONTACT
# =====================================================
@router.post("/")
def create_contact(payload: ContactCreate, db: Session = Depends(get_main_db)):
    # Check if list exists
    audience_list = db.query(AudienceList).filter(AudienceList.id == payload.list_id).first()
    if not audience_list:
        raise HTTPException(status_code=404, detail="List not found")

    # Process tags
    tags_value = []
    if payload.tags:
        if isinstance(payload.tags, list):
            tags_value = payload.tags
        else:
            tags_value = [payload.tags]

    # Find or create contact
    existing_contact = db.query(Contact).filter(Contact.email == payload.email).first()
    if existing_contact:
        contact = existing_contact
    else:
        contact = Contact(
            full_name=payload.full_name,
            email=payload.email,
            phone=payload.phone,
            status=payload.status,
            tags=tags_value,
            score=payload.score,
            campaign=payload.campaign,
            is_whatsapp=payload.is_whatsapp or False,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(contact)
        db.commit()
        db.refresh(contact)

        # Create notification
        create_notification(
            db=db,
            notification_type="contactImported",
            title="Contact Added",
            message=f'Contact "{contact.full_name}" added successfully',
        )

    # Check if contact already belongs to this list
    existing_mapping = (
        db.query(ListContact)
        .filter(
            ListContact.contact_id == contact.id,
            ListContact.list_id == payload.list_id
        )
        .first()
    )
    if existing_mapping:
        return {"message": "Contact already exists in this list"}

    # Create list mapping
    list_contact = ListContact(contact_id=contact.id, list_id=payload.list_id)
    db.add(list_contact)
    db.commit()

    return {"message": "Contact created successfully"}


# =====================================================
# UPDATE CONTACT
# =====================================================
@router.put("/{contact_id}")
def update_contact(
    contact_id: int, payload: ContactUpdate, db: Session = Depends(get_main_db)
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    if payload.full_name is not None:
        contact.full_name = payload.full_name

    if payload.email is not None:
        existing_email = (
            db.query(Contact)
            .filter(Contact.email == payload.email, Contact.id != contact_id)
            .first()
        )
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        contact.email = payload.email

    if payload.phone is not None:
        contact.phone = payload.phone

    if payload.status is not None:
        contact.status = payload.status

    if payload.tags is not None:
        if isinstance(payload.tags, list):
            contact.tags = payload.tags
        else:
            contact.tags = [payload.tags]

    if payload.score is not None:
        contact.score = payload.score

    if payload.campaign is not None:
        contact.campaign = payload.campaign

    if payload.is_whatsapp is not None:
        contact.is_whatsapp = payload.is_whatsapp

    contact.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(contact)

    return {"message": "Contact updated successfully"}


# =====================================================
# DELETE CONTACT
# =====================================================
@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_main_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    try:
        # Delete suppression records
        db.query(Suppression).filter(Suppression.contact_id == contact_id).delete(
            synchronize_session=False
        )

        # Delete list mappings
        db.query(ListContact).filter(ListContact.contact_id == contact_id).delete(
            synchronize_session=False
        )

        # Delete contact
        db.delete(contact)
        db.commit()

        return {"success": True, "message": "Contact deleted successfully"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# =====================================================
# ADD CONTACT TO LIST
# =====================================================
@router.post("/{contact_id}/add-to-list/{list_id}")
def add_contact_to_list(
    contact_id: int, list_id: int, db: Session = Depends(get_main_db)
):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    audience_list = db.query(AudienceList).filter(AudienceList.id == list_id).first()
    if not audience_list:
        raise HTTPException(status_code=404, detail="List not found")

    existing_mapping = (
        db.query(ListContact)
        .filter(ListContact.contact_id == contact_id, ListContact.list_id == list_id)
        .first()
    )
    if existing_mapping:
        raise HTTPException(
            status_code=400, detail="Contact already exists in this list"
        )

    new_mapping = ListContact(contact_id=contact_id, list_id=list_id)
    db.add(new_mapping)
    db.commit()

    return {"message": "Contact added to list successfully"}


# =====================================================
# REMOVE CONTACT FROM LIST
# =====================================================
@router.delete("/{contact_id}/remove-from-list/{list_id}")
def remove_contact_from_list(
    contact_id: int, list_id: int, db: Session = Depends(get_main_db)
):
    mapping = (
        db.query(ListContact)
        .filter(ListContact.contact_id == contact_id, ListContact.list_id == list_id)
        .first()
    )
    if not mapping:
        raise HTTPException(status_code=404, detail="Contact mapping not found")

    db.delete(mapping)
    db.commit()

    return {"message": "Contact removed from list successfully"}


# =====================================================
# BULK SET WHATSAPP - existing contacts update
# =====================================================
@router.post("/bulk-set-whatsapp")
def bulk_set_whatsapp(db: Session = Depends(get_main_db)):
    db.query(Contact).filter(Contact.phone.isnot(None), Contact.phone != "").update(
        {"is_whatsapp": True}, synchronize_session=False
    )
    db.commit()
    return {"message": "Done! All contacts with phone updated."}


# # # =====================================================
# # # app/routers/lists.py
# # # =====================================================

# # from fastapi import (
# #     APIRouter,
# #     Depends,
# #     HTTPException
# # )

# # from sqlalchemy.orm import Session

# # from pydantic import BaseModel

# # from typing import Optional

# # from datetime import datetime

# # from app.database import get_main_db

# # from app.models.lists import (
# #     AudienceList,
# #     ListContact
# # )

# # router = APIRouter()


# # # =====================================================
# # # SCHEMA
# # # =====================================================

# # class ListCreate(BaseModel):

# #     list_name: str

# #     description: Optional[str] = None

# #     is_archived: Optional[bool] = False


# # # =====================================================
# # # GET ALL LISTS
# # # =====================================================

# # @router.get("/")
# # def get_lists(
# #     db: Session = Depends(get_main_db)
# # ):

# #     # ==========================================
# #     # GET ALL LISTS
# #     # ==========================================

# #     lists = (
# #         db.query(AudienceList)
# #         .all()
# #     )

# #     # ==========================================
# #     # GET ALL CONTACT MAPPINGS ONLY ONCE
# #     # ==========================================

# #     mappings = (
# #         db.query(ListContact)
# #         .all()
# #     )

# #     # ==========================================
# #     # GROUP COUNTS
# #     # ==========================================

# #     list_counts = {}

# #     for mapping in mappings:

# #         if mapping.list_id not in list_counts:

# #             list_counts[mapping.list_id] = 0

# #         list_counts[mapping.list_id] += 1

# #     # ==========================================
# #     # FINAL RESPONSE
# #     # ==========================================

# #     result = []

# #     for item in lists:

# #         total_contacts = list_counts.get(
# #             item.id,
# #             0
# #         )

# #         result.append({

# #             "id": item.id,

# #             "list_name": item.list_name,

# #             "description": item.description,

# #             "is_archived": item.is_archived,

# #             "archived_at": item.archived_at,

# #             "contacts": total_contacts,

# #             "email_eligible": total_contacts,

# #             "wa_eligible": total_contacts,

# #             "campaigns": 0
# #         })

# #     return result


# # # =====================================================
# # # CREATE LIST
# # # =====================================================

# # @router.post("/")
# # def create_list(
# #     payload: ListCreate,
# #     db: Session = Depends(get_main_db)
# # ):

# #     # ==========================================
# #     # CLEAN NAME
# #     # ==========================================

# #     clean_name = payload.list_name.strip()

# #     # ==========================================
# #     # CHECK DUPLICATE
# #     # ==========================================

# #     existing_list = (
# #         db.query(AudienceList)
# #         .filter(
# #             AudienceList.list_name.ilike(
# #                 clean_name
# #             )
# #         )
# #         .first()
# #     )

# #     if existing_list:

# #         raise HTTPException(
# #             status_code=400,
# #             detail="List name already exists"
# #         )

# #     # ==========================================
# #     # CREATE LIST
# #     # ==========================================

# #     new_list = AudienceList(

# #         list_name=clean_name,

# #         description=payload.description,

# #         is_archived=payload.is_archived
# #     )

# #     # ==========================================
# #     # ARCHIVE DATE
# #     # ==========================================

# #     if payload.is_archived:

# #         new_list.archived_at = datetime.utcnow()

# #     db.add(new_list)

# #     db.commit()

# #     db.refresh(new_list)

# #     return new_list


# # # =====================================================
# # # ARCHIVE LIST
# # # =====================================================

# # @router.patch("/{id}/archive")
# # def archive_list(
# #     id: int,
# #     db: Session = Depends(get_main_db)
# # ):

# #     audience_list = (
# #         db.query(AudienceList)
# #         .filter(
# #             AudienceList.id == id
# #         )
# #         .first()
# #     )

# #     if not audience_list:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="List not found"
# #         )

# #     audience_list.is_archived = True

# #     audience_list.archived_at = datetime.utcnow()

# #     db.commit()

# #     db.refresh(audience_list)

# #     return audience_list


# # # =====================================================
# # # RESTORE LIST
# # # =====================================================

# # @router.patch("/{id}/restore")
# # def restore_list(
# #     id: int,
# #     db: Session = Depends(get_main_db)
# # ):

# #     audience_list = (
# #         db.query(AudienceList)
# #         .filter(
# #             AudienceList.id == id
# #         )
# #         .first()
# #     )

# #     if not audience_list:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="List not found"
# #         )

# #     audience_list.is_archived = False

# #     audience_list.archived_at = None

# #     db.commit()

# #     db.refresh(audience_list)

# #     return audience_list


# # # =====================================================
# # # DELETE LIST
# # # =====================================================

# # @router.delete("/{id}")
# # def delete_list(
# #     id: int,
# #     db: Session = Depends(get_main_db)
# # ):

# #     audience_list = (
# #         db.query(AudienceList)
# #         .filter(
# #             AudienceList.id == id
# #         )
# #         .first()
# #     )

# #     if not audience_list:

# #         raise HTTPException(
# #             status_code=404,
# #             detail="List not found"
# #         )

# #     # ==========================================
# #     # DELETE LIST CONTACT MAPPINGS
# #     # ==========================================

# #     db.query(ListContact).filter(
# #         ListContact.list_id == id
# #     ).delete()

# #     # ==========================================
# #     # DELETE LIST
# #     # ==========================================

# #     db.delete(audience_list)

# #     db.commit()

# #     return {
# #         "message": "List deleted successfully"
# #     }




# # =====================================================
# # app/routers/lists.py
# # =====================================================

# from fastapi import (
#     APIRouter,
#     Depends,
#     HTTPException
# )

# from sqlalchemy.orm import Session

# from pydantic import BaseModel

# from typing import Optional

# from datetime import datetime

# import re

# from app.database import get_main_db

# from app.models.lists import (
#     AudienceList,
#     ListContact
# )

# from app.models.contact import Contact
# from app.utils.notification_service import create_notification

# router = APIRouter()


# # =====================================================
# # SCHEMA
# # =====================================================

# class ListCreate(BaseModel):

#     list_name: str

#     description: Optional[str] = None

#     is_archived: Optional[bool] = False


# # =====================================================
# # GET ALL LISTS
# # =====================================================

# @router.get("/")
# def get_lists(
#     db: Session = Depends(get_main_db)
# ):

#     # ==========================================
#     # GET ALL LISTS
#     # ==========================================

#     lists = (
#         db.query(AudienceList)
#         .all()
#     )

#     # ==========================================
#     # GET CONTACT MAPPINGS + CONTACT DATA
#     # ==========================================

#     mappings = (
#         db.query(
#             ListContact.list_id,
#             Contact.email,
#             Contact.phone
#         )
#         .join(
#             Contact,
#             Contact.id == ListContact.contact_id
#         )
#         .all()
#     )

#     # ==========================================
#     # STATS HOLDER
#     # ==========================================

#     stats = {}

#     for item in mappings:

#         if item.list_id not in stats:

#             stats[item.list_id] = {

#                 "contacts": 0,

#                 "email_eligible": 0,

#                 "wa_eligible": 0
#             }

#         # ======================================
#         # TOTAL CONTACTS
#         # ======================================

#         stats[item.list_id]["contacts"] += 1

#         # ======================================
#         # EMAIL ELIGIBLE
#         # ======================================

#         if item.email:

#             email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'

#             if re.match(
#                 email_regex,
#                 item.email
#             ):

#                 stats[item.list_id]["email_eligible"] += 1

#         # ======================================
#         # WHATSAPP ELIGIBLE
#         # ======================================

#         if item.phone:

#             clean_phone = (
#                 item.phone
#                 .replace(" ", "")
#                 .replace("-", "")
#                 .replace("+", "")
#                 .replace("(", "")
#                 .replace(")", "")
#             )

#             # ==================================
#             # VALID NUMBER CHECK
#             # ==================================

#             if clean_phone.isdigit():

#                 # Supports India + international

#                 if 10 <= len(clean_phone) <= 15:

#                     # Avoid fake numbers

#                     if clean_phone not in [

#                         "0000000000",
#                         "1111111111",
#                         "1234567890",
#                         "9999999999"

#                     ]:

#                         stats[item.list_id]["wa_eligible"] += 1

#     # ==========================================
#     # FINAL RESPONSE
#     # ==========================================

#     result = []

#     for item in lists:

#         data = stats.get(item.id, {})

#         result.append({

#             "id": item.id,

#             "list_name": item.list_name,

#             "description": item.description,

#             "is_archived": item.is_archived,

#             "archived_at": item.archived_at,

#             "contacts": data.get(
#                 "contacts",
#                 0
#             ),

#             "email_eligible": data.get(
#                 "email_eligible",
#                 0
#             ),

#             "wa_eligible": data.get(
#                 "wa_eligible",
#                 0
#             ),

#             "campaigns": item.campaigns,

#             "created_at": item.created_at,

#             "updated_at": item.updated_at
#         })

#     return result


# # =====================================================
# # CREATE LIST
# # =====================================================

# @router.post("/")
# def create_list(
#     payload: ListCreate,
#     db: Session = Depends(get_main_db)
# ):

#     clean_name = payload.list_name.strip()

#     # ==========================================
#     # CHECK DUPLICATE
#     # ==========================================

#     existing_list = (
#         db.query(AudienceList)
#         .filter(
#             AudienceList.list_name.ilike(
#                 clean_name
#             )
#         )
#         .first()
#     )

#     if existing_list:

#         raise HTTPException(
#             status_code=400,
#             detail="List name already exists"
#         )

#     # ==========================================
#     # CREATE LIST
#     # ==========================================

#     new_list = AudienceList(

#         list_name=clean_name,

#         description=payload.description,

#         is_archived=payload.is_archived
#     )

#     if payload.is_archived:

#         new_list.archived_at = datetime.utcnow()

#     db.add(new_list)

#     db.commit()

#     db.refresh(new_list)
#     create_notification(
#      db=db,
#      notification_type="listCreated",
#      title="List Created",
#      message=f'List "{new_list.list_name}" created successfully'
# )

#     return new_list


# # =====================================================
# # ARCHIVE LIST
# # =====================================================

# @router.patch("/{id}/archive")
# def archive_list(
#     id: int,
#     db: Session = Depends(get_main_db)
# ):

#     audience_list = (
#         db.query(AudienceList)
#         .filter(
#             AudienceList.id == id
#         )
#         .first()
#     )

#     if not audience_list:

#         raise HTTPException(
#             status_code=404,
#             detail="List not found"
#         )

#     audience_list.is_archived = True

#     audience_list.archived_at = datetime.utcnow()

#     db.commit()

#     db.refresh(audience_list)

#     return audience_list


# # =====================================================
# # RESTORE LIST
# # =====================================================

# @router.patch("/{id}/restore")
# def restore_list(
#     id: int,
#     db: Session = Depends(get_main_db)
# ):

#     audience_list = (
#         db.query(AudienceList)
#         .filter(
#             AudienceList.id == id
#         )
#         .first()
#     )

#     if not audience_list:

#         raise HTTPException(
#             status_code=404,
#             detail="List not found"
#         )

#     audience_list.is_archived = False

#     audience_list.archived_at = None

#     db.commit()

#     db.refresh(audience_list)

#     return audience_list


# # =====================================================
# # DELETE LIST
# # =====================================================

# @router.delete("/{id}")
# def delete_list(
#     id: int,
#     db: Session = Depends(get_main_db)
# ):

#     audience_list = (
#         db.query(AudienceList)
#         .filter(
#             AudienceList.id == id
#         )
#         .first()
#     )

#     if not audience_list:

#         raise HTTPException(
#             status_code=404,
#             detail="List not found"
#         )

#     # ==========================================
#     # DELETE MAPPINGS
#     # ==========================================

#     db.query(ListContact).filter(
#         ListContact.list_id == id
#     ).delete()

#     # ==========================================
#     # DELETE LIST
#     # ==========================================

#     db.delete(audience_list)

#     db.commit()

#     return {
#         "message": "List deleted successfully"
#     }



from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session

from pydantic import BaseModel

from typing import Optional

from datetime import datetime

import re

from app.database import get_main_db

from app.models.lists import (
    AudienceList,
    ListContact
)

from app.models.contact import Contact
from app.models.campaign import Campaign
from app.utils.notification_service import create_notification

router = APIRouter()


# =====================================================
# SCHEMA
# =====================================================

class ListCreate(BaseModel):

    list_name: str
    description: Optional[str] = None
    is_archived: Optional[bool] = False


# =====================================================
# GET ALL LISTS
# =====================================================

@router.get("/")
def get_lists(
    db: Session = Depends(get_main_db)
):

    # ==========================================
    # GET ALL LISTS
    # ==========================================

    lists = (
        db.query(AudienceList)
        .all()
    )

    # ==========================================
    # GET CONTACT MAPPINGS + CONTACT DATA
    # ==========================================

    mappings = (
        db.query(
            ListContact.list_id,
            Contact.email,
            Contact.phone
        )
        .join(
            Contact,
            Contact.id == ListContact.contact_id
        )
        .all()
    )

    # ==========================================
    # CAMPAIGN COUNTS
    # ==========================================

    campaign_counts = {}

    campaigns = (
        db.query(Campaign)
        .filter(Campaign.sent_at.isnot(None))
        .all()
    )

    for campaign in campaigns:

        if not campaign.audience_list_ids:
            continue

        if isinstance(campaign.audience_list_ids, list):

            for list_item in campaign.audience_list_ids:

                # Case 1 -> [1,2,3]
                if isinstance(list_item, int):

                    campaign_counts[list_item] = (
                        campaign_counts.get(list_item, 0) + 1
                    )

                # Case 2 -> ["1","2"]
                elif isinstance(list_item, str):

                    try:

                        list_id = int(list_item)

                        campaign_counts[list_id] = (
                            campaign_counts.get(list_id, 0) + 1
                        )

                    except Exception:
                        pass

                # Case 3 -> [{"id":1,"name":"List"}]
                elif isinstance(list_item, dict):

                    list_id = (
                        list_item.get("id")
                        or list_item.get("list_id")
                    )

                    if list_id:

                        try:

                            list_id = int(list_id)

                            campaign_counts[list_id] = (
                                campaign_counts.get(list_id, 0) + 1
                            )

                        except Exception:
                            pass

    # ==========================================
    # CONTACT STATS
    # ==========================================

    stats = {}

    for item in mappings:

        if item.list_id not in stats:

            stats[item.list_id] = {

                "contacts": 0,
                "email_eligible": 0,
                "wa_eligible": 0
            }

        # ======================================
        # TOTAL CONTACTS
        # ======================================

        stats[item.list_id]["contacts"] += 1

        # ======================================
        # EMAIL ELIGIBLE
        # ======================================

        if item.email:

            email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'

            if re.match(
                email_regex,
                item.email
            ):

                stats[item.list_id]["email_eligible"] += 1

        # ======================================
        # WHATSAPP ELIGIBLE
        # ======================================

        if item.phone:

            clean_phone = (
                item.phone
                .replace(" ", "")
                .replace("-", "")
                .replace("+", "")
                .replace("(", "")
                .replace(")", "")
            )

            if clean_phone.isdigit():

                if 10 <= len(clean_phone) <= 15:

                    if clean_phone not in [

                        "0000000000",
                        "1111111111",
                        "1234567890",
                        "9999999999"

                    ]:

                        stats[item.list_id]["wa_eligible"] += 1

    # ==========================================
    # FINAL RESPONSE
    # ==========================================

    result = []

    for item in lists:

        data = stats.get(item.id, {})

        result.append({

            "id": item.id,

            "list_name": item.list_name,

            "description": item.description,

            "is_archived": item.is_archived,

            "archived_at": item.archived_at,

            "contacts": data.get(
                "contacts",
                0
            ),

            "email_eligible": data.get(
                "email_eligible",
                0
            ),

            "wa_eligible": data.get(
                "wa_eligible",
                0
            ),

            # Dynamic campaign count
            "campaigns": campaign_counts.get(
                item.id,
                0
            ),

            "created_at": item.created_at,

            "updated_at": item.updated_at
        })

    return result


# =====================================================
# CREATE LIST
# =====================================================

@router.post("/")
def create_list(
    payload: ListCreate,
    db: Session = Depends(get_main_db)
):

    clean_name = payload.list_name.strip()

    if not clean_name:
        raise HTTPException(
            status_code=400,
            detail="List name is required"
        )

    existing_list = (
        db.query(AudienceList)
        .filter(
            AudienceList.list_name.ilike(clean_name)
        )
        .first()
    )

    if existing_list:
        raise HTTPException(
            status_code=400,
            detail="List name already exists"
        )

    try:

        new_list = AudienceList(
            list_name=clean_name,
            description=payload.description,
            is_archived=payload.is_archived
        )

        if payload.is_archived:
            new_list.archived_at = datetime.utcnow()

        db.add(new_list)

        db.commit()

        db.refresh(new_list)

        create_notification(
            db=db,
            notification_type="listCreated",
            title="List Created",
            message=f'List "{new_list.list_name}" created successfully'
        )

        return new_list

    except Exception as e:

        db.rollback()

        print("CREATE LIST ERROR:", str(e))

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    clean_name = payload.list_name.strip()

    existing_list = (
        db.query(AudienceList)
        .filter(
            AudienceList.list_name.ilike(
                clean_name
            )
        )
        .first()
    )

    if existing_list:

        raise HTTPException(
            status_code=400,
            detail="List name already exists"
        )

    new_list = AudienceList(

        list_name=clean_name,

        description=payload.description,

        is_archived=payload.is_archived
    )

    if payload.is_archived:

        new_list.archived_at = datetime.utcnow()

    db.add(new_list)

    db.commit()

    db.refresh(new_list)

    create_notification(
        db=db,
        notification_type="listCreated",
        title="List Created",
        message=f'List "{new_list.list_name}" created successfully'
    )

    return new_list


# =====================================================
# ARCHIVE LIST
# =====================================================

@router.patch("/{id}/archive")
def archive_list(
    id: int,
    db: Session = Depends(get_main_db)
):

    audience_list = (
        db.query(AudienceList)
        .filter(
            AudienceList.id == id
        )
        .first()
    )

    if not audience_list:

        raise HTTPException(
            status_code=404,
            detail="List not found"
        )

    audience_list.is_archived = True
    audience_list.archived_at = datetime.utcnow()

    db.commit()
    db.refresh(audience_list)

    return audience_list


# =====================================================
# RESTORE LIST
# =====================================================

@router.patch("/{id}/restore")
def restore_list(
    id: int,
    db: Session = Depends(get_main_db)
):

    audience_list = (
        db.query(AudienceList)
        .filter(
            AudienceList.id == id
        )
        .first()
    )

    if not audience_list:

        raise HTTPException(
            status_code=404,
            detail="List not found"
        )

    audience_list.is_archived = False
    audience_list.archived_at = None

    db.commit()
    db.refresh(audience_list)

    return audience_list


# =====================================================
# DELETE LIST
# =====================================================

@router.delete("/{id}")
def delete_list(
    id: int,
    db: Session = Depends(get_main_db)
):

    audience_list = (
        db.query(AudienceList)
        .filter(
            AudienceList.id == id
        )
        .first()
    )

    if not audience_list:

        raise HTTPException(
            status_code=404,
            detail="List not found"
        )

    db.query(ListContact).filter(
        ListContact.list_id == id
    ).delete()

    db.delete(audience_list)

    db.commit()

    return {
        "message": "List deleted successfully"
    }
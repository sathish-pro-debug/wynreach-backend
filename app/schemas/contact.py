# # # from pydantic import BaseModel
# # # from typing import Optional


# # # class ContactBase(BaseModel):
# # #     full_name: str
# # #     email: Optional[str] = None
# # #     phone: Optional[str] = None
# # #     status: Optional[str] = "active"
# # #     tags: Optional[str] = None
# # #     score: Optional[int] = 0
# # #     campaign: Optional[str] = None
# # #     list_id: int


# # # class ContactCreate(ContactBase):
# # #     pass


# # # class ContactUpdate(BaseModel):
# # #     full_name: Optional[str] = None
# # #     email: Optional[str] = None
# # #     phone: Optional[str] = None
# # #     status: Optional[str] = None
# # #     tags: Optional[str] = None
# # #     score: Optional[int] = None
# # #     campaign: Optional[str] = None


# # # class ContactResponse(ContactBase):
# # #     id: int

# # #     class Config:
# # #         from_attributes = True

# # from pydantic import BaseModel
# # from typing import Optional
# # from datetime import datetime


# # class ContactBase(BaseModel):

# #     full_name: str

# #     email: Optional[str] = None

# #     phone: Optional[str] = None

# #     status: Optional[str] = "active"

# #     tags: Optional[str] = None

# #     score: Optional[int] = 0

# #     campaign: Optional[str] = None

# #     list_id: int


# # class ContactCreate(ContactBase):
# #     pass


# # class ContactUpdate(BaseModel):

# #     full_name: Optional[str] = None

# #     email: Optional[str] = None

# #     phone: Optional[str] = None

# #     status: Optional[str] = None

# #     tags: Optional[str] = None

# #     score: Optional[int] = None

# #     campaign: Optional[str] = None


# # class ContactResponse(ContactBase):

# #     id: int

# #     is_suppressed: bool

# #     suppression_reason: Optional[str] = None

# #     suppressed_at: Optional[datetime] = None

# #     class Config:

# #         from_attributes = True


# from pydantic import BaseModel
# from typing import Optional
# from datetime import datetime


# # ==========================================
# # BASE
# # ==========================================

# class ContactBase(BaseModel):

#     full_name: str

#     email: Optional[str] = None

#     phone: Optional[str] = None

#     status: Optional[str] = "active"

#     tags: Optional[str] = None

#     score: Optional[int] = 0

#     campaign: Optional[str] = None

#     list_id: int


# # ==========================================
# # CREATE
# # ==========================================

# class ContactCreate(ContactBase):
#     pass


# # ==========================================
# # UPDATE
# # ==========================================

# class ContactUpdate(BaseModel):

#     full_name: Optional[str] = None

#     email: Optional[str] = None

#     phone: Optional[str] = None

#     status: Optional[str] = None

#     tags: Optional[str] = None

#     score: Optional[int] = None

#     campaign: Optional[str] = None


# # ==========================================
# # RESPONSE
# # ==========================================

# class ContactResponse(BaseModel):

#     id: int

#     full_name: str

#     email: Optional[str]

#     phone: Optional[str]

#     status: str

#     tags: Optional[list] = []

#     score: Optional[int]

#     campaign: Optional[str]

#     list_name: Optional[str]

#     is_suppressed: bool

#     suppression_reason: Optional[str]

#     suppressed_at: Optional[datetime]

#     class Config:
#         from_attributes = True


# =====================================================
# app/schemas/contact_schema.py
# =====================================================

# from pydantic import BaseModel
# from typing import Optional
# from datetime import datetime


# # =====================================================
# # BASE
# # =====================================================

# class ContactBase(BaseModel):

#     full_name: str

#     email: Optional[str] = None

#     phone: Optional[str] = None

#     status: Optional[str] = "active"

#     tags: Optional[str] = None

#     score: Optional[int] = 0

#     campaign: Optional[str] = None

#     list_id: int


# # =====================================================
# # CREATE
# # =====================================================

# class ContactCreate(ContactBase):
#     pass


# # =====================================================
# # UPDATE
# # =====================================================

# class ContactUpdate(BaseModel):

#     full_name: Optional[str] = None

#     email: Optional[str] = None

#     phone: Optional[str] = None

#     status: Optional[str] = None

#     tags: Optional[str] = None

#     score: Optional[int] = None

#     campaign: Optional[str] = None


# # =====================================================
# # RESPONSE
# # =====================================================

# class ContactResponse(BaseModel):

#     id: int

#     full_name: str

#     email: Optional[str]

#     phone: Optional[str]

#     status: str

#     tags: Optional[list] = []

#     score: Optional[int]

#     campaign: Optional[str]

#     list_name: Optional[str]

#     is_suppressed: bool

#     suppression_reason: Optional[str]

#     suppressed_at: Optional[datetime]

#     class Config:
#         from_attributes = True


from pydantic import BaseModel

from typing import Optional, List

from datetime import datetime

# =====================================================
# BASE
# =====================================================


class ContactBase(BaseModel):

    full_name: str

    email: Optional[str] = None

    phone: Optional[str] = None

    status: Optional[str] = "active"

    tags: Optional[List[str]] = []

    score: Optional[int] = 0

    campaign: Optional[str] = None

    list_id: int

    is_whatsapp: Optional[bool] = False


# =====================================================
# CREATE
# =====================================================


class ContactCreate(ContactBase):
    pass


# =====================================================
# UPDATE
# =====================================================


class ContactUpdate(BaseModel):

    full_name: Optional[str] = None

    email: Optional[str] = None

    phone: Optional[str] = None

    status: Optional[str] = None

    tags: Optional[List[str]] = []

    score: Optional[int] = None

    campaign: Optional[str] = None

    is_whatsapp: Optional[bool] = None


# =====================================================
# RESPONSE
# =====================================================


class ContactResponse(BaseModel):

    id: int

    full_name: str

    email: Optional[str]

    phone: Optional[str]

    status: str

    tags: Optional[List[str]] = []

    score: Optional[int]

    campaign: Optional[str]

    list_name: Optional[str]

    is_suppressed: bool

    suppression_reason: Optional[str]

    suppressed_at: Optional[datetime]

    is_whatsapp: Optional[bool] = False

    class Config:

        from_attributes = True

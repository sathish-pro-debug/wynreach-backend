


# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     DateTime,
#     Boolean,
#     ForeignKey
# )

# from sqlalchemy.sql import func
# from sqlalchemy.orm import relationship

# from app.database import Base


# # =====================================================
# # AUDIENCE LIST MODEL
# # =====================================================

# class AudienceList(Base):

#     __tablename__ = "audience_lists"

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True
#     )

#     list_name = Column(
#         String,
#         nullable=False
#     )

#     description = Column(
#         String,
#         nullable=True
#     )

#     contact_count = Column(
#         Integer,
#         default=0
#     )

#     email_eligible = Column(
#         Integer,
#         default=0
#     )

#     wa_eligible = Column(
#         Integer,
#         default=0
#     )

#     campaigns = Column(
#         Integer,
#         default=0
#     )

#     is_archived = Column(
#         Boolean,
#         default=False
#     )

#     archived_at = Column(
#         DateTime,
#         nullable=True
#     )

#     created_at = Column(
#         DateTime,
#         server_default=func.now()
#     )

#     updated_at = Column(
#         DateTime,
#         default=func.now(),
#         onupdate=func.now()
#     )

#     # =================================================
#     # RELATIONSHIP
#     # =================================================

#     contacts = relationship(
#         "ListContact",
#         back_populates="audience_list",
#         cascade="all, delete"
#     )


# # =====================================================
# # LIST CONTACT MODEL
# # =====================================================

# class ListContact(Base):

#     __tablename__ = "list_contacts"

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True
#     )

#     # =================================================
#     # LIST RELATION
#     # =================================================

#     list_id = Column(
#         Integer,
#         ForeignKey("audience_lists.id"),
#         nullable=False
#     )

#     # =================================================
#     # CONTACT RELATION
#     # =================================================

#     contact_id = Column(
#         Integer,
#         nullable=False
#     )

#     # =================================================
#     # TIMESTAMPS
#     # =================================================

#     created_at = Column(
#         DateTime,
#         server_default=func.now()
#     )

#     # =================================================
#     # RELATIONSHIP
#     # =================================================

#     audience_list = relationship(
#         "AudienceList",
#         back_populates="contacts"
#     )



# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     DateTime,
#     Boolean,
#     ForeignKey,
#     UniqueConstraint
# )

# from sqlalchemy.sql import func

# from sqlalchemy.orm import relationship

# from app.database import Base


# # =====================================================
# # AUDIENCE LIST MODEL
# # =====================================================

# class AudienceList(Base):

#     __tablename__ = "audience_lists"

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True
#     )

#     list_name = Column(
#         String,
#         nullable=False
#     )

#     description = Column(
#         String,
#         nullable=True
#     )

#     contact_count = Column(
#         Integer,
#         default=0
#     )

#     email_eligible = Column(
#         Integer,
#         default=0
#     )

#     wa_eligible = Column(
#         Integer,
#         default=0
#     )

#     campaigns = Column(
#         Integer,
#         default=0
#     )

#     is_archived = Column(
#         Boolean,
#         default=False
#     )

#     archived_at = Column(
#         DateTime,
#         nullable=True
#     )

#     created_at = Column(
#         DateTime,
#         server_default=func.now()
#     )

#     updated_at = Column(
#         DateTime,
#         default=func.now(),
#         onupdate=func.now()
#     )

#     # =================================================
#     # RELATIONSHIP
#     # =================================================

#     contacts = relationship(
#         "ListContact",
#         back_populates="audience_list",
#         cascade="all, delete"
#     )


# # =====================================================
# # LIST CONTACT MODEL
# # =====================================================

# class ListContact(Base):

#     __tablename__ = "list_contacts"

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True
#     )

#     # =================================================
#     # LIST RELATION
#     # =================================================

#     list_id = Column(
#         Integer,
#         ForeignKey("audience_lists.id"),
#         nullable=False
#     )

#     # =================================================
#     # CONTACT RELATION
#     # =================================================

#     contact_id = Column(
#         Integer,
#         ForeignKey("contacts.id"),
#         nullable=False
#     )

#     # =================================================
#     # TIMESTAMPS
#     # =================================================

#     created_at = Column(
#         DateTime,
#         server_default=func.now()
#     )

#     # =================================================
#     # PREVENT SAME CONTACT DUPLICATE IN SAME LIST
#     # =================================================

#     __table_args__ = (

#         UniqueConstraint(
#             "list_id",
#             "contact_id",
#             name="unique_contact_per_list"
#         ),

#     )

#     # =================================================
#     # RELATIONSHIP
#     # =================================================

#     audience_list = relationship(
#         "AudienceList",
#         back_populates="contacts"
#     )

#     contact = relationship(
#         "Contact",
#         back_populates="lists"
#     )




from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    UniqueConstraint
)

from sqlalchemy.sql import func

from sqlalchemy.orm import relationship

from app.database import Base


# =====================================================
# AUDIENCE LIST MODEL
# =====================================================

class AudienceList(Base):

    __tablename__ = "audience_lists"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    list_name = Column(
        String,
        nullable=False,
        index=True
    )

    description = Column(
        String,
        nullable=True
    )

    contact_count = Column(
        Integer,
        default=0
    )

    email_eligible = Column(
        Integer,
        default=0
    )

    wa_eligible = Column(
        Integer,
        default=0
    )

    campaigns = Column(
        Integer,
        default=0
    )

    is_archived = Column(
        Boolean,
        default=False,
        index=True
    )

    archived_at = Column(
        DateTime,
        nullable=True
    )

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now()
    )

    # =================================================
    # RELATIONSHIP
    # =================================================

    contacts = relationship(
        "ListContact",
        back_populates="audience_list",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


# =====================================================
# LIST CONTACT MODEL
# =====================================================

class ListContact(Base):

    __tablename__ = "list_contacts"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # =================================================
    # LIST RELATION
    # =================================================

    list_id = Column(
        Integer,
        ForeignKey(
            "audience_lists.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # =================================================
    # CONTACT RELATION
    # =================================================

    contact_id = Column(
        Integer,
        ForeignKey(
            "contacts.id",
            ondelete="CASCADE"
        ),
        nullable=False,
        index=True
    )

    # =================================================
    # TIMESTAMPS
    # =================================================

    created_at = Column(
        DateTime,
        server_default=func.now()
    )

    # =================================================
    # UNIQUE CONSTRAINT
    # =================================================

    __table_args__ = (

        UniqueConstraint(
            "list_id",
            "contact_id",
            name="unique_contact_per_list"
        ),

    )

    # =================================================
    # RELATIONSHIP
    # =================================================

    audience_list = relationship(
        "AudienceList",
        back_populates="contacts",
        lazy="joined"
    )

    contact = relationship(
        "Contact",
        back_populates="lists",
        lazy="joined"
    )
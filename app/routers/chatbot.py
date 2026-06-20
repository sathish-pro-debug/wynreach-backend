# # from fastapi import APIRouter, Depends, HTTPException
# # from sqlalchemy.orm import Session
# # from typing import List
# # from app.database import get_main_db                     # ✅ correct dependency
# # from app.models.chatbot import Chatbot as ChatbotModel
# # from app.schemas.chatbot import (
# #     ChatbotCreate, ChatbotUpdate, ChatbotResponse,
# #     ChatRequest, ChatResponse
# # )
# # from app.services.chat_service import get_reply_from_chatbot
# # from datetime import datetime

# # router = APIRouter()

# # @router.get("/", response_model=List[ChatbotResponse])
# # def get_all_chatbots(db: Session = Depends(get_main_db)):
# #     return db.query(ChatbotModel).order_by(ChatbotModel.id.desc()).all()

# # @router.post("/", response_model=ChatbotResponse)
# # def create_chatbot(chatbot: ChatbotCreate, db: Session = Depends(get_main_db)):
# #     new_bot = ChatbotModel(
# #         name=chatbot.name,
# #         description=chatbot.description,
# #         status=chatbot.status,
# #         welcome_message=chatbot.welcome_message,
# #         buttons=[b.dict() for b in chatbot.buttons],
# #         faqs=[f.dict() for f in chatbot.faqs],
# #         conversations=0,
# #         satisfaction=0.0,
# #         responses=0
# #     )
# #     db.add(new_bot)
# #     db.commit()
# #     db.refresh(new_bot)
# #     return new_bot

# # @router.get("/{bot_id}", response_model=ChatbotResponse)
# # def get_chatbot(bot_id: int, db: Session = Depends(get_main_db)):
# #     bot = db.query(ChatbotModel).filter(ChatbotModel.id == bot_id).first()
# #     if not bot:
# #         raise HTTPException(status_code=404, detail="Chatbot not found")
# #     return bot

# # @router.put("/{bot_id}", response_model=ChatbotResponse)
# # def update_chatbot(bot_id: int, chatbot: ChatbotUpdate, db: Session = Depends(get_main_db)):
# #     bot = db.query(ChatbotModel).filter(ChatbotModel.id == bot_id).first()
# #     if not bot:
# #         raise HTTPException(status_code=404)
# #     update_data = chatbot.dict(exclude_unset=True)
# #     for key, value in update_data.items():
# #         if key == "buttons" and value is not None:
# #             value = [b.dict() for b in value]
# #         elif key == "faqs" and value is not None:
# #             value = [f.dict() for f in value]
# #         setattr(bot, key, value)
# #     bot.updated_at = datetime.utcnow()
# #     db.commit()
# #     db.refresh(bot)
# #     return bot

# # @router.delete("/{bot_id}")
# # def delete_chatbot(bot_id: int, db: Session = Depends(get_main_db)):
# #     bot = db.query(ChatbotModel).filter(ChatbotModel.id == bot_id).first()
# #     if not bot:
# #         raise HTTPException(status_code=404)
# #     db.delete(bot)
# #     db.commit()
# #     return {"message": "Chatbot deleted"}

# # @router.patch("/{bot_id}/status")
# # def toggle_status(bot_id: int, db: Session = Depends(get_main_db)):
# #     bot = db.query(ChatbotModel).filter(ChatbotModel.id == bot_id).first()
# #     if not bot:
# #         raise HTTPException(status_code=404)
# #     bot.status = "paused" if bot.status == "active" else "active"
# #     db.commit()
# #     return {"status": bot.status}

# # @router.post("/{bot_id}/duplicate", response_model=ChatbotResponse)
# # def duplicate_chatbot(bot_id: int, db: Session = Depends(get_main_db)):
# #     original = db.query(ChatbotModel).filter(ChatbotModel.id == bot_id).first()
# #     if not original:
# #         raise HTTPException(status_code=404)
# #     new_bot = ChatbotModel(
# #         name=f"{original.name} (Copy)",
# #         description=original.description,
# #         status="active",
# #         welcome_message=original.welcome_message,
# #         buttons=original.buttons,
# #         faqs=original.faqs,
# #         conversations=0,
# #         satisfaction=0.0,
# #         responses=0
# #     )
# #     db.add(new_bot)
# #     db.commit()
# #     db.refresh(new_bot)
# #     return new_bot

# # @router.post("/chat", response_model=ChatResponse)
# # def chat_endpoint(req: ChatRequest, db: Session = Depends(get_main_db)):
# #     bot = db.query(ChatbotModel).filter(ChatbotModel.id == req.chatbot_id).first()
# #     if not bot:
# #         raise HTTPException(status_code=404)
# #     bot.conversations += 1
# #     bot.responses += 1
# #     bot.last_active = datetime.utcnow()
# #     db.commit()
# #     reply = get_reply_from_chatbot(req.message, bot.faqs, bot.welcome_message)
# #     return ChatResponse(reply=reply)

# # ---------------------------------------------------
# # IMPORTS
# # ---------------------------------------------------
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from sqlalchemy import update
# from typing import List
# from datetime import datetime

# from app.database import get_main_db

# from app.models.chatbot import (
#     Chatbot as ChatbotModel,
#     ChatConversation,
#     ChatMessage
# )

# from app.schemas.chatbot import (
#     ChatbotCreate,
#     ChatbotUpdate,
#     ChatbotResponse,
#     ChatRequest,
#     ChatResponse
# )

# from app.services.chat_service import get_reply_from_chatbot

# router = APIRouter()


# # ---------------------------------------------------
# # GET ALL CHATBOTS
# # ---------------------------------------------------
# @router.get("/", response_model=List[ChatbotResponse])
# def get_all_chatbots(db: Session = Depends(get_main_db)):

#     return (
#         db.query(ChatbotModel)
#         .order_by(ChatbotModel.id.desc())
#         .all()
#     )


# # ---------------------------------------------------
# # CREATE CHATBOT
# # ---------------------------------------------------
# @router.post("/", response_model=ChatbotResponse)
# def create_chatbot(
#     chatbot: ChatbotCreate,
#     db: Session = Depends(get_main_db)
# ):

#     try:

#         new_bot = ChatbotModel(
#             name=chatbot.name,
#             description=chatbot.description,
#             status=chatbot.status,
#             welcome_message=chatbot.welcome_message,
#             buttons=[b.dict() for b in chatbot.buttons],
#             faqs=[f.dict() for f in chatbot.faqs],
#             conversations=0,
#             satisfaction=0.0,
#             responses=0,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow()
#         )

#         db.add(new_bot)

#         db.commit()

#         db.refresh(new_bot)

#         return new_bot

#     except Exception as e:

#         db.rollback()

#         print("CREATE CHATBOT ERROR:", e)

#         raise HTTPException(
#             status_code=500,
#             detail="Failed to create chatbot"
#         )


# # ---------------------------------------------------
# # GET SINGLE CHATBOT
# # ---------------------------------------------------
# @router.get("/{bot_id}", response_model=ChatbotResponse)
# def get_chatbot(
#     bot_id: int,
#     db: Session = Depends(get_main_db)
# ):

#     bot = (
#         db.query(ChatbotModel)
#         .filter(ChatbotModel.id == bot_id)
#         .first()
#     )

#     if not bot:

#         raise HTTPException(
#             status_code=404,
#             detail="Chatbot not found"
#         )

#     return bot


# # ---------------------------------------------------
# # UPDATE CHATBOT
# # ---------------------------------------------------
# @router.put("/{bot_id}", response_model=ChatbotResponse)
# def update_chatbot(
#     bot_id: int,
#     chatbot: ChatbotUpdate,
#     db: Session = Depends(get_main_db)
# ):

#     bot = (
#         db.query(ChatbotModel)
#         .filter(ChatbotModel.id == bot_id)
#         .first()
#     )

#     if not bot:

#         raise HTTPException(
#             status_code=404,
#             detail="Chatbot not found"
#         )

#     try:

#         update_data = chatbot.dict(exclude_unset=True)

#         for key, value in update_data.items():

#             if key == "buttons" and value is not None:
#                 value = [b.dict() for b in value]

#             elif key == "faqs" and value is not None:
#                 value = [f.dict() for f in value]

#             setattr(bot, key, value)

#         bot.updated_at = datetime.utcnow()

#         db.commit()

#         db.refresh(bot)

#         return bot

#     except Exception as e:

#         db.rollback()

#         print("UPDATE CHATBOT ERROR:", e)

#         raise HTTPException(
#             status_code=500,
#             detail="Failed to update chatbot"
#         )


# # ---------------------------------------------------
# # DELETE CHATBOT
# # ---------------------------------------------------
# @router.delete("/{bot_id}")
# def delete_chatbot(
#     bot_id: int,
#     db: Session = Depends(get_main_db)
# ):

#     bot = (
#         db.query(ChatbotModel)
#         .filter(ChatbotModel.id == bot_id)
#         .first()
#     )

#     if not bot:

#         raise HTTPException(
#             status_code=404,
#             detail="Chatbot not found"
#         )

#     try:

#         db.delete(bot)

#         db.commit()

#         return {
#             "success": True,
#             "message": "Chatbot deleted successfully"
#         }

#     except Exception as e:

#         db.rollback()

#         print("DELETE CHATBOT ERROR:", e)

#         raise HTTPException(
#             status_code=500,
#             detail="Failed to delete chatbot"
#         )


# # ---------------------------------------------------
# # TOGGLE CHATBOT STATUS
# # ---------------------------------------------------
# @router.patch("/{bot_id}/status")
# def toggle_status(
#     bot_id: int,
#     db: Session = Depends(get_main_db)
# ):

#     bot = (
#         db.query(ChatbotModel)
#         .filter(ChatbotModel.id == bot_id)
#         .first()
#     )

#     if not bot:

#         raise HTTPException(
#             status_code=404,
#             detail="Chatbot not found"
#         )

#     try:

#         bot.status = (
#             "paused"
#             if bot.status == "active"
#             else "active"
#         )

#         bot.updated_at = datetime.utcnow()

#         db.commit()

#         return {
#             "success": True,
#             "status": bot.status
#         }

#     except Exception as e:

#         db.rollback()

#         print("STATUS TOGGLE ERROR:", e)

#         raise HTTPException(
#             status_code=500,
#             detail="Failed to toggle chatbot status"
#         )


# # ---------------------------------------------------
# # DUPLICATE CHATBOT
# # ---------------------------------------------------
# @router.post("/{bot_id}/duplicate", response_model=ChatbotResponse)
# def duplicate_chatbot(
#     bot_id: int,
#     db: Session = Depends(get_main_db)
# ):

#     original = (
#         db.query(ChatbotModel)
#         .filter(ChatbotModel.id == bot_id)
#         .first()
#     )

#     if not original:

#         raise HTTPException(
#             status_code=404,
#             detail="Chatbot not found"
#         )

#     try:

#         new_bot = ChatbotModel(
#             name=f"{original.name} (Copy)",
#             description=original.description,
#             status="active",
#             welcome_message=original.welcome_message,
#             buttons=original.buttons,
#             faqs=original.faqs,
#             conversations=0,
#             satisfaction=0.0,
#             responses=0,
#             created_at=datetime.utcnow(),
#             updated_at=datetime.utcnow()
#         )

#         db.add(new_bot)

#         db.commit()

#         db.refresh(new_bot)

#         return new_bot

#     except Exception as e:

#         db.rollback()

#         print("DUPLICATE CHATBOT ERROR:", e)

#         raise HTTPException(
#             status_code=500,
#             detail="Failed to duplicate chatbot"
#         )


# # ---------------------------------------------------
# # CHAT ENDPOINT
# # ---------------------------------------------------
# @router.post("/chat", response_model=ChatResponse)
# def chat_endpoint(
#     req: ChatRequest,
#     db: Session = Depends(get_main_db)
# ):

#     # -----------------------------------------
#     # FIND CHATBOT
#     # -----------------------------------------
#     bot = (
#         db.query(ChatbotModel)
#         .filter(ChatbotModel.id == req.chatbot_id)
#         .first()
#     )

#     if not bot:

#         raise HTTPException(
#             status_code=404,
#             detail="Chatbot not found"
#         )

#     try:

#         # -----------------------------------------
#         # CREATE CONVERSATION
#         # -----------------------------------------
#         conversation = ChatConversation(
#             chatbot_id=bot.id,
#             started_at=datetime.utcnow(),
#             message_count=0
#         )

#         db.add(conversation)

#         # IMPORTANT
#         db.flush()

#         # -----------------------------------------
#         # SAVE USER MESSAGE
#         # -----------------------------------------
#         user_message = ChatMessage(
#             conversation_id=conversation.id,
#             role="user",
#             content=req.message
#         )

#         db.add(user_message)

#         # -----------------------------------------
#         # GENERATE BOT REPLY
#         # -----------------------------------------
#         reply = get_reply_from_chatbot(
#             req.message,
#             bot.faqs,
#             bot.welcome_message
#         )

#         # -----------------------------------------
#         # SAVE BOT MESSAGE
#         # -----------------------------------------
#         bot_message = ChatMessage(
#             conversation_id=conversation.id,
#             role="bot",
#             content=reply
#         )

#         db.add(bot_message)

#         # -----------------------------------------
#         # UPDATE CONVERSATION
#         # -----------------------------------------
#         conversation.message_count = 2
#         conversation.ended_at = datetime.utcnow()

#         # -----------------------------------------
#         # UPDATE CHATBOT STATS
#         # -----------------------------------------
#         db.execute(
#             update(ChatbotModel)
#             .where(ChatbotModel.id == bot.id)
#             .values(
#                 conversations=ChatbotModel.conversations + 1,
#                 responses=ChatbotModel.responses + 1,
#                 last_active=datetime.utcnow(),
#                 updated_at=datetime.utcnow()
#             )
#         )

#         # -----------------------------------------
#         # SAVE EVERYTHING
#         # -----------------------------------------
#         db.commit()

#         return ChatResponse(reply=reply)

#     except Exception as e:

#         db.rollback()

#         print("CHAT ENDPOINT ERROR:", e)

#         raise HTTPException(
#             status_code=500,
#             detail="Failed to process chat"
#         )




# app/routers/chatbot.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import update
from typing import List
from datetime import datetime

from app.database import get_main_db
from app.models.chatbot import Chatbot as ChatbotModel, ChatConversation, ChatMessage
from app.schemas.chatbot import (
    ChatbotCreate, ChatbotUpdate, ChatbotResponse,
    ChatRequest, ChatResponse
)
from app.services.chat_service import get_reply_from_chatbot

router = APIRouter()


# ---------------------------------------------------
# GET ALL CHATBOTS
# ---------------------------------------------------
@router.get("/", response_model=List[ChatbotResponse])
def get_all_chatbots(db: Session = Depends(get_main_db)):
    return db.query(ChatbotModel).order_by(ChatbotModel.id.desc()).all()


# ---------------------------------------------------
# CREATE CHATBOT
# ---------------------------------------------------
@router.post("/", response_model=ChatbotResponse)
def create_chatbot(chatbot: ChatbotCreate, db: Session = Depends(get_main_db)):
    try:
        new_bot = ChatbotModel(
            name=chatbot.name,
            description=chatbot.description,
            status=chatbot.status,          # 'active' or 'inactive'
            welcome_message=chatbot.welcome_message,
            buttons=[b.dict() for b in chatbot.buttons],
            faqs=[f.dict() for f in chatbot.faqs],
            conversations=0,
            satisfaction=0.0,
            responses=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_bot)
        db.commit()
        db.refresh(new_bot)
        return new_bot
    except Exception as e:
        db.rollback()
        print("CREATE CHATBOT ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to create chatbot")


# ---------------------------------------------------
# GET SINGLE CHATBOT
# ---------------------------------------------------
@router.get("/{bot_id}", response_model=ChatbotResponse)
def get_chatbot(bot_id: int, db: Session = Depends(get_main_db)):
    bot = db.query(ChatbotModel).filter(ChatbotModel.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    return bot


# ---------------------------------------------------
# UPDATE CHATBOT
# ---------------------------------------------------
@router.put("/{bot_id}", response_model=ChatbotResponse)
def update_chatbot(bot_id: int, chatbot: ChatbotUpdate, db: Session = Depends(get_main_db)):
    bot = db.query(ChatbotModel).filter(ChatbotModel.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    try:
        update_data = chatbot.dict(exclude_unset=True)
        for key, value in update_data.items():
            if key == "buttons" and value is not None:
                value = [b.dict() for b in value]
            elif key == "faqs" and value is not None:
                value = [f.dict() for f in value]
            setattr(bot, key, value)
        bot.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(bot)
        return bot
    except Exception as e:
        db.rollback()
        print("UPDATE CHATBOT ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to update chatbot")


# ---------------------------------------------------
# DELETE CHATBOT
# ---------------------------------------------------
@router.delete("/{bot_id}")
def delete_chatbot(bot_id: int, db: Session = Depends(get_main_db)):
    bot = db.query(ChatbotModel).filter(ChatbotModel.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    try:
        db.delete(bot)
        db.commit()
        return {"success": True, "message": "Chatbot deleted successfully"}
    except Exception as e:
        db.rollback()
        print("DELETE CHATBOT ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to delete chatbot")


# ---------------------------------------------------
# TOGGLE CHATBOT STATUS (active ↔ inactive)
# ---------------------------------------------------
@router.patch("/{bot_id}/status")
def toggle_status(bot_id: int, db: Session = Depends(get_main_db)):
    bot = db.query(ChatbotModel).filter(ChatbotModel.id == bot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    try:
        # ✅ Toggle between 'active' and 'inactive'
        bot.status = "inactive" if bot.status == "active" else "active"
        bot.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(bot)
        return {"success": True, "status": bot.status}
    except Exception as e:
        db.rollback()
        print("STATUS TOGGLE ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to toggle chatbot status")


# ---------------------------------------------------
# DUPLICATE CHATBOT
# ---------------------------------------------------
@router.post("/{bot_id}/duplicate", response_model=ChatbotResponse)
def duplicate_chatbot(bot_id: int, db: Session = Depends(get_main_db)):
    original = db.query(ChatbotModel).filter(ChatbotModel.id == bot_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Chatbot not found")
    try:
        new_bot = ChatbotModel(
            name=f"{original.name} (Copy)",
            description=original.description,
            status="active",
            welcome_message=original.welcome_message,
            buttons=original.buttons,
            faqs=original.faqs,
            conversations=0,
            satisfaction=0.0,
            responses=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_bot)
        db.commit()
        db.refresh(new_bot)
        return new_bot
    except Exception as e:
        db.rollback()
        print("DUPLICATE CHATBOT ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to duplicate chatbot")


# ---------------------------------------------------
# CHAT ENDPOINT (with inactive check)
# ---------------------------------------------------
@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_main_db)):
    # Find chatbot
    bot = db.query(ChatbotModel).filter(ChatbotModel.id == req.chatbot_id).first()
    if not bot:
        raise HTTPException(status_code=404, detail="Chatbot not found")

    # ✅ Block inactive chatbots
    if bot.status != "active":
        raise HTTPException(
            status_code=403,
            detail="This chatbot is currently inactive. Please activate it first."
        )

    try:
        # Create conversation
        conversation = ChatConversation(
            chatbot_id=bot.id,
            started_at=datetime.utcnow(),
            message_count=0
        )
        db.add(conversation)
        db.flush()

        # Save user message
        user_message = ChatMessage(
            conversation_id=conversation.id,
            role="user",
            content=req.message
        )
        db.add(user_message)

        # Generate bot reply
        reply = get_reply_from_chatbot(req.message, bot.faqs, bot.welcome_message)

        # Save bot message
        bot_message = ChatMessage(
            conversation_id=conversation.id,
            role="bot",
            content=reply
        )
        db.add(bot_message)

        # Update conversation
        conversation.message_count = 2
        conversation.ended_at = datetime.utcnow()

        # Update chatbot stats
        db.execute(
            update(ChatbotModel)
            .where(ChatbotModel.id == bot.id)
            .values(
                conversations=ChatbotModel.conversations + 1,
                responses=ChatbotModel.responses + 1,
                last_active=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
        )

        db.commit()
        return ChatResponse(reply=reply)

    except Exception as e:
        db.rollback()
        print("CHAT ENDPOINT ERROR:", e)
        raise HTTPException(status_code=500, detail="Failed to process chat")
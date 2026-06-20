from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel

# from app.database import get_main_db
from app.database import get_main_db
from app.models.inbox import Conversation, Message
from app.models.message_log import MessageLog
from datetime import datetime

import asyncio
from app.services.whatsapp_service import send_whatsapp_text

router = APIRouter()


class ConversationCreate(BaseModel):
    contact_name: str
    phone_number: Optional[str] = None
    tag: Optional[str] = None


class MessageCreate(BaseModel):
    from_type: str
    text: Optional[str] = None
    msg_type: Optional[str] = "text"
    content: Optional[dict] = None


class ConversationUpdate(BaseModel):
    status: Optional[str] = None
    assigned_agent: Optional[str] = None
    is_closed: Optional[bool] = None


@router.get("/")
def get_conversations(
    is_closed: Optional[bool] = None, db: Session = Depends(get_main_db)
):
    query = db.query(Conversation)
    if is_closed is not None:
        query = query.filter(Conversation.is_closed == is_closed)
    convs = query.order_by(Conversation.created_at.desc()).all()
    result = []
    for c in convs:
        msgs = (
            db.query(Message)
            .filter(Message.conversation_id == c.id)
            .order_by(Message.created_at)
            .all()
        )
        result.append(
            {
                "id": c.id,
                "contact_name": c.contact_name,
                "phone_number": c.phone_number,
                "last_message": c.last_message,
                "status": c.status,
                "tag": c.tag,
                "assigned_agent": c.assigned_agent,
                "is_closed": c.is_closed,
                "template_messages": c.template_messages,
                "session_messages": c.session_messages,
                "created_at": str(c.created_at),
                "messages": [
                    {
                        "id": m.id,
                        "from_type": m.from_type,
                        "text": m.text,
                        "msg_type": m.msg_type,
                        "content": m.content,
                        "is_read": m.is_read,
                        "created_at": str(m.created_at),
                    }
                    for m in msgs
                ],
            }
        )
    return result


@router.post("/")
def create_conversation(
    payload: ConversationCreate, db: Session = Depends(get_main_db)
):
    conv = Conversation(**payload.dict())
    db.add(conv)
    db.commit()
    db.refresh(conv)
    return conv


@router.patch("/{conv_id}")
def update_conversation(
    conv_id: int, payload: ConversationUpdate, db: Session = Depends(get_main_db)
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Not found")
    for key, value in payload.dict(exclude_unset=True).items():
        setattr(conv, key, value)
    db.commit()
    db.refresh(conv)
    return conv


# @router.post("/{conv_id}/messages")
# def send_message(
#     conv_id: int, payload: MessageCreate, db: Session = Depends(get_main_db)
# ):
#     conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
#     if not conv:
#         raise HTTPException(status_code=404, detail="Not found")

#     msg = Message(conversation_id=conv_id, **payload.dict())
#     db.add(msg)
#     conv.last_message = payload.text or ""

#     if payload.from_type == "agent":
#         conv.status = "intervened"
#         conv.session_messages += 1

#         if conv.phone_number and payload.text:
#             try:
#                 # phone_clean = (
#                 #     conv.phone_number.replace("+", "").replace(" ", "").replace("-", "")
#                 # )
#                 phone_raw = conv.phone_number.replace("+", "").replace(" ", "").replace("-", "")
#                 if phone_raw.startswith("91"):
#                     phone_clean = phone_raw
#                 else:
#                     phone_clean = "91" + phone_raw
#                 loop = asyncio.new_event_loop()
#                 asyncio.set_event_loop(loop)
#                 result = loop.run_until_complete(
#                     send_whatsapp_text(
#                         to_phone=phone_clean,
#                         text=payload.text,
#                     )
#                 )
#                 loop.close()
#                 wamid = result.get("messages", [{}])[0].get("id")
#                 msg.wamid = wamid
#                 db.add(msg)
#                 print(f"✅ WhatsApp sent: {result}")
#             except Exception as e:
#                 print(f"❌ WhatsApp send failed: {e}")

#     elif payload.from_type == "template":
#         conv.template_messages += 1
#         conv.is_closed = False

#     db.commit()
#     db.refresh(msg)
#     return msg


@router.post("/{conv_id}/messages")
def send_message(
    conv_id: int, payload: MessageCreate, db: Session = Depends(get_main_db)
):
    conv = db.query(Conversation).filter(Conversation.id == conv_id).first()
    if not conv:
        raise HTTPException(status_code=404, detail="Not found")

    msg = Message(conversation_id=conv_id, **payload.dict())
    db.add(msg)
    conv.last_message = payload.text or ""

    if payload.from_type == "agent":
        conv.status = "intervened"
        conv.session_messages += 1

    elif payload.from_type == "template":
        conv.template_messages += 1
        conv.is_closed = False

    # ✅ agent or template — இரண்டுக்கும் WhatsApp-க்கு send பண்ணு
    if (
        payload.from_type in ("agent", "template")
        and conv.phone_number
        and payload.text
    ):
        try:
            phone_raw = (
                conv.phone_number.replace("+", "").replace(" ", "").replace("-", "")
            )
            if phone_raw.startswith("91"):
                phone_clean = phone_raw
            else:
                phone_clean = "91" + phone_raw

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(
                send_whatsapp_text(
                    to_phone=phone_clean,
                    text=payload.text,
                )
            )
            loop.close()
            wamid = result.get("messages", [{}])[0].get("id")
            msg.wamid = wamid
            db.add(msg)
            print(f"✅ WhatsApp sent: {result}")
            log = MessageLog(
                recipient_name=conv.contact_name,
                recipient_phone=conv.phone_number,
                message=payload.text,
                template_name=payload.text if payload.from_type == "template" else None,
                status="sent",
                wamid=wamid,
                source="inbox",
                sent_at=datetime.utcnow(),
            )
            db.add(log)
        except Exception as e:
            print(f"❌ WhatsApp send failed: {e}")

    db.commit()
    db.refresh(msg)
    return msg


@router.get("/{conv_id}/messages")
def get_messages(conv_id: int, db: Session = Depends(get_main_db)):
    return (
        db.query(Message)
        .filter(Message.conversation_id == conv_id)
        .order_by(Message.created_at)
        .all()
    )

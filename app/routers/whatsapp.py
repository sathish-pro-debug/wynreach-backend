# app/routers/whatsapp.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.whatsapp_service import (
    send_whatsapp_template,
    send_bulk_whatsapp,
    get_whatsapp_templates,
    create_whatsapp_template,
)

from fastapi import Query, Request, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from app.database import get_log_db
from app.models.inbox import Conversation, Message
from app.database import get_main_db
from app.models.message_log import MessageLog
from datetime import datetime

router = APIRouter()


async def get_template_body(template_name: str) -> str:
    try:
        templates = await get_whatsapp_templates()
        for t in templates:
            if t.get("name") == template_name:
                components = t.get("components", [])
                for comp in components:
                    if comp.get("type") == "BODY":
                        return comp.get("text", template_name)
        return template_name
    except:
        return template_name


class SingleMessageRequest(BaseModel):
    to_phone: str
    template_name: str
    language_code: str = "en_US"
    components: Optional[list] = None


class BulkMessageRequest(BaseModel):
    campaign_id: str
    template_name: str
    language_code: str = "en_US"
    recipients: list[dict]


@router.get("/templates")
async def fetch_templates():
    try:
        templates = await get_whatsapp_templates()
        return {"success": True, "templates": templates, "count": len(templates)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_single_message(request: SingleMessageRequest):
    try:
        result = await send_whatsapp_template(
            to_phone=request.to_phone,
            template_name=request.template_name,
            language_code=request.language_code,
            components=request.components,
        )
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# @router.post("/send-bulk")
# async def send_bulk_messages(request: BulkMessageRequest):
#     try:
#         result = await send_bulk_whatsapp(
#             recipients=request.recipients,
#             template_name=request.template_name,
#             language_code=request.language_code,
#         )
#         return {"success": True, "campaign_id": request.campaign_id, "summary": result}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.post("/send-bulk")
async def send_bulk_messages(
    request: BulkMessageRequest, db: Session = Depends(get_main_db)  # இதை add pannunga
):
    try:
        result = await send_bulk_whatsapp(
            recipients=request.recipients,
            template_name=request.template_name,
            language_code=request.language_code,
        )

        # ✅ Success logs save
        for item in result["success"]:
            log = MessageLog(
                recipient_phone=item["phone"],
                recipient_name=item.get("name", item["phone"]),
                # message=f"Template: {request.template_name}",
                message=await get_template_body(request.template_name)
                or request.template_name,
                template_name=request.template_name,
                campaign_id=request.campaign_id,
                campaign_name=request.campaign_id,
                status="sent",
                wamid=item.get("message_id"),
                sent_at=datetime.utcnow(),
                direction="outgoing",
                source="campaign",
            )
            db.add(log)

        # ✅ Failed logs save
        for item in result["failed"]:
            log = MessageLog(
                recipient_phone=item["phone"],
                # message=f"Template: {request.template_name}",
                message=await get_template_body(request.template_name)
                or request.template_name,
                template_name=request.template_name,
                campaign_id=request.campaign_id,
                campaign_name=request.campaign_id,
                status="failed",
                error_reason=item.get("error"),
                sent_at=datetime.utcnow(),
                direction="outgoing",
                source="campaign",
            )
            db.add(log)

        db.commit()

        return {"success": True, "campaign_id": request.campaign_id, "summary": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
):
    if hub_verify_token == "wynreach123":
        return PlainTextResponse(hub_challenge)
    raise HTTPException(status_code=403, detail="Invalid verify token")


# @router.post("/webhook")
# async def receive_webhook(request: Request):
#     from app.database import main_engine
#     from sqlalchemy.orm import sessionmaker

#     MainSession = sessionmaker(bind=main_engine)
#     db = MainSession()

#     data = await request.json()
#     try:
#         entry = data["entry"][0]
#         changes = entry["changes"][0]
#         field = changes.get("field", "")
#         value = changes["value"]
#         import json

#         print("📥 WEBHOOK DATA:")
#         print(json.dumps(data, indent=2))

#         # ✅ Template status update
#         if field == "message_template_status_update":
#             template_name = value.get("message_template_name")
#             event = value.get("event")
#             print(f"📋 Template webhook: {template_name} → {event}")
#             if event == "APPROVED" and template_name:
#                 from app.database import MainSessionLocal
#                 from app.models.template import Template

#                 log_db = MainSessionLocal()
#                 t = (
#                     log_db.query(Template)
#                     .filter(Template.name == template_name)
#                     .first()
#                 )
#                 if t:
#                     t.status = "active"
#                     log_db.commit()
#                     print(f"✅ Template '{template_name}' auto-approved in DB!")
#                 log_db.close()

#         # ✅ Read receipt handle
#         # statuses = value.get("statuses", [])
#         # for status in statuses:
#         #     if status.get("status") == "read":
#         #         wamid = status.get("id")
#         #         msg = db.query(Message).filter(Message.wamid == wamid).first()
#         #         if msg:
#         #             msg.is_read = True
#         #             db.commit()

#         # ✅ Status update (delivered / read / failed)
#         statuses = value.get("statuses", [])
#         for status in statuses:
#             wamid = status.get("id")
#             status_val = status.get("status")

#             # MessageLog update
#             msg_log = db.query(MessageLog).filter(MessageLog.wamid == wamid).first()
#             if msg_log:
#                 msg_log.status = status_val
#                 if status_val == "delivered":
#                     msg_log.delivered_at = datetime.utcnow()
#                     msg_log.delivered = True
#                 elif status_val == "read":
#                     msg_log.read_at = datetime.utcnow()
#                     msg_log.is_read = True
#                     msg_log.delivered_at = msg_log.delivered_at or datetime.utcnow()
#                 db.commit()

#             # Inbox Message update (existing logic)
#             if status_val == "read":
#                 msg = db.query(Message).filter(Message.wamid == wamid).first()
#                 if msg:
#                     msg.is_read = True
#                     db.commit()

#         # ✅ Incoming messages
#         messages = value.get("messages", [])
#         for msg in messages:
#             phone = msg["from"]
#             text = msg.get("text", {}).get("body", "")
#             conv = (
#                 db.query(Conversation)
#                 .filter(Conversation.phone_number == phone)
#                 .first()
#             )
#             if not conv:
#                 conv = Conversation(
#                     contact_name=phone, phone_number=phone, status="unread"
#                 )
#                 db.add(conv)
#                 db.commit()
#                 db.refresh(conv)
#             new_msg = Message(
#                 conversation_id=conv.id,
#                 from_type="user",
#                 text=text,
#                 msg_type="text",
#             )
#             db.add(new_msg)
#             conv.last_message = text
#             conv.is_closed = False
#             conv.status = "unread"

#             # Incoming message log save
#             incoming_log = MessageLog(
#                 recipient_name=conv.contact_name or phone,
#                 recipient_phone=phone,
#                 message=text,
#                 status="received",
#                 source="inbox",
#                 direction="incoming",
#                 sent_at=datetime.utcnow(),
#             )
#             db.add(incoming_log)
#             db.commit()

#     except Exception as e:
#         print(f"Webhook error: {e}")
#     finally:
#         db.close()
#     return {"status": "ok"}


@router.post("/webhook")
async def receive_webhook(request: Request):
    from app.database import main_engine
    from sqlalchemy.orm import sessionmaker

    MainSession = sessionmaker(bind=main_engine)
    db = MainSession()

    data = await request.json()
    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        field = changes.get("field", "")
        value = changes["value"]
        import json

        print("📥 WEBHOOK DATA:")
        print(json.dumps(data, indent=2))

        # ✅ Template status update
        if field == "message_template_status_update":
            template_name = value.get("message_template_name")
            event = value.get("event")
            print(f"📋 Template webhook: {template_name} → {event}")
            if event == "APPROVED" and template_name:
                from app.database import MainSessionLocal
                from app.models.template import Template

                log_db = MainSessionLocal()
                t = (
                    log_db.query(Template)
                    .filter(Template.name == template_name)
                    .first()
                )
                if t:
                    t.status = "active"
                    log_db.commit()
                    print(f"✅ Template '{template_name}' auto-approved in DB!")
                log_db.close()

        # ✅ Status update (delivered / read / failed)
        statuses = value.get("statuses", [])
        for status in statuses:
            wamid = status.get("id")
            status_val = status.get("status")

            msg_log = db.query(MessageLog).filter(MessageLog.wamid == wamid).first()
            if msg_log:
                msg_log.status = status_val
                if status_val == "delivered":
                    msg_log.delivered_at = datetime.utcnow()
                    msg_log.delivered = True
                elif status_val == "read":
                    msg_log.read_at = datetime.utcnow()
                    msg_log.is_read = True
                    msg_log.delivered_at = msg_log.delivered_at or datetime.utcnow()
                db.commit()

            if status_val == "read":
                msg = db.query(Message).filter(Message.wamid == wamid).first()
                if msg:
                    msg.is_read = True
                    db.commit()

        # ✅ Incoming messages
        messages = value.get("messages", [])
        for msg in messages:
            phone = msg["from"]
            msg_type = msg.get("type", "")
            text = msg.get("text", {}).get("body", "")

            # ✅ Interactive button reply (Not Interested)
            if msg_type == "interactive":
                interactive = msg.get("interactive", {})
                button_reply = interactive.get("button_reply", {})
                button_id = button_reply.get("id", "").lower()
                button_title = button_reply.get("title", "")

                if (
                    "not_interested" in button_id
                    or "not interested" in button_title.lower()
                ):
                    from app.models.contact import Contact
                    from app.models.Suppression import Suppression

                    contact = db.query(Contact).filter(Contact.phone == phone).first()

                    if contact:
                        existing = (
                            db.query(Suppression)
                            .filter(
                                Suppression.contact_id == contact.id,
                                Suppression.channel == "WhatsApp",
                            )
                            .first()
                        )

                        if not existing:
                            suppression = Suppression(
                                contact_id=contact.id,
                                channel="WhatsApp",
                                reason="Opted Out",
                                source="WhatsApp Button",
                                created_at=datetime.utcnow(),
                            )
                            db.add(suppression)
                            contact.status = "suppressed"
                            db.commit()
                            print(f"✅ Auto suppressed: {phone} - Not Interested")
                continue  # interactive message inbox-ல save வேண்டாம்

            # ✅ Normal text message — inbox save
            conv = (
                db.query(Conversation)
                .filter(Conversation.phone_number == phone)
                .first()
            )
            if not conv:
                conv = Conversation(
                    contact_name=phone, phone_number=phone, status="unread"
                )
                db.add(conv)
                db.commit()
                db.refresh(conv)

            new_msg = Message(
                conversation_id=conv.id,
                from_type="user",
                text=text,
                msg_type="text",
            )
            db.add(new_msg)
            conv.last_message = text
            conv.is_closed = False
            conv.status = "unread"

            incoming_log = MessageLog(
                recipient_name=conv.contact_name or phone,
                recipient_phone=phone,
                message=text,
                status="received",
                source="inbox",
                direction="incoming",
                sent_at=datetime.utcnow(),
            )
            db.add(incoming_log)
            db.commit()

            # ✅ Chatbot auto-reply
            try:
                from app.models.chatbot import Chatbot
                from app.services.whatsapp_service import send_whatsapp_text

                active_bot = (
                    db.query(Chatbot).filter(Chatbot.status == "active").first()
                )

                if active_bot and text:
                    reply_text = None

                    # ✅ Same chatbot logic use பண்றோம்
                    from app.services.chat_service import get_reply_from_chatbot

                    reply_text = get_reply_from_chatbot(
                        message=text,
                        faqs=active_bot.faqs or [],
                        welcome_message=active_bot.welcome_message,
                    )

                    # WhatsApp-ல reply அனுப்பு
                    await send_whatsapp_text(to_phone=phone, text=reply_text)

                    # Inbox-ல bot reply save
                    bot_msg = Message(
                        conversation_id=conv.id,
                        from_type="bot",
                        text=reply_text,
                        msg_type="text",
                    )
                    db.add(bot_msg)
                    db.commit()
                    print(f"✅ Bot replied to {phone}: {reply_text[:50]}")

            except Exception as bot_error:
                print(f"⚠️ Bot reply error: {bot_error}")

    except Exception as e:
        print(f"Webhook error: {e}")
    finally:
        db.close()
    return {"status": "ok"}


@router.post("/templates/submit")
async def submit_template_to_meta(payload: dict):
    try:
        result = await create_whatsapp_template(
            name=payload.get("name"),
            body_text=payload.get("body"),
            language=payload.get("language", "en"),
            category=payload.get("category", "MARKETING"),
        )
        return {"success": True, "meta_response": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

    # @router.post("/templates/sync")
    # async def sync_templates_from_meta(db: Session = Depends(get_log_db)):
    from app.models.template import Template

    try:
        meta_templates = await get_whatsapp_templates()
        updated = []
        for mt in meta_templates:
            name = mt.get("name")
            if not name:
                continue
            t = db.query(Template).filter(Template.name == name).first()
            if t:
                t.status = "active"
                db.commit()
                updated.append(name)
            else:
                # DB-ல இல்லன்னா புதுசா create பண்ணும்
                new_t = Template(
                    name=name,
                    type="whatsapp",
                    category="Marketing",
                    content="[]",
                    variables=[],
                    status="active",
                )
                db.add(new_t)
                db.commit()
                updated.append(f"{name} (new)")
        return {"success": True, "synced": updated}
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/templates/sync")
async def sync_templates_from_meta(db: Session = Depends(get_log_db)):
    from app.models.template import Template
    from app.services.whatsapp_service import get_all_whatsapp_templates

    try:
        meta_templates = await get_all_whatsapp_templates()
        meta_names = set()
        updated = []

        for mt in meta_templates:
            name = mt.get("name")
            status = mt.get("status")
            if not name:
                continue
            meta_names.add(name)

            t = db.query(Template).filter(Template.name == name).first()
            if t:
                t.status = (
                    "active"
                    if status == "APPROVED"
                    else ("pending_review" if status == "PENDING" else "rejected")
                )
                db.commit()
                updated.append(name)
            else:
                new_t = Template(
                    name=name,
                    type="whatsapp",
                    category="Marketing",
                    content="[]",
                    variables=[],
                    status="active" if status == "APPROVED" else "pending_review",
                )
                db.add(new_t)
                db.commit()
                updated.append(f"{name} (new)")

        # ✅ Meta-la illama poiruchi (delete aaiduchu) WhatsApp templates-a
        # DB-laum delete pannunga
        deleted = []
        local_whatsapp_templates = (
            db.query(Template).filter(Template.type == "whatsapp").all()
        )

        for lt in local_whatsapp_templates:
            if lt.name not in meta_names:
                deleted.append(lt.name)
                db.delete(lt)

        db.commit()

        return {"success": True, "synced": updated, "deleted": deleted}
    except Exception as e:
        return {"success": False, "error": str(e)}


class TextMessageRequest(BaseModel):
    to_phone: str
    text: str


@router.post("/text")
async def send_text_message(request: TextMessageRequest):
    try:
        result = await send_whatsapp_text(
            to_phone=request.to_phone,
            text=request.text,
        )
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

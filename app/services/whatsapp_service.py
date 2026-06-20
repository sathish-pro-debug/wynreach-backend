# app/services/whatsapp_service.py

import httpx
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v20.0")

BASE_URL = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}"


# =====================================================
# SINGLE MESSAGE SEND
# =====================================================


async def send_whatsapp_template(
    to_phone: str,
    template_name: str,
    language_code: str = "en",
    components: Optional[list] = None,
) -> dict:

    url = f"{BASE_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"

    headers = {
        "Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}",
        "Content-Type": "application/json",
    }

    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "template",
        "template": {"name": template_name, "language": {"code": language_code}},
    }

    if components:
        payload["template"]["components"] = components

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        result = response.json()

        if response.status_code != 200:
            raise Exception(f"WhatsApp API Error: {result}")

        return result


# =====================================================
# BULK MESSAGE SEND
# =====================================================


async def send_bulk_whatsapp(
    recipients: list[dict], template_name: str, language_code: str = "en"
) -> dict:

    success = []
    failed = []

    for recipient in recipients:
        phone = recipient.get("phone")
        components = recipient.get("components", None)

        phone_clean = phone.replace("+", "").replace(" ", "").replace("-", "")

        try:
            result = await send_whatsapp_template(
                to_phone=phone_clean,
                template_name=template_name,
                language_code=language_code,
                components=components,
            )
            success.append(
                {
                    "phone": phone_clean,
                    "message_id": result.get("messages", [{}])[0].get("id"),
                }
            )

        except Exception as e:
            failed.append({"phone": phone_clean, "error": str(e)})
            print(f"   ❌ FAILED: {phone_clean} → {str(e)}")

    return {
        "total": len(recipients),
        "success_count": len(success),
        "failed_count": len(failed),
        "success": success,
        "failed": failed,
    }


# =====================================================
# GET TEMPLATES — Meta approved templates fetch
# =====================================================


async def get_whatsapp_templates() -> list:

    waba_id = os.getenv("WHATSAPP_WABA_ID", "2159005814867018")

    url = f"{BASE_URL}/{waba_id}/message_templates"

    headers = {"Authorization": f"Bearer {os.getenv('WHATSAPP_ACCESS_TOKEN')}"}

    params = {"fields": "name,status,language,components,category", "limit": 50}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        result = response.json()

        if response.status_code != 200:
            raise Exception(f"Template fetch error: {result}")

        templates = result.get("data", [])
        approved = [t for t in templates if t.get("status") == "APPROVED"]

        return approved


# =====================================================
# FREE TEXT MESSAGE SEND
# =====================================================
async def send_whatsapp_text(
    to_phone: str,
    text: str,
) -> dict:
    url = f"{BASE_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": text},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        result = response.json()
        if response.status_code != 200:
            raise Exception(f"WhatsApp API Error: {result}")
        return result


async def create_whatsapp_template(
    name: str,
    body_text: str,
    language: str = "en",
    category: str = "MARKETING",
) -> dict:

    waba_id = os.getenv("WHATSAPP_WABA_ID")
    url = f"{BASE_URL}/{waba_id}/message_templates"

    headers = {
        "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
        "Content-Type": "application/json",
    }

    payload = {
        "name": name.lower().replace(" ", "_"),
        "language": language,
        "category": category,
        "components": [
            {
                "type": "BODY",
                "text": body_text,
            }
        ],
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        result = response.json()
        print(f"Meta API Status: {response.status_code}")
        print(f"Meta API Response: {result}")
        if response.status_code != 200:
            raise Exception(f"Meta error: {result}")
        return result

async def delete_whatsapp_template(name: str) -> dict:
    """Delete a template from Meta WhatsApp Business Account"""
    waba_id = os.getenv("WHATSAPP_WABA_ID")
    url = f"{BASE_URL}/{waba_id}/message_templates"

    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"}
    params = {"name": name.lower().replace(" ", "_")}

    async with httpx.AsyncClient() as client:
        response = await client.delete(url, headers=headers, params=params)
        result = response.json()
        print(f"Meta Delete Status: {response.status_code}")
        print(f"Meta Delete Response: {result}")
        if response.status_code != 200:
            raise Exception(f"Meta delete error: {result}")
        return result


async def get_all_whatsapp_templates() -> list:
    """Get ALL templates regardless of status (used for sync, not sending)"""
    waba_id = os.getenv("WHATSAPP_WABA_ID", "2159005814867018")
    url = f"{BASE_URL}/{waba_id}/message_templates"

    headers = {"Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}"}
    params = {"fields": "name,status,language,components,category", "limit": 50}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        result = response.json()

        if response.status_code != 200:
            raise Exception(f"Template fetch error: {result}")

        return result.get("data", [])
# app/routers/webhook_proxy.py
from fastapi import APIRouter, Request
import httpx
import json

router = APIRouter(prefix="/api", tags=["Webhook Proxy"])

@router.post("/whatsapp/webhook")
async def webhook_proxy(request: Request):
    """
    Proxy webhook requests to both handlers.
    This keeps the existing URL but forwards to automation.
    """
    body = await request.body()
    data = json.loads(body)
    
    # Forward to automation webhook (async, non-blocking)
    async def forward_to_automation():
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://localhost:8000/api/automation/webhook",
                    json=data,
                    timeout=5.0
                )
        except Exception as e:
            print(f"Failed to forward to automation: {e}")
    
    # Run in background
    import asyncio
    asyncio.create_task(forward_to_automation())
    
    # Return the response from the main webhook handler
    # This would call your existing whatsapp.py webhook
    # For now, we return a generic response
    return {"status": "ok"}
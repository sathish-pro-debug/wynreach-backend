from fastapi import APIRouter

from app.schemas.ai_template import (
    AITemplateRequest,
    AITemplateResponse,
)

from app.services.ai_template_service import (
    generate_template,
)

router = APIRouter(
    prefix="/api/ai/templates",
    tags=["AI Templates"],
)


@router.post(
    "/generate",
    response_model=AITemplateResponse,
)
async def generate_ai_template(
    request: AITemplateRequest,
):
    return await generate_template(request.prompt)
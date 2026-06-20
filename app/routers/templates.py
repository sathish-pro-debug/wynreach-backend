from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime
from app.database import get_log_db
from app.models.template import Template
from app.utils.notification_service import create_notification
from app.utils.template_image_service import get_template_image_service
from app.utils.email_template_renderer import get_email_template_renderer
from app.utils.render_email_template import (
    PREVIEW_LOG_ID,
    normalize_template_blocks,
    render_blocks_to_html,
)

router = APIRouter()


class TemplateCreate(BaseModel):
    name: str
    type: str
    category: Optional[str] = None
    subject: Optional[str] = None
    content: str
    variables: Optional[list] = []


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    category: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    variables: Optional[list] = None
    status: Optional[str] = None


class TemplatePreviewRequest(BaseModel):
    template_id: Optional[int] = None
    template_content: Optional[Any] = None


class TemplateOut(BaseModel):
    id: int
    name: str
    type: str
    category: Optional[str]
    subject: Optional[str]
    content: str
    variables: Optional[list]
    status: str
    meta_approved: bool
    times_used: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.get("/")
def get_all_templates(
    type: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_log_db),
):
    """Get all templates with pagination and filtering"""
    query = db.query(Template)
    if type:
        query = query.filter(Template.type == type)
    if category:
        query = query.filter(Template.category == category)
    if status:
        query = query.filter(Template.status == status)
    if search:
        query = query.filter(Template.name.ilike(f"%{search}%"))
    total = query.count()
    templates = query.offset((page - 1) * limit).limit(limit).all()
    all_t = db.query(Template).all()
    return {
        "data": [TemplateOut.from_orm(t).dict() for t in templates],
        "total": total,
        "stats": {
            "total": len(all_t),
            "email": sum(1 for t in all_t if t.type == "email"),
            "whatsapp": sum(1 for t in all_t if t.type == "whatsapp"),
            "pending_review": sum(1 for t in all_t if t.status == "pending_review"),
        },
    }


@router.get("/{template_id}", response_model=TemplateOut)
def get_template(template_id: int, db: Session = Depends(get_log_db)):
    """Get a specific template"""
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")
    return t


@router.post("/preview")
def preview_template(payload: TemplatePreviewRequest, db: Session = Depends(get_log_db)):
    if payload.template_id is None and payload.template_content is None:
        raise HTTPException(
            status_code=400,
            detail="template_id or template_content is required",
        )

    if payload.template_id is not None:
        template = db.query(Template).filter(Template.id == payload.template_id).first()
        if not template:
            raise HTTPException(status_code=404, detail="Template not found")
        template_content = template.content
    else:
        template_content = payload.template_content

    blocks = normalize_template_blocks(template_content)
    html, diagnostics = render_blocks_to_html(
        blocks,
        log_id=PREVIEW_LOG_ID,
        validate_images=True,
        include_diagnostics=True,
    )

    return {
        "html": html,
        "diagnostics": diagnostics,
        "template_blocks_count": diagnostics["template_blocks_count"],
        "image_count": diagnostics["image_count"],
        "button_count": diagnostics["button_count"],
        "image_urls": diagnostics["image_urls"],
        "button_urls": diagnostics["button_urls"],
        "open_tracking_present": diagnostics["open_tracking_present"],
        "click_tracking_present": diagnostics["click_tracking_present"],
    }


@router.get("/{template_id}/preview")
def get_template_preview(template_id: int, db: Session = Depends(get_log_db)):
    """
    Get template with presigned URLs for image preview

    Returns template content with S3 keys replaced by presigned URLs
    for safe viewing in the frontend
    """
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        image_service = get_template_image_service()
        # Replace S3 keys with presigned URLs for preview
        content_with_urls = image_service.replace_s3_keys_with_presigned_urls(t.content)

        return {
            "id": t.id,
            "name": t.name,
            "type": t.type,
            "category": t.category,
            "subject": t.subject,
            "content": content_with_urls,
            "variables": t.variables,
            "status": t.status,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}/render-html")
def render_template_html(
    template_id: int,
    merge_tags: Optional[str] = Query(None),  # JSON string of merge tags
    db: Session = Depends(get_log_db),
):
    """
    Render template to HTML email format

    Query Parameters:
        merge_tags (str): JSON string of merge tags {{"first_name": "John", ...}}

    Returns HTML email content ready for sending
    """
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        # Parse merge tags if provided
        tags_dict = {}
        if merge_tags:
            import json

            tags_dict = json.loads(merge_tags)

        renderer = get_email_template_renderer()
        html = renderer.render_template_for_email(t.content, tags_dict)

        return {"html": html, "template_id": t.id, "template_name": t.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=TemplateOut, status_code=201)
def create_template(payload: TemplateCreate, db: Session = Depends(get_log_db)):
    """
    Create a new template

    Automatically converts Base64 images to S3 and stores S3 keys
    """
    data = payload.dict()

    try:
        # Process images: convert Base64 to S3
        image_service = get_template_image_service()
        processed_content, s3_keys = image_service.replace_image_urls_with_s3_keys(
            data["content"]
        )
        data["content"] = processed_content

    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Image processing failed: {str(e)}"
        )

    # Set status based on type
    if data.get("type") == "whatsapp":
        data["status"] = "pending_review"
    else:
        data["status"] = "active"

    # Create template
    t = Template(**data)
    db.add(t)
    db.commit()
    db.refresh(t)

    create_notification(
        db=db,
        notification_type="templateCreated",
        title="Template Created",
        message=f'Template "{t.name}" created successfully',
    )

    return t


@router.patch("/{template_id}", response_model=TemplateOut)
def update_template(
    template_id: int, payload: TemplateUpdate, db: Session = Depends(get_log_db)
):
    """
    Update a template

    Automatically converts Base64 images to S3 if content is updated
    """
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    data = payload.dict(exclude_unset=True)

    # Process images if content is being updated
    if "content" in data:
        try:
            image_service = get_template_image_service()
            processed_content, s3_keys = image_service.replace_image_urls_with_s3_keys(
                data["content"]
            )
            data["content"] = processed_content
        except Exception as e:
            raise HTTPException(
                status_code=400, detail=f"Image processing failed: {str(e)}"
            )

    # Update fields
    for key, value in data.items():
        setattr(t, key, value)

    db.commit()
    db.refresh(t)

    return t


@router.post("/{template_id}/duplicate", response_model=TemplateOut)
def duplicate_template(template_id: int, db: Session = Depends(get_log_db)):
    """Duplicate an existing template"""
    o = db.query(Template).filter(Template.id == template_id).first()
    if not o:
        raise HTTPException(status_code=404, detail="Template not found")

    new_t = Template(
        name=f"{o.name} (Copy)",
        type=o.type,
        category=o.category,
        subject=o.subject,
        content=o.content,  # S3 keys will be reused
        variables=o.variables,
    )
    db.add(new_t)
    db.commit()
    db.refresh(new_t)

    return new_t


@router.patch("/{template_id}/archive", response_model=TemplateOut)
def archive_template(template_id: int, db: Session = Depends(get_log_db)):
    """Archive a template"""
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    t.status = "archived"
    db.commit()
    db.refresh(t)

    return t


@router.post("/{template_id}/submit-meta", response_model=TemplateOut)
def submit_for_meta(template_id: int, db: Session = Depends(get_log_db)):
    """Submit template for Meta approval (WhatsApp)"""
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    t.status = "pending_review"
    db.commit()
    db.refresh(t)

    create_notification(
        db=db,
        notification_type="approvalRequested",
        title="Approval Requested",
        message=f'Template "{t.name}" submitted to Meta for approval',
    )

    return t


# @router.delete("/{template_id}")
# def delete_template(template_id: int, db: Session = Depends(get_log_db)):
#     """Delete a template"""
#     t = db.query(Template).filter(Template.id == template_id).first()
#     if not t:
#         raise HTTPException(status_code=404, detail="Template not found")

#     db.delete(t)
#     db.commit()

#     return {"message": "Template deleted successfully"}


@router.delete("/{template_id}")
async def delete_template(template_id: int, db: Session = Depends(get_log_db)):
    """Delete a template (also deletes from Meta if WhatsApp template)"""
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    # WhatsApp template-a Meta-layum delete pannunga
    if t.type == "whatsapp":
        try:
            from app.services.whatsapp_service import delete_whatsapp_template

            await delete_whatsapp_template(t.name)
        except Exception as e:
            print(f"⚠️ Meta delete failed (continuing with local delete): {e}")

    db.delete(t)
    db.commit()

    return {"message": "Template deleted successfully"}


@router.post("/{template_id}/validate-images")
def validate_template_images(template_id: int, db: Session = Depends(get_log_db)):
    """
    Validate all images in a template

    Returns validation report with image counts and any issues
    """
    t = db.query(Template).filter(Template.id == template_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Template not found")

    try:
        image_service = get_template_image_service()
        validation_report = image_service.validate_template_images(t.content)

        return {"template_id": t.id, "template_name": t.name, **validation_report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
from app.services.s3_service import get_s3_service

router = APIRouter()

@router.post("/upload-image")
async def upload_template_image(file: UploadFile = File(...)):
    """
    Upload an image for email template use
    
    Query Parameters:
        None
        
    Request Body:
        file (UploadFile): Image file (JPEG, PNG, GIF, WebP - max 10MB)
        
    Response:
        {
            "success": bool,
            "key": str,  # S3 object key for storing in template
            "url": str,  # Presigned URL for immediate use in preview
            "message": str
        }
        
    Errors:
        400: Invalid image type or file size exceeded
        500: S3 upload failed or configuration error
    """
    try:
        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No filename provided"
            )
        
        # Get S3 service
        s3_service = get_s3_service()
        
        # Upload image to S3
        s3_key = s3_service.upload_image(file.file, file.content_type)
        
        # Generate presigned URL for preview
        presigned_url = s3_service.get_presigned_url(s3_key)
        
        return {
            "success": True,
            "key": s3_key,
            "url": presigned_url,
            "message": f"Image uploaded successfully: {file.filename}"
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during upload: {str(e)}"
        )


@router.get("/presigned-url")
async def get_presigned_url(key: str):
    """
    Generate a presigned URL for an existing S3 object
    
    Query Parameters:
        key (str): S3 object key
        
    Response:
        {
            "success": bool,
            "url": str,  # Presigned URL
            "key": str   # S3 object key
        }
        
    Errors:
        400: Invalid or missing S3 key
        500: Failed to generate presigned URL
    """
    try:
        if not key:
            raise HTTPException(
                status_code=400,
                detail="S3 key is required"
            )
        
        s3_service = get_s3_service()
        
        # Validate key exists
        if not s3_service.validate_s3_key(key):
            raise HTTPException(
                status_code=404,
                detail=f"S3 object not found: {key}"
            )
        
        # Generate presigned URL
        url = s3_service.get_presigned_url(key)
        
        return {
            "success": True,
            "url": url,
            "key": key
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate presigned URL: {str(e)}"
        )


@router.delete("/delete-image")
async def delete_image(key: str):
    """
    Delete an image from S3
    
    Query Parameters:
        key (str): S3 object key to delete
        
    Response:
        {
            "success": bool,
            "message": str,
            "key": str
        }
        
    Errors:
        400: Invalid or missing S3 key
        500: Failed to delete image
    """
    try:
        if not key:
            raise HTTPException(
                status_code=400,
                detail="S3 key is required"
            )
        
        s3_service = get_s3_service()
        s3_service.delete_image(key)
        
        return {
            "success": True,
            "message": f"Image deleted successfully",
            "key": key
        }
        
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete image: {str(e)}"
        )
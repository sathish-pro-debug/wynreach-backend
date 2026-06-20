"""
S3 Service Layer for Template Image Management
- Handles image uploads to private AWS S3 bucket
- Generates presigned URLs for email sending
- Validates image types and sizes
"""

import boto3
import uuid
import os
from io import BytesIO
from typing import Tuple, Optional
from fastapi import HTTPException
from app.core.config import settings

class S3ImageService:
    def __init__(self):
        """Initialize S3 client with credentials from environment"""
        if not settings.AWS_ACCESS_KEY_ID_EMAIL or not settings.AWS_SECRET_ACCESS_KEY_EMAIL:
            raise HTTPException(
                status_code=500,
                detail="AWS credentials not configured"
            )
        
        if not settings.AWS_S3_BUCKET:
            raise HTTPException(
                status_code=500,
                detail="S3 bucket not configured"
            )
        
        self.s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID_EMAIL,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_EMAIL,
            region_name=settings.AWS_S3_REGION
        )
        self.bucket = settings.AWS_S3_BUCKET
        self.presigned_url_expiration = 604800  # 7 days

    def validate_image(self, file, content_type: str) -> bool:
        """
        Validate image type and size
        
        Args:
            file: File object from upload
            content_type: MIME type of the file
            
        Returns:
            bool: True if valid
            
        Raises:
            HTTPException: If validation fails
        """
        # Validate content type
        if content_type not in settings.ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image type. Allowed types: {', '.join(settings.ALLOWED_IMAGE_TYPES)}"
            )
        
        # Validate file size
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        if file_size > max_size_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds {settings.MAX_IMAGE_SIZE_MB}MB limit"
            )
        
        return True

    def upload_image(self, file, content_type: str) -> str:
        """
        Upload image to S3 bucket
        
        Args:
            file: File object from upload
            content_type: MIME type of the file
            
        Returns:
            str: S3 object key
            
        Raises:
            HTTPException: If upload fails
        """
        try:
            # Validate image
            self.validate_image(file, content_type)
            
            # Generate unique filename
            file_extension = content_type.split('/')[-1]
            filename = f"templates/images/{uuid.uuid4()}.{file_extension}"
            
            # Upload to S3
            self.s3_client.upload_fileobj(
                file,
                self.bucket,
                filename,
                ExtraArgs={
                    "ContentType": content_type,
                    "Metadata": {
                        "source": "wynreach-templates",
                        "upload_type": "template_image"
                    }
                }
            )
            
            return filename
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image to S3: {str(e)}"
            )

    def get_presigned_url(self, key: str, expiration: Optional[int] = None) -> str:
        """
        Generate presigned URL for private S3 object
        
        Args:
            key: S3 object key
            expiration: URL expiration time in seconds (default: 7 days)
            
        Returns:
            str: Presigned URL
            
        Raises:
            HTTPException: If URL generation fails
        """
        try:
            if not expiration:
                expiration = self.presigned_url_expiration
            
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={
                    "Bucket": self.bucket,
                    "Key": key
                },
                ExpiresIn=expiration
            )
            
            return url
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate presigned URL: {str(e)}"
            )

    def delete_image(self, key: str) -> bool:
        """
        Delete image from S3 bucket
        
        Args:
            key: S3 object key
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            HTTPException: If deletion fails
        """
        try:
            self.s3_client.delete_object(
                Bucket=self.bucket,
                Key=key
            )
            return True
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete image from S3: {str(e)}"
            )

    def validate_s3_key(self, key: str) -> bool:
        """
        Validate that an S3 key exists
        
        Args:
            key: S3 object key
            
        Returns:
            bool: True if object exists
        """
        try:
            self.s3_client.head_object(Bucket=self.bucket, Key=key)
            return True
        except:
            return False


# Create singleton instance
_s3_service = None

def get_s3_service() -> S3ImageService:
    """Get or create S3 service instance"""
    global _s3_service
    if _s3_service is None:
        _s3_service = S3ImageService()
    return _s3_service


# Backward compatibility functions
def upload_image(file, content_type):
    """Legacy function for backward compatibility"""
    service = get_s3_service()
    return service.upload_image(file, content_type)

def get_signed_url(key):
    """Legacy function for backward compatibility"""
    service = get_s3_service()
    return service.get_presigned_url(key)
import json
import re
import base64
import io
from typing import Dict, List, Optional, Tuple
from fastapi import HTTPException
from app.services.s3_service import get_s3_service


class TemplateImageService:
    """Service for managing images in email templates"""

    def _get_blocks(self, content: str):

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid template JSON")

        # New Builder Format
        if isinstance(data, list):
            return data, data

        # Legacy Format
        if isinstance(data, dict):

            if "blocks" in data:
                return data["blocks"], data

            return [], data

        raise HTTPException(status_code=400, detail="Unsupported template format")

    def __init__(self):
        self.s3_service = get_s3_service()

    def extract_image_blocks(self, content: str):
        blocks, _ = self._get_blocks(content)

        image_blocks = []

        for idx, block in enumerate(blocks):

            if block.get("type") == "image":

                props = block.get("props", {})

                image_blocks.append(
                    {
                        "index": idx,
                        "block": block,
                        "url": props.get("url", ""),
                        "alt": props.get("alt", "Image"),
                    }
                )

        return image_blocks

    def is_base64_image(self, url: str) -> bool:
        """
        Check if URL is a Base64-encoded image

        Args:
            url (str): URL string

        Returns:
            bool: True if Base64 image
        """
        return isinstance(url, str) and url.startswith("data:image")

    def is_s3_key(self, url: str) -> bool:
        """
        Check if URL is an S3 key (stored in template)

        Args:
            url (str): URL string

        Returns:
            bool: True if S3 key
        """
        return isinstance(url, str) and url.startswith("templates/images/")

    def base64_to_s3(self, base64_url: str) -> str:
        """
        Convert Base64 image to S3 object and return key

        Args:
            base64_url (str): Base64 data URL

        Returns:
            str: S3 object key

        Raises:
            HTTPException: If conversion fails
        """
        try:
            # Parse Base64 data URL
            match = re.match(r"data:image/(\w+);base64,(.+)", base64_url)
            if not match:
                raise ValueError("Invalid Base64 image format")

            image_type = match.group(1)
            base64_data = match.group(2)

            # Convert Base64 to binary
            image_data = base64.b64decode(base64_data)

            # Create file-like object
            image_file = io.BytesIO(image_data)
            content_type = f"image/{image_type}"

            # Upload to S3
            s3_key = self.s3_service.upload_image(image_file, content_type)

            return s3_key

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to convert Base64 image to S3: {str(e)}",
            )

    # def replace_image_urls_with_s3_keys(    self,    content: str):
    #     blocks, root = self._get_blocks(content)

    #     s3_keys = []

    #     for block in blocks:

    #         if block.get("type") != "image":
    #             continue

    #         props = block.get("props", {})
    #         url = props.get("url", "")

    #         if not url: 
    #             continue

    #     if self.is_base64_image(url):

    #         s3_key = self.base64_to_s3(url)

    #         block["props"]["url"] = s3_key

    #         s3_keys.append(s3_key)

    #     elif self.is_s3_key(url):

    #         s3_keys.append(url)

    #     return json.dumps(root), s3_keys

    # def replace_s3_keys_with_presigned_urls(self, content: str):
    #     blocks, root = self._get_blocks(content)

    #     for block in blocks:

    #         if block.get("type") != "image":
    #             continue

    #     props = block.get("props", {})

    #     url = props.get("url", "")

    #     if self.is_s3_key(url):

    #         block["props"]["url"] = self.s3_service.get_presigned_url(url)

    #     return json.dumps(data)


    def replace_image_urls_with_s3_keys(self, content: str):
        blocks, root = self._get_blocks(content)

        s3_keys = []

        for block in blocks:

            if block.get("type") != "image":
                continue

            props = block.get("props", {})
            url = props.get("url", "")

            if not url:
                continue

            if self.is_base64_image(url):

                s3_key = self.base64_to_s3(url)

                block["props"]["url"] = s3_key

                s3_keys.append(s3_key)

            elif self.is_s3_key(url):

                s3_keys.append(url)

        return json.dumps(root), s3_keys

    def replace_s3_keys_with_presigned_urls(self, content: str):
        blocks, root = self._get_blocks(content)

        for block in blocks:

            if block.get("type") != "image":
                continue

            props = block.get("props", {})

            url = props.get("url", "")

            if self.is_s3_key(url):

                block["props"]["url"] = self.s3_service.get_presigned_url(url)

        return json.dumps(root)


    def get_image_html(self, image_block: Dict, use_presigned: bool = False) -> str:
        """
        Generate HTML for an image block

        Args:
            image_block (Dict): Image block from template
            use_presigned (bool): If True, convert S3 keys to presigned URLs

        Returns:
            str: HTML image tag
        """
        props = image_block.get("props", {})
        url = props.get("url", "")
        alt = props.get("alt", "Image")

        # If S3 key and presigned URLs are needed, generate URL
        if use_presigned and self.is_s3_key(url):
            url = self.s3_service.get_presigned_url(url)

        return f'<img src="{url}" alt="{alt}" style="width: 100%; border-radius: 6px; display: block; margin: 8px 0;" />'

    def validate_template_images(self, content: str):
        blocks, _ = self._get_blocks(content)

        results = {
            "valid": True,
            "total_blocks": len(blocks),
            "image_blocks": 0,
            "base64_images": 0,
            "s3_images": 0,
            "invalid_images": [],
            "issues": [],
        }

        for idx, block in enumerate(blocks):

            if block.get("type") != "image":
                continue

        results["image_blocks"] += 1

        url = block.get("props", {}).get("url", "")

        if self.is_base64_image(url):

            results["base64_images"] += 1

        elif self.is_s3_key(url):

            results["s3_images"] += 1

        return results


# Singleton instance
_template_image_service = None


def get_template_image_service() -> TemplateImageService:
    """Get or create template image service instance"""
    global _template_image_service
    if _template_image_service is None:
        _template_image_service = TemplateImageService()
    return _template_image_service

"""
Email Template Renderer
Handles HTML generation from template JSON with presigned image URLs
"""

import json
from typing import Dict, Optional
from fastapi import HTTPException
from app.utils.template_image_service import get_template_image_service


class EmailTemplateRenderer:
    """Renders email template to HTML with presigned image URLs"""
    
    def __init__(self):
        self.image_service = get_template_image_service()
    
    def render_block(self, block: Dict) -> str:
        """
        Render a single template block to HTML
        
        Args:
            block (Dict): Template block
            
        Returns:
            str: HTML representation
        """
        block_type = block.get("type")
        props = block.get("props", {})
        
        if block_type == "header":
            text = props.get("text", "")
            color = props.get("color", "#000000")
            font_size = props.get("fontSize", "22px")
            align = props.get("align", "center")
            return f'<h1 style="color: {color}; font-size: {font_size}; text-align: {align}; margin: 8px 0; font-family: Arial, sans-serif; font-weight: bold;">{text}</h1>'
        
        elif block_type == "text":
            text = props.get("text", "")
            color = props.get("color", "#000000")
            font_size = props.get("fontSize", "14px")
            align = props.get("align", "left")
            # Replace newlines with <br> tags and preserve formatting
            html_text = text.replace("\n", "<br/>")
            return f'<p style="color: {color}; font-size: {font_size}; text-align: {align}; line-height: 1.6; margin: 8px 0; font-family: Arial, sans-serif; white-space: pre-wrap;">{html_text}</p>'
        
        elif block_type == "image":
            return self.image_service.get_image_html(block, use_presigned=True)
        
        elif block_type == "button":
            label = props.get("label", "Click Here")
            url = props.get("url", "#")
            bg_color = props.get("bgColor", "#4f46e5")
            text_color = props.get("textColor", "#ffffff")
            return f'<div style="text-align: center; margin: 14px 0;"><a href="{url}" style="display: inline-block; background-color: {bg_color}; color: {text_color}; padding: 11px 28px; border-radius: 7px; font-weight: bold; font-size: 14px; text-decoration: none; font-family: Arial, sans-serif;">{label}</a></div>'
        
        elif block_type == "columns":
            left = props.get("left", "")
            right = props.get("right", "")
            left_html = left.replace("\n", "<br/>")
            right_html = right.replace("\n", "<br/>")
            return f'<table style="width: 100%; margin: 8px 0;"><tr><td style="width: 50%; padding: 12px; background: #f8fafc; border-radius: 7px; font-size: 13px; color: #475569;">{left_html}</td><td style="width: 50%; padding: 12px; background: #f8fafc; border-radius: 7px; font-size: 13px; color: #475569;">{right_html}</td></tr></table>'
        
        elif block_type == "divider":
            color = props.get("color", "#e2e8f0")
            return f'<hr style="border: none; border-top: 1px solid {color}; margin: 14px 0;" />'
        
        elif block_type == "footer":
            text = props.get("text", "")
            color = props.get("color", "#94a3b8")
            font_size = props.get("fontSize", "12px")
            return f'<div style="text-align: center; color: {color}; font-size: {font_size}; padding: 10px 0; font-family: Arial, sans-serif;">{text}</div>'
        
        else:
            return ""
    
    def render_template_to_html(self, template_content: str) -> str:
        """
        Render entire template to HTML email
        
        Args:
            template_content (str): Template JSON as string
            
        Returns:
            str: HTML email content
            
        Raises:
            HTTPException: If rendering fails
        """
        try:
            data = json.loads(template_content)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid template JSON"
            )
        
        blocks = data.get("blocks", [])
        
        # Build HTML
        html_parts = []
        html_parts.append('<!DOCTYPE html>')
        html_parts.append('<html>')
        html_parts.append('<head>')
        html_parts.append('<meta charset="UTF-8">')
        html_parts.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        html_parts.append('<style>')
        html_parts.append('''
            body {
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333333;
                margin: 0;
                padding: 0;
            }
            .email-container {
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #ffffff;
            }
            a {
                color: #4f46e5;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
        ''')
        html_parts.append('</style>')
        html_parts.append('</head>')
        html_parts.append('<body>')
        html_parts.append('<div class="email-container">')
        
        # Render all blocks
        for block in blocks:
            html_parts.append(self.render_block(block))
        
        html_parts.append('</div>')
        html_parts.append('</body>')
        html_parts.append('</html>')
        
        return '\n'.join(html_parts)
    
    def replace_merge_tags(self, html: str, tags: Dict[str, str]) -> str:
        """
        Replace merge tags with actual values
        
        Args:
            html (str): HTML content with merge tags
            tags (Dict): Dictionary of tag values
            
        Returns:
            str: HTML with replaced tags
        """
        for key, value in tags.items():
            tag = f"{{{{{key}}}}}"  # {{key}}
            html = html.replace(tag, str(value))
        
        return html
    
    def render_template_for_email(
        self,
        template_content: str,
        merge_tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Render template to final HTML email with merge tags replaced
        
        Args:
            template_content (str): Template JSON
            merge_tags (Dict): Merge tags to replace
            
        Returns:
            str: Final HTML email
        """
        # First, replace S3 keys with presigned URLs
        template_with_urls = self.image_service.replace_s3_keys_with_presigned_urls(
            template_content
        )
        
        # Render to HTML
        html = self.render_template_to_html(template_with_urls)
        
        # Replace merge tags if provided
        if merge_tags:
            html = self.replace_merge_tags(html, merge_tags)
        
        return html


# Singleton instance
_renderer = None

def get_email_template_renderer() -> EmailTemplateRenderer:
    """Get or create email template renderer instance"""
    global _renderer
    if _renderer is None:
        _renderer = EmailTemplateRenderer()
    return _renderer

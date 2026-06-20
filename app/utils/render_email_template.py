from urllib.parse import quote
import os
import json
from html import escape

import requests
from fastapi import HTTPException

from app.utils.template_image_service import get_template_image_service
from app.services.r2_service import get_public_url

API_BASE_URL = os.getenv("API_BASE_URL", "https://reach.wynsync.tech")
PREVIEW_LOG_ID = "preview"


def make_absolute_url(url):
    """Convert relative URLs to absolute URLs for email clients"""
    if not url or url.strip() == "":
        return ""
    # Already absolute
    if url.startswith("http://") or url.startswith("https://"):
        return url
    # Relative URL - make absolute
    if url.startswith("/"):
        return f"{API_BASE_URL}{url}"
    # No leading slash - add it
    return f"{API_BASE_URL}/{url}"


def normalize_template_blocks(template_content):
    if isinstance(template_content, str):
        try:
            data = json.loads(template_content)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid template JSON")
    else:
        data = template_content

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        if isinstance(data.get("blocks"), list):
            return data["blocks"]
        return []
    raise HTTPException(status_code=400, detail="Unsupported template format")


def get_block_image_url(block):
    props = block.get("props", {})
    return (
        props.get("externalUrl")
        or props.get("previewUrl")
        or props.get("url")
        or props.get("src")
        or props.get("imageUrl")
        or ""
    )


def get_button_url(block):
    return (block.get("props", {}) or {}).get("url", "")


def _resolve_image_url(raw_url):
    if not raw_url:
        return ""
    if isinstance(raw_url, str) and raw_url.startswith("uploads/"):
        return get_public_url(raw_url)
    if isinstance(raw_url, str) and raw_url.startswith("templates/images/"):
        image_service = get_template_image_service()
        return image_service.s3_service.get_presigned_url(raw_url)
    return make_absolute_url(raw_url)


def _check_image_url(url):
    if not url:
        return False, "empty"
    if url.startswith("data:image"):
        return True, "embedded"
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code != 200:
            response = requests.get(url, timeout=5, stream=True, allow_redirects=True)
        valid = response.status_code == 200
        return valid, str(response.status_code)
    except Exception as exc:
        return False, str(exc)


def inspect_template_blocks(blocks, validate_images=False):
    diagnostics = {
        "template_blocks_count": len(blocks),
        "image_count": 0,
        "button_count": 0,
        "image_urls": [],
        "button_urls": [],
        "images": [],
    }

    for block in blocks:
        block_type = block.get("type")
        if block_type == "image":
            diagnostics["image_count"] += 1
            raw_url = get_block_image_url(block)
            resolved_url = _resolve_image_url(raw_url)
            status = "VALID"
            valid = True
            status_detail = "not_checked"
            if validate_images:
                valid, status_detail = _check_image_url(resolved_url)
                status = "VALID" if valid else "INVALID"

            print("IMAGE BLOCK:")
            print(block)
            print("IMAGE URL:")
            print(resolved_url or raw_url or "EMPTY")
            print("IMAGE STATUS:")
            print(status)

            if resolved_url:
                diagnostics["image_urls"].append(resolved_url)
            diagnostics["images"].append(
                {
                    "block": block,
                    "raw_url": raw_url,
                    "url": resolved_url,
                    "valid": valid,
                    "status": status,
                    "status_detail": status_detail,
                }
            )

        elif block_type == "button":
            diagnostics["button_count"] += 1
            button_url = get_button_url(block)
            if button_url:
                diagnostics["button_urls"].append(button_url)

    return diagnostics


def validate_template_images_for_send(blocks):
    diagnostics = inspect_template_blocks(blocks, validate_images=True)
    invalid = [item for item in diagnostics["images"] if not item["valid"]]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail="Campaign contains invalid image URLs.",
        )
    return diagnostics


def render_blocks_to_html(blocks, log_id=None, validate_images=False, include_diagnostics=False):

    html = ""
    diagnostics = inspect_template_blocks(blocks, validate_images=validate_images)

    for block in blocks:

        block_type = block.get("type")

        props = block.get("props", {})

        # HEADER
        if block_type == "header":
            html += f"""
            <h1 style="
                color:{props.get('color', '#0f172a')};
                font-size:{props.get('fontSize', '22px')};
                text-align:{props.get('align', 'center')};
                font-family:Arial,sans-serif;
                font-weight:bold;
                margin:8px 0;
            ">
                {props.get('text', '')}
            </h1>
            """

        # TEXT
        elif block_type == "text":

            html += f"""
            <p style="
                color:{props.get('color', '#000')};
                font-size:{props.get('fontSize', '14px')};
                text-align:{props.get('align', 'left')};
            ">
                {props.get('text', '')}
            </p>
            """

        # BUTTON
        elif block_type == "button":

            original_url = props.get("url", "#")

            tracked_url = original_url

            if log_id and original_url != "#":

                tracked_url = (
                    f"{API_BASE_URL}"
                    f"/api/track/click/{log_id}"
                    f"?url={quote(original_url)}"
                )

            html += f"""
            <div style="margin:20px 0;">
                <a href="{tracked_url}"
                   style="
                    background:{props.get('bgColor', '#4f46e5')};
                    color:{props.get('textColor', '#fff')};
                    padding:12px 20px;
                    text-decoration:none;
                    border-radius:6px;
                    display:inline-block;
                   ">
                    {props.get('label', 'Button')}
                </a>
            </div>
            """

        # DIVIDER
        elif block_type == "divider":

            html += f"""
            <hr style="
                border:none;
                border-top:1px solid {props.get('color', '#ddd')};
                margin:20px 0;
            "/>
            """

        # COLUMNS
        elif block_type == "columns":

            html += f"""
            <table width="100%" cellpadding="10">
                <tr>
                    <td width="50%">
                        {props.get('left', '')}
                    </td>
                    <td width="50%">
                        {props.get('right', '')}
                    </td>
                </tr>
            </table>
            """

        # IMAGE
        elif block_type == "image":
            image_info = next(
                (
                    item
                    for item in diagnostics["images"]
                    if item["block"] is block
                ),
                None,
            )
            image_url = image_info["url"] if image_info else ""

            if not image_url or (validate_images and image_info and not image_info["valid"]):
                html += """
                <div style="text-align:center;margin:20px 0;padding:28px;background:#f1f5f9;color:#64748b;font-family:Arial,sans-serif;border-radius:4px;">
                    Image not available
                </div>
                """
            else:
                html += f"""
            <div style="text-align:center;margin:20px 0;">
            <img
                src="{escape(image_url, quote=True)}"
                alt="{escape(props.get('alt', 'Image'), quote=True)}"
                style="
                    max-width:100%;
                    height:auto;
                    display:block;
                    margin:auto;
                    border-radius:4px;
                "
             />
            </div>
            """

        # FOOTER
        elif block_type == "footer":

            html += f"""
            <p style="
                color:{props.get('color', '#999')};
                font-size:{props.get('fontSize', '12px')};
                text-align:center;
                margin-top:30px;
            ">
                {props.get('text', '')}
            </p>
            """

    tracking_pixel = ""

    if log_id:

        tracking_pixel = f"""
        <img
            src="{API_BASE_URL}/api/track/open/{log_id}"
            width="1"
            height="1"
            style="display:none;"
        />
        """

    final_html = f"""
    <html>
        <body style="font-family:Arial;padding:20px;">
            {html}
            {tracking_pixel}
        </body>
    </html>
    """

    diagnostics["open_tracking_present"] = f"/api/track/open/{log_id}" in final_html
    diagnostics["click_tracking_present"] = "/api/track/click/" in final_html

    if include_diagnostics:
        return final_html, diagnostics

    return final_html

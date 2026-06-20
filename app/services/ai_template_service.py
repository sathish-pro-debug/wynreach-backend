import json
import base64

from openai import OpenAI

from app.core.config import settings


from app.services.r2_service import upload_image_bytes

client = OpenAI(api_key=settings.OPENAI_API_KEY)



SYSTEM_PROMPT = """
You are an expert email marketing designer.

Return ONLY valid JSON.

Generate an email template with these fields:

layout
name
font
logo
logoColor
bgColor
accentColor
buttonColor
buttonTextColor
buttonText
headerImg
tag
title
subtitle
body
footerText

headerImg must always be an empty string.

Also generate an "imagePrompt" field.

The imagePrompt should be extremely detailed because it will be used with an AI image generation model.

Describe:
- subject
- lighting
- camera angle
- background
- style
- colors
- composition

Do not generate an image URL.
"""

def generate_banner_image(image_prompt: str):

    result = client.images.generate(
        model="gpt-image-1",
        prompt=image_prompt,
        size="1536x1024",
    )

    return result.data[0].b64_json
async def generate_template(prompt: str):

    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
    )

    template = json.loads(response.output_text)
    image_prompt = template["imagePrompt"]

    image_base64 = generate_banner_image(image_prompt)

    image_bytes = base64.b64decode(image_base64)

    image_url = upload_image_bytes(image_bytes)

    template["headerImg"] = image_url

    return template
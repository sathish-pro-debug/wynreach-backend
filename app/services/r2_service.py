import boto3
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

r2 = boto3.client(
    "s3",
    endpoint_url=os.getenv("R2_ENDPOINT"),
    aws_access_key_id=os.getenv("R2_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("R2_SECRET_ACCESS_KEY"),
)
def upload_file(
    file,
    content_type
):

    ext = file.filename.split(".")[-1]

    key = f"uploads/{uuid.uuid4()}.{ext}"

    r2.upload_fileobj(
        file.file,
        os.getenv("R2_BUCKET_NAME"),
        key,
        ExtraArgs={
            "ContentType": content_type
        }
    )
    if not file.filename:
        raise Exception("Filename missing")

    if not content_type:
        raise Exception("Content type missing")

    return key
def get_public_url(key):

    return f"{os.getenv('R2_PUBLIC_URL')}/{key}"
import io


def upload_image_bytes(image_bytes: bytes):

    key = f"uploads/{uuid.uuid4()}.png"

    r2.upload_fileobj(
        io.BytesIO(image_bytes),
        os.getenv("R2_BUCKET_NAME"),
        key,
        ExtraArgs={
            "ContentType": "image/png"
        }
    )

    return get_public_url(key)
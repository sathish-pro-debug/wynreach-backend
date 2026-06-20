from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.r2_service import upload_file, get_public_url

router = APIRouter()


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...)
):

    try:

        if not file:
            raise HTTPException(
                status_code=400,
                detail="No file uploaded"
            )

        key = upload_file(
            file=file,
            content_type=file.content_type
        )

        url = get_public_url(key)

        return {
            "success": True,
            "key": key,
            "url": url
        }

    except HTTPException:
        raise

    except Exception as e:

        print("UPLOAD ERROR:", str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )
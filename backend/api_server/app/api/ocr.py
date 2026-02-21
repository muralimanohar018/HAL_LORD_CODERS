from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.services.ocr_service import extract_text_from_upload

router = APIRouter(tags=["ocr"])


class OCRExtractResponse(BaseModel):
    extracted_text: str
    source: str


@router.post("/ocr/extract", response_model=OCRExtractResponse)
async def ocr_extract(
    text: str | None = Form(default=None, description="Plain text input from frontend"),
    file: UploadFile | None = File(default=None, description="Upload image or PDF"),
) -> OCRExtractResponse:
    has_text = bool(text and text.strip())
    has_file = file is not None

    if not has_text and not has_file:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide either `text` or `file`",
        )

    if has_text and has_file:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide only one input source: `text` or `file`",
        )

    if has_text:
        return OCRExtractResponse(extracted_text=text.strip(), source="text")  # type: ignore[union-attr]

    extracted_text = await extract_text_from_upload(file)  # type: ignore[arg-type]
    return OCRExtractResponse(extracted_text=extracted_text, source="file")

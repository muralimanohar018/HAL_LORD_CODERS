from __future__ import annotations

from io import BytesIO
from pathlib import Path

import pytesseract
from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError
from pypdf import PdfReader
from pytesseract import TesseractNotFoundError

SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/bmp", "image/tiff"}
SUPPORTED_PDF_TYPES = {"application/pdf"}
SUPPORTED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}
WINDOWS_TESSERACT_PATH = Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe")

if WINDOWS_TESSERACT_PATH.exists():
    pytesseract.pytesseract.tesseract_cmd = str(WINDOWS_TESSERACT_PATH)


async def extract_text_from_upload(file: UploadFile) -> str:
    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Uploaded file is empty",
        )

    content_type = (file.content_type or "").lower()
    filename = (file.filename or "").lower().strip()
    is_pdf = content_type in SUPPORTED_PDF_TYPES or any(filename.endswith(ext) for ext in SUPPORTED_PDF_EXTENSIONS)
    is_image = content_type in SUPPORTED_IMAGE_TYPES or any(
        filename.endswith(ext) for ext in SUPPORTED_IMAGE_EXTENSIONS
    )

    if is_pdf:
        text = _extract_text_from_pdf(content)
    elif is_image:
        text = _extract_text_from_image(content)
    else:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported file type. Upload image or PDF.",
        )

    cleaned = " ".join(text.split())
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not extract readable text from the provided file",
        )

    return cleaned


def _extract_text_from_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(BytesIO(content))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid PDF file: {exc}",
        ) from exc

    parts: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text)

    return "\n".join(parts)


def _extract_text_from_image(content: bytes) -> str:
    try:
        image = Image.open(BytesIO(content))
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid image file",
        ) from exc

    try:
        return pytesseract.image_to_string(image)
    except TesseractNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Tesseract OCR engine is not installed on the server",
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OCR failed: {exc}",
        ) from exc

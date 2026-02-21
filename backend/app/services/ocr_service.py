"""OCR service module.

Responsibility:
- Text extraction from files only.
- No HTTP or database logic.
"""

from io import BytesIO


class OCRExtractionError(Exception):
    """Raised when OCR text extraction fails."""


def extract_text_from_image_bytes(image_bytes: bytes) -> str:
    """Extract raw text from image bytes using OCR."""
    if not image_bytes:
        raise OCRExtractionError("Image content is empty.")

    try:
        from PIL import Image
        import pytesseract
    except ImportError as exc:
        raise OCRExtractionError("OCR dependencies are not installed.") from exc

    try:
        image = Image.open(BytesIO(image_bytes))
        text = pytesseract.image_to_string(image).strip()
    except Exception as exc:
        raise OCRExtractionError("Unable to extract text from image.") from exc

    if not text:
        raise OCRExtractionError("No readable text found in image.")

    return text

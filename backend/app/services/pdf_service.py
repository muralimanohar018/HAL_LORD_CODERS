"""PDF service module.

Responsibility:
- PDF handling and validation only.
- No business orchestration, HTTP, or database logic.
"""

from io import BytesIO


class PDFExtractionError(Exception):
    """Raised when PDF extraction fails."""


def extract_text_from_pdf_bytes(pdf_bytes: bytes) -> str:
    """Extract and combine text from all pages in a PDF."""
    if not pdf_bytes:
        raise PDFExtractionError("PDF content is empty.")

    try:
        import pdfplumber
    except ImportError as exc:
        raise PDFExtractionError("PDF extraction dependency is not installed.") from exc

    try:
        with pdfplumber.open(BytesIO(pdf_bytes)) as pdf_document:
            page_texts = []
            for page in pdf_document.pages:
                text = (page.extract_text() or "").strip()
                if text:
                    page_texts.append(text)
    except Exception as exc:
        raise PDFExtractionError("Unable to read PDF content.") from exc

    combined_text = "\n".join(page_texts).strip()
    if not combined_text:
        raise PDFExtractionError("No readable text found in PDF.")

    return combined_text

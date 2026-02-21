"""File validation utilities.

Responsibility:
- Utility helpers for basic file checks only.
"""

from pathlib import Path
from typing import Any


def file_exists(file_path: str | Path) -> bool:
    """Return whether a file exists on disk."""
    return Path(file_path).is_file()


def validate_file_upload(filename: str | None, content_type: str | None, file_bytes: bytes) -> None:
    """Validate uploaded file metadata and content."""
    if not filename:
        raise ValueError("Uploaded file must include a filename.")
    if not content_type:
        raise ValueError("Uploaded file must include a content type.")
    if not file_bytes:
        raise ValueError("Uploaded file is empty.")

    allowed_types = {"application/pdf", "image/png", "image/jpeg", "image/jpg", "image/webp"}
    if content_type.lower() not in allowed_types:
        raise ValueError("Only PDF or image files are supported.")


def is_pdf_upload(filename: str | None, content_type: str | None) -> bool:
    """Return whether an upload should be treated as a PDF."""
    extension_is_pdf = bool(filename and filename.lower().endswith(".pdf"))
    content_type_is_pdf = (content_type or "").lower() == "application/pdf"
    return extension_is_pdf or content_type_is_pdf


def aggregate_risk_score(ml_response: dict[str, Any]) -> float:
    """Aggregate risk score from ML output."""
    probability = float(ml_response.get("fraud_probability", 0.0))
    normalized = min(max(probability, 0.0), 1.0)
    return round(normalized * 100.0, 2)

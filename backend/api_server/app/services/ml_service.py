from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings


async def analyze_text_with_ml(extracted_text: str) -> dict[str, Any]:
    settings = get_settings()

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="extracted_text is required",
        )

    try:
        async with httpx.AsyncClient(timeout=settings.ml_timeout_seconds) as client:
            response = await client.post(settings.ml_api_url, json={"text": extracted_text})
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="ML service timed out",
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="ML service unavailable",
        )

    if response.status_code >= 400:
        ml_detail: Any
        try:
            ml_detail = response.json()
        except ValueError:
            ml_detail = response.text or "ML service returned an error"
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"message": "ML service request failed", "ml_detail": ml_detail},
        )

    try:
        payload = response.json()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="ML service returned invalid JSON",
        )

    if not isinstance(payload, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="ML response must be a JSON object",
        )

    return payload

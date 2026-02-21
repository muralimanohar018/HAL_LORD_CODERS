from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import get_settings


def _normalize_ml_payload(payload: dict[str, Any]) -> dict[str, Any]:
    # New schema from hybrid service.
    if "ml_scam_probability" in payload:
        return payload

    # Legacy schema from older deployed service.
    if "scam_probability" in payload:
        probability = float(payload.get("scam_probability", 0.0))
        is_scam = bool(payload.get("is_scam", False))
        risk_level = str(payload.get("risk_level", "low")).upper()
        model_version = str(payload.get("model_version", "unknown"))
        threshold = float(payload.get("threshold", 0.7))

        return {
            "model_version": model_version,
            "ml_scam_probability": probability,
            "ml_is_scam": is_scam,
            "security": {
                "urls_found": [],
                "company_inferred": "",
                "company_verification_status": "not_provided",
                "behavior_warnings": [],
                "email_warnings": [],
                "domain_warnings": [],
                "whois_warnings": [],
                "security_risk_score": 0,
            },
            "urls_found": [],
            "company_inferred": None,
            "company_verification_status": "not_provided",
            "behavior_warnings": [],
            "email_warnings": [],
            "domain_warnings": [],
            "whois_warnings": [],
            "security_risk_score": 0,
            "final_risk_level": risk_level,
            "decision_thresholds": {
                "legacy": {"ml_probability_gte": threshold}
            },
        }

    return payload


async def analyze_text_with_ml(extracted_text: str) -> dict[str, Any]:
    settings = get_settings()

    if not extracted_text or not extracted_text.strip():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="extracted_text is required",
        )

    try:
        payload = {"text": str(extracted_text).strip()}
        async with httpx.AsyncClient(timeout=settings.ml_timeout_seconds) as client:
            response = await client.post(
                settings.ml_api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
            )
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

    return _normalize_ml_payload(payload)

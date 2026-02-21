"""ML connector module.

Responsibility:
- Send cleaned text to ML engine and receive response.
- No OCR, HTTP endpoint handling, or database logic.
"""

from typing import Any

from ..core.config import get_settings
from ..core.logging import get_logger


logger = get_logger(__name__)


class MLConnectorError(Exception):
    """Raised when the ML service call fails."""


def send_to_ml_engine(cleaned_text: str, timeout_seconds: float = 10.0) -> dict[str, Any]:
    """Send cleaned text to external ML endpoint and return model output."""
    if not cleaned_text:
        raise MLConnectorError("Cannot call ML service with empty text.")

    try:
        import requests
    except ImportError as exc:
        raise MLConnectorError("HTTP client dependency is not installed.") from exc

    settings = get_settings()
    if not settings.ml_endpoint:
        raise MLConnectorError("ML_ENDPOINT is not configured.")

    try:
        response = requests.post(
            settings.ml_endpoint,
            json={"text": cleaned_text},
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
    except requests.Timeout as exc:
        logger.error("ML service request timed out.")
        raise MLConnectorError("ML service timed out.") from exc
    except requests.RequestException as exc:
        logger.error("ML service request failed.")
        raise MLConnectorError("ML service is unreachable.") from exc
    except ValueError as exc:
        logger.error("ML service returned non-JSON response.")
        raise MLConnectorError("ML service returned invalid JSON.") from exc

    if not isinstance(payload, dict):
        raise MLConnectorError("ML service response format is invalid.")

    try:
        fraud_probability = float(payload["fraud_probability"])
        signals = [str(signal) for signal in payload.get("signals", [])]
        risk_label = str(payload["risk_label"])
    except (KeyError, TypeError, ValueError) as exc:
        raise MLConnectorError("ML service response missing required fields.") from exc

    return {
        "fraud_probability": fraud_probability,
        "signals": signals,
        "risk_label": risk_label,
    }

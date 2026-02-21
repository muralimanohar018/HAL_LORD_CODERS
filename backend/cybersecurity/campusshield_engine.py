"""
Combined CampusShield risk engine (ML + cybersecurity checks).
"""

from __future__ import annotations

import sys
from pathlib import Path

from .risk_aggregator import analyze_security

# Ensure project root is importable when called from backend runtime contexts.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ml.predict import predict_scam  # noqa: E402


ML_HIGH_THRESHOLD = 0.85
ML_MEDIUM_THRESHOLD = 0.65
SECURITY_HIGH_THRESHOLD = 60
SECURITY_MEDIUM_THRESHOLD = 30


def _final_risk_level(ml_prob: float, security_score: int) -> str:
    """
    Final decision thresholds.
    """
    if ml_prob >= ML_HIGH_THRESHOLD or security_score >= SECURITY_HIGH_THRESHOLD:
        return "HIGH"
    if ml_prob >= ML_MEDIUM_THRESHOLD or security_score >= SECURITY_MEDIUM_THRESHOLD:
        return "MEDIUM"
    return "LOW"


def analyze_message(text: str, company: str | None = None) -> dict:
    """
    Run both ML and cybersecurity modules and return a merged response.
    """
    ml_probability = predict_scam(text)
    security_result = analyze_security(text=text, company=company)
    security_score = int(security_result.get("security_risk_score", 0))
    final_level = _final_risk_level(ml_probability, security_score)

    return {
        "ml_scam_probability": round(float(ml_probability), 6),
        "ml_is_scam": ml_probability >= 0.50,
        "security": security_result,
        "final_risk_level": final_level,
        "decision_thresholds": {
            "high": {
                "ml_probability_gte": ML_HIGH_THRESHOLD,
                "security_risk_score_gte": SECURITY_HIGH_THRESHOLD,
            },
            "medium": {
                "ml_probability_gte": ML_MEDIUM_THRESHOLD,
                "security_risk_score_gte": SECURITY_MEDIUM_THRESHOLD,
            },
        },
    }


if __name__ == "__main__":
    sample = (
        "Apply now for internship. Pay 1500 registration fee and upload documents at "
        "https://tcs-career-portal.netlify.app contact tcs.hr.jobs@gmail.com"
    )
    print(analyze_message(sample, company="tcs"))

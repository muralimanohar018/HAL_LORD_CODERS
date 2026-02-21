"""
Combined CampusShield risk engine (ML + cybersecurity checks).
"""

from __future__ import annotations

import sys
from pathlib import Path

from .config import load_engine_config
from .risk_aggregator import analyze_security

# Ensure project root is importable when called from backend runtime contexts.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from ml.predict import predict_scam  # noqa: E402

ENGINE_CONFIG = load_engine_config()
MODEL_VERSION = ENGINE_CONFIG["model_version"]
THRESHOLDS = ENGINE_CONFIG["thresholds"]


def _final_risk_level(ml_prob: float, security_score: int) -> str:
    """
    Final decision thresholds.
    """
    if ml_prob >= THRESHOLDS["ml_high"] or security_score >= THRESHOLDS["security_high"]:
        return "HIGH"
    if ml_prob >= THRESHOLDS["ml_medium"] or security_score >= THRESHOLDS["security_medium"]:
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
        "model_version": MODEL_VERSION,
        "ml_scam_probability": round(float(ml_probability), 6),
        "ml_is_scam": ml_probability >= THRESHOLDS["ml_is_scam"],
        "security": security_result,
        "final_risk_level": final_level,
        "decision_thresholds": {
            "high": {
                "ml_probability_gte": THRESHOLDS["ml_high"],
                "security_risk_score_gte": THRESHOLDS["security_high"],
            },
            "medium": {
                "ml_probability_gte": THRESHOLDS["ml_medium"],
                "security_risk_score_gte": THRESHOLDS["security_medium"],
            },
        },
    }


if __name__ == "__main__":
    sample = (
        "Apply now for internship. Pay 1500 registration fee and upload documents at "
        "https://tcs-career-portal.netlify.app contact tcs.hr.jobs@gmail.com"
    )
    print(analyze_message(sample, company="tcs"))

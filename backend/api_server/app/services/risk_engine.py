from dataclasses import dataclass

from fastapi import HTTPException, status


@dataclass
class RiskResult:
    final_score: int
    risk_level: str
    ml_score: float
    reasons: list[str]


def evaluate_risk(ml_probability: float, reasons: list[str] | None = None) -> RiskResult:
    if ml_probability < 0.0 or ml_probability > 1.0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ml_probability must be between 0 and 1",
        )

    final_score = int(ml_probability * 100)

    if final_score <= 30:
        risk_level = "Safe"
    elif final_score <= 60:
        risk_level = "Suspicious"
    else:
        risk_level = "High Risk"

    return RiskResult(
        final_score=final_score,
        risk_level=risk_level,
        ml_score=ml_probability,
        reasons=reasons or [],
    )

from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.queries import create_scan
from app.models.scan_model import Scan


def create_scan_from_ml(
    db: Session,
    user_id: UUID,
    original_text: str | None,
    extracted_text: str | None,
    ml_response: dict[str, Any],
) -> Scan:
    ml_scam_probability = ml_response.get("ml_scam_probability")
    security_risk_score = ml_response.get("security_risk_score")
    final_risk_level = ml_response.get("final_risk_level")

    if ml_scam_probability is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="ML response missing `ml_scam_probability`",
        )
    if security_risk_score is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="ML response missing `security_risk_score`",
        )
    if final_risk_level is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="ML response missing `final_risk_level`",
        )

    try:
        ml_score = float(ml_scam_probability)
        risk_score = int(security_risk_score)
        risk_level = str(final_risk_level)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="ML response contains invalid risk values",
        )

    try:
        return create_scan(
            db=db,
            user_id=user_id,
            original_text=original_text,
            extracted_text=extracted_text,
            ml_score=ml_score,
            risk_score=risk_score,
            risk_level=risk_level,
        )
    except SQLAlchemyError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store scan",
        )

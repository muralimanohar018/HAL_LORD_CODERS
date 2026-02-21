from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.database.connection import get_db
from app.database.queries import create_scan
from app.services.risk_engine import evaluate_risk

router = APIRouter(tags=["analysis"])


class AnalyzeRequest(BaseModel):
    original_text: str | None = None
    extracted_text: str | None = None
    ml_probability: float = Field(..., ge=0.0, le=1.0)
    reasons: list[str] = Field(default_factory=list)


class AnalyzeResponse(BaseModel):
    final_score: int
    risk_level: str
    ml_score: float
    reasons: list[str]


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    payload: AnalyzeRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> AnalyzeResponse:
    risk_result = evaluate_risk(payload.ml_probability, payload.reasons)

    try:
        create_scan(
            db=db,
            user_id=user_id,
            original_text=payload.original_text,
            extracted_text=payload.extracted_text,
            ml_score=risk_result.ml_score,
            final_score=risk_result.final_score,
            risk_level=risk_result.risk_level,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
    )

    return AnalyzeResponse(
        final_score=risk_result.final_score,
        risk_level=risk_result.risk_level,
        ml_score=risk_result.ml_score,
        reasons=risk_result.reasons,
    )

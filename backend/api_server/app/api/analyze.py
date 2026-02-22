from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.database.connection import get_db
from app.services.ml_service import analyze_text_with_ml
from app.services.scan_service import create_scan_from_ml

router = APIRouter(tags=["analysis"])


class AnalyzeRequest(BaseModel):
    text: str


class AnalyzeResponse(BaseModel):
    processed_text: str
    source: str
    model_version: str | None = None
    ml_scam_probability: float
    ml_is_scam: bool
    security: dict
    urls_found: list[str]
    company_inferred: str | None = None
    company_verification_status: str | None = None
    behavior_warnings: list[str]
    email_warnings: list[str]
    domain_warnings: list[str]
    whois_warnings: list[str]
    security_risk_score: int
    final_risk_level: str
    decision_thresholds: dict

    model_config = ConfigDict(extra="allow")


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    payload: AnalyzeRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> AnalyzeResponse:
    cleaned_text = payload.text.strip()
    if not cleaned_text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="`text` is required",
        )

    ml_response = await analyze_text_with_ml(cleaned_text)

    create_scan_from_ml(
        db=db,
        user_id=user_id,
        original_text=cleaned_text,
        extracted_text=cleaned_text,
        ml_response=ml_response,
    )

    return AnalyzeResponse(processed_text=cleaned_text, source="text", **ml_response)

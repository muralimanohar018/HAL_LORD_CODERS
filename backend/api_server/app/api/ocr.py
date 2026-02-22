from uuid import UUID

from fastapi import APIRouter, Depends, File, UploadFile
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.database.connection import get_db
from app.services.ml_service import analyze_text_with_ml
from app.services.ocr_service import extract_text_from_upload
from app.services.scan_service import create_scan_from_ml

router = APIRouter(tags=["ocr"])


class OCRAnalyzeResponse(BaseModel):
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


@router.post("/ocr/extract", response_model=OCRAnalyzeResponse)
async def ocr_extract(
    file: UploadFile = File(..., description="Upload image or PDF"),
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> OCRAnalyzeResponse:
    extracted_text = await extract_text_from_upload(file)
    ml_response = await analyze_text_with_ml(extracted_text)

    create_scan_from_ml(
        db=db,
        user_id=user_id,
        original_text=None,
        extracted_text=extracted_text,
        ml_response=ml_response,
    )

    return OCRAnalyzeResponse(processed_text=extracted_text, source="file", **ml_response)

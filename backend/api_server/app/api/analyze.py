from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.database.connection import get_db
from app.services.ml_service import analyze_text_with_ml
from app.services.ocr_service import extract_text_from_upload
from app.services.scan_service import create_scan_from_ml

router = APIRouter(tags=["analysis"])


class AnalyzeRequest(BaseModel):
    original_text: str | None = None
    extracted_text: str


class AnalyzeResponse(BaseModel):
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


async def _run_analysis_pipeline(
    *,
    user_id: UUID,
    db: Session,
    original_text: str | None,
    extracted_text: str,
) -> AnalyzeResponse:
    ml_response = await analyze_text_with_ml(extracted_text)

    create_scan_from_ml(
        db=db,
        user_id=user_id,
        original_text=original_text,
        extracted_text=extracted_text,
        ml_response=ml_response,
    )

    return AnalyzeResponse(**ml_response)


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze(
    payload: AnalyzeRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> AnalyzeResponse:
    return await _run_analysis_pipeline(
        user_id=user_id,
        db=db,
        original_text=payload.original_text,
        extracted_text=payload.extracted_text,
    )


@router.post("/analyze-pipeline", response_model=AnalyzeResponse)
async def analyze_pipeline(
    text: str | None = Form(default=None, description="Plain text input from frontend"),
    file: UploadFile | None = File(default=None, description="Upload image or PDF"),
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> AnalyzeResponse:
    has_text = bool(text and text.strip())
    has_file = file is not None

    if not has_text and not has_file:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide either `text` or `file`",
        )
    if has_text and has_file:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide only one input source: `text` or `file`",
        )

    if has_text:
        extracted_text = text.strip()  # type: ignore[union-attr]
        saved_original = extracted_text
    else:
        extracted_text = await extract_text_from_upload(file)  # type: ignore[arg-type]
        saved_original = None

    return await _run_analysis_pipeline(
        user_id=user_id,
        db=db,
        original_text=saved_original,
        extracted_text=extracted_text,
    )

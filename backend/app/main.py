"""Application entrypoint.

Responsibilities:
- Initialize the FastAPI app
- Load environment variables
- Register API routes
- Configure middleware
- Expose health endpoint

No OCR, ML, or database logic belongs here.
"""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from .core.config import load_environment
from .core.logging import get_logger
from .db.supabase_client import SupabaseInsertError, save_scan_result
from .schemas.request_schema import AnalysisRequestSchema
from .schemas.response_schema import AnalysisResponseSchema
from .services.ml_connector import MLConnectorError, send_to_ml_engine
from .services.ocr_service import OCRExtractionError, extract_text_from_image_bytes
from .services.pdf_service import PDFExtractionError, extract_text_from_pdf_bytes
from .services.text_cleaner import clean_text
from .utils.file_validator import aggregate_risk_score, is_pdf_upload, validate_file_upload

load_environment()
logger = get_logger(__name__)

app = FastAPI(title="Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", summary="Health check")
def health() -> dict[str, str]:
    """Basic health endpoint."""
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalysisResponseSchema, summary="Analyze text or file input")
async def analyze(
    text: Annotated[str | None, Form()] = None,
    file: UploadFile | None = File(default=None),
) -> AnalysisResponseSchema:
    """Run the analysis pipeline and return a normalized response."""
    try:
        request_data = AnalysisRequestSchema(
            text=text,
            file_name=file.filename if file else None,
            file_content_type=file.content_type if file else None,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=400, detail="Invalid request payload.") from exc

    if not request_data.text and file is None:
        raise HTTPException(status_code=400, detail="Provide either text or a supported file.")

    try:
        input_text = request_data.text or ""
        if file is not None:
            file_bytes = await file.read()
            validate_file_upload(request_data.file_name, request_data.file_content_type, file_bytes)
            if is_pdf_upload(request_data.file_name, request_data.file_content_type):
                input_text = extract_text_from_pdf_bytes(file_bytes)
            else:
                input_text = extract_text_from_image_bytes(file_bytes)

        cleaned_text = clean_text(input_text)
        if not cleaned_text:
            raise HTTPException(status_code=400, detail="No readable text could be processed.")

        ml_response = send_to_ml_engine(cleaned_text)
        risk_score = aggregate_risk_score(ml_response)
        save_scan_result(cleaned_text, ml_response, risk_score)

        return AnalysisResponseSchema(
            risk_score=risk_score,
            risk_label=str(ml_response["risk_label"]),
            signals=[str(item) for item in ml_response.get("signals", [])],
            timestamp=datetime.now(timezone.utc),
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (OCRExtractionError, PDFExtractionError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except MLConnectorError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except SupabaseInsertError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Unexpected failure during analyze pipeline.")
        raise HTTPException(status_code=500, detail="Internal server error.") from exc

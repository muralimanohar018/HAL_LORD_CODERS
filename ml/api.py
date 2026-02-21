"""
FastAPI service for CampusShield scam prediction.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    # Works when loaded as package: ml.api
    from .predict import predict_scam
except ImportError:
    # Works when running as a direct script from project root.
    from predict import predict_scam


SCAM_THRESHOLD = 0.70

app = FastAPI(
    title="CampusShield ML API",
    version="1.0.0",
    description="TF-IDF + Logistic Regression inference API for recruitment scam detection.",
)


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Job/internship message text")


class PredictResponse(BaseModel):
    scam_probability: float
    is_scam: bool
    risk_level: str
    threshold: float


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    try:
        probability = predict_scam(payload.text)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}") from exc

    is_scam = probability >= SCAM_THRESHOLD
    risk_level = "high" if is_scam else "low"

    return PredictResponse(
        scam_probability=round(probability, 6),
        is_scam=is_scam,
        risk_level=risk_level,
        threshold=SCAM_THRESHOLD,
    )

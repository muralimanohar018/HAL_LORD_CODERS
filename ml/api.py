"""
FastAPI service for CampusShield scam prediction.
"""

from __future__ import annotations

import logging
import os
import time

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

try:
    # Works when loaded as package: ml.api
    from .predict import predict_scam, predict_scam_batch
except ImportError:
    # Works when running as a direct script from project root.
    from predict import predict_scam, predict_scam_batch


LOGGER = logging.getLogger("campusshield.api")
MODEL_VERSION = os.getenv("MODEL_VERSION", "tfidf-logreg-v1")
SCAM_THRESHOLD = float(os.getenv("SCAM_THRESHOLD", "0.70"))

app = FastAPI(
    title="CampusShield ML API",
    version="1.1.0",
    description="TF-IDF + Logistic Regression inference API for recruitment scam detection.",
)


class PredictRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Job/internship message text")


class PredictResponse(BaseModel):
    scam_probability: float
    is_scam: bool
    risk_level: str
    threshold: float
    model_version: str
    latency_ms: float


class BatchPredictRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1, description="List of job/internship messages")


class BatchPredictItem(BaseModel):
    text: str
    scam_probability: float
    is_scam: bool
    risk_level: str


class BatchPredictResponse(BaseModel):
    predictions: list[BatchPredictItem]
    threshold: float
    model_version: str
    latency_ms: float


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "model_version": MODEL_VERSION}


@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest) -> PredictResponse:
    start_time = time.perf_counter()
    try:
        probability = predict_scam(payload.text)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Inference failed: {exc}") from exc

    latency_ms = (time.perf_counter() - start_time) * 1000
    is_scam = probability >= SCAM_THRESHOLD
    risk_level = "high" if is_scam else "low"

    LOGGER.info(
        "predict completed threshold=%.3f probability=%.6f is_scam=%s latency_ms=%.2f",
        SCAM_THRESHOLD,
        probability,
        is_scam,
        latency_ms,
    )

    return PredictResponse(
        scam_probability=round(probability, 6),
        is_scam=is_scam,
        risk_level=risk_level,
        threshold=SCAM_THRESHOLD,
        model_version=MODEL_VERSION,
        latency_ms=round(latency_ms, 3),
    )


@app.post("/batch-predict", response_model=BatchPredictResponse)
def batch_predict(payload: BatchPredictRequest) -> BatchPredictResponse:
    start_time = time.perf_counter()

    if not payload.texts:
        raise HTTPException(status_code=400, detail="`texts` must contain at least one message.")

    try:
        probabilities = predict_scam_batch(payload.texts)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Batch inference failed: {exc}") from exc

    predictions: list[BatchPredictItem] = []
    for text, probability in zip(payload.texts, probabilities):
        is_scam = probability >= SCAM_THRESHOLD
        risk_level = "high" if is_scam else "low"
        predictions.append(
            BatchPredictItem(
                text=text,
                scam_probability=round(probability, 6),
                is_scam=is_scam,
                risk_level=risk_level,
            )
        )

    latency_ms = (time.perf_counter() - start_time) * 1000
    LOGGER.info(
        "batch_predict completed items=%d threshold=%.3f latency_ms=%.2f",
        len(payload.texts),
        SCAM_THRESHOLD,
        latency_ms,
    )

    return BatchPredictResponse(
        predictions=predictions,
        threshold=SCAM_THRESHOLD,
        model_version=MODEL_VERSION,
        latency_ms=round(latency_ms, 3),
    )

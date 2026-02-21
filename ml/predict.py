"""
Inference utility for CampusShield scam detection model.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib

try:
    # Works when imported as package: ml.predict
    from .preprocess import clean_text
except ImportError:
    # Works when running as a direct script from project root.
    from preprocess import clean_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = PROJECT_ROOT / "model.pkl"
VECTORIZER_PATH = PROJECT_ROOT / "vectorizer.pkl"


def _load_artifacts() -> tuple[Any, Any]:
    """
    Load model and vectorizer with clear errors if files are missing.
    """
    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing model file: {MODEL_PATH}. Run `python ml/train_model.py` first."
        )
    if not VECTORIZER_PATH.exists():
        raise FileNotFoundError(
            f"Missing vectorizer file: {VECTORIZER_PATH}. Run `python ml/train_model.py` first."
        )

    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
    return model, vectorizer


def predict_scam(text: str) -> float:
    """
    Return scam probability for class 1.
    """
    model, vectorizer = _load_artifacts()
    cleaned = clean_text(text)
    features = vectorizer.transform([cleaned])
    probability = model.predict_proba(features)[0][1]
    return float(probability)


if __name__ == "__main__":
    sample_text = "Pay ₹1500 registration fee to confirm internship"
    score = predict_scam(sample_text)
    print(f"Scam probability: {score:.4f}")

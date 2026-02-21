"""
Evaluation script for CampusShield scam detection model.
"""

from __future__ import annotations

from pathlib import Path

import joblib
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split

try:
    # Works when imported as package: ml.evaluate
    from .train_model import (
        DATASET_FILENAME,
        RANDOM_STATE,
        TARGET_COLUMN,
        load_and_prepare_data,
    )
except ImportError:
    # Works when running as a direct script from project root.
    from train_model import (
        DATASET_FILENAME,
        RANDOM_STATE,
        TARGET_COLUMN,
        load_and_prepare_data,
    )


def evaluate_model() -> None:
    """
    Evaluate saved model/vectorizer on deterministic test split.
    """
    project_root = Path(__file__).resolve().parents[1]
    dataset_path = project_root / DATASET_FILENAME
    model_path = project_root / "model.pkl"
    vectorizer_path = project_root / "vectorizer.pkl"

    if not model_path.exists():
        raise FileNotFoundError(
            f"Missing model file: {model_path}. Run `python ml/train_model.py` first."
        )
    if not vectorizer_path.exists():
        raise FileNotFoundError(
            f"Missing vectorizer file: {vectorizer_path}. Run `python ml/train_model.py` first."
        )

    texts, labels = load_and_prepare_data(dataset_path)
    _, X_test, _, y_test = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

    X_test_vec = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_vec)

    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, digits=4)

    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(report)


if __name__ == "__main__":
    evaluate_model()

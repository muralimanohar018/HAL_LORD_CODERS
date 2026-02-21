"""
Evaluation script for CampusShield scam detection model.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

try:
    # Works when imported as package: ml.evaluate
    from .train_model import (
        DATASET_FILENAME,
        RANDOM_STATE,
        load_and_prepare_data,
    )
except ImportError:
    # Works when running as a direct script from project root.
    from train_model import (
        DATASET_FILENAME,
        RANDOM_STATE,
        load_and_prepare_data,
    )


DEFAULT_REPORT_PATH = "ml/final_model_report.json"


def evaluate_model(dataset_path: Path, model_path: Path, vectorizer_path: Path) -> dict[str, Any]:
    """
    Evaluate saved model/vectorizer on deterministic test split.
    """
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
    report_text = classification_report(y_test, y_pred, digits=4)
    report_dict = classification_report(y_test, y_pred, digits=4, output_dict=True)
    matrix = confusion_matrix(y_test, y_pred).tolist()

    print(f"Accuracy: {accuracy:.4f}")
    print("Classification Report:")
    print(report_text)

    return {
        "dataset_path": str(dataset_path.resolve()),
        "model_path": str(model_path.resolve()),
        "vectorizer_path": str(vectorizer_path.resolve()),
        "samples_total": int(len(texts)),
        "samples_test": int(len(X_test)),
        "accuracy": round(float(accuracy), 6),
        "classification_report": report_dict,
        "confusion_matrix": matrix,
        "split": {"test_size": 0.2, "random_state": RANDOM_STATE, "stratified": True},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate CampusShield model on `text,label` dataset schema."
    )
    parser.add_argument("--dataset", type=str, default=DATASET_FILENAME)
    parser.add_argument("--model", type=str, default="model.pkl")
    parser.add_argument("--vectorizer", type=str, default="vectorizer.pkl")
    parser.add_argument("--report", type=str, default=DEFAULT_REPORT_PATH)
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]

    dataset_path = (project_root / args.dataset).resolve()
    model_path = (project_root / args.model).resolve()
    vectorizer_path = (project_root / args.vectorizer).resolve()
    report_path = (project_root / args.report).resolve()

    result = evaluate_model(
        dataset_path=dataset_path,
        model_path=model_path,
        vectorizer_path=vectorizer_path,
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Report saved to: {report_path}")

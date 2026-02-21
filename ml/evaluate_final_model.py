"""
Deterministic evaluation script for CampusShield final model artifacts.

Usage:
python ml/evaluate_final_model.py
python ml/evaluate_final_model.py --dataset combined_all_datasets_training.csv
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

try:
    from .preprocess import clean_text
except ImportError:
    from preprocess import clean_text


DEFAULT_DATASET = "combined_all_datasets_training.csv"
DEFAULT_REPORT = "ml/final_model_report.json"


def _load_dataset(path: Path) -> tuple[pd.Series, pd.Series]:
    """
    Load dataset with schema-aware text extraction.
    Supports:
    - text,label
    - message,label
    - fake job postings schema with fraudulent + text columns
    """
    df = pd.read_csv(path)

    if {"text", "label"}.issubset(df.columns):
        text = df["text"].fillna("").astype(str)
        label = df["label"].astype(int)
    elif {"message", "label"}.issubset(df.columns):
        text = df["message"].fillna("").astype(str)
        label = df["label"].astype(int)
    elif {"fraudulent", "title", "company_profile", "description", "requirements", "benefits"}.issubset(
        df.columns
    ):
        text = (
            df[["title", "company_profile", "description", "requirements", "benefits"]]
            .fillna("")
            .agg(" ".join, axis=1)
            .astype(str)
        )
        label = df["fraudulent"].astype(int)
    else:
        raise ValueError(f"Unsupported dataset schema: {list(df.columns)}")

    cleaned = text.apply(clean_text)
    valid = cleaned.str.len() >= 20
    cleaned = cleaned[valid]
    label = label[valid]

    # Deterministic ordering before split.
    frame = pd.DataFrame({"text": cleaned, "label": label})
    frame = frame.sort_values(["label", "text"], kind="mergesort").reset_index(drop=True)
    return frame["text"], frame["label"]


def evaluate(dataset_path: Path, model_path: Path, vectorizer_path: Path) -> dict[str, Any]:
    X, y = _load_dataset(dataset_path)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    model = joblib.load(model_path)
    vectorizer = joblib.load(vectorizer_path)

    X_test_vec = vectorizer.transform(X_test)
    y_pred = model.predict(X_test_vec)

    acc = float(accuracy_score(y_test, y_pred))
    report_dict = classification_report(y_test, y_pred, digits=4, output_dict=True)
    matrix = confusion_matrix(y_test, y_pred).tolist()

    return {
        "dataset_path": str(dataset_path),
        "model_path": str(model_path),
        "vectorizer_path": str(vectorizer_path),
        "samples_total": int(len(X)),
        "samples_test": int(len(X_test)),
        "accuracy": round(acc, 6),
        "classification_report": report_dict,
        "confusion_matrix": matrix,
        "split": {"test_size": 0.2, "random_state": 42, "stratified": True},
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deterministic final-model evaluator.")
    parser.add_argument("--dataset", type=str, default=DEFAULT_DATASET)
    parser.add_argument("--model", type=str, default="model.pkl")
    parser.add_argument("--vectorizer", type=str, default="vectorizer.pkl")
    parser.add_argument("--report", type=str, default=DEFAULT_REPORT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]

    dataset_path = (project_root / args.dataset).resolve()
    model_path = (project_root / args.model).resolve()
    vectorizer_path = (project_root / args.vectorizer).resolve()
    report_path = (project_root / args.report).resolve()

    result = evaluate(dataset_path=dataset_path, model_path=model_path, vectorizer_path=vectorizer_path)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"Accuracy: {result['accuracy']:.6f}")
    print(f"Total samples: {result['samples_total']} | Test samples: {result['samples_test']}")
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()


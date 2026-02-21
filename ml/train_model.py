"""
Training script for CampusShield recruitment scam detection model.
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

try:
    # Works when imported as package: ml.train_model
    from .preprocess import clean_text
except ImportError:
    # Works when running as a direct script from project root.
    from preprocess import clean_text


RANDOM_STATE = 42
MAX_FEATURES = 5000
TEXT_COLUMN = "text"
TARGET_COLUMN = "label"
DATASET_FILENAME = "combined_all_datasets_training.csv"


def load_and_prepare_data(dataset_path: Path) -> tuple[pd.Series, pd.Series]:
    """
    Load CSV data with `text,label` schema and clean text.
    """
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}. Place '{DATASET_FILENAME}' in the project root."
        )

    df = pd.read_csv(dataset_path)

    missing_columns = [col for col in [TEXT_COLUMN, TARGET_COLUMN] if col not in df.columns]
    if missing_columns:
        raise ValueError(
            f"Missing required columns in dataset: {missing_columns}. "
            "Expected schema: `text,label`."
        )

    texts = df[TEXT_COLUMN].fillna("").astype(str).apply(clean_text)
    labels = pd.to_numeric(df[TARGET_COLUMN], errors="coerce")
    if labels.isna().any():
        raise ValueError("Column `label` contains non-numeric values.")
    labels = labels.astype(int)

    invalid_labels = sorted(set(labels.unique()) - {0, 1})
    if invalid_labels:
        raise ValueError(f"Column `label` must contain only 0/1, found: {invalid_labels}")

    valid_rows = texts.str.len() > 0
    texts = texts[valid_rows].reset_index(drop=True)
    labels = labels[valid_rows].reset_index(drop=True)

    if texts.empty:
        raise ValueError("No usable rows found after cleaning. Check dataset content.")

    return texts, labels


def train_model() -> None:
    """
    Train TF-IDF + Logistic Regression model and save artifacts.
    """
    project_root = Path(__file__).resolve().parents[1]
    dataset_path = project_root / DATASET_FILENAME
    model_path = project_root / "model.pkl"
    vectorizer_path = project_root / "vectorizer.pkl"

    texts, labels = load_and_prepare_data(dataset_path)

    X_train, X_test, y_train, _ = train_test_split(
        texts,
        labels,
        test_size=0.2,
        random_state=RANDOM_STATE,
        stratify=labels,
    )

    vectorizer = TfidfVectorizer(max_features=MAX_FEATURES)
    X_train_vec = vectorizer.fit_transform(X_train)

    model = LogisticRegression(max_iter=1000, random_state=RANDOM_STATE)
    model.fit(X_train_vec, y_train)

    # Persist artifacts for inference/evaluation scripts.
    joblib.dump(model, model_path)
    joblib.dump(vectorizer, vectorizer_path)

    print("Training complete.")
    print(f"Model saved to: {model_path}")
    print(f"Vectorizer saved to: {vectorizer_path}")
    print(f"Train samples: {len(X_train)} | Test samples: {len(X_test)}")


if __name__ == "__main__":
    train_model()

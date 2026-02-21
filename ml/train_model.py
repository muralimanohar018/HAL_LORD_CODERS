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
TEXT_COLUMNS = ["title", "company_profile", "description", "requirements", "benefits"]
TARGET_COLUMN = "fraudulent"
DATASET_FILENAME = "fake_job_postings.csv"


def load_and_prepare_data(dataset_path: Path) -> tuple[pd.Series, pd.Series]:
    """
    Load CSV data, combine relevant text columns, and clean the combined text.
    """
    if not dataset_path.exists():
        raise FileNotFoundError(
            f"Dataset not found: {dataset_path}. Place '{DATASET_FILENAME}' in the project root."
        )

    df = pd.read_csv(dataset_path)

    missing_columns = [col for col in TEXT_COLUMNS + [TARGET_COLUMN] if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns in dataset: {missing_columns}")

    combined_text = df[TEXT_COLUMNS].fillna("").agg(" ".join, axis=1)
    cleaned_text = combined_text.apply(clean_text)
    labels = df[TARGET_COLUMN].astype(int)

    return cleaned_text, labels


def train_model() -> None:
    """
    Train TF-IDF + Logistic Regression model and save artifacts.
    """
    project_root = Path(__file__).resolve().parents[1]
    dataset_path = project_root / DATASET_FILENAME
    model_path = project_root / "model.pkl"
    vectorizer_path = project_root / "vectorizer.pkl"

    texts, labels = load_and_prepare_data(dataset_path)

    X_train, X_test, y_train, y_test = train_test_split(
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

"""
Text preprocessing utilities for CampusShield scam detection.
"""

from __future__ import annotations

import re
import string
from functools import lru_cache

import nltk
from nltk.corpus import stopwords


@lru_cache(maxsize=1)
def _english_stopwords() -> set[str]:
    """
    Return cached English stopwords, downloading the corpus if needed.
    """
    try:
        return set(stopwords.words("english"))
    except LookupError:
        nltk.download("stopwords", quiet=True)
        return set(stopwords.words("english"))


def clean_text(text: str) -> str:
    """
    Clean input text by:
    - lowercasing
    - removing URLs
    - removing numbers
    - removing punctuation
    - removing extra spaces
    - removing English stopwords
    """
    if text is None:
        text = ""
    elif not isinstance(text, str):
        text = str(text)

    text = text.lower()
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()

    stop_words = _english_stopwords()
    tokens = [token for token in text.split() if token not in stop_words]

    return " ".join(tokens)

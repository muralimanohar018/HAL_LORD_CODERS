"""
Configuration loader for CampusShield cybersecurity engine.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_MODEL_VERSION = "campusshield-hybrid-v2.0"
DEFAULT_THRESHOLDS = {
    "ml_high": 0.85,
    "ml_medium": 0.65,
    "ml_is_scam": 0.50,
    "security_high": 60,
    "security_medium": 30,
}


def _safe_float(value: Any, fallback: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return fallback


def _safe_int(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def load_engine_config() -> dict[str, Any]:
    """
    Load thresholds and model metadata from engine_config.json.
    Falls back to defaults when file is missing/invalid.
    """
    config_path = Path(__file__).with_name("engine_config.json")
    if not config_path.exists():
        return {
            "model_version": DEFAULT_MODEL_VERSION,
            "thresholds": DEFAULT_THRESHOLDS.copy(),
        }

    try:
        raw = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {
            "model_version": DEFAULT_MODEL_VERSION,
            "thresholds": DEFAULT_THRESHOLDS.copy(),
        }

    raw_thresholds = raw.get("thresholds", {})
    thresholds = {
        "ml_high": _safe_float(raw_thresholds.get("ml_high"), DEFAULT_THRESHOLDS["ml_high"]),
        "ml_medium": _safe_float(raw_thresholds.get("ml_medium"), DEFAULT_THRESHOLDS["ml_medium"]),
        "ml_is_scam": _safe_float(
            raw_thresholds.get("ml_is_scam"), DEFAULT_THRESHOLDS["ml_is_scam"]
        ),
        "security_high": _safe_int(
            raw_thresholds.get("security_high"), DEFAULT_THRESHOLDS["security_high"]
        ),
        "security_medium": _safe_int(
            raw_thresholds.get("security_medium"), DEFAULT_THRESHOLDS["security_medium"]
        ),
    }

    # Ensure ordering invariants to avoid invalid configuration states.
    if thresholds["ml_medium"] > thresholds["ml_high"]:
        thresholds["ml_medium"] = thresholds["ml_high"]
    if thresholds["security_medium"] > thresholds["security_high"]:
        thresholds["security_medium"] = thresholds["security_high"]

    model_version = str(raw.get("model_version", DEFAULT_MODEL_VERSION)).strip() or DEFAULT_MODEL_VERSION
    return {"model_version": model_version, "thresholds": thresholds}


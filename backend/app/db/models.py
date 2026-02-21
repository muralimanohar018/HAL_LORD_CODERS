"""Database models module.

Responsibility:
- Define storage structures only.
- No business logic.
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class AnalysisRecord:
    """Storage representation for an analysis record."""

    record_id: str
    payload: dict[str, Any] = field(default_factory=dict)

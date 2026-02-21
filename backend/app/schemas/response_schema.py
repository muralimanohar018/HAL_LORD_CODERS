"""Response schemas.

Responsibility:
- Define API output structures only.
"""

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class AnalysisResponseSchema(BaseModel):
    """Output response structure for analysis results."""

    risk_score: float = 0.0
    risk_label: str = ""
    signals: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

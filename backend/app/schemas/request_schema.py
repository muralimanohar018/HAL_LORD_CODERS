"""Request schemas.

Responsibility:
- Define API input structures only.
"""

from typing import Any

from pydantic import BaseModel, Field


class MetadataSchema(BaseModel):
    """Optional metadata for a request."""

    source: str | None = None
    tags: list[str] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)


class AnalysisRequestSchema(BaseModel):
    """Input request structure for analysis operations."""

    text: str | None = None
    file_name: str | None = None
    file_content_type: str | None = None
    metadata: MetadataSchema = Field(default_factory=MetadataSchema)

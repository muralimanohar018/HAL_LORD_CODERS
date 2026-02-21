from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.auth import get_current_user_id
from app.database.connection import get_db
from app.database.queries import list_scans_for_user

router = APIRouter(tags=["history"])


class ScanHistoryItem(BaseModel):
    id: UUID
    user_id: UUID
    original_text: str | None
    extracted_text: str | None
    ml_score: float | None
    final_score: int | None
    risk_level: str | None
    created_at: datetime | None


@router.get("/history", response_model=list[ScanHistoryItem])
async def history(
    limit: int = Query(default=100, ge=1, le=500),
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
) -> list[ScanHistoryItem]:
    try:
        scans = list_scans_for_user(db=db, user_id=user_id, limit=limit)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
    )

    return [
        ScanHistoryItem(
            id=scan.id,
            user_id=scan.user_id,
            original_text=scan.original_text,
            extracted_text=scan.extracted_text,
            ml_score=scan.ml_score,
            final_score=scan.final_score,
            risk_level=scan.risk_level,
            created_at=scan.created_at,
        )
        for scan in scans
    ]

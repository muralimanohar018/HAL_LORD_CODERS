from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.models.scan_model import Scan


def create_scan(
    db: Session,
    user_id: UUID,
    original_text: str | None,
    extracted_text: str | None,
    ml_score: float,
    risk_score: int,
    risk_level: str,
) -> Scan:
    scan = Scan(
        user_id=user_id,
        original_text=original_text,
        extracted_text=extracted_text,
        ml_score=ml_score,
        risk_score=risk_score,
        risk_level=risk_level,
    )
    try:
        db.add(scan)
        db.commit()
        db.refresh(scan)
        return scan
    except SQLAlchemyError:
        db.rollback()
        raise


def list_scans_for_user(db: Session, user_id: UUID, limit: int = 100) -> Sequence[Scan]:
    return (
        db.query(Scan)
        .filter(Scan.user_id == user_id)
        .order_by(desc(Scan.checked_at))
        .limit(limit)
        .all()
    )

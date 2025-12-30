from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, func
import logging
from app.models import MedicalField, Doctor

logger = logging.getLogger(__name__)

def _row_to_dict(row) -> Dict[str, Any]:
    """Convert SQLAlchemy Row to dictionary"""
    try:
        return dict(row._mapping)
    except Exception:
        return dict(row)


class MedicalFieldRepository:
    """Data access layer for medical fields using SQLAlchemy"""

    @staticmethod
    def get_all_active_fields(db: Session) -> List[Dict[str, Any]]:
        """Fetch all active medical fields"""
        stmt = (
            select(
                MedicalField.id,
                MedicalField.medical_field_name,
                MedicalField.description,
                MedicalField.icon,
                MedicalField.is_active,
                MedicalField.created_at,
            )
            .where(MedicalField.is_active == True)
            .order_by(MedicalField.medical_field_name.asc())
        )

        rows = db.execute(stmt).all()
        return [_row_to_dict(row) for row in rows]

    @staticmethod
    def get_field_by_id(db: Session, field_id: int) -> Optional[Dict[str, Any]]:
        """Fetch medical field by ID"""
        stmt = select(
            MedicalField.id,
            MedicalField.medical_field_name,
            MedicalField.description,
            MedicalField.icon,
            MedicalField.is_active,
            MedicalField.created_at,
        ).where(MedicalField.id == field_id)

        row = db.execute(stmt).first()
        return _row_to_dict(row) if row else None

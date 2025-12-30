from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, update, func
import logging
from app.models import Patient

logger = logging.getLogger(__name__)


def _row_to_dict(row) -> Dict[str, Any]:
    """Convert SQLAlchemy Row to dictionary"""
    try:
        return dict(row._mapping)
    except Exception:
        return dict(row)


def _patient_to_dict(patient: Patient) -> Dict[str, Any]:
    """Convert Patient object to dictionary"""
    return {
        "id": patient.id,
        "phone_number": patient.phone_number,
        "full_name": patient.full_name,
        "email": patient.email,
        "date_of_birth": patient.date_of_birth,
        "gender": patient.gender,
        "time_zone": patient.time_zone,
        "emergency_contact": patient.emergency_contact,
        "address": patient.address,
        "created_at": patient.created_at,
        "is_active": patient.is_active,
    }


class PatientRepository:
    """Data access layer for patients using SQLAlchemy"""

    @staticmethod
    def get_patient_by_id(db: Session, patient_id: int) -> Optional[Dict[str, Any]]:
        """Fetch patient by ID"""
        stmt = select(
            Patient.id,
            Patient.phone_number,
            Patient.full_name,
            Patient.email,
            Patient.date_of_birth,
            Patient.gender,
            Patient.time_zone,
            Patient.emergency_contact,
            Patient.address,
            Patient.created_at,
            Patient.is_active,
        ).where(Patient.id == patient_id)

        row = db.execute(stmt).first()
        return _row_to_dict(row) if row else None

    @staticmethod
    def get_patient_by_phone(db: Session, phone_number: str) -> Optional[Dict[str, Any]]:
        """Fetch patient by phone number"""
        stmt = select(
            Patient.id,
            Patient.phone_number,
            Patient.full_name,
            Patient.email,
            Patient.date_of_birth,
            Patient.gender,
            Patient.time_zone,
            Patient.emergency_contact,
            Patient.address,
            Patient.created_at,
            Patient.is_active,
        ).where(Patient.phone_number == phone_number)

        row = db.execute(stmt).first()
        return _row_to_dict(row) if row else None

    @staticmethod
    def check_patient_exists(db: Session, phone_number: str) -> Optional[Dict[str, Any]]:
        """Check if patient exists by phone number"""
        stmt = select(Patient.id).where(Patient.phone_number == phone_number)

        row = db.execute(stmt).first()
        return _row_to_dict(row) if row else None

    @staticmethod
    def create_patient(
        db: Session, phone_number: str, time_zone: str = "Asia/Jerusalem"
    ) -> Dict[str, Any]:
        """Create a new patient"""
        patient = Patient(
            phone_number=phone_number,
            time_zone=time_zone,
            is_active=True,
        )

        db.add(patient)
        db.flush()  # Flush to get the ID and trigger defaults
        db.refresh(patient)  # Refresh to get server defaults

        return _patient_to_dict(patient)

    @staticmethod
    def update_patient(
        db: Session, patient_id: int, updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update patient with dynamic fields"""
        if not updates:
            raise ValueError("No updates provided")

        # Add updated_at to updates
        updates["updated_at"] = func.now()

        stmt = (
            update(Patient)
            .where(Patient.id == patient_id)
            .values(**updates)
            .returning(
                Patient.id,
                Patient.phone_number,
                Patient.full_name,
                Patient.email,
                Patient.date_of_birth,
                Patient.gender,
                Patient.time_zone,
                Patient.emergency_contact,
                Patient.address,
                Patient.created_at,
                Patient.is_active,
            )
        )

        row = db.execute(stmt).first()
        return _row_to_dict(row) if row else None
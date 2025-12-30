from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from sqlalchemy.orm import Session, aliased
from sqlalchemy import select, func
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.medical_field import MedicalField

logger = logging.getLogger(__name__)

def _appointment_row_to_dict(
    appointment, doctor=None, medical_field=None
) -> Dict[str, Any]:
    return {
        "id": appointment.id,
        "patient_id": appointment.patient_id,
        "doctor_id": appointment.doctor_id,
        "medical_field_id": appointment.medical_field_id,
        "appointment_time": appointment.appointment_time,
        "duration_minutes": appointment.duration_minutes,
        "status": appointment.status,
        "reason_for_visit": appointment.reason_for_visit,
        "notes": getattr(appointment, "notes", None),
        "created_at": getattr(appointment, "created_at", None),
        "updated_at": getattr(appointment, "updated_at", None),
        "doctor_name": getattr(doctor, "name", None) if doctor else None,
        "doctor_specialization": getattr(doctor, "specialization", None) if doctor else None,
        "consultation_fee": getattr(doctor, "consultation_fee", None) if doctor else None,
        "medical_field_name": getattr(medical_field, "medical_field_name", None)
        if medical_field
        else None,
    }
class AppointmentRepository:
    """Data access layer for appointments (SQLAlchemy ORM)."""

    @staticmethod
    def get_appointments(
        db: Session,
        patient_id: int,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        DoctorA = aliased(Doctor)
        MFA = aliased(MedicalField)

        stmt = (
            select(Appointment, DoctorA, MFA)
            .join(DoctorA, Appointment.doctor_id == DoctorA.id)
            .join(MFA, Appointment.medical_field_id == MFA.id)
            .where(Appointment.patient_id == patient_id)
            .order_by(Appointment.appointment_time.desc())
            .limit(limit)
            .offset(offset)
        )

        if status_filter:
            stmt = stmt.where(Appointment.status == status_filter)

        rows = db.execute(stmt).all()
        return [_appointment_row_to_dict(a, d, mf) for (a, d, mf) in rows]

    @staticmethod
    def get_upcoming_appointments(
        db: Session, patient_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        DoctorA = aliased(Doctor)
        MFA = aliased(MedicalField)

        stmt = (
            select(Appointment, DoctorA, MFA)
            .join(DoctorA, Appointment.doctor_id == DoctorA.id)
            .join(MFA, Appointment.medical_field_id == MFA.id)
            .where(Appointment.patient_id == patient_id)
            .where(Appointment.appointment_time > datetime.utcnow())
            .where(Appointment.status.not_in(["cancelled", "no_show"]))
            .order_by(Appointment.appointment_time.asc())
            .limit(limit)
        )

        rows = db.execute(stmt).all()
        return [_appointment_row_to_dict(a, d, mf) for (a, d, mf) in rows]

    @staticmethod
    def get_past_appointments(
        db: Session, patient_id: int, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        DoctorA = aliased(Doctor)
        MFA = aliased(MedicalField)

        stmt = (
            select(Appointment, DoctorA, MFA)
            .join(DoctorA, Appointment.doctor_id == DoctorA.id)
            .join(MFA, Appointment.medical_field_id == MFA.id)
            .where(Appointment.patient_id == patient_id)
            .where(
                (Appointment.appointment_time < datetime.utcnow())
                | (Appointment.status.in_(["cancelled", "completed", "no_show"]))
            )
            .order_by(Appointment.appointment_time.desc())
            .limit(limit)
            .offset(offset)
        )

        rows = db.execute(stmt).all()
        return [_appointment_row_to_dict(a, d, mf) for (a, d, mf) in rows]

    @staticmethod
    def get_appointment_by_id(
        db: Session, appointment_id: int, patient_id: int
    ) -> Optional[Dict[str, Any]]:
        DoctorA = aliased(Doctor)
        MFA = aliased(MedicalField)

        stmt = (
            select(Appointment, DoctorA, MFA)
            .join(DoctorA, Appointment.doctor_id == DoctorA.id)
            .join(MFA, Appointment.medical_field_id == MFA.id)
            .where(Appointment.id == appointment_id)
            .where(Appointment.patient_id == patient_id)
        )

        row = db.execute(stmt).first()
        if not row:
            return None
        a, d, mf = row
        return _appointment_row_to_dict(a, d, mf)

    @staticmethod
    def get_doctor_info(db: Session, doctor_id: int) -> Optional[Dict[str, Any]]:
        doc = db.get(Doctor, doctor_id)
        if not doc:
            return None
        return {
            "id": doc.id,
            "is_available": getattr(doc, "is_available", None),
            "time_zone": getattr(doc, "time_zone", None),
        }

    @staticmethod
    def get_doctor_details(db: Session, doctor_id: int) -> Optional[Dict[str, Any]]:
        stmt = (
            select(Doctor, MedicalField)
            .join(MedicalField, Doctor.medical_field_id == MedicalField.id)
            .where(Doctor.id == doctor_id)
        )
        row = db.execute(stmt).first()
        if not row:
            return None
        d, mf = row
        return {
            "doctor_name": d.name,
            "doctor_specialization": d.specialization,
            "consultation_fee": d.consultation_fee,
            "medical_field_name": mf.medical_field_name,
        }

    @staticmethod
    def get_patient_appointments(
        db: Session, patient_id: int, statuses: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        if statuses is None:
            statuses = ["scheduled", "confirmed"]

        stmt = (
            select(Appointment.id, Appointment.appointment_time, Appointment.duration_minutes)
            .where(Appointment.patient_id == patient_id)
            .where(Appointment.status.in_(statuses))
        )

        rows = db.execute(stmt).all()
        return [
            {
                "id": r.id,
                "appointment_time": r.appointment_time,
                "duration_minutes": r.duration_minutes,
            }
            for r in rows
        ]

    @staticmethod
    def create_appointment(
        db: Session,
        patient_id: int,
        doctor_id: int,
        medical_field_id: int,
        appointment_time: datetime,
        duration_minutes: int,
        reason_for_visit: Optional[str],
    ) -> Dict[str, Any]:
        appt = Appointment(
            patient_id=patient_id,
            doctor_id=doctor_id,
            medical_field_id=medical_field_id,
            appointment_time=appointment_time,
            duration_minutes=duration_minutes,
            reason_for_visit=reason_for_visit,
            status="scheduled",
        )
        db.add(appt)
        db.flush()  # assigns appt.id

        return AppointmentRepository.get_appointment_by_id(db, appt.id, patient_id) or _appointment_row_to_dict(appt)

    @staticmethod
    def update_appointment(
        db: Session, appointment_id: int, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        appt = db.get(Appointment, appointment_id)
        if not appt:
            raise ValueError("Appointment not found")

        # Allowlist to avoid arbitrary attribute writes
        allowed = {
            "doctor_id",
            "medical_field_id",
            "appointment_time",
            "duration_minutes",
            "status",
            "reason_for_visit",
            "notes",
            "patient_id",
        }

        for key, value in updates.items():
            if key in allowed:
                setattr(appt, key, value)

        if hasattr(appt, "updated_at"):
            appt.updated_at = func.now()

        db.flush()
        # Use patient_id from the object (safe even if it changed)
        return AppointmentRepository.get_appointment_by_id(db, appt.id, appt.patient_id) or _appointment_row_to_dict(appt)

    @staticmethod
    def cancel_appointment(db: Session, appointment_id: int) -> None:
        appt = db.get(Appointment, appointment_id)
        if not appt:
            return

        appt.status = "cancelled"
        if hasattr(appt, "cancelled_at"):
            appt.cancelled_at = func.now()
        if hasattr(appt, "updated_at"):
            appt.updated_at = func.now()

        db.flush()

    @staticmethod
    def get_appointment_simple(db: Session, appointment_id: int) -> Optional[Dict[str, Any]]:
        appt = db.get(Appointment, appointment_id)
        if not appt:
            return None

        # Return all columns (best-effort) as a dict without joins.
        data: Dict[str, Any] = {}
        for col in appt.__table__.columns:
            data[col.name] = getattr(appt, col.name)
        return data

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, or_
import logging

from app.models import Doctor, MedicalField, Appointment, DoctorWorkingHours

logger = logging.getLogger(__name__)


def _row_to_dict(row) -> Dict[str, Any]:
    """Convert SQLAlchemy Row to dictionary"""
    try:
        return dict(row._mapping)
    except Exception:
        return dict(row)


class DoctorRepository:
    """Data access layer for doctors using SQLAlchemy"""

    @staticmethod
    def get_doctors(
        db: Session,
        medical_field_id: Optional[int] = None,
        min_rating: Optional[float] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Fetch doctors with optional filters"""
        stmt = (
            select(
                Doctor.id,
                Doctor.name,
                Doctor.medical_field_id,
                MedicalField.medical_field_name,
                Doctor.specialization,
                Doctor.years_of_experience,
                Doctor.rating,
                Doctor.total_reviews,
                Doctor.bio,
                Doctor.consultation_fee,
                Doctor.image_url,
                Doctor.is_available,
                Doctor.time_zone,
                Doctor.created_at,
            )
            .select_from(Doctor)
            .outerjoin(MedicalField, Doctor.medical_field_id == MedicalField.id)
            .where(Doctor.is_available == True)
        )

        # Apply filters
        if medical_field_id:
            stmt = stmt.where(Doctor.medical_field_id == medical_field_id)

        if min_rating is not None:
            stmt = stmt.where(Doctor.rating >= min_rating)

        if search:
            search_pattern = f"%{search}%"
            stmt = stmt.where(
                or_(
                    Doctor.name.ilike(search_pattern),
                    Doctor.specialization.ilike(search_pattern),
                )
            )

        # Order and paginate
        stmt = (
            stmt.order_by(Doctor.rating.desc().nullslast(), Doctor.total_reviews.desc())
            .limit(limit)
            .offset(offset)
        )

        rows = db.execute(stmt).all()
        return [_row_to_dict(row) for row in rows]

    @staticmethod
    def get_doctor_by_id(db: Session, doctor_id: int) -> Optional[Dict[str, Any]]:
        """Fetch doctor by ID with medical field"""
        stmt = (
            select(
                Doctor,
                MedicalField.medical_field_name,
            )
            .select_from(Doctor)
            .outerjoin(MedicalField, Doctor.medical_field_id == MedicalField.id)
            .where(Doctor.id == doctor_id)
        )

        row = db.execute(stmt).first()
        if not row:
            return None

        # Combine Doctor object attributes with medical_field_name
        doctor, medical_field_name = row
        return {
            "id": doctor.id,
            "name": doctor.name,
            "medical_field_id": doctor.medical_field_id,
            "medical_field_name": medical_field_name,
            "specialization": doctor.specialization,
            "years_of_experience": doctor.years_of_experience,
            "rating": float(doctor.rating) if doctor.rating else None,
            "total_reviews": doctor.total_reviews,
            "bio": doctor.bio,
            "consultation_fee": float(doctor.consultation_fee) if doctor.consultation_fee else None,
            "image_url": doctor.image_url,
            "is_available": doctor.is_available,
            "time_zone": doctor.time_zone,
            "created_at": doctor.created_at,
        }

    @staticmethod
    def get_doctor_working_hours(db: Session, doctor_id: int) -> List[Dict[str, Any]]:
        """Fetch working hours for a doctor"""
        stmt = (
            select(DoctorWorkingHours)
            .where(
                and_(
                    DoctorWorkingHours.doctor_id == doctor_id,
                    DoctorWorkingHours.is_active == True,
                )
            )
            .order_by(DoctorWorkingHours.day_of_week)
        )

        working_hours = db.execute(stmt).scalars().all()

        return [
            {
                "id": wh.id,
                "doctor_id": wh.doctor_id,
                "day_of_week": wh.day_of_week,
                "start_time": wh.start_time,
                "end_time": wh.end_time,
                "slot_duration_minutes": wh.slot_duration_minutes,
                "is_active": wh.is_active,
            }
            for wh in working_hours
        ]

    @staticmethod
    def get_doctor_basic_info(db: Session, doctor_id: int) -> Optional[Dict[str, Any]]:
        """Fetch basic doctor info (id, timezone, availability)"""
        stmt = select(
            Doctor.id, Doctor.time_zone, Doctor.is_available
        ).where(Doctor.id == doctor_id)

        row = db.execute(stmt).first()
        return _row_to_dict(row) if row else None

    @staticmethod
    def get_working_hours_for_day(
        db: Session, doctor_id: int, day_of_week: int
    ) -> Optional[Dict[str, Any]]:
        """Get working hours for specific day (0=Sunday)"""
        stmt = (
            select(
                DoctorWorkingHours.start_time,
                DoctorWorkingHours.end_time,
                DoctorWorkingHours.slot_duration_minutes,
            )
            .where(
                and_(
                    DoctorWorkingHours.doctor_id == doctor_id,
                    DoctorWorkingHours.day_of_week == day_of_week,
                    DoctorWorkingHours.is_active == True,
                )
            )
        )

        row = db.execute(stmt).first()
        return _row_to_dict(row) if row else None

    @staticmethod
    def get_doctor_appointments(db: Session, doctor_id: int) -> List[Dict[str, Any]]:
        """
        Fetch all scheduled/confirmed appointments for a doctor
        
        CRITICAL: This must return appointments to filter out booked slots!
        """
        stmt = (
            select(
                Appointment.id,
                Appointment.appointment_time,
                Appointment.duration_minutes,
                Appointment.status,
            )
            .where(
                and_(
                    Appointment.doctor_id == doctor_id,
                    Appointment.status.in_(["scheduled", "confirmed"]),
                )
            )
            .order_by(Appointment.appointment_time.asc())
        )

        rows = db.execute(stmt).all()
        
        result = [
            {
                "id": row.id,
                "appointment_time": row.appointment_time,
                "duration_minutes": row.duration_minutes or 30,
                "status": row.status,
            }
            for row in rows
        ]
        
        # Debug logging
        logger.info(f"get_doctor_appointments for doctor {doctor_id}: found {len(result)} appointments")
        if result:
            logger.debug(f"First appointment: {result[0]}")
        
        return result

    @staticmethod
    def get_patient_appointments(
        db: Session, 
        patient_id: int,
        start_date: Optional[Any] = None,
        end_date: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch patient's appointments (for checking conflicts)
        
        Args:
            patient_id: Patient ID
            start_date: Optional start datetime filter
            end_date: Optional end datetime filter
            
        Returns:
            List of patient's appointments
        """
        stmt = (
            select(
                Appointment.id,
                Appointment.doctor_id,
                Appointment.appointment_time,
                Appointment.duration_minutes,
                Appointment.status,
            )
            .where(
                and_(
                    Appointment.patient_id == patient_id,
                    Appointment.status.in_(["scheduled", "confirmed"]),
                )
            )
        )
        
        # Add date filters if provided
        if start_date:
            stmt = stmt.where(Appointment.appointment_time >= start_date)
        if end_date:
            stmt = stmt.where(Appointment.appointment_time < end_date)
        
        stmt = stmt.order_by(Appointment.appointment_time.asc())
        
        rows = db.execute(stmt).all()
        
        result = [
            {
                "id": row.id,
                "doctor_id": row.doctor_id,
                "appointment_time": row.appointment_time,
                "duration_minutes": row.duration_minutes or 30,
                "status": row.status,
            }
            for row in rows
        ]
        
        logger.info(f"get_patient_appointments for patient {patient_id}: found {len(result)} appointments")
        
        return result
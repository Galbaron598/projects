from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DoctorRepository:
    """Data access layer for doctors"""

    @staticmethod
    def get_doctors(
        cursor,
        medical_field_id: Optional[int] = None,
        min_rating: Optional[float] = None,
        search: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Fetch doctors with optional filters"""
        query = """
            SELECT 
                d.id,
                d.name,
                d.medical_field_id,
                mf.medical_field_name,
                d.specialization,
                d.years_of_experience,
                d.rating,
                d.total_reviews,
                d.bio,
                d.consultation_fee,
                d.image_url,
                d.is_available,
                d.time_zone,
                d.created_at
            FROM doctors d
            LEFT JOIN medical_fields mf ON d.medical_field_id = mf.id
            WHERE d.is_available = TRUE
        """
        params = []

        if medical_field_id:
            query += " AND d.medical_field_id = %s"
            params.append(medical_field_id)

        if min_rating is not None:
            query += " AND d.rating >= %s"
            params.append(min_rating)

        if search:
            query += " AND (d.name ILIKE %s OR d.specialization ILIKE %s)"
            s = f"%{search}%"
            params.extend([s, s])

        query += " ORDER BY d.rating DESC, d.total_reviews DESC"
        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def get_doctor_by_id(cursor, doctor_id: int) -> Optional[Dict[str, Any]]:
        """Fetch doctor by ID with medical field"""
        cursor.execute(
            """
            SELECT d.*, mf.medical_field_name
            FROM doctors d
            LEFT JOIN medical_fields mf ON d.medical_field_id = mf.id
            WHERE d.id = %s
            """,
            (doctor_id,),
        )
        return cursor.fetchone()

    @staticmethod
    def get_doctor_working_hours(cursor, doctor_id: int) -> List[Dict[str, Any]]:
        """Fetch working hours for a doctor"""
        cursor.execute(
            """
            SELECT *
            FROM doctor_working_hours
            WHERE doctor_id = %s AND is_active = TRUE
            ORDER BY day_of_week
            """,
            (doctor_id,),
        )
        return cursor.fetchall()

    @staticmethod
    def get_doctor_basic_info(cursor, doctor_id: int) -> Optional[Dict[str, Any]]:
        """Fetch basic doctor info (id, timezone, availability)"""
        cursor.execute(
            "SELECT id, time_zone, is_available FROM doctors WHERE id = %s",
            (doctor_id,),
        )
        return cursor.fetchone()

    @staticmethod
    def get_working_hours_for_day(
        cursor, doctor_id: int, day_of_week: int
    ) -> Optional[Dict[str, Any]]:
        """Get working hours for specific day (0=Sunday)"""
        cursor.execute(
            """
            SELECT start_time, end_time, slot_duration_minutes
            FROM doctor_working_hours
            WHERE doctor_id = %s
              AND day_of_week = %s
              AND is_active = TRUE
            """,
            (doctor_id, day_of_week),
        )
        return cursor.fetchone()

    @staticmethod
    def get_doctor_appointments(cursor, doctor_id: int) -> List[Dict[str, Any]]:
        """Fetch all scheduled/confirmed appointments for a doctor"""
        cursor.execute(
            """
            SELECT appointment_time, duration_minutes
            FROM appointments
            WHERE doctor_id = %s
              AND status IN ('scheduled', 'confirmed')
            """,
            (doctor_id,),
        )
        return cursor.fetchall()
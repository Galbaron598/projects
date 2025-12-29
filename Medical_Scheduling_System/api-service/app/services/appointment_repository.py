from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

BASE_SELECT = """
    SELECT 
        a.id,
        a.patient_id,
        a.doctor_id,
        a.medical_field_id,
        a.appointment_time,
        a.duration_minutes,
        a.status,
        a.reason_for_visit,
        a.notes,
        a.created_at,
        a.updated_at,
        d.name as doctor_name,
        d.specialization as doctor_specialization,
        d.consultation_fee,
        mf.medical_field_name
    FROM appointments a
    JOIN doctors d ON a.doctor_id = d.id
    JOIN medical_fields mf ON a.medical_field_id = mf.id
"""


class AppointmentRepository:
    """Data access layer for appointments"""

    @staticmethod
    def get_appointments(
        cursor,
        patient_id: int,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """Fetch appointments with optional status filter"""
        query = BASE_SELECT + " WHERE a.patient_id = %s"
        params = [patient_id]

        if status_filter:
            query += " AND a.status = %s"
            params.append(status_filter)

        query += " ORDER BY a.appointment_time DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        return cursor.fetchall()

    @staticmethod
    def get_upcoming_appointments(
        cursor, patient_id: int, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Fetch upcoming appointments for a patient"""
        cursor.execute(
            BASE_SELECT
            + """
            WHERE a.patient_id = %s
              AND a.appointment_time > NOW()
              AND a.status NOT IN ('cancelled', 'no_show')
            ORDER BY a.appointment_time ASC
            LIMIT %s
            """,
            (patient_id, limit),
        )
        return cursor.fetchall()

    @staticmethod
    def get_past_appointments(
        cursor, patient_id: int, limit: int = 20, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Fetch past appointments for a patient"""
        cursor.execute(
            BASE_SELECT
            + """
            WHERE a.patient_id = %s
              AND (
                  a.appointment_time < NOW()
                  OR a.status IN ('cancelled', 'completed', 'no_show')
              )
            ORDER BY a.appointment_time DESC
            LIMIT %s OFFSET %s
            """,
            (patient_id, limit, offset),
        )
        return cursor.fetchall()

    @staticmethod
    def get_appointment_by_id(
        cursor, appointment_id: int, patient_id: int
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single appointment by ID"""
        cursor.execute(
            BASE_SELECT + " WHERE a.id = %s AND a.patient_id = %s",
            (appointment_id, patient_id),
        )
        return cursor.fetchone()

    @staticmethod
    def get_doctor_info(cursor, doctor_id: int) -> Optional[Dict[str, Any]]:
        """Fetch doctor information including timezone"""
        cursor.execute(
            """
            SELECT id, is_available, time_zone
            FROM doctors
            WHERE id = %s
            """,
            (doctor_id,),
        )
        return cursor.fetchone()

    @staticmethod
    def get_doctor_details(cursor, doctor_id: int) -> Optional[Dict[str, Any]]:
        """Fetch doctor details with medical field"""
        cursor.execute(
            """
            SELECT 
                d.name as doctor_name,
                d.specialization as doctor_specialization,
                d.consultation_fee,
                mf.medical_field_name
            FROM doctors d
            JOIN medical_fields mf ON d.medical_field_id = mf.id
            WHERE d.id = %s
            """,
            (doctor_id,),
        )
        return cursor.fetchone()

    @staticmethod
    def get_patient_appointments(
        cursor, patient_id: int, statuses: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Fetch all patient appointments with optional status filter"""
        if statuses is None:
            statuses = ["scheduled", "confirmed"]

        cursor.execute(
            """
            SELECT id, appointment_time, duration_minutes
            FROM appointments
            WHERE patient_id = %s
              AND status = ANY(%s)
            """,
            (patient_id, statuses),
        )
        return cursor.fetchall()

    @staticmethod
    def create_appointment(
        cursor,
        patient_id: int,
        doctor_id: int,
        medical_field_id: int,
        appointment_time: datetime,
        duration_minutes: int,
        reason_for_visit: Optional[str],
    ) -> Dict[str, Any]:
        """Insert a new appointment"""
        cursor.execute(
            """
            INSERT INTO appointments (
                patient_id,
                doctor_id,
                medical_field_id,
                appointment_time,
                duration_minutes,
                reason_for_visit,
                status
            )
            VALUES (%s, %s, %s, %s, %s, %s, 'scheduled')
            RETURNING *
            """,
            (
                patient_id,
                doctor_id,
                medical_field_id,
                appointment_time,
                duration_minutes,
                reason_for_visit,
            ),
        )
        return cursor.fetchone()

    @staticmethod
    def update_appointment(
        cursor, appointment_id: int, updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an appointment with dynamic fields"""
        set_clauses = []
        params = []

        for field, value in updates.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)

        set_clauses.append("updated_at = NOW()")
        params.append(appointment_id)

        query = f"""
            UPDATE appointments
            SET {', '.join(set_clauses)}
            WHERE id = %s
            RETURNING *
        """
        cursor.execute(query, params)
        return cursor.fetchone()

    @staticmethod
    def cancel_appointment(cursor, appointment_id: int) -> None:
        """Cancel an appointment (soft delete)"""
        cursor.execute(
            """
            UPDATE appointments
            SET status = 'cancelled',
                cancelled_at = NOW(),
                updated_at = NOW()
            WHERE id = %s
            """,
            (appointment_id,),
        )

    @staticmethod
    def get_appointment_simple(cursor, appointment_id: int) -> Optional[Dict[str, Any]]:
        """Fetch basic appointment info without joins"""
        cursor.execute(
            "SELECT * FROM appointments WHERE id = %s", (appointment_id,)
        )
        return cursor.fetchone()
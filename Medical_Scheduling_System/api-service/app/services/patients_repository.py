from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PatientRepository:
    """Data access layer for patients"""

    @staticmethod
    def get_patient_by_id(cursor, patient_id: int) -> Optional[Dict[str, Any]]:
        """Fetch patient by ID"""
        cursor.execute(
            """
            SELECT 
                id,
                phone_number,
                full_name,
                email,
                date_of_birth,
                gender,
                time_zone,
                emergency_contact,
                address,
                created_at,
                is_active
            FROM patients 
            WHERE id = %s
            """,
            (patient_id,),
        )
        return cursor.fetchone()

    @staticmethod
    def get_patient_by_phone(cursor, phone_number: str) -> Optional[Dict[str, Any]]:
        """Fetch patient by phone number"""
        cursor.execute(
            """
            SELECT
                id,
                phone_number,
                full_name,
                email,
                date_of_birth,
                gender,
                time_zone,
                emergency_contact,
                address,
                created_at,
                is_active
            FROM patients
            WHERE phone_number = %s
            """,
            (phone_number,),
        )
        return cursor.fetchone()

    @staticmethod
    def check_patient_exists(cursor, phone_number: str) -> Optional[Dict[str, Any]]:
        """Check if patient exists by phone number"""
        cursor.execute(
            "SELECT id FROM patients WHERE phone_number = %s",
            (phone_number,),
        )
        return cursor.fetchone()

    @staticmethod
    def create_patient(cursor, phone_number: str, time_zone: str = "Asia/Jerusalem") -> Dict[str, Any]:
        """Create a new patient"""
        cursor.execute(
            """
            INSERT INTO patients (
                phone_number,
                time_zone,
                is_active
            )
            VALUES (%s, %s, true)
            RETURNING
                id,
                phone_number,
                full_name,
                email,
                date_of_birth,
                gender,
                time_zone,
                emergency_contact,
                address,
                created_at,
                is_active
            """,
            (phone_number, time_zone),
        )
        return cursor.fetchone()

    @staticmethod
    def update_patient(cursor, patient_id: int, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update patient with dynamic fields"""
        set_clauses = []
        params = []

        for field, value in updates.items():
            set_clauses.append(f"{field} = %s")
            params.append(value)

        set_clauses.append("updated_at = NOW()")
        params.append(patient_id)

        query = f"""
            UPDATE patients
            SET {', '.join(set_clauses)}
            WHERE id = %s
            RETURNING
                id,
                phone_number,
                full_name,
                email,
                date_of_birth,
                gender,
                time_zone,
                emergency_contact,
                address,
                created_at,
                is_active
        """

        cursor.execute(query, params)
        return cursor.fetchone()
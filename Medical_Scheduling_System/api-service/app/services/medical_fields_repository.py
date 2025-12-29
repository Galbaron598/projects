from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class MedicalFieldRepository:
    """Data access layer for medical fields"""

    @staticmethod
    def get_all_active_fields(cursor) -> List[Dict[str, Any]]:
        """Fetch all active medical fields"""
        cursor.execute(
            """
            SELECT 
                id, 
                medical_field_name, 
                description, 
                icon, 
                is_active,
                created_at
            FROM medical_fields
            WHERE is_active = TRUE
            ORDER BY medical_field_name ASC
            """
        )
        return cursor.fetchall()

    @staticmethod
    def get_field_by_id(cursor, field_id: int) -> Optional[Dict[str, Any]]:
        """Fetch medical field by ID"""
        cursor.execute(
            """
            SELECT 
                id, 
                medical_field_name, 
                description, 
                icon, 
                is_active,
                created_at
            FROM medical_fields
            WHERE id = %s
            """,
            (field_id,),
        )
        return cursor.fetchone()

    @staticmethod
    def count_available_doctors(cursor, field_id: int) -> int:
        """Count available doctors in a medical field"""
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM doctors
            WHERE medical_field_id = %s 
              AND is_available = TRUE
            """,
            (field_id,),
        )
        result = cursor.fetchone()
        return result["count"] if result else 0
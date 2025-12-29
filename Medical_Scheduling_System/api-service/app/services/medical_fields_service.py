from typing import Dict, Any, List
from fastapi import HTTPException
import logging

from app.services.medical_fields_repository import MedicalFieldRepository

logger = logging.getLogger(__name__)


class MedicalFieldService:
    """Business logic layer for medical fields"""

    def __init__(self):
        self.repo = MedicalFieldRepository()

    def get_all_fields(self, cursor) -> List[Dict[str, Any]]:
        """Get all active medical fields"""
        fields = self.repo.get_all_active_fields(cursor)
        logger.info(f"Retrieved {len(fields)} medical fields")
        return fields

    def get_field_by_id(self, cursor, field_id: int) -> Dict[str, Any]:
        """Get specific medical field by ID with validation"""
        field = self.repo.get_field_by_id(cursor, field_id)
        
        if not field:
            raise HTTPException(
                status_code=404,
                detail=f"Medical field with ID {field_id} not found"
            )
        
        return field

    def get_doctors_count_for_field(self, cursor, field_id: int) -> Dict[str, Any]:
        """Get count of available doctors in this field"""
        count = self.repo.count_available_doctors(cursor, field_id)
        return {
            "medical_field_id": field_id,
            "doctors_count": count
        }
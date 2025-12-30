from typing import Dict, Any, List
from fastapi import HTTPException
from sqlalchemy.orm import Session
import logging

from app.repository.medical_fields_repository import MedicalFieldRepository

logger = logging.getLogger(__name__)
class MedicalFieldService:
    """Business logic layer for medical fields"""

    def __init__(self):
        self.repo = MedicalFieldRepository()

    def get_all_fields(self, db: Session) -> List[Dict[str, Any]]:
        """Get all active medical fields"""
        fields = self.repo.get_all_active_fields(db)
        logger.info(f"Retrieved {len(fields)} medical fields")
        return fields

    def get_field_by_id(self, db: Session, field_id: int) -> Dict[str, Any]:
        """Get specific medical field by ID with validation"""
        field = self.repo.get_field_by_id(db, field_id)
        
        if not field:
            raise HTTPException(
                status_code=404,
                detail=f"Medical field with ID {field_id} not found"
            )
        
        return field

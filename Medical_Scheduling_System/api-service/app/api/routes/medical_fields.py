from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
import logging

from app.schemas.medical_field import MedicalFieldResponse
from app.core.database import get_db
from app.services.medical_fields_service import MedicalFieldService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/medical-fields", tags=["Medical Fields"])

@router.get("", response_model=List[MedicalFieldResponse])
async def get_medical_fields(db: Session = Depends(get_db)):
    """Get all active medical fields/specialties"""
    try:
        service = MedicalFieldService()
        return service.get_all_fields(db)

    except Exception as e:
        logger.error(f"Error fetching medical fields: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical fields",
        )

@router.get("/{field_id}", response_model=MedicalFieldResponse)
async def get_medical_field(field_id: int, db: Session = Depends(get_db)):
    """Get specific medical field by ID"""
    try:
        service = MedicalFieldService()
        return service.get_field_by_id(db, field_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching medical field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical field",
        )

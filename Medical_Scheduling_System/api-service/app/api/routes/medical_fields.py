from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from app.schemas.medical_field import MedicalFieldResponse
from app.core.database import get_db
from app.services.medical_fields_service import MedicalFieldService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/medical-fields", tags=["Medical Fields"])


@router.get("/", response_model=List[MedicalFieldResponse])
async def get_medical_fields():
    """Get all active medical fields/specialties"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                service = MedicalFieldService()
                return service.get_all_fields(cursor)

    except Exception as e:
        logger.error(f"Error fetching medical fields: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical fields",
        )


@router.get("/{field_id}", response_model=MedicalFieldResponse)
async def get_medical_field(field_id: int):
    """Get specific medical field by ID"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                service = MedicalFieldService()
                return service.get_field_by_id(cursor, field_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching medical field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical field",
        )


@router.get("/{field_id}/doctors-count")
async def get_doctors_count(field_id: int):
    """Get count of available doctors in this field"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                service = MedicalFieldService()
                return service.get_doctors_count_for_field(cursor, field_id)

    except Exception as e:
        logger.error(f"Error counting doctors for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count doctors",
        )
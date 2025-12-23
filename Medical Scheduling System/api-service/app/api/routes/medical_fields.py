from fastapi import APIRouter, HTTPException, status
from typing import List
from app.schemas.medical_field import MedicalFieldResponse
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/medical-fields", tags=["Medical Fields"])

@router.get("/", response_model=List[MedicalFieldResponse])
async def get_medical_fields():
    """Get all active medical fields/specialties"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
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
                """)
                fields = cursor.fetchall()
                logger.info(f"Retrieved {len(fields)} medical fields")
                return fields
                
    except Exception as e:
        logger.error(f"Error fetching medical fields: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical fields"
        )

@router.get("/{field_id}", response_model=MedicalFieldResponse)
async def get_medical_field(field_id: int):
    """Get specific medical field by ID"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id, 
                        medical_field_name, 
                        description, 
                        icon, 
                        is_active,
                        created_at
                    FROM medical_fields
                    WHERE id = %s
                """, (field_id,))
                field = cursor.fetchone()
                
                if not field:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Medical field with ID {field_id} not found"
                    )
                
                return field
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching medical field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve medical field"
        )

@router.get("/{field_id}/doctors-count")
async def get_doctors_count(field_id: int):
    """Get count of available doctors in this field"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) as count
                    FROM doctors
                    WHERE medical_field_id = %s 
                      AND is_available = TRUE
                """, (field_id,))
                result = cursor.fetchone()
                return {"medical_field_id": field_id, "doctors_count": result['count']}
                
    except Exception as e:
        logger.error(f"Error counting doctors for field {field_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to count doctors"
        )

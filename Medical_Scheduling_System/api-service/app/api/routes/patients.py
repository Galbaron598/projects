from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import logging

from app.schemas.patient import PatientResponse, PatientUpdate, PatientCreate
from app.middleware.auth_middleware import verify_token
from app.core.database import get_db
from app.services.patient_service import PatientService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/patients", tags=["Patients"])

@router.get("/profile", response_model=PatientResponse)
async def get_current_patient(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
    patient_id: int = Query(..., gt=0, description="Patient id"),
):
    """Get patient information by patient_id (auth required)"""
    try:
        service = PatientService()
        return service.get_patient_profile(db, patient_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient information",
        )

@router.patch("/profile", response_model=PatientResponse)
async def update_current_patient(
    update_data: PatientUpdate,
    db: Session = Depends(get_db),
    patient_id: int = Query(..., gt=0, description="Patient id"),
    _: dict = Depends(verify_token),
):
    """Update patient profile by patient_id (auth required)"""
    try:
        service = PatientService()
        return service.update_patient_profile(db, patient_id, update_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient information",
        )

@router.post("/new", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(payload: PatientCreate, db: Session = Depends(get_db)):
    """Create a new patient (phone number only)"""
    try:
        service = PatientService()
        return service.create_or_get_patient(db, payload.phone_number)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create patient",
        )

@router.get("/exists")
async def patient_exists(
    phone_number: str = Query(..., min_length=7, max_length=20),
    db: Session = Depends(get_db)
):
    """Check if a patient exists by phone number"""
    try:
        service = PatientService()
        return service.check_patient_exists(db, phone_number)

    except Exception as e:
        logger.error(f"Error checking patient existence: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to check patient existence",
        )
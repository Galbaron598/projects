from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from app.schemas.doctor import DoctorResponse, DoctorDetailResponse
from app.core.database import get_db
from app.repository.doctors_repository import DoctorRepository
from app.services.doctors_service import DoctorService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/doctors", tags=["Doctors"])


@router.get("/", response_model=List[DoctorResponse])
async def get_doctors(
    db: Session = Depends(get_db),
    medical_field_id: Optional[int] = Query(
        None, description="Filter by medical field"
    ),
    min_rating: Optional[float] = Query(
        None, ge=0, le=5, description="Minimum rating"
    ),
    search: Optional[str] = Query(
        None, description="Search by name or specialization"
    ),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get list of doctors with optional filters"""
    try:
        repo = DoctorRepository()
        return repo.get_doctors(
            db,
            medical_field_id=medical_field_id,
            min_rating=min_rating,
            search=search,
            limit=limit,
            offset=offset,
        )

    except Exception as e:
        logger.error(f"Error fetching doctors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve doctors",
        )


@router.get("/{doctor_id}", response_model=DoctorDetailResponse)
async def get_doctor(doctor_id: int, db: Session = Depends(get_db)):
    """Get detailed information about a specific doctor"""
    try:
        service = DoctorService()
        return service.get_doctor_with_details(db, doctor_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching doctor {doctor_id}: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve doctor information"
        )


@router.get("/{doctor_id}/available-slots")
async def get_available_slots(
    doctor_id: int,
    db: Session = Depends(get_db),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
):
    """
    Get available time slots for a doctor on a specific date.
    Returns only free slots (no overlaps) in ISO format.
    """
    try:
        service = DoctorService()
        return service.get_available_slots(db, doctor_id, date)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching available slots for doctor {doctor_id}: {e}"
        )
        raise HTTPException(
            status_code=500, detail="Failed to retrieve available slots"
        )
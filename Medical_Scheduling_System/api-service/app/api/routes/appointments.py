from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
)
from app.middleware.auth_middleware import verify_token
from app.core.database import get_db
from app.repository.appointment_repository import AppointmentRepository
from app.services.appointment_service import AppointmentService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
    patient_id: int = Query(..., gt=0, description="Patient id"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get all appointments for a patient with optional filtering"""
    try:
        repo = AppointmentRepository()
        return repo.get_appointments(db, patient_id, status_filter, limit, offset)

    except Exception as e:
        logger.error(f"Error fetching appointments: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve appointments"
        )


@router.get("/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointments(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
    patient_id: int = Query(..., gt=0, description="Patient id"),
    limit: int = Query(10, ge=1, le=50),
):
    """Get upcoming appointments for a patient"""
    try:
        repo = AppointmentRepository()
        return repo.get_upcoming_appointments(db, patient_id, limit)

    except Exception as e:
        logger.error(f"Error fetching upcoming appointments: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve upcoming appointments"
        )


@router.get("/past", response_model=List[AppointmentResponse])
async def get_past_appointments(
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
    patient_id: int = Query(..., gt=0, description="Patient id"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get past appointments for a patient"""
    try:
        repo = AppointmentRepository()
        return repo.get_past_appointments(db, patient_id, limit, offset)

    except Exception as e:
        logger.error(f"Error fetching past appointments: {e}")
        raise HTTPException(
            status_code=500, detail="Failed to retrieve past appointments"
        )


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
    patient_id: int = Query(..., gt=0, description="Patient id"),
):
    """Get a specific appointment by ID"""
    try:
        repo = AppointmentRepository()
        appointment = repo.get_appointment_by_id(db, appointment_id, patient_id)
        
        if not appointment:
            raise HTTPException(
                status_code=404,
                detail=f"Appointment {appointment_id} not found",
            )
        return appointment

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching appointment {appointment_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve appointment")


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Create a new appointment"""
    try:
        service = AppointmentService()
        return service.create_appointment(
            db,
            appointment.patient_id,
            appointment.doctor_id,
            appointment.medical_field_id,
            appointment.appointment_time,
            appointment.duration_minutes,
            appointment.reason_for_visit,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create appointment")


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Update an existing appointment"""
    try:
        service = AppointmentService()
        return service.update_appointment(
            db,
            appointment_id,
            appointment_time=update_data.appointment_time,
            status=update_data.status,
            notes=update_data.notes,
            cancellation_reason=update_data.cancellation_reason,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment {appointment_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update appointment")


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(verify_token),
):
    """Cancel an appointment (soft delete)"""
    try:
        service = AppointmentService()
        service.cancel_appointment(db, appointment_id)
        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling appointment {appointment_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel appointment")
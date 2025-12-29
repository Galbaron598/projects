from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from app.schemas.appointment import (
    AppointmentCreate,
    AppointmentResponse,
    AppointmentUpdate,
    AppointmentStats,
)
from app.middleware.auth_middleware import verify_token
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/appointments", tags=["Appointments"])


BASE_SELECT = """
    SELECT 
        a.id,
        a.patient_id,
        a.doctor_id,
        a.medical_field_id,
        a.appointment_time,
        a.duration_minutes,
        a.status,
        a.reason_for_visit,
        a.notes,
        a.created_at,
        a.updated_at,
        d.name as doctor_name,
        d.specialization as doctor_specialization,
        d.consultation_fee,
        mf.medical_field_name
    FROM appointments a
    JOIN doctors d ON a.doctor_id = d.id
    JOIN medical_fields mf ON a.medical_field_id = mf.id
"""


@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    _: dict = Depends(verify_token),
    patient_id: int = Query(..., gt=0, description="Patient id"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Get patient's appointments with optional filters

    - **patient_id**: Patient id
    - **status_filter**: scheduled, confirmed, cancelled, completed, no_show
    - **limit**: max 100
    - **offset**: pagination offset
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                query = (
                    BASE_SELECT
                    + """
                    WHERE a.patient_id = %s
                    """
                )
                params = [patient_id]

                if status_filter:
                    query += " AND a.status = %s"
                    params.append(status_filter)

                query += " ORDER BY a.appointment_time DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])

                cursor.execute(query, params)
                rows = cursor.fetchall()
                logger.info(f"Retrieved {len(rows)} appointments for patient {patient_id}")
                return rows

    except Exception as e:
        logger.error(f"Error fetching appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve appointments")


@router.get("/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointments(
    _: dict = Depends(verify_token),
    patient_id: int = Query(..., gt=0, description="Patient id"),
    limit: int = Query(10, ge=1, le=50),
):
    """Get patient's upcoming appointments (future, not cancelled/no_show)"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    BASE_SELECT
                    + """
                    WHERE a.patient_id = %s
                      AND a.appointment_time > NOW()
                      AND a.status NOT IN ('cancelled', 'no_show')
                    ORDER BY a.appointment_time ASC
                    LIMIT %s
                    """,
                    (patient_id, limit),
                )
                rows = cursor.fetchall()
                logger.info(f"Retrieved {len(rows)} upcoming appointments for patient {patient_id}")
                return rows

    except Exception as e:
        logger.error(f"Error fetching upcoming appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve upcoming appointments")


@router.get("/past", response_model=List[AppointmentResponse])
async def get_past_appointments(
    _: dict = Depends(verify_token),
    patient_id: int = Query(..., gt=0, description="Patient id"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """Get patient's past appointments"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    BASE_SELECT
                    + """
                    WHERE a.patient_id = %s
                      AND (
                          a.appointment_time < NOW()
                          OR a.status IN ('cancelled', 'completed', 'no_show')
                      )
                    ORDER BY a.appointment_time DESC
                    LIMIT %s OFFSET %s
                    """,
                    (patient_id, limit, offset),
                )
                return cursor.fetchall()

    except Exception as e:
        logger.error(f"Error fetching past appointments: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve past appointments")


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    _: dict = Depends(verify_token),
    patient_id: int = Query(..., gt=0, description="Patient id"),
):
    """Get specific appointment by ID for a patient"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    BASE_SELECT
                    + """
                    WHERE a.id = %s AND a.patient_id = %s
                    """,
                    (appointment_id, patient_id),
                )
                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")
                return row

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching appointment {appointment_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve appointment")


@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    _: dict = Depends(verify_token),
):
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT id, is_available 
                    FROM doctors 
                    WHERE id = %s
                    """,
                    (appointment.doctor_id,),
                )
                doctor = cursor.fetchone()
                if not doctor:
                    raise HTTPException(status_code=404, detail=f"Doctor {appointment.doctor_id} not found")
                if not doctor["is_available"]:
                    raise HTTPException(status_code=400, detail="Doctor is not currently available")

                # doctor slot conflict
                cursor.execute(
                    """
                    SELECT id FROM appointments
                    WHERE doctor_id = %s
                      AND appointment_time = %s
                      AND status NOT IN ('cancelled', 'no_show')
                    """,
                    (appointment.doctor_id, appointment.appointment_time),
                )
                if cursor.fetchone():
                    raise HTTPException(status_code=409, detail="This time slot is already booked")

                # patient conflict
                cursor.execute(
                    """
                    SELECT id FROM appointments
                    WHERE patient_id = %s
                      AND appointment_time = %s
                      AND status NOT IN ('cancelled', 'no_show')
                    """,
                    (appointment.patient_id, appointment.appointment_time),
                )
                if cursor.fetchone():
                    raise HTTPException(status_code=409, detail="You already have an appointment at this time")

                cursor.execute(
                    """
                    INSERT INTO appointments (
                        patient_id,
                        doctor_id,
                        medical_field_id,
                        appointment_time,
                        duration_minutes,
                        reason_for_visit,
                        status
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, 'scheduled')
                    RETURNING *
                    """,
                    (
                        appointment.patient_id,
                        appointment.doctor_id,
                        appointment.medical_field_id,
                        appointment.appointment_time,
                        appointment.duration_minutes,
                        appointment.reason_for_visit,
                    ),
                )
                new_appointment = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT 
                        d.name as doctor_name,
                        d.specialization as doctor_specialization,
                        d.consultation_fee,
                        mf.medical_field_name
                    FROM doctors d
                    JOIN medical_fields mf ON d.medical_field_id = mf.id
                    WHERE d.id = %s
                    """,
                    (appointment.doctor_id,),
                )
                info = cursor.fetchone()

                result = {**new_appointment, **info}
                logger.info(f"Created appointment {result['id']} for patient {appointment.patient_id}")
                return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(status_code=500, detail="Failed to create appointment")


@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    _: dict = Depends(verify_token),
):
    """
    Update appointment:
    - cancel via status='cancelled'
    - add notes
    - reschedule via appointment_time
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM appointments WHERE id = %s",
                    (appointment_id,),
                )
                existing = cursor.fetchone()
                if not existing:
                    raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")

                if existing["status"] in ["completed", "no_show"]:
                    raise HTTPException(status_code=400, detail="Cannot modify completed or no-show appointments")

                updates = []
                params = []

                # ✅ RESCHEDULE
                if update_data.appointment_time is not None:
                    new_time = update_data.appointment_time

                    cursor.execute(
                        """
                        SELECT id FROM appointments
                        WHERE doctor_id = %s
                          AND appointment_time = %s
                          AND id <> %s
                          AND status NOT IN ('cancelled', 'no_show')
                        """,
                        (existing["doctor_id"], new_time, appointment_id),
                    )
                    if cursor.fetchone():
                        raise HTTPException(status_code=409, detail="This time slot is already booked")

                    cursor.execute(
                        """
                        SELECT id FROM appointments
                        WHERE patient_id = %s
                          AND appointment_time = %s
                          AND id <> %s
                          AND status NOT IN ('cancelled', 'no_show')
                        """,
                        (existing["patient_id"], new_time, appointment_id),
                    )
                    if cursor.fetchone():
                        raise HTTPException(status_code=409, detail="You already have an appointment at this time")

                    updates.append("appointment_time = %s")
                    params.append(new_time)

                if update_data.status:
                    if update_data.status in ["completed", "no_show"]:
                        raise HTTPException(status_code=403, detail="Only staff can mark appointments as completed or no-show")
                    updates.append("status = %s")
                    params.append(update_data.status)
                    if update_data.status == "cancelled":
                        updates.append("cancelled_at = NOW()")

                if update_data.notes is not None:
                    updates.append("notes = %s")
                    params.append(update_data.notes)

                if update_data.cancellation_reason is not None:
                    updates.append("cancellation_reason = %s")
                    params.append(update_data.cancellation_reason)

                if not updates:
                    raise HTTPException(status_code=400, detail="No valid update fields provided")

                updates.append("updated_at = NOW()")
                params.append(appointment_id)

                query = f"""
                    UPDATE appointments
                    SET {', '.join(updates)}
                    WHERE id = %s
                    RETURNING *
                """
                cursor.execute(query, params)
                updated_appointment = cursor.fetchone()

                cursor.execute(
                    """
                    SELECT 
                        d.name as doctor_name,
                        d.specialization as doctor_specialization,
                        d.consultation_fee,
                        mf.medical_field_name
                    FROM doctors d
                    JOIN medical_fields mf ON d.medical_field_id = mf.id
                    WHERE d.id = %s
                    """,
                    (updated_appointment["doctor_id"],),
                )
                info = cursor.fetchone()

                return {**updated_appointment, **info}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment {appointment_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update appointment")


@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    _: dict = Depends(verify_token),
):
    """Cancel appointment (soft-cancel: status=cancelled)"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT status FROM appointments WHERE id = %s",
                    (appointment_id,),
                )
                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail=f"Appointment {appointment_id} not found")

                if row["status"] in ["completed", "no_show"]:
                    raise HTTPException(status_code=400, detail="Cannot cancel completed or no-show appointments")
                if row["status"] == "cancelled":
                    raise HTTPException(status_code=400, detail="Appointment is already cancelled")

                cursor.execute(
                    """
                    UPDATE appointments
                    SET status = 'cancelled',
                        cancelled_at = NOW(),
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (appointment_id,),
                )
                logger.info(f"Cancelled appointment {appointment_id}")
                return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling appointment {appointment_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel appointment")

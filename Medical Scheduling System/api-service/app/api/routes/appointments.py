from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from app.schemas.appointment import (
    AppointmentCreate, 
    AppointmentResponse,
    AppointmentUpdate,
    AppointmentStats
)
from app.middleware.auth_middleware import verify_token
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/appointments", tags=["Appointments"])

# @router.get("", response_model=List[AppointmentResponse])
@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    user: dict = Depends(verify_token),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get user's appointments with optional filters
    
    - **status_filter**: Filter by appointment status (scheduled, confirmed, cancelled, completed)
    - **limit**: Number of results (max 100)
    - **offset**: Pagination offset
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                query = """
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
                    WHERE a.patient_id = %s
                """
                params = [user['user_id']]
                
                if status_filter:
                    query += " AND a.status = %s"
                    params.append(status_filter)
                
                query += " ORDER BY a.appointment_time DESC LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                appointments = cursor.fetchall()
                
                logger.info(f"Retrieved {len(appointments)} appointments for user {user['user_id']}")
                return appointments
                
    except Exception as e:
        logger.error(f"Error fetching appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve appointments"
        )

@router.get("/upcoming", response_model=List[AppointmentResponse])
async def get_upcoming_appointments(
    user: dict = Depends(verify_token),
    limit: int = Query(10, ge=1, le=50)
):
    """Get user's upcoming appointments (future, not cancelled)"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
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
                    WHERE a.patient_id = %s
                      AND a.appointment_time > NOW()
                      AND a.status NOT IN ('cancelled', 'no_show')
                    ORDER BY a.appointment_time ASC
                    LIMIT %s
                """, (user['user_id'], limit))
                
                appointments = cursor.fetchall()
                logger.info(f"Retrieved {len(appointments)} upcoming appointments")
                return appointments
                
    except Exception as e:
        logger.error(f"Error fetching upcoming appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve upcoming appointments"
        )

@router.get("/past", response_model=List[AppointmentResponse])
async def get_past_appointments(
    user: dict = Depends(verify_token),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """Get user's past appointments"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
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
                    WHERE a.patient_id = %s
                      AND (
                          a.appointment_time < NOW()
                          OR a.status IN ('cancelled', 'completed', 'no_show')
                      )
                    ORDER BY a.appointment_time DESC
                    LIMIT %s OFFSET %s
                """, (user['user_id'], limit, offset))
                
                appointments = cursor.fetchall()
                return appointments
                
    except Exception as e:
        logger.error(f"Error fetching past appointments: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve past appointments"
        )

@router.get("/stats", response_model=AppointmentStats)
async def get_appointment_stats(user: dict = Depends(verify_token)):
    """Get user's appointment statistics"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE appointment_time > NOW() AND status NOT IN ('cancelled', 'no_show')) as upcoming,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed,
                        COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled
                    FROM appointments
                    WHERE patient_id = %s
                """, (user['user_id'],))
                
                stats = cursor.fetchone()
                return {
                    "total_appointments": stats['total'],
                    "upcoming_appointments": stats['upcoming'],
                    "completed_appointments": stats['completed'],
                    "cancelled_appointments": stats['cancelled']
                }
                
    except Exception as e:
        logger.error(f"Error fetching appointment stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve appointment statistics"
        )

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    user: dict = Depends(verify_token)
):
    """Get specific appointment by ID"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
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
                    WHERE a.id = %s AND a.patient_id = %s
                """, (appointment_id, user['user_id']))
                
                appointment = cursor.fetchone()
                
                if not appointment:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Appointment {appointment_id} not found"
                    )
                
                return appointment
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching appointment {appointment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve appointment"
        )

# @router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    user: dict = Depends(verify_token)
):
    """
    Create a new appointment
    
    - **doctor_id**: ID of the doctor
    - **medical_field_id**: Medical specialty ID
    - **appointment_time**: Appointment date and time (ISO format)
    - **duration_minutes**: Duration (default: 30)
    - **reason_for_visit**: Optional reason for the visit
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Verify doctor exists and is available
                cursor.execute("""
                    SELECT id, is_available 
                    FROM doctors 
                    WHERE id = %s
                """, (appointment.doctor_id,))
                
                doctor = cursor.fetchone()
                if not doctor:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Doctor {appointment.doctor_id} not found"
                    )
                
                if not doctor['is_available']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Doctor is not currently available"
                    )
                
                # Check if time slot is available
                cursor.execute("""
                    SELECT id FROM appointments
                    WHERE doctor_id = %s
                      AND appointment_time = %s
                      AND status NOT IN ('cancelled', 'no_show')
                """, (appointment.doctor_id, appointment.appointment_time))
                
                if cursor.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="This time slot is already booked"
                    )
                
                # Check if patient already has an appointment at this time
                cursor.execute("""
                    SELECT id FROM appointments
                    WHERE patient_id = %s
                      AND appointment_time = %s
                      AND status NOT IN ('cancelled', 'no_show')
                """, (user['user_id'], appointment.appointment_time))
                
                if cursor.fetchone():
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="You already have an appointment at this time"
                    )
                
                # Create appointment
                cursor.execute("""
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
                """, (
                    user['user_id'],
                    appointment.doctor_id,
                    appointment.medical_field_id,
                    appointment.appointment_time,
                    appointment.duration_minutes,
                    appointment.reason_for_visit
                ))
                
                new_appointment = cursor.fetchone()
                
                # Get additional info
                cursor.execute("""
                    SELECT 
                        d.name as doctor_name,
                        d.specialization as doctor_specialization,
                        d.consultation_fee,
                        mf.medical_field_name
                    FROM doctors d
                    JOIN medical_fields mf ON d.medical_field_id = mf.id
                    WHERE d.id = %s
                """, (appointment.doctor_id,))
                
                info = cursor.fetchone()
                
                # Combine results
                result = {**new_appointment, **info}
                
                logger.info(f"Created appointment {result['id']} for user {user['user_id']}")
                return result
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating appointment: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create appointment"
        )

@router.patch("/{appointment_id}", response_model=AppointmentResponse)
async def update_appointment(
    appointment_id: int,
    update_data: AppointmentUpdate,
    user: dict = Depends(verify_token)
):
    """
    Update appointment (cancel, add notes, change status)
    
    - **status**: New status (scheduled, confirmed, cancelled, completed, no_show)
    - **notes**: Add notes to the appointment
    - **cancellation_reason**: Reason for cancellation (if status=cancelled)
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Check if appointment exists and belongs to user
                cursor.execute("""
                    SELECT * FROM appointments 
                    WHERE id = %s AND patient_id = %s
                """, (appointment_id, user['user_id']))
                
                existing = cursor.fetchone()
                
                if not existing:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Appointment {appointment_id} not found"
                    )
                
                # Check if appointment can be modified
                if existing['status'] in ['completed', 'no_show']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot modify completed or no-show appointments"
                    )
                
                # Build update query
                updates = []
                params = []
                
                if update_data.status:
                    # Don't allow patients to mark as completed or no_show
                    if update_data.status in ['completed', 'no_show']:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only staff can mark appointments as completed or no-show"
                        )
                    
                    updates.append("status = %s")
                    params.append(update_data.status)
                    
                    if update_data.status == 'cancelled':
                        updates.append("cancelled_at = NOW()")
                
                if update_data.notes:
                    updates.append("notes = %s")
                    params.append(update_data.notes)
                
                if update_data.cancellation_reason:
                    updates.append("cancellation_reason = %s")
                    params.append(update_data.cancellation_reason)
                
                if not updates:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No valid update fields provided"
                    )
                
                updates.append("updated_at = NOW()")
                params.append(appointment_id)
                
                # Execute update
                query = f"""
                    UPDATE appointments 
                    SET {', '.join(updates)}
                    WHERE id = %s
                    RETURNING *
                """
                
                cursor.execute(query, params)
                updated_appointment = cursor.fetchone()
                
                # Get additional info
                cursor.execute("""
                    SELECT 
                        d.name as doctor_name,
                        d.specialization as doctor_specialization,
                        d.consultation_fee,
                        mf.medical_field_name
                    FROM doctors d
                    JOIN medical_fields mf ON d.medical_field_id = mf.id
                    WHERE d.id = %s
                """, (updated_appointment['doctor_id'],))
                
                info = cursor.fetchone()
                result = {**updated_appointment, **info}
                
                logger.info(f"Updated appointment {appointment_id}")
                return result
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating appointment {appointment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update appointment"
        )

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_appointment(
    appointment_id: int,
    user: dict = Depends(verify_token)
):
    """
    Delete (cancel) an appointment
    
    Note: This actually sets status to 'cancelled' rather than deleting
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Check if appointment exists and can be cancelled
                cursor.execute("""
                    SELECT status, appointment_time 
                    FROM appointments 
                    WHERE id = %s AND patient_id = %s
                """, (appointment_id, user['user_id']))
                
                appointment = cursor.fetchone()
                
                if not appointment:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Appointment {appointment_id} not found"
                    )
                
                if appointment['status'] in ['completed', 'no_show']:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Cannot cancel completed or no-show appointments"
                    )
                
                if appointment['status'] == 'cancelled':
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Appointment is already cancelled"
                    )
                
                # Cancel appointment
                cursor.execute("""
                    UPDATE appointments 
                    SET status = 'cancelled', 
                        cancelled_at = NOW(),
                        updated_at = NOW()
                    WHERE id = %s
                """, (appointment_id,))
                
                logger.info(f"Cancelled appointment {appointment_id}")
                return None
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling appointment {appointment_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel appointment"
        )
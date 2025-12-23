from fastapi import APIRouter, HTTPException, status, Query
from typing import List, Optional
from app.schemas.doctor import DoctorResponse, DoctorDetailResponse, WorkingHoursResponse
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/doctors", tags=["Doctors"])

@router.get("/", response_model=List[DoctorResponse])
async def get_doctors(
    medical_field_id: Optional[int] = Query(None, description="Filter by medical field"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Minimum rating"),
    search: Optional[str] = Query(None, description="Search by name or specialization"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get all doctors with optional filters
    
    - **medical_field_id**: Filter by specialty
    - **min_rating**: Minimum doctor rating
    - **search**: Search in name and specialization
    - **limit**: Number of results (max 100)
    - **offset**: Pagination offset
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Build dynamic query
                query = """
                    SELECT 
                        d.id,
                        d.name,
                        d.medical_field_id,
                        mf.medical_field_name,
                        d.specialization,
                        d.years_of_experience,
                        d.rating,
                        d.total_reviews,
                        d.bio,
                        d.consultation_fee,
                        d.image_url,
                        d.is_available,
                        d.time_zone,
                        d.created_at
                    FROM doctors d
                    LEFT JOIN medical_fields mf ON d.medical_field_id = mf.id
                    WHERE d.is_available = TRUE
                """
                params = []
                
                if medical_field_id:
                    query += " AND d.medical_field_id = %s"
                    params.append(medical_field_id)
                
                if min_rating:
                    query += " AND d.rating >= %s"
                    params.append(min_rating)
                
                if search:
                    query += " AND (d.name ILIKE %s OR d.specialization ILIKE %s)"
                    search_term = f"%{search}%"
                    params.extend([search_term, search_term])
                
                query += " ORDER BY d.rating DESC, d.total_reviews DESC"
                query += " LIMIT %s OFFSET %s"
                params.extend([limit, offset])
                
                cursor.execute(query, params)
                doctors = cursor.fetchall()
                
                logger.info(f"Retrieved {len(doctors)} doctors")
                return doctors
                
    except Exception as e:
        logger.error(f"Error fetching doctors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve doctors"
        )

@router.get("/{doctor_id}", response_model=DoctorDetailResponse)
async def get_doctor(doctor_id: int):
    """Get detailed information about a specific doctor"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Get doctor info
                cursor.execute("""
                    SELECT 
                        d.*,
                        mf.medical_field_name
                    FROM doctors d
                    LEFT JOIN medical_fields mf ON d.medical_field_id = mf.id
                    WHERE d.id = %s
                """, (doctor_id,))
                doctor = cursor.fetchone()
                
                if not doctor:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Doctor with ID {doctor_id} not found"
                    )
                
                # Get working hours
                cursor.execute("""
                    SELECT *
                    FROM doctor_working_hours
                    WHERE doctor_id = %s AND is_active = TRUE
                    ORDER BY day_of_week
                """, (doctor_id,))
                working_hours = cursor.fetchall()
                
                doctor['working_hours'] = working_hours
                return doctor
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching doctor {doctor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve doctor information"
        )

@router.get("/{doctor_id}/available-slots")
async def get_available_slots(
    doctor_id: int,
    date: str = Query(..., description="Date in YYYY-MM-DD format")
):
    """Get available appointment slots for a doctor on a specific date"""
    try:
        from datetime import datetime, time, timedelta
        
        # Parse date
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
        
        # Check if date is in the future
        if target_date < datetime.now().date():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book appointments in the past"
            )
        
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Get doctor's working hours for this day
                day_of_week = target_date.weekday()  # 0=Monday, 6=Sunday
                # Convert to our format (0=Sunday)
                day_of_week = (day_of_week + 1) % 7
                
                cursor.execute("""
                    SELECT start_time, end_time, slot_duration_minutes
                    FROM doctor_working_hours
                    WHERE doctor_id = %s 
                      AND day_of_week = %s 
                      AND is_active = TRUE
                """, (doctor_id, day_of_week))
                
                working_hours = cursor.fetchone()
                
                if not working_hours:
                    return {
                        "doctor_id": doctor_id,
                        "date": date,
                        "available_slots": []
                    }
                
                # Generate time slots
                start_time = working_hours['start_time']
                end_time = working_hours['end_time']
                slot_duration = working_hours['slot_duration_minutes']
                
                # Get booked appointments for this date
                cursor.execute("""
                    SELECT appointment_time
                    FROM appointments
                    WHERE doctor_id = %s
                      AND DATE(appointment_time) = %s
                      AND status NOT IN ('cancelled', 'no_show')
                """, (doctor_id, target_date))
                
                booked_times = [row['appointment_time'] for row in cursor.fetchall()]
                
                # Generate available slots
                available_slots = []
                current_time = datetime.combine(target_date, start_time)
                end_datetime = datetime.combine(target_date, end_time)
                
                while current_time < end_datetime:
                    # Check if this slot is booked
                    if current_time not in booked_times:
                        # Check if slot is not in the past
                        if current_time > datetime.now():
                            available_slots.append({
                                "start_time": current_time.isoformat(),
                                "end_time": (current_time + timedelta(minutes=slot_duration)).isoformat(),
                                "available": True
                            })
                    
                    current_time += timedelta(minutes=slot_duration)
                
                return {
                    "doctor_id": doctor_id,
                    "date": date,
                    "available_slots": available_slots
                }
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching available slots for doctor {doctor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve available slots"
        )
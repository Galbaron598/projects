"""
Appointment Service - Business logic for appointment management
"""

from datetime import datetime, timedelta, time
from typing import List, Dict, Optional
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)


def check_appointment_conflicts(
    doctor_id: int,
    appointment_time: datetime,
    duration_minutes: int,
    exclude_appointment_id: Optional[int] = None
) -> bool:
    """
    Check if an appointment time conflicts with existing appointments
    
    Args:
        doctor_id: Doctor ID
        appointment_time: Proposed appointment time
        duration_minutes: Duration of appointment
        exclude_appointment_id: Appointment ID to exclude (for updates)
        
    Returns:
        True if there's a conflict, False if slot is available
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Calculate end time
                end_time = appointment_time + timedelta(minutes=duration_minutes)
                
                # Check for overlapping appointments
                query = """
                    SELECT COUNT(*) as conflict_count
                    FROM appointments
                    WHERE doctor_id = %s
                      AND status NOT IN ('cancelled', 'no_show')
                      AND (
                          -- New appointment starts during existing appointment
                          (appointment_time <= %s 
                           AND appointment_time + (duration_minutes || ' minutes')::INTERVAL > %s)
                          OR
                          -- New appointment ends during existing appointment
                          (appointment_time < %s
                           AND appointment_time + (duration_minutes || ' minutes')::INTERVAL >= %s)
                          OR
                          -- New appointment completely contains existing appointment
                          (appointment_time >= %s 
                           AND appointment_time + (duration_minutes || ' minutes')::INTERVAL <= %s)
                      )
                """
                params = [
                    doctor_id,
                    appointment_time, appointment_time,
                    end_time, end_time,
                    appointment_time, end_time
                ]
                
                # Exclude current appointment if updating
                if exclude_appointment_id:
                    query += " AND id != %s"
                    params.append(exclude_appointment_id)
                
                cursor.execute(query, params)
                result = cursor.fetchone()
                
                has_conflict = result['conflict_count'] > 0
                
                if has_conflict:
                    logger.info(f"Conflict found for doctor {doctor_id} at {appointment_time}")
                else:
                    logger.info(f"No conflict for doctor {doctor_id} at {appointment_time}")
                
                return has_conflict
                
    except Exception as e:
        logger.error(f"Error checking conflicts: {e}")
        raise


def get_available_time_slots(
    doctor_id: int,
    date: datetime.date,
    timezone: str = 'UTC'
) -> List[Dict]:
    """
    Get available time slots for a doctor on a specific date
    
    Args:
        doctor_id: Doctor ID
        date: Date to check
        timezone: Timezone for the slots
        
    Returns:
        List of available time slots with start and end times
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Get doctor's working hours for this day
                day_of_week = (date.weekday() + 1) % 7  # Convert to 0=Sunday format
                
                cursor.execute("""
                    SELECT start_time, end_time, slot_duration_minutes
                    FROM doctor_working_hours
                    WHERE doctor_id = %s 
                      AND day_of_week = %s 
                      AND is_active = TRUE
                """, (doctor_id, day_of_week))
                
                working_hours = cursor.fetchone()
                
                if not working_hours:
                    logger.info(f"Doctor {doctor_id} doesn't work on day {day_of_week}")
                    return []
                
                # Get all booked appointments for this date
                cursor.execute("""
                    SELECT appointment_time, duration_minutes
                    FROM appointments
                    WHERE doctor_id = %s
                      AND DATE(appointment_time AT TIME ZONE %s) = %s
                      AND status NOT IN ('cancelled', 'no_show')
                """, (doctor_id, timezone, date))
                
                booked_appointments = cursor.fetchall()
                booked_times = {
                    appt['appointment_time'].replace(tzinfo=None): appt['duration_minutes']
                    for appt in booked_appointments
                }
                
                # Generate all possible slots
                available_slots = []
                current_time = datetime.combine(date, working_hours['start_time'])
                end_time = datetime.combine(date, working_hours['end_time'])
                slot_duration = working_hours['slot_duration_minutes']
                
                while current_time + timedelta(minutes=slot_duration) <= end_time:
                    # Check if this slot is booked
                    is_booked = current_time in booked_times
                    
                    # Check if slot is in the past
                    is_past = current_time < datetime.now()
                    
                    if not is_booked and not is_past:
                        available_slots.append({
                            'start_time': current_time.isoformat(),
                            'end_time': (current_time + timedelta(minutes=slot_duration)).isoformat(),
                            'duration_minutes': slot_duration,
                            'available': True
                        })
                    
                    current_time += timedelta(minutes=slot_duration)
                
                logger.info(f"Found {len(available_slots)} available slots for doctor {doctor_id} on {date}")
                return available_slots
                
    except Exception as e:
        logger.error(f"Error getting available slots: {e}")
        raise


def calculate_appointment_end_time(
    start_time: datetime,
    duration_minutes: int
) -> datetime:
    """
    Calculate appointment end time
    
    Args:
        start_time: Appointment start time
        duration_minutes: Duration in minutes
        
    Returns:
        End time as datetime
    """
    return start_time + timedelta(minutes=duration_minutes)


def validate_appointment_time(
    appointment_time: datetime,
    duration_minutes: int = 30
) -> Dict[str, bool]:
    """
    Validate appointment time against business rules
    
    Args:
        appointment_time: Proposed appointment time
        duration_minutes: Duration of appointment
        
    Returns:
        Dict with validation results
    """
    validations = {
        'is_future': appointment_time > datetime.now(),
        'is_business_hours': 8 <= appointment_time.hour <= 18,
        'is_valid_duration': 15 <= duration_minutes <= 120,
        'is_not_weekend': appointment_time.weekday() < 5,  # Monday=0, Sunday=6
    }
    
    validations['is_valid'] = all(validations.values())
    
    return validations


def get_appointment_statistics(patient_id: int) -> Dict:
    """
    Get appointment statistics for a patient
    
    Args:
        patient_id: Patient ID
        
    Returns:
        Dict with statistics
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total,
                        COUNT(*) FILTER (WHERE status = 'completed') as completed,
                        COUNT(*) FILTER (WHERE status = 'cancelled') as cancelled,
                        COUNT(*) FILTER (WHERE status = 'no_show') as no_show,
                        COUNT(*) FILTER (
                            WHERE appointment_time > NOW() 
                            AND status NOT IN ('cancelled', 'no_show')
                        ) as upcoming
                    FROM appointments
                    WHERE patient_id = %s
                """, (patient_id,))
                
                stats = cursor.fetchone()
                
                return {
                    'total_appointments': stats['total'],
                    'completed_appointments': stats['completed'],
                    'cancelled_appointments': stats['cancelled'],
                    'no_show_appointments': stats['no_show'],
                    'upcoming_appointments': stats['upcoming'],
                    'completion_rate': (
                        stats['completed'] / stats['total'] * 100 
                        if stats['total'] > 0 else 0
                    )
                }
                
    except Exception as e:
        logger.error(f"Error getting appointment statistics: {e}")
        raise
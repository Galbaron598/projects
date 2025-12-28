"""
Availability Service - Manage doctor availability and schedules
"""

from datetime import datetime, time, timedelta
from typing import List, Dict, Optional
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)


def get_doctor_availability(
    doctor_id: int,
    start_date: datetime.date,
    end_date: datetime.date
) -> Dict:
    """
    Get doctor's availability for a date range
    
    Args:
        doctor_id: Doctor ID
        start_date: Start date
        end_date: End date
        
    Returns:
        Dict with availability information
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Get doctor info
                cursor.execute("""
                    SELECT id, name, is_available, time_zone
                    FROM doctors
                    WHERE id = %s
                """, (doctor_id,))
                
                doctor = cursor.fetchone()
                
                if not doctor:
                    raise ValueError(f"Doctor {doctor_id} not found")
                
                if not doctor['is_available']:
                    return {
                        'doctor_id': doctor_id,
                        'doctor_name': doctor['name'],
                        'is_available': False,
                        'message': 'Doctor is currently unavailable'
                    }
                
                # Get working hours
                cursor.execute("""
                    SELECT day_of_week, start_time, end_time, slot_duration_minutes
                    FROM doctor_working_hours
                    WHERE doctor_id = %s AND is_active = TRUE
                    ORDER BY day_of_week
                """, (doctor_id,))
                
                working_hours = cursor.fetchall()
                
                # Get blocked time slots
                cursor.execute("""
                    SELECT start_time, end_time, reason
                    FROM blocked_time_slots
                    WHERE doctor_id = %s
                      AND start_time BETWEEN %s AND %s
                    ORDER BY start_time
                """, (doctor_id, start_date, end_date))
                
                blocked_slots = cursor.fetchall()
                
                return {
                    'doctor_id': doctor_id,
                    'doctor_name': doctor['name'],
                    'is_available': True,
                    'time_zone': doctor['time_zone'],
                    'working_hours': [
                        {
                            'day': wh['day_of_week'],
                            'start': wh['start_time'].strftime('%H:%M'),
                            'end': wh['end_time'].strftime('%H:%M'),
                            'slot_duration': wh['slot_duration_minutes']
                        }
                        for wh in working_hours
                    ],
                    'blocked_slots': [
                        {
                            'start': bs['start_time'].isoformat(),
                            'end': bs['end_time'].isoformat(),
                            'reason': bs['reason']
                        }
                        for bs in blocked_slots
                    ] if blocked_slots else []
                }
                
    except Exception as e:
        logger.error(f"Error getting doctor availability: {e}")
        raise


def is_time_slot_available(
    doctor_id: int,
    slot_time: datetime,
    duration_minutes: int = 30
) -> bool:
    """
    Check if a specific time slot is available
    
    Args:
        doctor_id: Doctor ID
        slot_time: Proposed time slot
        duration_minutes: Duration of slot
        
    Returns:
        True if available, False otherwise
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Check if doctor is available
                cursor.execute("""
                    SELECT is_available FROM doctors WHERE id = %s
                """, (doctor_id,))
                
                doctor = cursor.fetchone()
                if not doctor or not doctor['is_available']:
                    return False
                
                # Check if within working hours
                day_of_week = (slot_time.weekday() + 1) % 7
                slot_time_only = slot_time.time()
                
                cursor.execute("""
                    SELECT start_time, end_time
                    FROM doctor_working_hours
                    WHERE doctor_id = %s
                      AND day_of_week = %s
                      AND is_active = TRUE
                      AND %s >= start_time
                      AND %s <= end_time
                """, (doctor_id, day_of_week, slot_time_only, slot_time_only))
                
                working_hours = cursor.fetchone()
                if not working_hours:
                    logger.info(f"Time {slot_time} is outside working hours")
                    return False
                
                # Check for conflicting appointments
                end_time = slot_time + timedelta(minutes=duration_minutes)
                
                cursor.execute("""
                    SELECT COUNT(*) as conflicts
                    FROM appointments
                    WHERE doctor_id = %s
                      AND status NOT IN ('cancelled', 'no_show')
                      AND (
                          (appointment_time < %s 
                           AND appointment_time + (duration_minutes || ' minutes')::INTERVAL > %s)
                          OR
                          (appointment_time < %s
                           AND appointment_time + (duration_minutes || ' minutes')::INTERVAL > %s)
                      )
                """, (doctor_id, end_time, slot_time, end_time, slot_time))
                
                result = cursor.fetchone()
                
                is_available = result['conflicts'] == 0
                
                logger.info(f"Slot {slot_time} for doctor {doctor_id}: {'available' if is_available else 'not available'}")
                return is_available
                
    except Exception as e:
        logger.error(f"Error checking slot availability: {e}")
        return False


def get_next_available_slot(
    doctor_id: int,
    start_from: datetime = None
) -> Optional[datetime]:
    """
    Find the next available slot for a doctor
    
    Args:
        doctor_id: Doctor ID
        start_from: Start searching from this time (default: now)
        
    Returns:
        Next available slot time or None if not found in next 30 days
    """
    if start_from is None:
        start_from = datetime.now()
    
    # Search for next 30 days
    for days_ahead in range(30):
        check_date = (start_from + timedelta(days=days_ahead)).date()
        day_of_week = (check_date.weekday() + 1) % 7
        
        try:
            with get_db() as conn:
                with conn.cursor() as cursor:
                    # Get working hours for this day
                    cursor.execute("""
                        SELECT start_time, end_time, slot_duration_minutes
                        FROM doctor_working_hours
                        WHERE doctor_id = %s
                          AND day_of_week = %s
                          AND is_active = TRUE
                    """, (doctor_id, day_of_week))
                    
                    working_hours = cursor.fetchone()
                    
                    if not working_hours:
                        continue
                    
                    # Generate time slots for this day
                    current_time = datetime.combine(check_date, working_hours['start_time'])
                    end_time = datetime.combine(check_date, working_hours['end_time'])
                    slot_duration = working_hours['slot_duration_minutes']
                    
                    while current_time + timedelta(minutes=slot_duration) <= end_time:
                        # Only check future times
                        if current_time > datetime.now():
                            if is_time_slot_available(doctor_id, current_time, slot_duration):
                                logger.info(f"Next available slot: {current_time}")
                                return current_time
                        
                        current_time += timedelta(minutes=slot_duration)
                        
        except Exception as e:
            logger.error(f"Error searching for available slot: {e}")
            continue
    
    logger.info(f"No available slots found for doctor {doctor_id} in next 30 days")
    return None


def get_busy_hours_summary(
    doctor_id: int,
    date: datetime.date
) -> Dict:
    """
    Get summary of busy vs available hours for a doctor on a specific date
    
    Args:
        doctor_id: Doctor ID
        date: Date to check
        
    Returns:
        Dict with busy/available hours summary
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                day_of_week = (date.weekday() + 1) % 7
                
                # Get total working hours
                cursor.execute("""
                    SELECT 
                        EXTRACT(EPOCH FROM (end_time - start_time)) / 3600 as working_hours
                    FROM doctor_working_hours
                    WHERE doctor_id = %s
                      AND day_of_week = %s
                      AND is_active = TRUE
                """, (doctor_id, day_of_week))
                
                working_hours_result = cursor.fetchone()
                
                if not working_hours_result:
                    return {
                        'working_hours': 0,
                        'booked_hours': 0,
                        'available_hours': 0,
                        'utilization_rate': 0
                    }
                
                total_working_hours = working_hours_result['working_hours']
                
                # Get booked hours
                cursor.execute("""
                    SELECT 
                        COALESCE(SUM(duration_minutes), 0) / 60.0 as booked_hours
                    FROM appointments
                    WHERE doctor_id = %s
                      AND DATE(appointment_time) = %s
                      AND status NOT IN ('cancelled', 'no_show')
                """, (doctor_id, date))
                
                booked_result = cursor.fetchone()
                booked_hours = booked_result['booked_hours']
                available_hours = max(0, total_working_hours - booked_hours)
                
                return {
                    'working_hours': round(total_working_hours, 2),
                    'booked_hours': round(booked_hours, 2),
                    'available_hours': round(available_hours, 2),
                    'utilization_rate': round(
                        (booked_hours / total_working_hours * 100) if total_working_hours > 0 else 0,
                        2
                    )
                }
                
    except Exception as e:
        logger.error(f"Error getting busy hours summary: {e}")
        raise
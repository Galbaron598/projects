
from datetime import datetime, timedelta, time as dt_time
from zoneinfo import ZoneInfo
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException


def day_of_week_sun0(dt: datetime) -> int:
    """
    Convert datetime to day-of-week where Sunday=0
    
    Python's weekday(): Monday=0, Tuesday=1, ..., Sunday=6
    We want: Sunday=0, Monday=1, Tuesday=2, ..., Saturday=6
    """
    python_weekday = dt.weekday()  # Mon=0, Sun=6
    return (python_weekday + 1) % 7  # Sun=0, Mon=1, ..., Sat=6


def ensure_tz(dt: datetime) -> datetime:
    """
    Ensure datetime has timezone info (convert to UTC if naive)
    
    Args:
        dt: datetime object (may be naive or aware)
        
    Returns:
        datetime with UTC timezone
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC"))
    else:
        # Already timezone-aware - convert to UTC
        return dt.astimezone(ZoneInfo("UTC"))


def intervals_overlap(start1: datetime, end1: datetime, start2: datetime, end2: datetime) -> bool:
    """
    Check if two time intervals overlap
    
    Two intervals overlap if:
    - interval1 starts before interval2 ends AND
    - interval2 starts before interval1 ends
    """
    # Ensure all datetimes are timezone-aware UTC
    start1 = ensure_tz(start1)
    end1 = ensure_tz(end1)
    start2 = ensure_tz(start2)
    end2 = ensure_tz(end2)
    
    # Check overlap condition
    return start1 < end2 and start2 < end1


def validate_within_working_hours(
    db: Session,
    doctor_id: int,
    appt_start_utc: datetime,
    duration_minutes: int,
    doctor_tz: ZoneInfo,
    enforce_slot_alignment: bool = False,
) -> None:
    """
    Validate that an appointment falls within doctor's working hours
    
    Args:
        db: Database session
        doctor_id: Doctor ID
        appt_start_utc: Appointment start time (UTC)
        duration_minutes: Duration of appointment
        doctor_tz: Doctor's timezone
        enforce_slot_alignment: Whether to enforce slot alignment (not used currently)
        
    Raises:
        HTTPException if not within working hours
    """
    from app.repository.doctors_repository import DoctorRepository
    
    repo = DoctorRepository()
    
    # Convert to doctor's local time
    appt_start_local = ensure_tz(appt_start_utc).astimezone(doctor_tz)
    appt_end_local = appt_start_local + timedelta(minutes=duration_minutes)
    
    # Get day of week
    day_of_week = day_of_week_sun0(appt_start_local)
    
    # Get working hours for this day
    working_hours = repo.get_working_hours_for_day(db, doctor_id, day_of_week)
    
    if not working_hours:
        raise HTTPException(
            status_code=400,
            detail=f"Doctor is not available on this day"
        )
    
    # Extract time components
    appt_start_time = appt_start_local.time()
    appt_end_time = appt_end_local.time()
    
    # Get working hours (these are time objects)
    work_start = working_hours['start_time']
    work_end = working_hours['end_time']
    
    # Check if appointment is within working hours
    if appt_start_time < work_start or appt_end_time > work_end:
        raise HTTPException(
            status_code=400,
            detail=f"Appointment must be between {work_start} and {work_end}"
        )


def check_overlapping_conflict(
    db: Session,
    doctor_id: int,
    appt_start_utc: datetime,
    duration_minutes: int,
    exclude_appointment_id: Optional[int] = None,
) -> bool:
    """
    Check if proposed appointment conflicts with existing appointments
    
    Args:
        db: Database session
        doctor_id: Doctor ID
        appt_start_utc: Proposed appointment start time (UTC)
        duration_minutes: Duration in minutes
        exclude_appointment_id: Appointment ID to exclude (for updates)
        
    Returns:
        True if there IS a conflict, False if no conflict
    """
    from app.repository.doctors_repository import DoctorRepository
    
    repo = DoctorRepository()
    
    # Get doctor's existing appointments
    existing_appointments = repo.get_doctor_appointments(db, doctor_id)
    
    # Calculate proposed appointment end time
    appt_start = ensure_tz(appt_start_utc)
    appt_end = appt_start + timedelta(minutes=duration_minutes)
    
    # Check each existing appointment for overlap
    for existing in existing_appointments:
        if exclude_appointment_id and existing.get('id') == exclude_appointment_id:
            continue
        
        existing_start = ensure_tz(existing['appointment_time'])
        existing_duration = int(existing.get('duration_minutes', 30))
        existing_end = existing_start + timedelta(minutes=existing_duration)
        
        # Check for overlap
        if intervals_overlap(appt_start, appt_end, existing_start, existing_end):
            return True  # Conflict found
    
    return False  # No conflict


def time_slot_is_available(
    slot_start: datetime,
    slot_end: datetime,
    existing_appointments: list
) -> bool:
    """
    Check if a time slot is available (not conflicting with existing appointments)
    
    Args:
        slot_start: Start time of the slot to check
        slot_end: End time of the slot to check
        existing_appointments: List of dicts with 'appointment_time' and 'duration_minutes'
        
    Returns:
        True if slot is available, False if there's a conflict
    """
    slot_start = ensure_tz(slot_start)
    slot_end = ensure_tz(slot_end)
    
    for appt in existing_appointments:
        appt_start = ensure_tz(appt['appointment_time'])
        appt_duration = int(appt.get('duration_minutes', 30))
        appt_end = appt_start + timedelta(minutes=appt_duration)
        
        if intervals_overlap(slot_start, slot_end, appt_start, appt_end):
            return False
    
    return True


def validate_no_conflicts(
    appointment_time: datetime,
    duration_minutes: int,
    existing_appointments: list
) -> bool:
    """
    Validate that proposed appointment doesn't conflict with existing ones
    
    Args:
        appointment_time: Proposed appointment start time
        duration_minutes: Duration of appointment
        existing_appointments: List of existing appointments
        
    Returns:
        True if no conflicts, False if there's a conflict
    """
    appt_start = ensure_tz(appointment_time)
    appt_end = appt_start + timedelta(minutes=duration_minutes)
    
    for existing in existing_appointments:
        existing_start = ensure_tz(existing['appointment_time'])
        existing_duration = int(existing.get('duration_minutes', 30))
        existing_end = existing_start + timedelta(minutes=existing_duration)
        
        if intervals_overlap(appt_start, appt_end, existing_start, existing_end):
            return False  # Conflict found
    
    return True  # No conflict


def get_day_boundaries(date, tz: ZoneInfo) -> tuple:
    """
    Get start and end datetime for a given date in a timezone
    
    Args:
        date: Date to get boundaries for (date or datetime)
        tz: Timezone
        
    Returns:
        Tuple of (start_of_day, end_of_day) in UTC
    """
    # Handle both date and datetime objects
    if isinstance(date, datetime):
        date = date.date()
    
    start_local = datetime.combine(date, dt_time(0, 0), tzinfo=tz)
    end_local = datetime.combine(date, dt_time(23, 59, 59), tzinfo=tz)
    
    start_utc = start_local.astimezone(ZoneInfo("UTC"))
    end_utc = end_local.astimezone(ZoneInfo("UTC"))
    
    return start_utc, end_utc
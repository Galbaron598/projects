from datetime import datetime, timedelta, time as dt_time
from typing import Optional
from zoneinfo import ZoneInfo
from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from fastapi import HTTPException

from app.models import DoctorWorkingHours, Appointment


def day_of_week_sun0(local_dt: datetime) -> int:
    """Convert Python weekday Mon=0..Sun=6 -> schema Sun=0..Sat=6."""
    return (local_dt.weekday() + 1) % 7

def ensure_tz(dt: datetime) -> datetime:
    """
    Ensure appointment_time is timezone-aware.
    assume UTC (consistent with frontend sending toISOString()).
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt


def intervals_overlap(a_start: datetime, a_end: datetime, b_start: datetime, b_end: datetime) -> bool:
    """Check if two time intervals overlap"""
    return not (a_end <= b_start or a_start >= b_end)


def validate_within_working_hours(
    db: Session,
    doctor_id: int,
    appt_time_utc: datetime,
    duration_minutes: int,
    doctor_tz: ZoneInfo,
    enforce_slot_alignment: bool = True,
) -> None:
    """
    Validates:
      1) appointment is in the future
      2) falls inside doctor working hours (local day + local times)
    """
    now_utc = datetime.now(ZoneInfo("UTC"))
    if appt_time_utc <= now_utc:
        raise HTTPException(status_code=400, detail="Cannot book appointments in the past")

    appt_local = appt_time_utc.astimezone(doctor_tz)
    dow = day_of_week_sun0(appt_local)

    # Get working hours using SQLAlchemy
    stmt = (
        select(
            DoctorWorkingHours.start_time,
            DoctorWorkingHours.end_time,
            DoctorWorkingHours.slot_duration_minutes,
        )
        .where(
            and_(
                DoctorWorkingHours.doctor_id == doctor_id,
                DoctorWorkingHours.day_of_week == dow,
                DoctorWorkingHours.is_active == True,
            )
        )
    )

    result = db.execute(stmt).first()
    if not result:
        raise HTTPException(status_code=400, detail="Doctor does not work on this day")

    # Convert result to dictionary-like access
    start_t: dt_time = result[0]  # start_time
    end_t: dt_time = result[1]    # end_time
    slot_minutes = int(result[2] or 30)  # slot_duration_minutes

    work_start_local = datetime.combine(appt_local.date(), start_t, tzinfo=doctor_tz)
    work_end_local = datetime.combine(appt_local.date(), end_t, tzinfo=doctor_tz)

    appt_end_local = appt_local + timedelta(minutes=duration_minutes)

    if appt_local < work_start_local or appt_end_local > work_end_local:
        raise HTTPException(status_code=400, detail="Appointment time is outside doctor working hours")

    if enforce_slot_alignment:
        delta_minutes = int((appt_local - work_start_local).total_seconds() // 60)
        if delta_minutes % slot_minutes != 0:
            raise HTTPException(
                status_code=400,
                detail="Appointment time is not aligned to the doctor's slot duration",
            )


def check_overlapping_conflict(
    db: Session,
    *,
    doctor_id: int,
    appt_start_utc: datetime,
    duration_minutes: int,
    exclude_appointment_id: Optional[int] = None,
) -> bool:
    """
    Overlap check (safe for variable duration):
    existing_start < new_end AND existing_end > new_start
    """
    appt_end_utc = appt_start_utc + timedelta(minutes=duration_minutes)

    # Build SQLAlchemy query
    stmt = (
        select(
            Appointment.id,
            Appointment.appointment_time,
            Appointment.duration_minutes,
        )
        .where(
            and_(
                Appointment.doctor_id == doctor_id,
                Appointment.status.in_(["scheduled", "confirmed"]),
            )
        )
    )

    if exclude_appointment_id is not None:
        stmt = stmt.where(Appointment.id != exclude_appointment_id)

    results = db.execute(stmt).all()

    for row in results:
        existing_start = ensure_tz(row[1])  # appointment_time
        existing_end = existing_start + timedelta(minutes=int(row[2] or 30))  # duration_minutes
        
        if intervals_overlap(existing_start, existing_end, appt_start_utc, appt_end_utc):
            return True

    return False
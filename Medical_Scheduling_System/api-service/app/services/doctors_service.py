from datetime import datetime, timedelta, time as dt_time
from typing import Dict, Any, List
from zoneinfo import ZoneInfo
from fastapi import HTTPException
from sqlalchemy.orm import Session
import logging

from app.repository.doctors_repository import DoctorRepository
from app.services.appointment_rules import (
    day_of_week_sun0,
    ensure_tz,
    intervals_overlap,
)

logger = logging.getLogger(__name__)

class DoctorService:
    """Business logic layer for doctors"""

    def __init__(self):
        self.repo = DoctorRepository()

    def get_doctor_with_details(self, db: Session, doctor_id: int) -> Dict[str, Any]:
        """Get doctor with working hours"""
        doctor = self.repo.get_doctor_by_id(db, doctor_id)
        if not doctor:
            raise HTTPException(
                status_code=404, detail=f"Doctor with ID {doctor_id} not found"
            )

        working_hours = self.repo.get_doctor_working_hours(db, doctor_id)
        doctor["working_hours"] = working_hours
        return doctor

    def validate_date_format(self, date_str: str) -> datetime:
        """Validate and parse date string"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400, detail="Invalid date format. Use YYYY-MM-DD"
            )

    def validate_doctor_availability(
        self, db: Session, doctor_id: int
    ) -> Dict[str, Any]:
        """Check if doctor exists and is available"""
        doctor = self.repo.get_doctor_basic_info(db, doctor_id)
        if not doctor:
            raise HTTPException(
                status_code=404, detail=f"Doctor {doctor_id} not found"
            )
        return doctor

    def validate_date_not_past(
        self, target_date: datetime, doctor_tz: ZoneInfo
    ) -> None:
        """Ensure date is not in the past (in doctor's timezone)"""
        now_local = datetime.now(doctor_tz)
        if target_date < now_local.date():
            raise HTTPException(
                status_code=400, detail="Cannot book appointments in the past"
            )

    def get_working_hours_for_date(
        self, db: Session, doctor_id: int, target_date: datetime, doctor_tz: ZoneInfo
    ) -> Dict[str, Any]:
        """Get working hours for the specific date"""
        local_day_dt = datetime.combine(
            target_date, dt_time(12, 0), tzinfo=doctor_tz
        )
        day_of_week = day_of_week_sun0(local_day_dt)

        working_hours = self.repo.get_working_hours_for_day(
            db, doctor_id, day_of_week
        )
        if not working_hours:
            return None

        return {
            "start_time": working_hours["start_time"],
            "end_time": working_hours["end_time"],
            "slot_duration_minutes": int(
                working_hours["slot_duration_minutes"] or 30
            ),
        }

    def get_existing_appointments_as_intervals(
        self, db: Session, doctor_id: int
    ) -> List[tuple]:
        """Get all existing appointments as UTC time intervals"""
        appointments = self.repo.get_doctor_appointments(db, doctor_id)

        intervals = []
        for appt in appointments:
            start_utc = ensure_tz(appt["appointment_time"])
            end_utc = start_utc + timedelta(
                minutes=int(appt["duration_minutes"] or 30)
            )
            intervals.append((start_utc, end_utc))

        return intervals

    def generate_available_slots(
        self,
        target_date: datetime,
        working_hours: Dict[str, Any],
        existing_intervals: List[tuple],
        doctor_tz: ZoneInfo,
    ) -> List[Dict[str, Any]]:
        """Generate available time slots"""
        start_time = working_hours["start_time"]
        end_time = working_hours["end_time"]
        slot_minutes = working_hours["slot_duration_minutes"]

        work_start_local = datetime.combine(
            target_date, start_time, tzinfo=doctor_tz
        )
        work_end_local = datetime.combine(target_date, end_time, tzinfo=doctor_tz)

        now_local = datetime.now(doctor_tz)
        available_slots = []
        current_local = work_start_local

        while current_local + timedelta(minutes=slot_minutes) <= work_end_local:
            # Only show future slots
            if current_local > now_local:
                slot_start_utc = current_local.astimezone(ZoneInfo("UTC"))
                slot_end_utc = (
                    current_local + timedelta(minutes=slot_minutes)
                ).astimezone(ZoneInfo("UTC"))

                # Check for conflicts
                is_conflict = any(
                    intervals_overlap(es, ee, slot_start_utc, slot_end_utc)
                    for (es, ee) in existing_intervals
                )

                if not is_conflict:
                    available_slots.append(
                        {
                            "start_time": slot_start_utc.isoformat(),
                            "end_time": slot_end_utc.isoformat(),
                            "available": True,
                        }
                    )

            current_local += timedelta(minutes=slot_minutes)

        return available_slots

    def get_available_slots(
        self, db: Session, doctor_id: int, date_str: str
    ) -> Dict[str, Any]:
        """Get available slots for a doctor on a specific date"""
        # Validate date format
        target_date = self.validate_date_format(date_str)

        # Validate doctor
        doctor = self.validate_doctor_availability(db, doctor_id)
        if not doctor["is_available"]:
            return {
                "doctor_id": doctor_id,
                "date": date_str,
                "available_slots": [],
            }

        # Get doctor timezone
        doctor_tz = ZoneInfo(doctor["time_zone"] or "Asia/Jerusalem")

        # Validate date is not in past
        self.validate_date_not_past(target_date, doctor_tz)

        # Get working hours for this date
        working_hours = self.get_working_hours_for_date(
            db, doctor_id, target_date, doctor_tz
        )
        if not working_hours:
            return {
                "doctor_id": doctor_id,
                "date": date_str,
                "available_slots": [],
            }

        # Get existing appointments
        existing_intervals = self.get_existing_appointments_as_intervals(
            db, doctor_id
        )

        # Generate available slots
        available_slots = self.generate_available_slots(
            target_date, working_hours, existing_intervals, doctor_tz
        )

        return {
            "doctor_id": doctor_id,
            "date": date_str,
            "available_slots": available_slots,
        }
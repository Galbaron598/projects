from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from zoneinfo import ZoneInfo
from fastapi import HTTPException
import logging

from appointment_repository import AppointmentRepository
from appointment_rules import (
    ensure_tz,
    validate_within_working_hours,
    check_overlapping_conflict,
    intervals_overlap,
)

logger = logging.getLogger(__name__)


class AppointmentService:
    """Business logic layer for appointments"""

    def __init__(self):
        self.repo = AppointmentRepository()

    def validate_doctor_availability(self, cursor, doctor_id: int) -> Dict[str, Any]:
        """Validate doctor exists and is available"""
        doctor = self.repo.get_doctor_info(cursor, doctor_id)
        if not doctor:
            raise HTTPException(
                status_code=404, detail=f"Doctor {doctor_id} not found"
            )
        if not doctor["is_available"]:
            raise HTTPException(
                status_code=400, detail="Doctor is not currently available"
            )
        return doctor

    def validate_appointment_modifiable(self, appointment: Dict[str, Any]) -> None:
        """Check if appointment can be modified"""
        if appointment["status"] in ["completed", "no_show"]:
            raise HTTPException(
                status_code=400,
                detail="Cannot modify completed or no-show appointments",
            )

    def check_doctor_time_slot(
        self,
        cursor,
        doctor_id: int,
        appointment_time: datetime,
        duration_minutes: int,
        doctor_tz: ZoneInfo,
        exclude_appointment_id: Optional[int] = None,
    ) -> None:
        """Validate time slot against doctor's working hours and existing appointments"""
        appt_start_utc = ensure_tz(appointment_time)

        # Check working hours
        validate_within_working_hours(
            cursor,
            doctor_id,
            appt_start_utc,
            duration_minutes,
            doctor_tz,
            enforce_slot_alignment=True,
        )

        # Check overlapping appointments
        if check_overlapping_conflict(
            cursor,
            doctor_id=doctor_id,
            appt_start_utc=appt_start_utc,
            duration_minutes=duration_minutes,
            exclude_appointment_id=exclude_appointment_id,
        ):
            raise HTTPException(
                status_code=409, detail="This time slot is already booked"
            )

    def check_patient_conflicts(
        self,
        cursor,
        patient_id: int,
        appointment_time: datetime,
        duration_minutes: int,
    ) -> None:
        """Check if patient has conflicting appointments"""
        appt_start_utc = ensure_tz(appointment_time)
        appt_end_utc = appt_start_utc + timedelta(minutes=duration_minutes)

        patient_appointments = self.repo.get_patient_appointments(
            cursor, patient_id, statuses=["scheduled", "confirmed"]
        )

        for existing in patient_appointments:
            existing_start = ensure_tz(existing["appointment_time"])
            existing_end = existing_start + timedelta(
                minutes=int(existing["duration_minutes"] or 30)
            )

            if intervals_overlap(
                existing_start, existing_end, appt_start_utc, appt_end_utc
            ):
                raise HTTPException(
                    status_code=409,
                    detail="You already have an appointment at this time",
                )

    def create_appointment(
        self,
        cursor,
        patient_id: int,
        doctor_id: int,
        medical_field_id: int,
        appointment_time: datetime,
        duration_minutes: Optional[int],
        reason_for_visit: Optional[str],
    ) -> Dict[str, Any]:
        """Create a new appointment with all validations"""
        # Validate doctor
        doctor = self.validate_doctor_availability(cursor, doctor_id)
        doctor_tz = ZoneInfo(doctor["time_zone"] or "Asia/Jerusalem")

        duration = int(duration_minutes or 30)
        appt_start_utc = ensure_tz(appointment_time)

        # Validate time slot
        self.check_doctor_time_slot(
            cursor, doctor_id, appt_start_utc, duration, doctor_tz
        )

        # Check patient conflicts
        self.check_patient_conflicts(cursor, patient_id, appt_start_utc, duration)

        # Create appointment
        new_appointment = self.repo.create_appointment(
            cursor,
            patient_id,
            doctor_id,
            medical_field_id,
            appt_start_utc,
            duration,
            reason_for_visit,
        )

        # Enrich with doctor details
        doctor_details = self.repo.get_doctor_details(cursor, doctor_id)
        return {**new_appointment, **doctor_details}

    def update_appointment(
        self,
        cursor,
        appointment_id: int,
        appointment_time: Optional[datetime] = None,
        status: Optional[str] = None,
        notes: Optional[str] = None,
        cancellation_reason: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update an appointment with validations"""
        # Fetch existing appointment
        existing = self.repo.get_appointment_simple(cursor, appointment_id)
        if not existing:
            raise HTTPException(
                status_code=404, detail=f"Appointment {appointment_id} not found"
            )

        # Validate modifiable
        self.validate_appointment_modifiable(existing)

        updates = {}

        # Handle rescheduling
        if appointment_time is not None:
            doctor = self.repo.get_doctor_info(cursor, existing["doctor_id"])
            doctor_tz = ZoneInfo((doctor and doctor["time_zone"]) or "Asia/Jerusalem")

            new_start_utc = ensure_tz(appointment_time)
            duration = int(existing["duration_minutes"] or 30)

            self.check_doctor_time_slot(
                cursor,
                existing["doctor_id"],
                new_start_utc,
                duration,
                doctor_tz,
                exclude_appointment_id=appointment_id,
            )

            updates["appointment_time"] = new_start_utc

        # Handle status change
        if status:
            if status in ["completed", "no_show"]:
                raise HTTPException(
                    status_code=403,
                    detail="Only staff can mark appointments as completed or no-show",
                )
            updates["status"] = status
            if status == "cancelled":
                updates["cancelled_at"] = "NOW()"

        # Handle notes and cancellation reason
        if notes is not None:
            updates["notes"] = notes
        if cancellation_reason is not None:
            updates["cancellation_reason"] = cancellation_reason

        if not updates:
            raise HTTPException(
                status_code=400, detail="No valid update fields provided"
            )

        # Perform update
        updated_appointment = self.repo.update_appointment(
            cursor, appointment_id, updates
        )

        # Enrich with doctor details
        doctor_details = self.repo.get_doctor_details(
            cursor, updated_appointment["doctor_id"]
        )
        return {**updated_appointment, **doctor_details}

    def cancel_appointment(self, cursor, appointment_id: int) -> None:
        """Cancel an appointment with validations"""
        appointment = self.repo.get_appointment_simple(cursor, appointment_id)
        if not appointment:
            raise HTTPException(
                status_code=404, detail=f"Appointment {appointment_id} not found"
            )

        if appointment["status"] in ["completed", "no_show"]:
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel completed or no-show appointments",
            )
        if appointment["status"] == "cancelled":
            raise HTTPException(
                status_code=400, detail="Appointment is already cancelled"
            )

        self.repo.cancel_appointment(cursor, appointment_id)
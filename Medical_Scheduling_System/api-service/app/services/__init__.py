"""
Business logic services for the API
"""

from .appointment_service import (
    check_appointment_conflicts,
    get_available_time_slots,
    calculate_appointment_end_time
)
from .availability_service import (
    get_doctor_availability,
    is_time_slot_available
)

__all__ = [
    'check_appointment_conflicts',
    'get_available_time_slots',
    'calculate_appointment_end_time',
    'get_doctor_availability',
    'is_time_slot_available',
]
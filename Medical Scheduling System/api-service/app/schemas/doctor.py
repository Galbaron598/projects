from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, time

class DoctorBase(BaseModel):
    name: str
    medical_field_id: int
    specialization: Optional[str] = None
    years_of_experience: Optional[int] = None
    bio: Optional[str] = None
    consultation_fee: Optional[Decimal] = None

class DoctorResponse(BaseModel):
    id: int
    name: str
    medical_field_id: int
    medical_field_name: Optional[str] = None
    specialization: Optional[str]
    years_of_experience: Optional[int]
    rating: Optional[Decimal]
    total_reviews: Optional[int]
    bio: Optional[str]
    consultation_fee: Optional[Decimal]
    image_url: Optional[str]
    is_available: bool
    time_zone: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DoctorDetailResponse(DoctorResponse):
    """Detailed doctor info including working hours"""
    working_hours: Optional[List[dict]] = None

class WorkingHoursResponse(BaseModel):
    id: int
    doctor_id: int
    day_of_week: int
    start_time: time
    end_time: time
    slot_duration_minutes: int
    is_active: bool
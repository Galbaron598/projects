from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time

class DoctorBase(BaseModel):
    name: str
    medical_field_id: int
    specialization: Optional[str] = None
    years_of_experience: Optional[int] = None
    bio: Optional[str] = None
    consultation_fee: Optional[float] = None

class DoctorResponse(BaseModel):
    id: int
    name: str
    medical_field_id: int
    medical_field_name: Optional[str] = None
    specialization: Optional[str] = None
    years_of_experience: Optional[int] = None
    rating: Optional[float] = None
    total_reviews: Optional[int] = None
    bio: Optional[str] = None
    consultation_fee: Optional[float] = None
    image_url: Optional[str] = None
    is_available: bool = True
    time_zone: str = "Asia/Jerusalem"
    created_at: Optional[datetime] = None
    
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
    
    class Config:
        from_attributes = True
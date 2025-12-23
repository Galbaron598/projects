
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from decimal import Decimal

class AppointmentCreate(BaseModel):
    doctor_id: int = Field(..., gt=0)
    medical_field_id: int = Field(..., gt=0)
    appointment_time: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    reason_for_visit: Optional[str] = Field(None, max_length=500)
    
    @validator('appointment_time')
    def validate_future_time(cls, v):
        if v < datetime.utcnow():
            raise ValueError('Appointment time must be in the future')
        return v

class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    medical_field_id: int
    appointment_time: datetime
    duration_minutes: int
    status: str
    reason_for_visit: Optional[str]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    # Joined fields
    doctor_name: Optional[str] = None
    doctor_specialization: Optional[str] = None
    medical_field_name: Optional[str] = None
    consultation_fee: Optional[Decimal] = None
    
    class Config:
        from_attributes = True

class AppointmentUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern='^(scheduled|confirmed|cancelled|completed|no_show)$')
    notes: Optional[str] = Field(None, max_length=1000)
    cancellation_reason: Optional[str] = Field(None, max_length=500)

class AppointmentStats(BaseModel):
    total_appointments: int
    upcoming_appointments: int
    completed_appointments: int
    cancelled_appointments: int

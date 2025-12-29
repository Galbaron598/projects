
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime, timezone
from decimal import Decimal

class AppointmentCreate(BaseModel):
    patient_id: int = Field(..., gt=0)
    doctor_id: int = Field(..., gt=0)
    medical_field_id: int = Field(..., gt=0)
    appointment_time: datetime
    duration_minutes: int = Field(default=30, ge=15, le=120)
    reason_for_visit: Optional[str] = Field(None, max_length=500)
    
    @field_validator("appointment_time")
    @classmethod
    def validate_future_time(cls, v):
        now = datetime.now(timezone.utc)
        # Ensure v is aware; if naive, assume UTC
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        if v < datetime.now(timezone.utc):
            raise ValueError("appointment_time must be in the future")
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
    cancellation_reason: Optional[str] = None
    cancelled_at: Optional[datetime] = None
    
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
    appointment_time: Optional[datetime] = None

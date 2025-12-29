from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, date

class PatientResponse(BaseModel):
    id: int
    phone_number: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[Literal["male", "female", "other"]] = None
    time_zone: str
    emergency_contact: Optional[str] = None
    address: Optional[str] = None
    created_at: datetime
    is_active: bool


    class Config:
        from_attributes = True


class PatientUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern="^(male|female|other)$")
    time_zone: Optional[str] = None
    emergency_contact: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)


class PatientCreate(BaseModel):
    phone_number: str = Field(..., min_length=7, max_length=20)

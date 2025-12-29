from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date

class PatientResponse(BaseModel):
    id: int
    phone_number: str
    full_name: Optional[str]
    email: Optional[str]
    date_of_birth: Optional[date]
    gender: Optional[str]
    time_zone: str
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class PatientUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = Field(None, max_length=100)
    date_of_birth: Optional[date] = None
    gender: Optional[str] = Field(None, pattern='^(male|female|other)$')
    time_zone: Optional[str] = None
    
class PatientCreate(BaseModel):
    phone_number: str = Field(..., min_length=7, max_length=20)

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MedicalFieldBase(BaseModel):
    medical_field_name: str
    description: Optional[str] = None
    # icon: Optional[str] = None

class MedicalFieldResponse(BaseModel):
    id: int
    medical_field_name: str
    description: Optional[str]
    # icon: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

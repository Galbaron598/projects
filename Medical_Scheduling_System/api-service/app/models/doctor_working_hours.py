from sqlalchemy import Column, Integer, Time, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class DoctorWorkingHours(Base):
    """Doctor working hours model"""
    
    __tablename__ = "doctor_working_hours"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False, index=True)
    
    day_of_week = Column(Integer, nullable=False)  # 0=Sunday, 1=Monday, ..., 6=Saturday
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    
    slot_duration_minutes = Column(Integer, nullable=False, server_default="30")
    is_active = Column(Boolean, nullable=False, server_default="true")

    # Relationships
    doctor = relationship("Doctor", back_populates="working_hours")
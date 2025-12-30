from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)

    patient_id = Column(Integer, nullable=False, index=True)

    doctor_id = Column(Integer, ForeignKey("doctors.id"), nullable=False, index=True)
    medical_field_id = Column(Integer, ForeignKey("medical_fields.id"), nullable=False, index=True)

    appointment_time = Column(DateTime(timezone=True), nullable=False, index=True)

    duration_minutes = Column(Integer, nullable=False, server_default="30")

    status = Column(String(32), nullable=False, server_default="scheduled", index=True)

    reason_for_visit = Column(String(500), nullable=True)
    notes = Column(Text, nullable=True)

    cancellation_reason = Column(String(500), nullable=True)
    cancelled_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())

    # Relationships
    doctor = relationship("Doctor", back_populates="appointments", lazy="joined")
    medical_field = relationship("MedicalField", lazy="joined")

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class MedicalField(Base):
    __tablename__ = "medical_fields"

    id = Column(Integer, primary_key=True, index=True)

    medical_field_name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    icon = Column(String(255), nullable=True)

    is_active = Column(Boolean, nullable=False, server_default="true")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Optional relationship
    doctors = relationship("Doctor", back_populates="medical_field", lazy="selectin")

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False, index=True)
    specialization = Column(String(255), nullable=True)

    medical_field_id = Column(
        Integer,
        ForeignKey("medical_fields.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    years_of_experience = Column(Integer, nullable=True)
    rating = Column(Numeric(2, 1), nullable=True)  # e.g. 4.5
    total_reviews = Column(Integer, nullable=True)
    bio = Column(Text, nullable=True)

    consultation_fee = Column(Numeric(10, 2), nullable=True)

    image_url = Column(String(1024), nullable=True)

    is_available = Column(Boolean, nullable=False, server_default="true")

    # timezone string like "UTC", "Asia/Jerusalem"
    time_zone = Column(String(64), nullable=False, server_default="UTC")

    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


    medical_field = relationship("MedicalField", back_populates="doctors", lazy="joined",)

    appointments = relationship("Appointment", back_populates="doctor", lazy="selectin",cascade="all, delete-orphan",)

    working_hours = relationship("DoctorWorkingHours", back_populates="doctor", lazy="selectin", cascade="all, delete-orphan",)

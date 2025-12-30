from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Boolean,
    CheckConstraint,
    text,
)
from app.core.database import Base

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)

    phone_number = Column(String(20), unique=True, nullable=False, index=True)

    full_name = Column(String(100), nullable=True)
    email = Column(String(100), nullable=True)

    date_of_birth = Column(Date, nullable=True)

    gender = Column(
        String(10),
        CheckConstraint(
            "gender IN ('male', 'female', 'other')",
            name="patients_gender_check",
        ),
        nullable=True,
    )

    time_zone = Column(
        String(50),
        nullable=False,
        server_default=text("'Asia/Jerusalem'"),
    )

    emergency_contact = Column(String(20), nullable=True)
    address = Column(String(500), nullable=True)

    is_active = Column(Boolean, nullable=False, server_default=text("true"))

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    def __repr__(self) -> str:
        return f"<Patient id={self.id} phone={self.phone_number}>"

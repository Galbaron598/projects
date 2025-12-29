from typing import Dict, Any
from fastapi import HTTPException, status
import logging

from app.services.patients_repository import PatientRepository
from app.schemas.patient import PatientUpdate

logger = logging.getLogger(__name__)


class PatientService:
    """Business logic layer for patients"""

    def __init__(self):
        self.repo = PatientRepository()

    def get_patient_profile(self, cursor, patient_id: int) -> Dict[str, Any]:
        """Get patient profile with validation"""
        patient = self.repo.get_patient_by_id(cursor, patient_id)

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found",
            )

        logger.info(f"Retrieved profile for patient {patient_id}")
        return patient

    def update_patient_profile(
        self, cursor, patient_id: int, update_data: PatientUpdate
    ) -> Dict[str, Any]:
        """Update patient profile with validation"""
        # Check if patient exists
        existing = self.repo.get_patient_by_id(cursor, patient_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found",
            )

        # Build updates dictionary
        updates = {}

        if update_data.full_name is not None:
            updates["full_name"] = update_data.full_name

        if update_data.email is not None:
            updates["email"] = update_data.email

        if update_data.date_of_birth is not None:
            updates["date_of_birth"] = update_data.date_of_birth

        if update_data.gender is not None:
            updates["gender"] = update_data.gender

        if update_data.time_zone is not None:
            updates["time_zone"] = update_data.time_zone

        if update_data.emergency_contact is not None:
            updates["emergency_contact"] = update_data.emergency_contact

        if update_data.address is not None:
            updates["address"] = update_data.address

        if not updates:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid update fields provided",
            )

        # Perform update
        updated_patient = self.repo.update_patient(cursor, patient_id, updates)

        if not updated_patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Patient profile not found",
            )

        logger.info(f"Updated profile for patient {patient_id}")
        return updated_patient

    def create_or_get_patient(self, cursor, phone_number: str) -> Dict[str, Any]:
        """Create new patient or return existing one"""
        # Check if patient already exists
        existing_patient = self.repo.check_patient_exists(cursor, phone_number)

        if existing_patient:
            # Return full patient data
            return self.repo.get_patient_by_phone(cursor, phone_number)

        # Create new patient
        patient = self.repo.create_patient(cursor, phone_number)

        if not patient:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create patient",
            )

        logger.info(f"Created new patient {patient['id']} with phone {phone_number}")
        return patient

    def check_patient_exists(self, cursor, phone_number: str) -> Dict[str, Any]:
        """Check if patient exists by phone number"""
        result = self.repo.check_patient_exists(cursor, phone_number)
        return {
            "exists": bool(result),
            "id": result["id"] if result else None
        }
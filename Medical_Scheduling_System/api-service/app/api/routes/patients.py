from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.patient import PatientResponse, PatientUpdate
from app.middleware.auth_middleware import verify_token
from app.core.database import get_db
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/patients", tags=["Patients"])

@router.get("/profile", response_model=PatientResponse)
async def get_current_patient(user: dict = Depends(verify_token)):
    """Get current logged-in patient information"""
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id,
                        phone_number,
                        full_name,
                        email,
                        date_of_birth,
                        gender,
                        time_zone,
                        created_at,
                        is_active
                    FROM patients 
                    WHERE id = %s
                """, (user['user_id'],))
                
                patient = cursor.fetchone()
                
                if not patient:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Patient profile not found"
                    )
                
                logger.info(f"Retrieved profile for patient {user['user_id']}")
                return patient
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching patient profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve patient information"
        )

@router.patch("/profile", response_model=PatientResponse)
async def update_current_patient(
    update_data: PatientUpdate,
    user: dict = Depends(verify_token)
):
    """
    Update current patient profile
    
    - **full_name**: Patient's full name
    - **email**: Email address
    - **date_of_birth**: Birth date (YYYY-MM-DD)
    - **gender**: Gender (male/female/other)
    - **time_zone**: Timezone (e.g., Asia/Jerusalem)
    """
    try:
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Build update query
                updates = []
                params = []
                
                if update_data.full_name is not None:
                    updates.append("full_name = %s")
                    params.append(update_data.full_name)
                
                if update_data.email is not None:
                    updates.append("email = %s")
                    params.append(update_data.email)
                
                if update_data.date_of_birth is not None:
                    updates.append("date_of_birth = %s")
                    params.append(update_data.date_of_birth)
                
                if update_data.gender is not None:
                    updates.append("gender = %s")
                    params.append(update_data.gender)
                
                if update_data.time_zone is not None:
                    updates.append("time_zone = %s")
                    params.append(update_data.time_zone)
                
                if not updates:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No valid update fields provided"
                    )
                
                updates.append("updated_at = NOW()")
                params.append(user['user_id'])
                
                # Execute update
                query = f"""
                    UPDATE patients 
                    SET {', '.join(updates)}
                    WHERE id = %s
                    RETURNING 
                        id,
                        phone_number,
                        full_name,
                        email,
                        date_of_birth,
                        gender,
                        time_zone,
                        created_at,
                        is_active
                """
                
                cursor.execute(query, params)
                updated_patient = cursor.fetchone()
                
                logger.info(f"Updated profile for patient {user['user_id']}")
                return updated_patient
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating patient profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update patient information"
        )
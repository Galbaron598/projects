from fastapi import APIRouter, HTTPException, status
from app.schemas.auth import (
    SendOTPRequest, SendOTPResponse,
    VerifyOTPRequest, VerifyOTPResponse,
    ValidateTokenRequest, ValidateTokenResponse
)
from app.services import otp_service
from app.core.security import create_access_token, verify_token
from app.core.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/send-otp", response_model=SendOTPResponse)
async def send_otp(request: SendOTPRequest):
    """Send OTP to phone number"""
    try:
        # Generate OTP
        otp_code = otp_service.generate_otp()
        
        # Save to database
        otp_service.save_otp(request.phone_number, otp_code)
        
        # Send SMS
        otp_service.send_otp_sms(request.phone_number, otp_code)
        
        return SendOTPResponse(
            success=True,
            message="OTP sent successfully",
            otp_code=otp_code  # Remove in production!
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/verify-otp", response_model=VerifyOTPResponse)
async def verify_otp_endpoint(request: VerifyOTPRequest):
    """Verify OTP and login"""
    try:
        # Verify OTP
        if not otp_service.verify_otp(request.phone_number, request.otp_code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired OTP"
            )
        
        # Get or create patient
        with get_db() as conn:
            with conn.cursor() as cursor:
                # Check if patient exists
                cursor.execute(
                    "SELECT * FROM patients WHERE phone_number = %s",
                    (request.phone_number,)
                )
                patient = cursor.fetchone()
                
                is_new_user = False
                if not patient:
                    # Create new patient
                    cursor.execute(
                        """
                        INSERT INTO patients (phone_number, full_name)
                        VALUES (%s, %s)
                        RETURNING *
                        """,
                        (request.phone_number, request.full_name)
                    )
                    patient = cursor.fetchone()
                    is_new_user = True
        
        # Generate JWT token
        token = create_access_token({
            "user_id": patient['id'],
            "phone_number": patient['phone_number']
        })
        
        return VerifyOTPResponse(
            success=True,
            token=token,
            user={
                "id": patient['id'],
                "phone_number": patient['phone_number'],
                "full_name": patient['full_name'],
                "is_new_user": is_new_user
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.post("/validate-token", response_model=ValidateTokenResponse)
async def validate_token_endpoint(request: ValidateTokenRequest):
    """Validate JWT token (for other services)"""
    try:
        payload = verify_token(request.token)
        
        if payload:
            return ValidateTokenResponse(
                valid=True,
                user_id=payload.get("user_id"),
                phone_number=payload.get("phone_number")
            )
        else:
            return ValidateTokenResponse(
                valid=False,
                error="Invalid or expired token"
            )
    except Exception as e:
        return ValidateTokenResponse(
            valid=False,
            error=str(e)
        )
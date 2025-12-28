from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime, timedelta

from app.models.schemas import (
    RequestOTPRequest,
    VerifyOTPRequest,
    OTPResponse,
    VerifyOTPResponse,
    UserResponse,
    MessageResponse,
    HealthResponse,
    UserInfo,
    ValidateTokenResponse,
    ValidateTokenRequest
)
from app.core.config import otp_store, user_sessions, OTP_EXPIRY_MINUTES
from app.core.security import get_current_user
from app.utils.auth_utils import generate_otp, generate_token

router = APIRouter()


@router.post("/request-otp", response_model=OTPResponse, status_code=status.HTTP_200_OK)
async def request_otp(request: RequestOTPRequest):
    """
    Request OTP for phone number
    
    The OTP will be displayed in the server console and returned in the response
    for testing purposes. In production, send it via SMS instead.
    """
    phone_number = request.phoneNumber
    
    # Generate OTP
    otp = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=OTP_EXPIRY_MINUTES)
    
    # Store OTP
    otp_store[phone_number] = {
        'otp': otp,
        'expires_at': expires_at,
        'verified': False
    }
    
    # Log OTP to console (in production, send via SMS)
    print(f"\n📱 OTP for {phone_number}: {otp}")
    print(f"⏰ Expires at: {expires_at.strftime('%H:%M:%S')}\n")
    
    return OTPResponse(
        message="OTP sent successfully",
        debug={
            'otp': otp,
            'expiresIn': f'{OTP_EXPIRY_MINUTES} minutes'
        }
    )


@router.post("/verify-otp", response_model=VerifyOTPResponse, status_code=status.HTTP_200_OK)
async def verify_otp(request: VerifyOTPRequest):
    """
    Verify OTP and return JWT token
    
    Returns authentication token and user information.
    """
    phone_number = request.phoneNumber
    otp = request.otp
    
    # Check if OTP exists
    if phone_number not in otp_store:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No OTP request found for this number"
        )
    
    stored_otp = otp_store[phone_number]
    
    # Check if OTP is expired
    if datetime.utcnow() > stored_otp['expires_at']:
        del otp_store[phone_number]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP has expired. Please request a new one."
        )
    
    # Verify OTP
    if stored_otp['otp'] != otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    # Mark as verified
    stored_otp['verified'] = True
    
    # Check if user exists (returning user) or create new user
    is_new_user = phone_number not in user_sessions
    
    if is_new_user:
        user_sessions[phone_number] = {
            'phone_number': phone_number,
            'created_at': datetime.utcnow().isoformat(),
            'appointments': []
        }
    
    user_data = user_sessions[phone_number]
    
    # Generate JWT token
    token = generate_token(phone_number)
    
    # Clean up OTP
    del otp_store[phone_number]
    
    print(f"✅ User {phone_number} verified successfully")
    
    return VerifyOTPResponse(
        message="Authentication successful",
        token=token,
        user=UserInfo(
            phoneNumber=user_data['phone_number'],
            isNewUser=is_new_user,
            createdAt=user_data['created_at']
        )
    )


@router.get("/me", response_model=UserResponse, status_code=status.HTTP_200_OK)
async def get_user_info(current_user: str = Depends(get_current_user)):
    """
    Get current user information
    
    Requires valid JWT token in Authorization header.
    """
    user_data = user_sessions[current_user]
    
    return UserResponse(
        user=UserInfo(
            phoneNumber=user_data['phone_number'],
            createdAt=user_data['created_at'],
            isNewUser=len(user_data['appointments']) == 0
        )
    )


@router.post("/logout", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def logout(current_user: str = Depends(get_current_user)):
    """
    Logout user
    
    In a stateless JWT system, logout is typically handled client-side
    by deleting the token. This endpoint is optional.
    """
    print(f"👋 User {current_user} logged out")
    
    return MessageResponse(message="Logged out successfully")


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """
    Health check endpoint
    
    Returns service status and statistics.
    """
    return HealthResponse(
        status="OK",
        timestamp=datetime.utcnow().isoformat(),
        activeOTPs=len(otp_store),
        activeUsers=len(user_sessions)
    )


@router.post("/validate-token", response_model=ValidateTokenResponse)
async def validate_token_endpoint(request: ValidateTokenRequest):
    """
    Validate JWT token (for internal services / microservices)
    """
    try:
        payload = verify_token(request.token)

        return ValidateTokenResponse(
            valid=True,
            phoneNumber=payload.get("sub")
        )

    except Exception as e:
        return ValidateTokenResponse(
            valid=False,
            error=str(e)
        )
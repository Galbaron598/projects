from pydantic import BaseModel, Field, validator
from typing import Optional, Dict


class RequestOTPRequest(BaseModel):
    phoneNumber: str = Field(..., description="Phone number for OTP")
    
    @validator('phoneNumber')
    def validate_phone_number(cls, v):
        if not v:
            raise ValueError('Phone number is required')
        # Remove spaces and dashes
        cleaned = v.replace(' ', '').replace('-', '')
        # Check if it's between 10-15 digits (with optional + at start)
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]
        if not cleaned.isdigit() or not (10 <= len(cleaned) <= 15):
            raise ValueError('Invalid phone number format')
        return v


class VerifyOTPRequest(BaseModel):
    phoneNumber: str = Field(..., description="Phone number")
    otp: str = Field(..., description="6-digit OTP code")


class OTPResponse(BaseModel):
    message: str
    debug: Optional[Dict] = None


class UserInfo(BaseModel):
    phoneNumber: str
    isNewUser: bool
    createdAt: str


class VerifyOTPResponse(BaseModel):
    message: str
    token: str
    user: UserInfo


class UserResponse(BaseModel):
    user: UserInfo


class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    activeOTPs: int
    activeUsers: int
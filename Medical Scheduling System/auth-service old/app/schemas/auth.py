from pydantic import BaseModel, Field
from typing import Optional

class SendOTPRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=20)

class SendOTPResponse(BaseModel):
    success: bool
    message: str
    otp_code: Optional[str] = None  # For testing only

class VerifyOTPRequest(BaseModel):
    phone_number: str = Field(..., min_length=10, max_length=20)
    otp_code: str = Field(..., min_length=6, max_length=6)
    full_name: Optional[str] = None

class VerifyOTPResponse(BaseModel):
    success: bool
    token: str
    user: dict

class ValidateTokenRequest(BaseModel):
    token: str

class ValidateTokenResponse(BaseModel):
    valid: bool
    user_id: Optional[int] = None
    phone_number: Optional[str] = None
    error: Optional[str] = None
    
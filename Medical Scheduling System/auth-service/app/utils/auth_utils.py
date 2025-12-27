import random
import string
import jwt
from datetime import datetime, timedelta
from app.core.config import JWT_SECRET, JWT_EXPIRY_DAYS


def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))


def generate_token(phone_number: str) -> str:
    """Generate JWT token"""
    payload = {
        'phone_number': phone_number,
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRY_DAYS),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')
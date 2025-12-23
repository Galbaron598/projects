import random
import string
from datetime import datetime, timedelta
from app.core.config import get_settings
from app.core.database import get_db

settings = get_settings()

def generate_otp() -> str:
    """Generate random OTP code"""
    return ''.join(random.choices(string.digits, k=settings.OTP_LENGTH))

def save_otp(phone_number: str, otp_code: str) -> None:
    """Save OTP to database"""
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRATION_MINUTES)
    
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO otp_codes (phone_number, otp_code, expires_at)
                VALUES (%s, %s, %s)
                """,
                (phone_number, otp_code, expires_at)
            )

def verify_otp(phone_number: str, otp_code: str) -> bool:
    """Verify OTP code"""
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id FROM otp_codes
                WHERE phone_number = %s
                  AND otp_code = %s
                  AND is_verified = FALSE
                  AND expires_at > NOW()
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (phone_number, otp_code)
            )
            result = cursor.fetchone()
            
            if result:
                # Mark as verified
                cursor.execute(
                    "UPDATE otp_codes SET is_verified = TRUE WHERE id = %s",
                    (result['id'],)
                )
                return True
            return False

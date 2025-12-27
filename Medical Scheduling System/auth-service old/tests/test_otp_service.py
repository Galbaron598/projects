"""
Tests for OTP service
"""

import pytest
from app.services import otp_service
from datetime import datetime, timedelta


def test_generate_otp():
    """Test OTP code generation"""
    otp = otp_service.generate_otp()
    
    assert otp is not None
    assert len(otp) == 6
    assert otp.isdigit()


def test_generate_multiple_otps_are_different():
    """Test that generated OTPs are different"""
    otp1 = otp_service.generate_otp()
    otp2 = otp_service.generate_otp()
    
    # Should be different (though rare chance they're the same)
    # Run multiple times to be sure
    otps = [otp_service.generate_otp() for _ in range(10)]
    assert len(set(otps)) > 1  # At least some should be different


def test_save_otp(clean_db):
    """Test saving OTP to database"""
    phone = "0501234567"
    otp = "123456"
    
    otp_service.save_otp(phone, otp)
    
    # Verify OTP was saved
    cursor = clean_db.cursor()
    cursor.execute("""
        SELECT * FROM otp_codes 
        WHERE phone_number = %s AND otp_code = %s
    """, (phone, otp))
    
    result = cursor.fetchone()
    cursor.close()
    
    assert result is not None
    assert result['phone_number'] == phone
    assert result['otp_code'] == otp
    assert result['is_verified'] is False


def test_verify_otp_success(clean_db):
    """Test successful OTP verification"""
    phone = "0501234567"
    otp = "123456"
    
    # Save OTP
    otp_service.save_otp(phone, otp)
    
    # Verify OTP
    is_valid = otp_service.verify_otp(phone, otp)
    
    assert is_valid is True
    
    # Check that OTP is marked as verified
    cursor = clean_db.cursor()
    cursor.execute("""
        SELECT is_verified FROM otp_codes 
        WHERE phone_number = %s AND otp_code = %s
    """, (phone, otp))
    
    result = cursor.fetchone()
    cursor.close()
    
    assert result['is_verified'] is True


def test_verify_otp_wrong_code(clean_db):
    """Test OTP verification with wrong code"""
    phone = "0501234567"
    correct_otp = "123456"
    wrong_otp = "999999"
    
    # Save OTP
    otp_service.save_otp(phone, correct_otp)
    
    # Try to verify with wrong code
    is_valid = otp_service.verify_otp(phone, wrong_otp)
    
    assert is_valid is False


def test_verify_otp_expired(clean_db):
    """Test OTP verification with expired code"""
    phone = "0501234567"
    otp = "123456"
    
    # Manually insert expired OTP
    cursor = clean_db.cursor()
    expired_time = datetime.utcnow() - timedelta(minutes=10)
    
    cursor.execute("""
        INSERT INTO otp_codes (phone_number, otp_code, expires_at)
        VALUES (%s, %s, %s)
    """, (phone, otp, expired_time))
    clean_db.commit()
    cursor.close()
    
    # Try to verify expired OTP
    is_valid = otp_service.verify_otp(phone, otp)
    
    assert is_valid is False


def test_verify_otp_already_used(clean_db):
    """Test that OTP cannot be reused"""
    phone = "0501234567"
    otp = "123456"
    
    # Save and verify OTP
    otp_service.save_otp(phone, otp)
    otp_service.verify_otp(phone, otp)
    
    # Try to verify again
    is_valid = otp_service.verify_otp(phone, otp)
    
    assert is_valid is False


def test_send_otp_sms(capsys):
    """Test OTP SMS sending (mock)"""
    phone = "0501234567"
    otp = "123456"
    
    otp_service.send_otp_sms(phone, otp)
    
    # Check console output
    captured = capsys.readouterr()
    assert phone in captured.out
    assert otp in captured.out
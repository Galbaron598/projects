"""
Tests for authentication API routes
"""

import pytest


def test_root_endpoint(client):
    """Test root endpoint"""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data['service'] == 'auth-service'
    assert data['status'] == 'running'


def test_send_otp(client, clean_db):
    """Test sending OTP"""
    response = client.post(
        "/auth/send-otp",
        json={"phone_number": "0501234567"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
    assert 'otp_code' in data  # Test mode shows OTP


def test_send_otp_invalid_phone(client):
    """Test sending OTP with invalid phone"""
    response = client.post(
        "/auth/send-otp",
        json={"phone_number": "invalid"}
    )
    
    assert response.status_code == 422  # Validation error


def test_verify_otp_success(client, clean_db):
    """Test successful OTP verification"""
    phone = "0501234567"
    
    # Send OTP
    send_response = client.post(
        "/auth/send-otp",
        json={"phone_number": phone}
    )
    otp = send_response.json()['otp_code']
    
    # Verify OTP
    verify_response = client.post(
        "/auth/verify-otp",
        json={
            "phone_number": phone,
            "otp_code": otp,
            "full_name": "Test User"
        }
    )
    
    assert verify_response.status_code == 200
    data = verify_response.json()
    assert data['success'] is True
    assert 'token' in data
    assert data['user']['phone_number'] == phone


def test_verify_otp_wrong_code(client, clean_db):
    """Test OTP verification with wrong code"""
    phone = "0501234567"
    
    # Send OTP
    client.post("/auth/send-otp", json={"phone_number": phone})
    
    # Verify with wrong code
    response = client.post(
        "/auth/verify-otp",
        json={
            "phone_number": phone,
            "otp_code": "999999",
            "full_name": "Test User"
        }
    )
    
    assert response.status_code == 400


def test_validate_token_valid(client, clean_db):
    """Test validating a valid token"""
    phone = "0501234567"
    
    # Get token
    send_response = client.post("/auth/send-otp", json={"phone_number": phone})
    otp = send_response.json()['otp_code']
    
    verify_response = client.post(
        "/auth/verify-otp",
        json={"phone_number": phone, "otp_code": otp, "full_name": "Test"}
    )
    token = verify_response.json()['token']
    
    # Validate token
    validate_response = client.post(
        "/auth/validate-token",
        json={"token": token}
    )
    
    assert validate_response.status_code == 200
    data = validate_response.json()
    assert data['valid'] is True
    assert 'user_id' in data


def test_validate_token_invalid(client):
    """Test validating an invalid token"""
    response = client.post(
        "/auth/validate-token",
        json={"token": "invalid.token"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['valid'] is False


def test_returning_user(client, clean_db, sample_patient):
    """Test login flow for returning user"""
    phone = sample_patient['phone_number']
    
    # Send OTP
    send_response = client.post("/auth/send-otp", json={"phone_number": phone})
    otp = send_response.json()['otp_code']
    
    # Verify OTP
    response = client.post(
        "/auth/verify-otp",
        json={"phone_number": phone, "otp_code": otp}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['user']['is_new_user'] is False
    assert data['user']['full_name'] == sample_patient['full_name']

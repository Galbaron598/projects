"""
Tests for patients endpoints
"""

import pytest
from unittest.mock import patch


@pytest.fixture(autouse=True)
def mock_auth(monkeypatch, sample_patient):
    """Mock authentication for all tests"""
    async def mock_verify_token(*args, **kwargs):
        return {"user_id": sample_patient, "phone_number": "0501234567"}
    
    from app.middleware import auth_middleware
    monkeypatch.setattr(auth_middleware, 'verify_token', mock_verify_token)


def test_get_current_patient(authed_client, auth_headers, sample_patient):
    """Test getting current patient profile"""
    response = authed_client.get("/api/patients/me", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == sample_patient
    assert data['phone_number'] == '0501234567'
    assert data['full_name'] == 'Test Patient'


def test_update_patient_profile(authed_client, auth_headers):
    """Test updating patient profile"""
    update_data = {
        "full_name": "Updated Name",
        "email": "test@example.com",
        "gender": "male"
    }
    
    response = authed_client.patch(
        "/api/patients/me",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['full_name'] == "Updated Name"
    assert data['email'] == "test@example.com"
    assert data['gender'] == "male"


def test_update_patient_invalid_gender(authed_client, auth_headers):
    """Test updating with invalid gender"""
    update_data = {
        "gender": "invalid"
    }
    
    response = authed_client.patch(
        "/api/patients/me",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 422  # Validation error


def test_patient_endpoints_require_auth(unauth_client):
    """Test that patient endpoints require authentication"""
    response = unauth_client.get("/api/patients/me")
    assert response.status_code == 401
repr("")

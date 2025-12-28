"""
Tests for appointments endpoints
"""

import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch, AsyncMock


# # Mock the auth middleware for testing
# @pytest.fixture(autouse=True)
# def mock_auth(monkeypatch):
#     """Mock authentication for all tests"""
#     async def mock_verify_token(*args, **kwargs):
#         return {"user_id": 1, "phone_number": "0501234567"}
    
#     from app.middleware import auth_middleware
#     monkeypatch.setattr(auth_middleware, 'verify_token', mock_verify_token)


 
def test_get_appointments_empty(authed_client, auth_headers, clean_db):
    """Test getting appointments when user has none"""
    r = authed_client.get("/api/appointments")
    assert r.status_code == 200


def test_get_appointments(authed_client, auth_headers, sample_appointment):
    """Test getting user's appointments"""
    response = authed_client.get("/api/appointments", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]['id'] == sample_appointment


def test_get_upcoming_appointments(authed_client, auth_headers, sample_appointment):
    """Test getting upcoming appointments only"""
    response = authed_client.get("/api/appointments/upcoming", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert all(
        datetime.fromisoformat(apt['appointment_time'].replace('Z', '+00:00')) > datetime.now(timezone.utc)
        for apt in data
    )


def test_get_appointment_stats(authed_client, auth_headers, sample_appointment):
    """Test getting appointment statistics"""
    response = authed_client.get("/api/appointments/stats", headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json()
    assert 'total_appointments' in data
    assert 'upcoming_appointments' in data
    assert 'completed_appointments' in data
    assert 'cancelled_appointments' in data


def test_create_appointment(authed_client, auth_headers, sample_doctor, sample_medical_field):
    """Test creating a new appointment"""
    appointment_time = datetime.now() + timedelta(days=2)
    appointment_time = appointment_time.replace(hour=14, minute=0, second=0, microsecond=0)
    
    appointment_data = {
        "doctor_id": sample_doctor,
        "medical_field_id": sample_medical_field,
        "appointment_time": appointment_time.isoformat() + "Z",
        "duration_minutes": 30,
        "reason_for_visit": "Regular checkup"
    }
    
    response = authed_client.post(
        "/api/appointments",
        json=appointment_data,
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data['doctor_id'] == sample_doctor
    assert data['status'] == 'scheduled'


def test_create_appointment_conflict(authed_client, auth_headers, sample_appointment, 
                                     sample_doctor, sample_medical_field):
    """Test creating appointment with time conflict"""
    # Try to book the same time as existing appointment
    tomorrow = datetime.now() + timedelta(days=1)
    appointment_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    appointment_data = {
        "doctor_id": sample_doctor,
        "medical_field_id": sample_medical_field,
        "appointment_time": appointment_time.isoformat() + "Z",
        "duration_minutes": 30
    }
    
    response = authed_client.post(
        "/api/appointments",
        json=appointment_data,
        headers=auth_headers
    )
    
    assert response.status_code == 409  # Conflict


def test_create_appointment_past_time(authed_client, auth_headers, sample_doctor, sample_medical_field):
    """Test creating appointment in the past"""
    past_time = datetime.now() - timedelta(days=1)
    
    appointment_data = {
        "doctor_id": sample_doctor,
        "medical_field_id": sample_medical_field,
        "appointment_time": past_time.isoformat() + "Z",
        "duration_minutes": 30
    }
    
    response = authed_client.post(
        "/api/appointments",
        json=appointment_data,
        headers=auth_headers
    )

    assert response.status_code == 422  # Validation error


def test_update_appointment(authed_client, auth_headers, sample_appointment):
    """Test updating an appointment"""
    update_data = {
        "notes": "Please bring medical records"
    }
    
    response = authed_client.patch(
        f"/api/appointments/{sample_appointment}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['notes'] == "Please bring medical records"


def test_cancel_appointment(authed_client, auth_headers, sample_appointment):
    """Test cancelling an appointment"""
    update_data = {
        "status": "cancelled",
        "cancellation_reason": "Schedule conflict"
    }
    
    response = authed_client.patch(
        f"/api/appointments/{sample_appointment}",
        json=update_data,
        headers=auth_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'cancelled'
    assert data['cancellation_reason'] == "Schedule conflict"


def test_delete_appointment(authed_client, auth_headers, sample_appointment):
    """Test deleting (cancelling) an appointment"""
    response = authed_client.delete(
        f"/api/appointments/{sample_appointment}",
        headers=auth_headers
    )
    
    assert response.status_code == 204


def test_update_appointment_not_found(authed_client, auth_headers):
    """Test updating non-existent appointment"""
    response = authed_client.patch(
        "/api/appointments/99999",
        json={"notes": "test"},
        headers=auth_headers
    )
    
    assert response.status_code == 404


def test_appointments_require_auth(unauth_client):
    """Test that appointments endpoints require authentication"""
    response = unauth_client.get("/api/appointments")
    assert response.status_code == 401
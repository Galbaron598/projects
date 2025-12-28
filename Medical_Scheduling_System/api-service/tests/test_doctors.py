"""
Tests for doctors endpoints
"""

import pytest
from datetime import datetime, timedelta


def test_get_doctors_empty(authed_client, clean_db):
    """Test getting doctors when database is empty"""
    response = authed_client.get("/api/doctors")
    
    assert response.status_code == 200
    assert response.json() == []


def test_get_doctors(authed_client, sample_doctor):
    """Test getting all doctors"""
    response = authed_client.get("/api/doctors")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Dr. Test'
    assert float(data[0]['rating']) == 4.5


def test_get_doctors_by_field(authed_client, sample_doctor, sample_medical_field):
    """Test filtering doctors by medical field"""
    response = authed_client.get(f"/api/doctors?medical_field_id={sample_medical_field}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['medical_field_id'] == sample_medical_field


def test_get_doctors_by_rating(authed_client, sample_doctor):
    """Test filtering doctors by minimum rating"""
    response = authed_client.get("/api/doctors?min_rating=4.0")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert float(data[0]['rating']) >= 4.0


def test_get_doctor_by_id(authed_client, sample_doctor):
    """Test getting specific doctor"""
    response = authed_client.get(f"/api/doctors/{sample_doctor}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == sample_doctor
    assert data['name'] == 'Dr. Test'
    assert 'working_hours' in data


def test_get_doctor_not_found(authed_client):
    """Test getting non-existent doctor"""
    response = authed_client.get("/api/doctors/99999")
    
    assert response.status_code == 404


def test_get_available_slots(authed_client, sample_doctor):
    """Test getting available time slots"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = authed_client.get(f"/api/doctors/{sample_doctor}/available-slots?date={tomorrow}")
    
    assert response.status_code == 200
    data = response.json()
    assert 'doctor_id' in data
    assert 'date' in data
    assert 'available_slots' in data
    assert isinstance(data['available_slots'], list)


def test_get_available_slots_invalid_date(authed_client, sample_doctor):
    """Test getting slots with invalid date format"""
    response = authed_client.get(f"/api/doctors/{sample_doctor}/available-slots?date=invalid-date")
    
    assert response.status_code == 400


def test_get_available_slots_past_date(authed_client, sample_doctor):
    """Test getting slots for past date"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = authed_client.get(f"/api/doctors/{sample_doctor}/available-slots?date={yesterday}")
    
    assert response.status_code == 400
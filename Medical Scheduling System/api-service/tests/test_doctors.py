"""
Tests for doctors endpoints
"""

import pytest
from datetime import datetime, timedelta


def test_get_doctors_empty(client, clean_db):
    """Test getting doctors when database is empty"""
    response = client.get("/api/doctors")
    
    assert response.status_code == 200
    assert response.json() == []


def test_get_doctors(client, sample_doctor):
    """Test getting all doctors"""
    response = client.get("/api/doctors")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['name'] == 'Dr. Test'
    assert data[0]['rating'] == 4.5


def test_get_doctors_by_field(client, sample_doctor, sample_medical_field):
    """Test filtering doctors by medical field"""
    response = client.get(f"/api/doctors?medical_field_id={sample_medical_field}")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['medical_field_id'] == sample_medical_field


def test_get_doctors_by_rating(client, sample_doctor):
    """Test filtering doctors by minimum rating"""
    response = client.get("/api/doctors?min_rating=4.0")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['rating'] >= 4.0


def test_get_doctor_by_id(client, sample_doctor):
    """Test getting specific doctor"""
    response = client.get(f"/api/doctors/{sample_doctor}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == sample_doctor
    assert data['name'] == 'Dr. Test'
    assert 'working_hours' in data


def test_get_doctor_not_found(client):
    """Test getting non-existent doctor"""
    response = client.get("/api/doctors/99999")
    
    assert response.status_code == 404


def test_get_available_slots(client, sample_doctor):
    """Test getting available time slots"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = client.get(f"/api/doctors/{sample_doctor}/available-slots?date={tomorrow}")
    
    assert response.status_code == 200
    data = response.json()
    assert 'doctor_id' in data
    assert 'date' in data
    assert 'available_slots' in data
    assert isinstance(data['available_slots'], list)


def test_get_available_slots_invalid_date(client, sample_doctor):
    """Test getting slots with invalid date format"""
    response = client.get(f"/api/doctors/{sample_doctor}/available-slots?date=invalid-date")
    
    assert response.status_code == 400


def test_get_available_slots_past_date(client, sample_doctor):
    """Test getting slots for past date"""
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    response = client.get(f"/api/doctors/{sample_doctor}/available-slots?date={yesterday}")
    
    assert response.status_code == 400
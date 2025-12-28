"""
Tests for medical fields endpoints
"""

import pytest


def test_get_medical_fields_empty(authed_client, clean_db):
    """Test getting medical fields when database is empty"""
    response = authed_client.get("/api/medical-fields")
    
    assert response.status_code == 200
    assert response.json() == []


def test_get_medical_fields(authed_client, sample_medical_field):
    """Test getting medical fields"""
    response = authed_client.get("/api/medical-fields")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]['medical_field_name'] == 'Cardiology'
    assert data[0]['icon'] == 'heart'


def test_get_medical_field_by_id(authed_client, sample_medical_field):
    """Test getting specific medical field"""
    response = authed_client.get(f"/api/medical-fields/{sample_medical_field}")
    
    assert response.status_code == 200
    data = response.json()
    assert data['id'] == sample_medical_field
    assert data['medical_field_name'] == 'Cardiology'


def test_get_medical_field_not_found(authed_client):
    """Test getting non-existent medical field"""
    response = authed_client.get("/api/medical-fields/99999")
    
    assert response.status_code == 404


def test_get_doctors_count(authed_client, sample_medical_field, sample_doctor):
    """Test getting doctor count for a field"""
    response = authed_client.get(f"/api/medical-fields/{sample_medical_field}/doctors-count")
    
    assert response.status_code == 200
    data = response.json()
    assert data['medical_field_id'] == sample_medical_field
    assert data['doctors_count'] == 1
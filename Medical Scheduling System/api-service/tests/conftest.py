"""
Pytest configuration and fixtures for API service tests
"""

import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app


@pytest.fixture(scope="session")
def test_db_connection():
    """Create a test database connection"""
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="medical_scheduling_test",  # Use separate test database
        user="postgres",
        password="postgres",
        cursor_factory=RealDictCursor
    )
    yield conn
    conn.close()


@pytest.fixture(scope="function")
def clean_db(test_db_connection):
    """Clean database before each test"""
    cursor = test_db_connection.cursor()
    
    # Clear all tables
    cursor.execute("TRUNCATE TABLE appointments CASCADE")
    cursor.execute("TRUNCATE TABLE doctor_working_hours CASCADE")
    cursor.execute("TRUNCATE TABLE doctors CASCADE")
    cursor.execute("TRUNCATE TABLE medical_fields CASCADE")
    cursor.execute("TRUNCATE TABLE patients CASCADE")
    cursor.execute("TRUNCATE TABLE otp_codes CASCADE")
    
    test_db_connection.commit()
    cursor.close()
    
    yield test_db_connection


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_medical_field(clean_db):
    """Create a sample medical field"""
    cursor = clean_db.cursor()
    cursor.execute("""
        INSERT INTO medical_fields (medical_field_name, description, icon)
        VALUES ('Cardiology', 'Heart specialists', 'heart')
        RETURNING id
    """)
    field_id = cursor.fetchone()['id']
    clean_db.commit()
    cursor.close()
    return field_id


@pytest.fixture
def sample_doctor(clean_db, sample_medical_field):
    """Create a sample doctor"""
    cursor = clean_db.cursor()
    cursor.execute("""
        INSERT INTO doctors (
            name, medical_field_id, specialization, 
            years_of_experience, rating, consultation_fee
        )
        VALUES ('Dr. Test', %s, 'Test Specialty', 10, 4.5, 300.00)
        RETURNING id
    """, (sample_medical_field,))
    doctor_id = cursor.fetchone()['id']
    
    # Add working hours
    cursor.execute("""
        INSERT INTO doctor_working_hours (doctor_id, day_of_week, start_time, end_time)
        VALUES 
            (%s, 0, '09:00', '17:00'),
            (%s, 1, '09:00', '17:00'),
            (%s, 2, '09:00', '17:00'),
            (%s, 3, '09:00', '17:00'),
            (%s, 4, '09:00', '17:00')
    """, (doctor_id, doctor_id, doctor_id, doctor_id, doctor_id))
    
    clean_db.commit()
    cursor.close()
    return doctor_id


@pytest.fixture
def sample_patient(clean_db):
    """Create a sample patient"""
    cursor = clean_db.cursor()
    cursor.execute("""
        INSERT INTO patients (phone_number, full_name)
        VALUES ('0501234567', 'Test Patient')
        RETURNING id
    """)
    patient_id = cursor.fetchone()['id']
    clean_db.commit()
    cursor.close()
    return patient_id


@pytest.fixture
def auth_token(sample_patient):
    """Create a mock auth token"""
    # In real tests, you'd get this from auth service
    # For now, return a mock token
    return "test_token_12345"


@pytest.fixture
def auth_headers(auth_token):
    """Create authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}


@pytest.fixture
def sample_appointment(clean_db, sample_patient, sample_doctor, sample_medical_field):
    """Create a sample appointment"""
    cursor = clean_db.cursor()
    
    appointment_time = datetime.now() + timedelta(days=1)
    appointment_time = appointment_time.replace(hour=10, minute=0, second=0, microsecond=0)
    
    cursor.execute("""
        INSERT INTO appointments (
            patient_id, doctor_id, medical_field_id,
            appointment_time, duration_minutes, status
        )
        VALUES (%s, %s, %s, %s, 30, 'scheduled')
        RETURNING id
    """, (sample_patient, sample_doctor, sample_medical_field, appointment_time))
    
    appointment_id = cursor.fetchone()['id']
    clean_db.commit()
    cursor.close()
    
    return appointment_id
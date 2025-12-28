"""
Pytest configuration and fixtures for API service tests
"""

import os
import sys
from datetime import datetime, timedelta, timezone
from fastapi import Header
import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi.testclient import TestClient

# -----------------------------------------------------------------------------
# 1) Make sure api-service package is importable
# -----------------------------------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# -----------------------------------------------------------------------------
# 2) Force TEST DB settings via env BEFORE importing the app/settings
# -----------------------------------------------------------------------------
TEST_DB_HOST = os.getenv("TEST_DB_HOST", "localhost")
TEST_DB_PORT = os.getenv("TEST_DB_PORT", "5432")
TEST_DB_NAME = os.getenv("TEST_DB_NAME", "medical_scheduling_test")
TEST_DB_USER = os.getenv("TEST_DB_USER", os.getenv("USER", "postgres"))
TEST_DB_PASSWORD = os.getenv("TEST_DB_PASSWORD", "")

os.environ["DB_HOST"] = TEST_DB_HOST
os.environ["DB_PORT"] = str(TEST_DB_PORT)
os.environ["DB_NAME"] = TEST_DB_NAME
os.environ["DB_USER"] = TEST_DB_USER
os.environ["DB_PASSWORD"] = TEST_DB_PASSWORD

# -----------------------------------------------------------------------------
# 3) Import app after env is set
# -----------------------------------------------------------------------------
from main import app
from app.core.config import get_settings
from app.core.database import DatabasePool
from app.middleware.auth_middleware import verify_token


def _reset_settings_and_pool():
    get_settings.cache_clear()
    DatabasePool.close_pool()


# -----------------------------------------------------------------------------
# DB Fixtures
# -----------------------------------------------------------------------------
@pytest.fixture(scope="session")
def test_db_connection():
    conn = psycopg2.connect(
        host=TEST_DB_HOST,
        port=int(TEST_DB_PORT),
        database=TEST_DB_NAME,
        user=TEST_DB_USER,
        password=TEST_DB_PASSWORD,
        cursor_factory=RealDictCursor,
    )
    yield conn
    conn.close()


@pytest.fixture(scope="session", autouse=True)
def ensure_test_schema(test_db_connection):
    cur = test_db_connection.cursor()

    # core tables
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS medical_fields (
            id SERIAL PRIMARY KEY,
            medical_field_name TEXT NOT NULL,
            description TEXT,
            icon TEXT
        );

        CREATE TABLE IF NOT EXISTS doctors (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            medical_field_id INTEGER REFERENCES medical_fields(id),
            specialization TEXT,
            years_of_experience INTEGER,
            rating NUMERIC,
            consultation_fee NUMERIC
        );

        CREATE TABLE IF NOT EXISTS doctor_working_hours (
            id SERIAL PRIMARY KEY,
            doctor_id INTEGER NOT NULL REFERENCES doctors(id) ON DELETE CASCADE,
            day_of_week INTEGER NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL
        );

        CREATE TABLE IF NOT EXISTS patients (
            id SERIAL PRIMARY KEY,
            phone_number TEXT UNIQUE NOT NULL,
            full_name TEXT
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id SERIAL PRIMARY KEY,
            patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
            doctor_id INTEGER REFERENCES doctors(id) ON DELETE CASCADE,
            medical_field_id INTEGER REFERENCES medical_fields(id) ON DELETE CASCADE,
            appointment_time TIMESTAMPTZ NOT NULL,
            duration_minutes INTEGER NOT NULL DEFAULT 30,
            status TEXT NOT NULL DEFAULT 'scheduled',
            notes TEXT,
            cancellation_reason TEXT,
            reason_for_visit TEXT
        );
        """
    )

    # columns your API uses
    cur.execute(
        """
        ALTER TABLE doctors
          ADD COLUMN IF NOT EXISTS is_available BOOLEAN NOT NULL DEFAULT TRUE;
        """
    )

    cur.execute(
        """
        ALTER TABLE appointments
          ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
          ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMPTZ;
        """
    )

    test_db_connection.commit()
    cur.close()

    _reset_settings_and_pool()


@pytest.fixture(scope="function")
def clean_db(test_db_connection):
    cursor = test_db_connection.cursor()
    cursor.execute(
        """
        TRUNCATE TABLE
            appointments,
            doctor_working_hours,
            doctors,
            medical_fields,
            patients
        RESTART IDENTITY CASCADE;
        """
    )
    test_db_connection.commit()
    cursor.close()

    _reset_settings_and_pool()
    yield test_db_connection


# -----------------------------------------------------------------------------
# Client Fixtures
# -----------------------------------------------------------------------------
@pytest.fixture
def authed_client(clean_db, sample_patient):
    async def fake_verify_token(authorization: str = Header(None)) -> dict:
        return {"user_id": sample_patient, "phone_number": "0501234567"}

    app.dependency_overrides[verify_token] = fake_verify_token
    yield TestClient(app)
    app.dependency_overrides.clear()



@pytest.fixture
def unauth_client(clean_db):
    app.router.redirect_slashes = True
    return TestClient(app)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test_token_12345"}


# -----------------------------------------------------------------------------
# Sample data fixtures
# -----------------------------------------------------------------------------
@pytest.fixture
def sample_medical_field(clean_db):
    cursor = clean_db.cursor()
    cursor.execute(
        """
        INSERT INTO medical_fields (medical_field_name, description, icon)
        VALUES ('Cardiology', 'Heart specialists', 'heart')
        RETURNING id
        """
    )
    
    field_id = cursor.fetchone()["id"]
    
    cursor.execute(
        """
        ALTER TABLE medical_fields
            ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
        """
    )
    clean_db.commit()
    cursor.close()
    return field_id


@pytest.fixture
def sample_doctor(clean_db, sample_medical_field):
    cursor = clean_db.cursor()
    cursor.execute(
        """
        INSERT INTO doctors (
            name, medical_field_id, specialization,
            years_of_experience, rating, consultation_fee, is_available, total_reviews
        )
        VALUES ('Dr. Test', %s, 'Test Specialty', 10, 4.5, 300.00, TRUE, 5)
        RETURNING id
        """,
        (sample_medical_field,),
    )
    doctor_id = cursor.fetchone()["id"]
    
    cursor.execute(
        """
        ALTER TABLE doctors
            ADD COLUMN IF NOT EXISTS is_available BOOLEAN NOT NULL DEFAULT TRUE,
            ADD COLUMN IF NOT EXISTS total_reviews INTEGER NOT NULL DEFAULT 0,
            ADD COLUMN IF NOT EXISTS bio TEXT NOT NULL DEFAULT '',
            ADD COLUMN IF NOT EXISTS image_url TEXT NOT NULL DEFAULT '',
            ADD COLUMN IF NOT EXISTS time_zone TEXT NOT NULL DEFAULT 'UTC',
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW();
        """
    )

    cursor.execute(
        """
        INSERT INTO doctor_working_hours (doctor_id, day_of_week, start_time, end_time)
        VALUES
            (%s, 0, '09:00', '17:00'),
            (%s, 1, '09:00', '17:00'),
            (%s, 2, '09:00', '17:00'),
            (%s, 3, '09:00', '17:00'),
            (%s, 4, '09:00', '17:00')
        """,
        (doctor_id, doctor_id, doctor_id, doctor_id, doctor_id),
    )

    clean_db.commit()
    cursor.close()
    return doctor_id


@pytest.fixture
def sample_patient(clean_db):
    cursor = clean_db.cursor()
    cursor.execute(
        """
        INSERT INTO patients (phone_number, full_name)
        VALUES ('0501234567', 'Test Patient')
        RETURNING id
        """
    )
    
    patient_id = cursor.fetchone()["id"]
    
    cursor.execute(
        """
    ALTER TABLE patients
        ADD COLUMN IF NOT EXISTS email TEXT,
        ADD COLUMN IF NOT EXISTS gender TEXT,
        ADD COLUMN IF NOT EXISTS date_of_birth DATE,
        ADD COLUMN IF NOT EXISTS address TEXT,
        ADD COLUMN IF NOT EXISTS emergency_contact_name TEXT,
        ADD COLUMN IF NOT EXISTS emergency_contact_phone TEXT,
        ADD COLUMN IF NOT EXISTS medical_history TEXT,
        ADD COLUMN IF NOT EXISTS allergies TEXT,
        ADD COLUMN IF NOT EXISTS current_medications TEXT,
        ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE,
        ADD COLUMN IF NOT EXISTS time_zone TEXT NOT NULL DEFAULT 'UTC';
        """
    )
    
    
    clean_db.commit()
    cursor.close()
    return patient_id


@pytest.fixture
def sample_appointment(clean_db, sample_patient, sample_doctor, sample_medical_field):
    cursor = clean_db.cursor()

    # timezone-aware datetime (UTC)
    appointment_time = datetime.now(timezone.utc) + timedelta(days=1)
    appointment_time = appointment_time.replace(hour=10, minute=0, second=0, microsecond=0)

    cursor.execute(
        """
        INSERT INTO appointments (
            patient_id, doctor_id, medical_field_id,
            appointment_time, duration_minutes, status
        )
        VALUES (%s, %s, %s, %s, 30, 'scheduled')
        RETURNING id
        """,
        (sample_patient, sample_doctor, sample_medical_field, appointment_time),
    )

    appointment_id = cursor.fetchone()["id"]
    clean_db.commit()
    cursor.close()
    return appointment_id

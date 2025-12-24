"""
Pytest configuration and fixtures for auth service tests
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
    """Create test database connection"""
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        database="medical_scheduling_test",
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
    
    cursor.execute("TRUNCATE TABLE otp_codes CASCADE")
    cursor.execute("TRUNCATE TABLE patients CASCADE")
    
    test_db_connection.commit()
    cursor.close()
    
    yield test_db_connection


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_patient(clean_db):
    """Create a sample patient"""
    cursor = clean_db.cursor()
    cursor.execute("""
        INSERT INTO patients (phone_number, full_name)
        VALUES ('0501234567', 'Test User')
        RETURNING id, phone_number, full_name
    """)
    patient = cursor.fetchone()
    clean_db.commit()
    cursor.close()
    return patient
"""
Tests for token service
"""

import pytest
from app.services.token_service import (
    generate_token,
    verify_token,
    is_token_expired,
    refresh_token,
    extract_user_id_from_token
)
from datetime import datetime, timedelta


def test_generate_token():
    """Test token generation"""
    user_data = {
        'id': 1,
        'phone_number': '0501234567'
    }
    
    token = generate_token(user_data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 50  # JWT tokens are long


def test_verify_valid_token():
    """Test verifying a valid token"""
    user_data = {
        'id': 1,
        'phone_number': '0501234567'
    }
    
    token = generate_token(user_data)
    payload = verify_token(token)
    
    assert payload is not None
    assert payload['user_id'] == 1
    assert payload['phone_number'] == '0501234567'


def test_verify_invalid_token():
    """Test verifying an invalid token"""
    invalid_token = "invalid.token.here"
    
    payload = verify_token(invalid_token)
    
    assert payload is None


def test_verify_tampered_token():
    """Test verifying a tampered token"""
    user_data = {'id': 1, 'phone_number': '0501234567'}
    token = generate_token(user_data)
    
    # Tamper with token
    tampered_token = token[:-10] + "tampered!!"
    
    payload = verify_token(tampered_token)
    
    assert payload is None


def test_token_not_expired():
    """Test that newly created token is not expired"""
    user_data = {'id': 1, 'phone_number': '0501234567'}
    token = generate_token(user_data)
    
    is_expired = is_token_expired(token)
    
    assert is_expired is False


def test_extract_user_id():
    """Test extracting user ID from token"""
    user_data = {'id': 123, 'phone_number': '0501234567'}
    token = generate_token(user_data)
    
    user_id = extract_user_id_from_token(token)
    
    assert user_id == 123


def test_refresh_token():
    """Test refreshing a token"""
    user_data = {'id': 1, 'phone_number': '0501234567'}
    old_token = generate_token(user_data)
    
    new_token = refresh_token(old_token)
    
    assert new_token is not None
    assert new_token != old_token  # Should be different
    
    # Verify new token is valid
    payload = verify_token(new_token)
    assert payload['user_id'] == 1


def test_refresh_invalid_token():
    """Test refreshing an invalid token"""
    invalid_token = "invalid.token"
    
    new_token = refresh_token(invalid_token)
    
    assert new_token is None
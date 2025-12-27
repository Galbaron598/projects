"""
Token Service - JWT token generation and validation
Handles creating and verifying JWT tokens for authentication
"""

from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()


def generate_token(user_data: Dict) -> str:
    """
    Generate JWT access token for authenticated user
    
    Args:
        user_data: Dictionary containing user information
                  Expected keys: id, phone_number
    
    Returns:
        JWT token as string
        
    Example:
        >>> user = {'id': 1, 'phone_number': '0501234567'}
        >>> token = generate_token(user)
        >>> print(token)
        'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...'
    """
    try:
        # Calculate expiration time
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES)
        
        # Prepare token payload
        payload = {
            "user_id": user_data.get('id'),
            "phone_number": user_data.get('phone_number'),
            "exp": expire,
            "iat": datetime.utcnow(),  # Issued at
            "type": "access"
        }
        
        # Generate token
        encoded_jwt = jwt.encode(
            payload,
            settings.JWT_SECRET_KEY,
            algorithm=settings.JWT_ALGORITHM
        )
        
        logger.info(f"Generated token for user_id: {user_data.get('id')}")
        return encoded_jwt
        
    except Exception as e:
        logger.error(f"Error generating token: {e}")
        raise


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode JWT token
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded token payload as dictionary if valid, None if invalid
        
    Example:
        >>> token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
        >>> payload = verify_token(token)
        >>> print(payload)
        {'user_id': 1, 'phone_number': '0501234567', 'exp': ...}
    """
    try:
        # Decode and verify token
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Check if token has expired
        exp = payload.get('exp')
        if exp and datetime.utcnow() > datetime.fromtimestamp(exp):
            logger.warning("Token has expired")
            return None
        
        logger.info(f"Token verified for user_id: {payload.get('user_id')}")
        return payload
        
    except JWTError as e:
        logger.warning(f"Invalid token: {e}")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {e}")
        return None


def decode_token_without_verification(token: str) -> Optional[Dict]:
    """
    Decode JWT token WITHOUT verification (for debugging only)
    
    WARNING: This does NOT verify the token signature!
    Only use for debugging or getting token info before verification.
    
    Args:
        token: JWT token string
    
    Returns:
        Decoded payload or None if invalid format
    """
    try:
        payload = jwt.decode(
            token,
            options={"verify_signature": False}
        )
        return payload
    except Exception as e:
        logger.error(f"Error decoding token: {e}")
        return None


def get_token_expiration(token: str) -> Optional[datetime]:
    """
    Get expiration datetime from token
    
    Args:
        token: JWT token string
    
    Returns:
        Expiration datetime or None if token is invalid
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        exp = payload.get('exp')
        if exp:
            return datetime.fromtimestamp(exp)
        return None
        
    except Exception as e:
        logger.error(f"Error getting token expiration: {e}")
        return None


def is_token_expired(token: str) -> bool:
    """
    Check if token is expired
    
    Args:
        token: JWT token string
    
    Returns:
        True if expired, False if still valid
    """
    try:
        expiration = get_token_expiration(token)
        if expiration is None:
            return True
        return datetime.utcnow() > expiration
    except Exception:
        return True


def refresh_token(old_token: str) -> Optional[str]:
    """
    Generate a new token from an old (but valid) token
    
    Args:
        old_token: Current JWT token
    
    Returns:
        New JWT token or None if old token is invalid
        
    Note:
        This creates a new token with updated expiration time
        while keeping the same user data
    """
    try:
        # Verify old token
        payload = verify_token(old_token)
        
        if not payload:
            logger.warning("Cannot refresh: invalid token")
            return None
        
        # Create new token with same user data
        user_data = {
            'id': payload.get('user_id'),
            'phone_number': payload.get('phone_number')
        }
        
        new_token = generate_token(user_data)
        logger.info(f"Token refreshed for user_id: {user_data['id']}")
        
        return new_token
        
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        return None


def extract_user_id_from_token(token: str) -> Optional[int]:
    """
    Extract user ID from token without full verification
    Useful for logging or quick checks
    
    Args:
        token: JWT token string
    
    Returns:
        User ID or None
    """
    try:
        payload = decode_token_without_verification(token)
        return payload.get('user_id') if payload else None
    except Exception:
        return None


def create_token_for_testing(user_id: int, phone_number: str) -> str:
    """
    Create a token for testing purposes
    
    Args:
        user_id: User ID
        phone_number: Phone number
    
    Returns:
        JWT token
        
    Note:
        Only use this in test environments!
    """
    user_data = {
        'id': user_id,
        'phone_number': phone_number
    }
    return generate_token(user_data)
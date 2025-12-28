"""
Auth Client - Communicates with Auth Service
WITH CACHING for better performance
"""

import httpx
from app.core.config import get_settings
import logging
from functools import lru_cache
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
settings = get_settings()

# Simple in-memory cache for validated tokens
# In production, use Redis for distributed caching
_token_cache = {}


async def validate_token_with_auth_service(token: str, use_cache: bool = True) -> dict:
    """
    Validate JWT token by calling auth service
    
    Args:
        token: JWT token string
        use_cache: Whether to use cached results
        
    Returns:
        dict with user_id and phone_number if valid
    """
    
    # Check cache first
    if use_cache and token in _token_cache:
        cached_data, cached_time = _token_cache[token]
        # Cache valid for 5 minutes
        if datetime.now() - cached_time < timedelta(minutes=5):
            logger.info(f"Token found in cache for user_id: {cached_data.get('user_id')}")
            return cached_data
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/validate-token",
                json={"token": token}
            )
            
            if response.status_code != 200:
                logger.warning(f"Auth service returned status {response.status_code}")
                return None
            
            data = response.json()
            
            if data.get("valid"):
                user_data = {
                    "user_id": data.get("user_id"),
                    "phone_number": data.get("phone_number")
                }
                
                # Store in cache
                _token_cache[token] = (user_data, datetime.now())
                
                # Limit cache size (prevent memory leak)
                if len(_token_cache) > 1000:
                    # Remove oldest entries
                    oldest_tokens = sorted(_token_cache.keys(), 
                                         key=lambda k: _token_cache[k][1])[:100]
                    for old_token in oldest_tokens:
                        del _token_cache[old_token]
                
                logger.info(f"Token validated for user_id: {user_data.get('user_id')}")
                return user_data
            else:
                logger.warning("Token validation failed")
                return None
                
    except httpx.TimeoutException:
        logger.error("Auth service timeout")
        return None
    except httpx.RequestError as e:
        logger.error(f"Auth service connection error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error validating token: {e}")
        return None


def clear_token_cache():
    """Clear the token cache (useful for testing)"""
    global _token_cache
    _token_cache = {}
    logger.info("Token cache cleared")
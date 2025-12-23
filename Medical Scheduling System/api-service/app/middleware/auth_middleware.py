from fastapi import HTTPException, status, Header
import httpx
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

async def verify_token(authorization: str = Header(None)) -> dict:
    """Verify JWT token with auth service"""
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization header provided"
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )
    
    try:
        # Extract token
        token = authorization.replace("Bearer ", "")
        
        # Call auth service to validate
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{settings.AUTH_SERVICE_URL}/auth/validate-token",
                json={"token": token}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token validation failed"
                )
            
            data = response.json()
            
            if data.get("valid"):
                logger.info(f"Token validated for user_id: {data.get('user_id')}")
                return {
                    "user_id": data.get("user_id"),
                    "phone_number": data.get("phone_number")
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=data.get("error", "Invalid token")
                )
                
    except httpx.TimeoutException:
        logger.error("Auth service timeout")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service is currently unavailable"
        )
    except httpx.RequestError as e:
        logger.error(f"Auth service connection error: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to authentication service"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication error"
        )
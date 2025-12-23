from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "api-service"
    PORT: int = 8001
    DEBUG: bool = True
    
    # Database
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "medical_scheduling"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    
    # Connection Pool
    DB_POOL_MIN_CONN: int = 5
    DB_POOL_MAX_CONN: int = 20
    
    # Auth Service
    AUTH_SERVICE_URL: str = "http://localhost:8000"
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
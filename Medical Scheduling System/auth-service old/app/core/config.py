from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Service
    SERVICE_NAME: str = "auth-service"
    PORT: int = 8000
    DEBUG: bool = True
    
    # # Database
    # DB_HOST: str = "localhost"
    # DB_PORT: int = 5432
    # DB_NAME: str = "medical_scheduling"
    # DB_USER: str = "postgres"
    # DB_PASSWORD: str = "postgres"
    
    # JWT
    JWT_SECRET_KEY: str = "your-secret-key-change-this"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 10080  # 7 days
    
    # OTP
    OTP_EXPIRATION_MINUTES: int = 5
    OTP_LENGTH: int = 6
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()
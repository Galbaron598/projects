import os
from typing import Dict

# Configuration
JWT_SECRET = os.getenv('JWT_SECRET', 'your-super-secret-jwt-key-change-in-production')
OTP_EXPIRY_MINUTES = 5
JWT_EXPIRY_DAYS = 7
JWT_ALGORITHM = "HS256"

# In-memory storage (replaces database)
otp_store: Dict[str, Dict] = {}
user_sessions: Dict[str, Dict] = {}
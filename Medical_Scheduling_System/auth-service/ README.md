# Medical Scheduling Auth Service - Modular Structure

A well-structured FastAPI authentication service with OTP and JWT, organized into separate modules for maintainability and scalability.

## 📁 Project Structure

```
auth-service/
│
├── main.py                          # Entry point - runs the server
│
├── app/
│   ├── __init__.py                  # App package initializer
│   ├── main.py                      # FastAPI app & CORS config
│   │
│   ├── core/                        # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py                # Configuration & storage
│   │   └── security.py              # JWT validation & dependencies
│   │
│   ├── models/                      # Data models
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic models
│   │
│   ├── routes/                      # API endpoints
│   │   ├── __init__.py
│   │   └── auth.py                  # Authentication routes
│   │
│   └── utils/                       # Utility functions
│       ├── __init__.py
│       └── auth_utils.py            # OTP & JWT generation
│
├── test_auth.py                     # Test script
├── requirements.txt                 # Dependencies
├── .env.example                     # Environment template
├── .gitignore                       # Git exclusions
└── README.md                        # This file
```

## 📦 File Descriptions

### Root Level

- **main.py** - Application entry point that starts uvicorn server
- **test_auth.py** - Automated test suite
- **requirements.txt** - Python package dependencies
- **.env.example** - Environment variables template
- **.gitignore** - Files to exclude from git

### app/

- **main.py** - FastAPI application initialization and CORS setup

### app/core/

- **config.py** - Application configuration and in-memory storage
- **security.py** - JWT token validation and authentication dependencies

### app/models/

- **schemas.py** - Pydantic models for request/response validation
  - RequestOTPRequest
  - VerifyOTPRequest
  - OTPResponse
  - VerifyOTPResponse
  - UserInfo
  - UserResponse
  - MessageResponse
  - HealthResponse

### app/routes/

- **auth.py** - Authentication endpoints
  - POST /api/auth/request-otp
  - POST /api/auth/verify-otp
  - GET /api/auth/me
  - POST /api/auth/logout
  - GET /api/auth/health

### app/utils/

- **auth_utils.py** - Helper functions
  - generate_otp() - Creates 6-digit OTP
  - generate_token() - Creates JWT token

## 🚀 Installation & Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv

# Activate on Windows:
venv\Scripts\activate

# Activate on macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment (Optional)

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run the Server

```bash
# Using main.py (recommended)
python main.py

# Or using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Test the Service

```bash
source venv/bin/activate
python3 test_auth.py
```

## 📡 API Endpoints

### POST /api/auth/request-otp
Request OTP for phone number

**Request:**
```json
{
  "phoneNumber": "+1234567890"
}
```

**Response:**
```json
{
  "message": "OTP sent successfully",
  "debug": {
    "otp": "123456",
    "expiresIn": "5 minutes"
  }
}
```

### POST /api/auth/verify-otp
Verify OTP and get JWT token

**Request:**
```json
{
  "phoneNumber": "+1234567890",
  "otp": "123456"
}
```

**Response:**
```json
{
  "message": "Authentication successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "phoneNumber": "+1234567890",
    "isNewUser": true,
    "createdAt": "2024-01-15T10:30:00.000000"
  }
}
```

### GET /api/auth/me
Get current user info (Protected)

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

**Response:**
```json
{
  "user": {
    "phoneNumber": "+1234567890",
    "createdAt": "2024-01-15T10:30:00.000000",
    "isNewUser": false
  }
}
```

### POST /api/auth/logout
Logout user (Protected)

**Headers:**
```
Authorization: Bearer <JWT_TOKEN>
```

### GET /api/auth/health
Health check endpoint

**Response:**
```json
{
  "status": "OK",
  "timestamp": "2024-01-15T10:30:00.000000",
  "activeOTPs": 3,
  "activeUsers": 5
}
```

## 🧪 Testing

### Run Automated Tests
```bash
python test_auth.py
```

### Interactive API Docs
Open in browser:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Manual Testing with cURL

```bash
# 1. Request OTP
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+1234567890"}'

# 2. Verify OTP
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "+1234567890", "otp": "123456"}'

# 3. Get user info
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🏗️ Adding New Features

### 1. Add New Route

Create a new file in `app/routes/`:

```python
# app/routes/appointments.py
from fastapi import APIRouter, Depends
from app.core.security import get_current_user

router = APIRouter()

@router.get("/")
async def get_appointments(current_user: str = Depends(get_current_user)):
    return {"appointments": []}
```

Register in `app/main.py`:

```python
from app.routes import auth, appointments

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(appointments.router, prefix="/api/appointments", tags=["Appointments"])
```

### 2. Add New Model

Add to `app/models/schemas.py`:

```python
class Appointment(BaseModel):
    id: int
    doctor: str
    dateTime: str
```

### 3. Add Utility Function

Add to `app/utils/`:

```python
# app/utils/email_utils.py
def send_email(to: str, subject: str, body: str):
    # Email logic here
    pass
```

## 🔒 Security Best Practices

### Development
- ✅ OTP shown in console/response for testing
- ✅ In-memory storage (no database)
- ✅ CORS enabled for all origins

### Production
- 🔐 Use environment variables for `JWT_SECRET`
- 🔐 Implement SMS gateway (Twilio, AWS SNS)
- 🔐 Remove `debug` from OTP response
- 🔐 Add rate limiting
- 🔐 Use HTTPS only
- 🔐 Restrict CORS to specific origins
- 🔐 Add database for persistence
- 🔐 Implement refresh tokens
- 🔐 Add logging and monitoring

## 🎯 Why This Structure?

### Separation of Concerns
- **Routes**: Handle HTTP requests
- **Models**: Define data structures
- **Utils**: Reusable functions
- **Core**: Configuration & security

### Benefits
- ✅ Easy to test individual components
- ✅ Clear organization for team collaboration
- ✅ Simple to add new features
- ✅ Easier to maintain and debug
- ✅ Follows FastAPI best practices

## 📝 Environment Variables

Create `.env` file:

```env
JWT_SECRET=your-super-secret-jwt-key-change-in-production
PORT=8000
ENVIRONMENT=development
```

## 🚀 Deployment

### Using Uvicorn
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Using Gunicorn
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📄 License

MIT License - Free to use for your Medical Scheduling System assignment!
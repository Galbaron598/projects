# Medical Scheduling System - Authentication Service

A lightweight **FastAPI authentication microservice** that provides OTP-based phone authentication with JWT tokens. This service is designed for simplicity and demonstration purposes, using **in-memory storage** instead of a database.

## 🎯 Purpose

This authentication service is a **standalone microservice** that:
- ✅ Generates and verifies OTP (One-Time Password) codes
- ✅ Issues JWT tokens for authenticated users
- ✅ Validates tokens for protected routes
- ✅ Runs independently from the main API service

**Architecture**: Microservices pattern with separate auth and API services.

---

## 🚀 Features

### Core Functionality
- **OTP Generation**: 6-digit codes with configurable expiry
- **OTP Verification**: Secure verification with automatic cleanup
- **JWT Token Generation**: Stateless authentication tokens
- **Token Validation**: Endpoint for other services to validate tokens
- **Session Management**: In-memory user session tracking
- **Logout**: Token invalidation endpoint

### Technical Highlights
- ✅ **No Database Required**: In-memory storage for simplicity
- ✅ **Fast Startup**: No migrations or database setup
- ✅ **Stateless JWT**: Self-contained authentication tokens
- ✅ **CORS Enabled**: Works with frontend on different ports
- ✅ **Swagger UI**: Interactive API documentation
- ✅ **Type Safety**: Pydantic schemas for request/response validation

---

## 🛠️ Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **FastAPI** | Web Framework | ^0.104.0 |
| **Pydantic** | Data Validation | ^2.0.0 |
| **PyJWT** | JWT Tokens | ^2.8.0 |
| **Uvicorn** | ASGI Server | ^0.24.0 |
| **Python** | Runtime | 3.9+ |

---

## 📦 Installation & Setup

### Prerequisites

- **Python** 3.9 or higher
- **pip** (Python package manager)
- **Virtual environment** (recommended)

Check your Python version:
```bash
python --version  # or python3 --version
```

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd auth-service
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate

# You should see (venv) in your terminal prompt
```

### Step 3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
# Check installed packages
pip list

Should see:
fastapi
uvicorn
pydantic
PyJWT
python-jose
passlib
```

---

## 🚀 Running the Service

### Development Mode (with auto-reload)

```bash
# Default: runs on port 8000
uvicorn main:app --reload

# With custom port
uvicorn main:app --reload --port 8000

# With custom host (for network access)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# With logs
uvicorn main:app --reload --log-level info
```

Expected output:
```
INFO:     Will watch for changes in these directories: ['/path/to/auth-service']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Started server process [12346]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Using Python Script

```bash
# If you have a run script
python main.py

# Or with Python module
python -m uvicorn main:app --reload
```

```

**Note**: In production, the OTP would be sent via SMS. For testing, it's displayed in the response and server console.

#### 2. Verify OTP

```http
POST /api/auth/verify-otp
Content-Type: application/json

{
  "phoneNumber": "0501234567",
  "otp": "123456"
}
```

**Response** (200 OK):
```json
{
  "message": "Authentication successful",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "phoneNumber": "0501234567",
    "isNewUser": true,
    "createdAt": "2024-12-30T10:00:00Z"
  }
}
```

#### 3. Validate Token (Internal Use)

```http
POST /api/auth/validate-token
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response** (200 OK):
```json
{
  "valid": true,
  "phoneNumber": "0501234567"
}
```

#### 4. Logout

```http
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response** (200 OK):
```json
{
  "message": "Logged out successfully"
}
```

---

## 🔗 Connecting from Frontend

### Configuration

In your frontend `.env` file:

```env
# Auth Service (Port 8000)
VITE_AUTH_SERVICE_URL=http://localhost:8000

# API Service (Port 8001)
VITE_API_SERVICE_URL=http://localhost:8001
```

### API Service Setup (axios)

```javascript
// src/services/api.js
import axios from 'axios'

const AUTH_SERVICE_URL = import.meta.env.VITE_AUTH_SERVICE_URL || 'http://localhost:8000'

const authService = axios.create({
  baseURL: AUTH_SERVICE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 10000,
})

// Example: Request OTP
export const requestOTP = async (phoneNumber) => {
  const response = await authService.post('/api/auth/request-otp', {
    phoneNumber
  })
  return response.data
}

// Example: Verify OTP
export const verifyOTP = async (phoneNumber, otp) => {
  const response = await authService.post('/api/auth/verify-otp', {
    phoneNumber,
    otp
  })
  return response.data
}
```

### Usage in React Component

```javascript
import { requestOTP, verifyOTP } from './services/api'

// Request OTP
const handleRequestOTP = async () => {
  try {
    const data = await requestOTP('0501234567')
    console.log('OTP:', data.debug.otp) // For testing
    message.success('OTP sent!')
  } catch (error) {
    message.error('Failed to send OTP')
  }
}

// Verify OTP
const handleVerifyOTP = async () => {
  try {
    const data = await verifyOTP('0501234567', '123456')
    localStorage.setItem('token', data.token)
    navigate('/dashboard')
  } catch (error) {
    message.error('Invalid OTP')
  }
}
```

---

## 🔐 JWT Token Structure

### What's in the Token?

The JWT token contains:

```json
{
  "sub": "0501234567",      // Subject (phone number)
  "exp": 1735567200,        // Expiration timestamp
  "iat": 1735563600,        // Issued at timestamp
  "type": "access"          // Token type
}
```

### Current Implementation

**For this assignment**, the JWT token is used **only for authentication**:
- ✅ Verify user is logged in
- ✅ Protect routes from unauthorized access
- ✅ Validate requests to API service

### Production Considerations

In a production system, the JWT would typically include:

```json
{
  "sub": "0501234567",           // Phone number
  "user_id": 123,                // Database user ID
  "patient_id": 456,             // Patient record ID
  "roles": ["patient"],          // User roles
  "permissions": ["book", "view"], // Permissions
  "exp": 1735567200,
  "iat": 1735563600
}
```

**Why not include it now?**
- ✅ **Simplicity**: No database to query user info from
- ✅ **Demonstration**: Shows understanding of both approaches
- ✅ **Time constraint**: 10-hour assignment scope
- ✅ **Works for requirements**: Current flow is sufficient

**Migration path**: When adding a database, simply include `patient_id` in the token payload, and the frontend can extract it without additional API calls.

---

## 🗄️ Storage Architecture

### In-Memory Storage (Current)

This service uses **Python dictionaries** for storage:

```python
# OTP Storage (temporary)
otp_store = {
    "0501234567": {
        "otp": "123456",
        "expires_at": datetime(2024, 12, 30, 10, 5, 0),
        "verified": False
    }
}

# User Sessions (persistent during runtime)
user_sessions = {
    "0501234567": {
        "phone_number": "0501234567",
        "created_at": "2024-12-30T10:00:00Z",
        "appointments": []
    }
}
```

### Why No Database?

**For this assignment:**
- ✅ **Faster development**: No schema design/migrations needed
- ✅ **Simpler setup**: No database installation required
- ✅ **Meets requirements**: OTP and JWT authentication work perfectly
- ✅ **Easy testing**: Fresh state on every restart
- ✅ **Time efficient**: Focus on frontend/API integration

**Trade-offs:**
- ❌ Data lost on restart
- ❌ No data persistence
- ❌ Single-instance only (can't scale horizontally)
- ❌ No historical data

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```env
# JWT Configuration
JWT_SECRET_KEY=your-super-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=1440  # 24 hours

# OTP Configuration
OTP_LENGTH=6
OTP_EXPIRY_MINUTES=5

# Server Configuration
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=info

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Environment
ENVIRONMENT=development
DEBUG=true
```

---

## 🧪 Testing the Service

### Using curl

```bash
# 1. Request OTP
curl -X POST http://localhost:8000/api/auth/request-otp \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "0501234567"}'

# 2. Verify OTP (use OTP from previous response)
curl -X POST http://localhost:8000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"phoneNumber": "0501234567", "otp": "123456"}'

# 3. Validate Token
curl -X POST http://localhost:8000/api/auth/validate-token \
  -H "Content-Type: application/json" \
  -d '{"token": "YOUR_JWT_TOKEN"}'

# 4. Logout (replace with your token)
curl -X POST http://localhost:8000/api/auth/logout \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using Postman

1. **Import Collection**: Create new collection "Auth Service"
2. **Add Requests**: Create requests for each endpoint
3. **Environment Variables**: Set `{{base_url}}` = `http://localhost:8000`
4. **Test Flow**:
   - Request OTP
   - Copy OTP from response
   - Verify OTP
   - Save token from response
   - Use token for logout

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000/api/auth"

# Request OTP
response = requests.post(f"{BASE_URL}/request-otp", json={
    "phoneNumber": "0501234567"
})
otp = response.json()["debug"]["otp"]
print(f"OTP: {otp}")

# Verify OTP
response = requests.post(f"{BASE_URL}/verify-otp", json={
    "phoneNumber": "0501234567",
    "otp": otp
})
token = response.json()["token"]
print(f"Token: {token}")

# Validate Token
response = requests.post(f"{BASE_URL}/validate-token", json={
    "token": token
})
print(response.json())
```

---


---


---

## 🔐 Security Considerations

### Current Implementation

- ✅ **JWT Tokens**: Stateless authentication
- ✅ **OTP Expiry**: 5-minute timeout
- ✅ **Token Expiry**: 24-hour validity
- ✅ **HTTPS Ready**: Works with SSL/TLS
- ✅ **CORS Configured**: Prevents unauthorized origins

### Production Hardening

---

## 📝 Development Notes

### Design Decisions

1. **Why FastAPI?**
   - Fast development
   - Automatic API documentation
   - Built-in validation (Pydantic)
   - Async support
   - Type hints

2. **Why In-Memory Storage?**
   - Simplifies assignment
   - No database setup needed
   - Faster development
   - Demonstrates understanding without overengineering

3. **Why Separate Auth Service?**
   - Microservices best practice
   - Independent scaling
   - Security isolation
   - Clear separation of concerns

4. **Why Port 8000?**
   - FastAPI convention
   - Avoids conflicts with other services
   - Easy to remember (Auth = 8000, API = 8001)

---

## 👨‍💻 Author

Gal Baron
---

## 📞 Support

For issues or questions:
1. Check Swagger UI at http://localhost:8000/docs
2. Review FastAPI docs: https://fastapi.tiangolo.com
3. Check server console logs


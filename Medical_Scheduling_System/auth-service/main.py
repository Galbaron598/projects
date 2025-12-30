from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth

# Initialize FastAPI app
app = FastAPI(
    title="Medical Scheduling Auth Service",
    description="Authentication service with OTP and JWT",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Medical Scheduling Auth Service",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "request_otp": "POST /api/auth/request-otp",
            "verify_otp": "POST /api/auth/verify-otp",
            "get_user": "GET /api/auth/profile",
            "logout": "POST /api/auth/logout",
            "health": "GET /api/auth/health"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

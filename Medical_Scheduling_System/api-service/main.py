from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import appointments, doctors, medical_fields, patients
from app.core.config import get_settings
from app.core.database import DatabasePool
import logging
# import debugpy

# debugpy.listen(("0.0.0.0", 5678))
# print("✅ API debugpy listening on 5678")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="Medical Scheduling - API Service",
    description="Main API for medical appointments and doctor management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        settings.FRONTEND_URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(medical_fields.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(patients.router)

@app.on_event("startup")
async def startup_event():
    """Initialize connection pool on startup"""
    logger.info("Starting API Service...")
    DatabasePool.get_pool()
    logger.info("Database connection pool initialized")

@app.on_event("shutdown")
async def shutdown_event():
    """Close connection pool on shutdown"""
    logger.info("Shutting down API Service...")
    DatabasePool.close_pool()
    logger.info("Database connection pool closed")

@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import appointments, doctors, medical_fields, patients
from app.core.config import get_settings
from app.core.database import close_db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Modern replacement for @app.on_event startup/shutdown (deprecated)."""
    logger.info("Starting API Service...")
    # Engine is created at import time in app.core.database
    logger.info("Database engine ready (SQLAlchemy)")
    try:
        yield
    finally:
        logger.info("Shutting down API Service...")
        close_db()  # engine.dispose()
        logger.info("Database engine disposed")


app = FastAPI(
    title="Medical Scheduling - API Service",
    description="Main API for medical appointments and doctor management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        settings.FRONTEND_URL,
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


@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": settings.SERVICE_NAME}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )

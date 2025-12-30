from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from contextlib import contextmanager
from typing import Generator
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create the declarative base - THIS IS WHAT YOUR MODELS NEED
Base = declarative_base()

# Build database URL
DATABASE_URL = (
    f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}"
    f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
)

# Create engine with connection pooling (replaces psycopg2 pool)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=settings.DB_POOL_MIN_CONN,  # Minimum connections in pool
    max_overflow=settings.DB_POOL_MAX_CONN - settings.DB_POOL_MIN_CONN,  # Additional connections
    echo=False,  # Set to True to see SQL queries in logs
    pool_recycle=3600,  # Recycle connections after 1 hour
)

# Create SessionLocal class (replaces your cursor-based connections)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Auto-commit on success
    except Exception as e:
        db.rollback()  # Auto-rollback on error
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


@contextmanager
def get_db_context():
    """
    Context manager for database session (non-FastAPI usage)
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully!")


def drop_db():
    Base.metadata.drop_all(bind=engine)
    logger.info("Database tables dropped!")


def close_db():
    """
    Close database connection pool
    Call this on application shutdown
    """
    engine.dispose()
    logger.info("Database connection pool closed")


# Log successful initialization
logger.info(
    f"Database connection pool initialized "
    f"(pool_size={settings.DB_POOL_MIN_CONN}, "
    f"max_overflow={settings.DB_POOL_MAX_CONN - settings.DB_POOL_MIN_CONN})"
)
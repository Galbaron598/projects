
import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class DatabasePool:
    """Singleton connection pool for better performance"""
    _pool = None
    
    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            try:
                cls._pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=settings.DB_POOL_MIN_CONN,
                    maxconn=settings.DB_POOL_MAX_CONN,
                    host=settings.DB_HOST,
                    port=settings.DB_PORT,
                    database=settings.DB_NAME,
                    user=settings.DB_USER,
                    password=settings.DB_PASSWORD,
                    cursor_factory=RealDictCursor
                )
                logger.info(f"Database connection pool created (min={settings.DB_POOL_MIN_CONN}, max={settings.DB_POOL_MAX_CONN})")
            except Exception as e:
                logger.error(f"Failed to create database pool: {e}")
                raise
        return cls._pool
    
    @classmethod
    def close_pool(cls):
        if cls._pool:
            cls._pool.closeall()
            cls._pool = None
            logger.info("Database connection pool closed")

@contextmanager
def get_db():
    """Get database connection from pool"""
    pool = DatabasePool.get_pool()
    conn = pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        pool.putconn(conn)
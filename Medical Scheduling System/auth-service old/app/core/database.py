# import psycopg2
# from psycopg2.extras import RealDictCursor
# from contextlib import contextmanager
# from app.core.config import get_settings

# settings = get_settings()

# def get_db_connection():
#     """Create database connection"""
#     return psycopg2.connect(
#         host=settings.DB_HOST,
#         port=settings.DB_PORT,
#         database=settings.DB_NAME,
#         user=settings.DB_USER,
#         password=settings.DB_PASSWORD,
#         cursor_factory=RealDictCursor
#     )

# @contextmanager
# def get_db():
#     """Context manager for database connections"""
#     conn = get_db_connection()
#     try:
#         yield conn
#         conn.commit()
#     except Exception:
#         conn.rollback()
#         raise
#     finally:
#         conn.close()
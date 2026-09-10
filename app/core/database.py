# app/core/database.py
"""
Cấu hình kết nối Cơ Sở Dữ Liệu Hỗ Trợ Linh Hoạt (Dual-Database Architecture):
1. SQLite (Development & Local Standalone): Chế độ WAL mode, busy_timeout 30s, foreign keys ON.
2. PostgreSQL / MySQL (Production & Centralized Server): Connection Pooling (10-20 connections), pool_pre_ping, pool_recycle.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if is_sqlite:
    # Cấu hình SQLite: check_same_thread=False cho đa luồng FastAPI
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
        pool_pre_ping=True
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        cursor.execute("PRAGMA journal_mode = WAL;")
        cursor.execute("PRAGMA busy_timeout = 30000;")
        cursor.close()

else:
    # Cấu hình PostgreSQL / MySQL: Connection Pooling tối ưu tải cao
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_recycle=3600,
        pool_pre_ping=True,
        echo=False
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency cung cấp database session cho từng request và tự động đóng sau khi kết thúc."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# C?u h?nh engine: SQLite c?n check_same_thread=False khi ch?y ?a lu?ng FastAPI
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency cung c?p database session cho t?ng request v? t? ??ng ??ng sau khi k?t th?c."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

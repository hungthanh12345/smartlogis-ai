import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SmartLogis AI - H? th?ng Qu?n l? Kho T?ch h?p AI"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Secret Key & JWT Config
    SECRET_KEY: str = os.getenv("SECRET_KEY", "smartlogis-secret-key-2026-secure-production-jwt-token")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 gi?
    
    # Database URL: M?c ??nh SQLite file c?c b? ?? ch?y ngay kh?ng c?n c?i ??t;
    # c? th? c?u h?nh PostgreSQL qua bi?n m?i tr??ng DATABASE_URL
    # V? d? PostgreSQL: postgresql://postgres:postgres@localhost:5432/smartlogis_db
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./smartlogis.db")
    
    # Google Gemini API
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()

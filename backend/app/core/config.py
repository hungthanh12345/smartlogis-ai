import os
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_curr_dir = os.path.dirname(os.path.abspath(__file__))
_backend_dir = os.path.dirname(os.path.dirname(_curr_dir))
_root_dir = os.path.dirname(_backend_dir)
_env_files = tuple(dict.fromkeys([
    os.path.join(_backend_dir, ".env"),
    os.path.join(_root_dir, ".env"),
    os.path.join(os.getcwd(), ".env"),
    os.path.join(os.getcwd(), "backend", ".env"),
    ".env"
]))

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=_env_files,
        env_file_encoding="utf-8",
        extra="allow"
    )

    # Application Info & Environment
    PROJECT_NAME: str = "SmartLogis AI - Hệ thống Quản lý Kho Thông minh Tích hợp AI"
    VERSION: str = "4.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug_bool(cls, v):
        if isinstance(v, str):
            return v.lower() in ("true", "1", "yes", "t", "dev", "development")
        return bool(v)

    # Server & Network Endpoints
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    BASE_URL: str = "http://localhost:8000"
    SERVER_DOMAIN: str = "smartlogis-ai.com"
    
    # API & WebSocket Endpoints
    API_V1_STR: str = "/api/v1"
    API_DOCS_URL: str = "/docs"
    API_REDOC_URL: str = "/redoc"
    WEBSOCKET_ENDPOINT: str = "/ws/inventory"
    
    # Secret Key & JWT Config
    SECRET_KEY: str = "smartlogis-super-secret-key-2026-production-ready"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 giờ
    
    # Database Connection Parameters
    DATABASE_URL: str = "sqlite:///./smartlogis.db"
    DB_TYPE: str = "sqlite"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "smartlogis_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgrespassword"
    
    # Database Connection Pooling
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True
    
    # Google Gemini AI API Configuration & Endpoints
    GEMINI_API_KEY: str = ""
    GEMINI_API_ENDPOINT: str = "https://generativelanguage.googleapis.com/v1beta"
    GEMINI_MODEL: str = "gemini-2.0-flash"
    GEMINI_FALLBACK_MODEL: str = "gemini-1.5-flash"
    AI_TIMEOUT_SECONDS: float = 20.0
    AI_MAX_RETRIES: int = 3
    
    # Database Management Tool (pgAdmin 4)
    PGADMIN_PORT: int = 5050
    PGADMIN_DEFAULT_EMAIL: str = "admin@smartlogis.vn"
    PGADMIN_DEFAULT_PASSWORD: str = "adminpassword"

settings = Settings()

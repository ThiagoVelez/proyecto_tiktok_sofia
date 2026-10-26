"""
Configuración centralizada y tipada del sistema mediante variables de entorno (Pydantic Settings).
Incluye soporte para MySQL, Redis, Object Storage (S3/MinIO), Rate Limiting y Seguridad.
"""

import os
from pathlib import Path
from typing import List, Optional, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Entorno
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Red y Servidor
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:5173", "http://127.0.0.1:5173"]

    # MySQL Database Config
    DATABASE_URL: Optional[str] = None
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "proyecto_sofia"

    # Redis Config (Caché, Rate Limit y Pub/Sub de WebSockets)
    REDIS_HOST: str = "127.0.0.1"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_ENABLED: bool = True

    # Seguridad y Criptografía JWT
    SECRET_KEY: str = "sofia_super_secret_jwt_key_2026_tiktok_clone"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    SECURITY_HEADERS_ENABLED: bool = True

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_LOGIN_PER_MINUTE: str = "10/minute"
    RATE_LIMIT_REGISTER_PER_MINUTE: str = "5/minute"
    RATE_LIMIT_PIN_PER_MINUTE: str = "5/minute"
    RATE_LIMIT_UPLOAD_PER_MINUTE: str = "10/minute"

    # Almacenamiento Multimedia (Local o S3/MinIO)
    STORAGE_BACKEND: str = "local"  # "local" o "s3"
    UPLOAD_DIR: str = str(BASE_DIR / "uploads")
    MAX_VIDEO_SIZE_MB: int = 100
    ALLOWED_VIDEO_EXTENSIONS: List[str] = ["mp4", "mov", "webm", "avi"]
    ALLOWED_IMAGE_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]

    # S3 / MinIO Object Storage Config
    S3_ENDPOINT_URL: Optional[str] = "http://127.0.0.1:9000"
    S3_ACCESS_KEY: Optional[str] = "minioadmin"
    S3_SECRET_KEY: Optional[str] = "minioadmin"
    S3_BUCKET_NAME: str = "proyecto-sofia-media"
    S3_REGION: str = "us-east-1"
    S3_PUBLIC_URL: Optional[str] = None

    # Parámetros de Control Parental por Defecto
    DEFAULT_SCREEN_TIME_LIMIT_MINS: int = 120
    DEFAULT_CURFEW_START: str = "22:00"
    DEFAULT_CURFEW_END: str = "06:00"

    @property
    def database_url(self) -> str:
        """Genera el Connection String para SQLAlchemy con driver PyMySQL."""
        if self.DATABASE_URL:
            url = str(self.DATABASE_URL)
            if url.startswith("mysql://"):
                url = url.replace("mysql://", "mysql+pymysql://", 1)
            return url
        pwd = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return f"mysql+pymysql://{self.DB_USER}{pwd}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def redis_url(self) -> str:
        """Genera la URL de conexión a Redis."""
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        return v

    class Config:
        env_file = str(BASE_DIR / ".env")
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()

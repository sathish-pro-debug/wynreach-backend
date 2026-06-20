from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
class Settings(BaseSettings):
    MAIN_DB_URL: str
    LOG_DB_URL: str = ""
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    APP_NAME: str = "Wynreach"
    DEBUG: bool = True
    FRONTEND_URL: str = "http://localhost:5173"
    # AWS SES Settings
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-south-1"
    SES_FROM_EMAIL: Optional[str] = None
    # AWS S3 Settings for Template Images
    AWS_ACCESS_KEY_ID_EMAIL: Optional[str] = None
    AWS_SECRET_ACCESS_KEY_EMAIL: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_REGION: str = "ap-south-1"
    # Image Upload Settings
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/gif", "image/webp"]
    # WhatsApp Settings
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_ACCESS_TOKEN: Optional[str] = None
    WHATSAPP_WABA_ID: Optional[str] = None
    WHATSAPP_API_VERSION: str = "v20.0"
    # Metrics
    METRICS_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    PROMETHEUS_ENABLED: bool = False
    # Redis for metrics aggregation
    REDIS_URL: Optional[str] = None
    ENABLE_REDIS_METRICS: bool = False
    # Cache TTL for metrics summary (seconds)
    METRICS_CACHE_TTL: int = 5
    # IP allowlist for metrics endpoints (comma-separated)
    METRICS_IP_ALLOWLIST: Optional[str] = None
    # Trusted header for client IP when behind proxy (e.g., X-Forwarded-For)
    METRICS_TRUSTED_HEADER: Optional[str] = "X-Forwarded-For"
    class Config:
        env_file = ".env"
        extra = "ignore"
@lru_cache()
def get_settings():
    return Settings()
settings = get_settings()

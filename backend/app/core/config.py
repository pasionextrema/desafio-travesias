import os
import re
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "DesafioDeTravesias"
    app_env: str = "development"
    app_debug: bool = True
    secret_key: str
    backend_port: int = 8000

    database_url: str = ""
    database_private_url: str = ""
    database_url_sync: str = ""

    redis_url: str = "redis://localhost:6379/0"
    redis_private_url: str = ""

    def _get_raw_db_url(self) -> str:
        for key in ("DATABASE_PRIVATE_URL", "DATABASE_URL", "database_private_url", "database_url"):
            val = os.environ.get(key, "")
            if val and "postgres" in val:
                return val
        return self.database_url or self.database_private_url

    def _ensure_async_db_url(self) -> str:
        url = self._get_raw_db_url()
        if not url:
            return ""
        url = url.replace("postgres://", "postgresql://", 1)
        if "+asyncpg" in url:
            return url
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if "sslmode" not in url:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}sslmode=disable"
        return url

    def _ensure_sync_db_url(self) -> str:
        url = self._get_raw_db_url()
        if not url:
            return ""
        return re.sub(r"\+\w+", "", url, count=1)

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    frontend_url: str = "http://localhost:5173"

    google_client_id: str | None = None
    google_client_secret: str | None = None
    microsoft_client_id: str | None = None
    microsoft_client_secret: str | None = None
    facebook_client_id: str | None = None
    facebook_client_secret: str | None = None

    youtube_api_key: str | None = None
    youtube_channel_id: str | None = None

    deepseek_api_key: str | None = None
    deepseek_base_url: str = "https://api.deepseek.com"

    sendgrid_api_key: str | None = None
    from_email: str = "noreply@pasionextrema.org"

    paypal_client_id: str | None = None
    paypal_client_secret: str | None = None
    paypal_mode: str = "sandbox"

    stripe_secret_key: str | None = None
    stripe_webhook_secret: str | None = None

    cloudinary_cloud_name: str | None = None
    cloudinary_api_key: str | None = None
    cloudinary_api_secret: str | None = None

    fcm_server_key: str | None = None

    sentry_dsn: str | None = None

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache
def get_settings() -> Settings:
    return Settings()

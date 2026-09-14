from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any
import json

class Settings(BaseSettings):
    SUPABASE_URL: str = "http://localhost:54321"
    SUPABASE_ANON_KEY: str = "dummy_anon_key"
    SUPABASE_SERVICE_KEY: str = "dummy_service_key"
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CORS_ORIGINS: Any = ["http://localhost:5173", "http://localhost:3000", "*"]
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    @property
    def cors_list(self) -> list[str]:
        val = self.CORS_ORIGINS
        origins: list[str] = []
        if isinstance(val, list):
            origins = [str(x) for x in val]
        elif isinstance(val, str):
            if val.startswith("["):
                try:
                    origins = [str(x) for x in json.loads(val)]
                except Exception:
                    pass
            if not origins:
                origins = [i.strip() for i in val.split(",") if i.strip()]
        else:
            origins = ["*"]

        # Normalize: strip trailing slashes because Origin headers never have trailing slashes
        clean_origins = []
        for o in origins:
            cleaned = o.rstrip("/")
            if cleaned:
                clean_origins.append(cleaned)
        return clean_origins or ["*"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

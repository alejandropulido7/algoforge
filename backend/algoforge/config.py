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
        if isinstance(val, list):
            return [str(x) for x in val]
        if isinstance(val, str):
            if val.startswith("["):
                try:
                    return json.loads(val)
                except Exception:
                    pass
            return [i.strip() for i in val.split(",") if i.strip()]
        return ["*"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

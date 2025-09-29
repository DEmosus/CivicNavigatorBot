import os
import json
from pathlib import Path
from typing import List, Union, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyUrl, field_validator, model_validator

# Always resolve paths relative to backend/
BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env" if os.getenv("TESTING") != "1" else None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if ENV_FILE else None,
        env_file_encoding="utf-8",
    )

    # Environment
    ENV: str = "development"

    # Database
    DATABASE_URL: AnyUrl | str = f"sqlite:///{BASE_DIR}/dev.db"

    # JWT
    JWT_SECRET_KEY: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 24

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "https://civic-navigator-nine.vercel.app/"
    ]

    # Optional integrations
    SENTRY_DSN: Optional[str] = None
    AI_PROVIDER: str = "none"
    AI_API_KEY: Optional[str] = None

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def split_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @model_validator(mode="after")
    def check_jwt_secret(self) -> "Settings":
        if self.ENV == "production" and not self.JWT_SECRET_KEY:
            raise ValueError("JWT_SECRET_KEY must be set in production environment")
        if self.ENV == "development" and not self.JWT_SECRET_KEY:
            self.JWT_SECRET_KEY = None
        return self

    @model_validator(mode="after")
    def check_database_url(self) -> "Settings":
        # Ensure SQLite paths are always inside backend/
        if str(self.DATABASE_URL).startswith("sqlite:///./"):
            relative_path = str(self.DATABASE_URL).replace("sqlite:///./", "")
            self.DATABASE_URL = f"sqlite:///{BASE_DIR}/{relative_path}"

        if self.ENV == "production":
            if not self.DATABASE_URL or str(self.DATABASE_URL).endswith("dev.db"):
                raise ValueError(
                    "DATABASE_URL must be set to a production database in production environment"
                )
        return self


settings: Settings = Settings()

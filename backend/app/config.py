"""Application configuration (environment-driven, with sensible local defaults)."""
from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Repo layout: <root>/backend/app/config.py  ->  root = parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = BACKEND_DIR.parent
DATA_DIR = ROOT_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Integration layer ---
    crm_base_url: str = "http://localhost:3001"
    # Fallback file used when the JSON Server isn't reachable.
    crm_fallback_file: str = str(DATA_DIR / "crm_db.json")

    # --- Persistence ---
    database_url: str = f"sqlite:///{BACKEND_DIR / 'salesiq.db'}"

    # --- ML ---
    mlflow_tracking_uri: str = f"file:{BACKEND_DIR / 'mlruns'}"
    mlflow_experiment: str = "salesiq"
    model_dir: str = str(BACKEND_DIR / "models")

    # --- AI (Gemini) ---
    gemini_api_key: str | None = None
    gemini_model: str = "gemini-2.5-flash"

    # --- App ---
    app_name: str = "SalesIQ API"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()

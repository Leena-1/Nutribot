"""Backend configuration (environment-based) and paths."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent


class Settings(BaseSettings):
    """
    Environment-based settings for the FastAPI backend.

    Set values via environment variables or a local `.env` file (not committed).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="NUTRIBOT_",
        case_sensitive=False,
        extra="ignore",
    )

    # ---- Server / CORS ----
    environment: str = Field(default="dev", description="dev|staging|prod")
    cors_allow_origins: List[str] = Field(default_factory=lambda: ["*"])

    # ---- Paths (overrideable for deployments) ----
    unified_csv_path: Path = Field(
        default=PROJECT_ROOT / "datasets" / "processed" / "unified_food_features.csv"
    )
    food_model_dir: Path = Field(default=PROJECT_ROOT / "ml_model" / "saved_models" / "food_cnn")
    disease_model_dir: Path = Field(default=PROJECT_ROOT / "ml_model" / "saved_models" / "disease_model")
    food_mapping_path: Path = Field(default=PROJECT_ROOT / "ml_model" / "food_mapping.json")

    # ---- Rate limiting ----
    rate_limit_per_minute: int = Field(default=60, ge=1)

    # ---- Caching / Redis ----
    redis_url: Optional[str] = Field(default=None, description="e.g. redis://localhost:6379/0")
    cache_ttl_seconds: int = Field(default=3600, ge=1)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


# Backwards-compatible constants (older imports)
_s = get_settings()
UNIFIED_CSV = _s.unified_csv_path
FOOD_CNN_DIR = _s.food_model_dir
DISEASE_MODEL_DIR = _s.disease_model_dir

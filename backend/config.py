"""Application configuration loaded from environment variables and .env file."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """SkillBridge application settings.

    Reads from environment variables first, then falls back to .env file.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # --- AI ---
    ANTHROPIC_API_KEY: str = "not-set"
    AI_MODEL: str = "claude-sonnet-4-20250514"
    AI_MAX_TOKENS: int = 2000
    AI_TIMEOUT: int = 30

    # --- App ---
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    APP_TITLE: str = "SkillBridge Career Navigator"

    # --- Paths ---
    DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"

    # --- Health check ---
    HEALTH_CHECK_CACHE_TTL: int = 60

    @property
    def ai_configured(self) -> bool:
        return self.ANTHROPIC_API_KEY not in ("not-set", "your_key_here", "")


settings = Settings()

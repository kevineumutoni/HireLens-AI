"""
Configuration management for HireLens-AI backend.
Supports multiple Gemini API keys via GEMINI_API_KEYS (comma-separated).
Falls back to GEMINI_API_KEY if only one key is set.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """HireLens configuration."""

    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)

    GEMINI_API_KEYS_RAW: Optional[str] = os.getenv("GEMINI_API_KEYS", None)

    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"
    API_TIMEOUT_SECONDS: int = 60

    PREFERRED_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")
    FALLBACK_MODELS: List[str] = ["gemini-1.5-flash", "gemini-1.5-pro"]

    TEMPERATURE: float = 0.2
    MAX_OUTPUT_TOKENS: int = 4096

    TOP_N_CANDIDATES: int = 10
    BATCH_SIZE: int = 5
    REQUEST_DELAY_MS: int = 500

    MONGODB_URI: str = os.getenv("MONGODB_URI")
    MONGODB_DB: str = "hirelens"

    FRONTEND_URL: str = os.getenv("FRONTEND_URL")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    API_HOST: str = "0.0.0.0"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    @property
    def api_keys(self) -> List[str]:
        """
        Returns the full list of Gemini API keys to rotate through.
        Priority:
          1. GEMINI_API_KEYS  (comma-separated list)
          2. GEMINI_API_KEY   (single key fallback)
        """
        keys: List[str] = []

        if self.GEMINI_API_KEYS_RAW:
            for k in self.GEMINI_API_KEYS_RAW.split(","):
                k = k.strip()
                if k:
                    keys.append(k)

        if self.GEMINI_API_KEY and self.GEMINI_API_KEY not in keys:
            keys.append(self.GEMINI_API_KEY)

        return keys


settings = Settings()

_keys = settings.api_keys
if not _keys:
    print("WARNING: No GEMINI API keys found in environment")
else:
    print(f"Gemini API key pool: {len(_keys)} key(s) loaded")

# src/config/settings.py
"""
Configuration management for HireLens-AI backend.
Loads settings from .env file using Pydantic v2.
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """HireLens configuration - no hardcoded values, using latest Gemini models."""
    
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"
    API_TIMEOUT_SECONDS: int = 60
    
    # ==================== Model Selection ====================
    # LATEST available models (2.0-flash is DEPRECATED)
    PREFERRED_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    FALLBACK_MODELS: List[str] = ["gemini-1.5-flash", "gemini-1.5-pro"]
    
    TEMPERATURE: float = 0.2  # Very low for deterministic output
    MAX_OUTPUT_TOKENS: int = 2000
    
    TOP_N_CANDIDATES: int = 10
    BATCH_SIZE: int = 3
    
    REQUEST_DELAY_MS: int = 500  # 500ms between requests

    MONGODB_URI: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    MONGODB_DB: str = "hirelens"

    FRONTEND_URL: str = "http://localhost:3000"
    
    API_PORT: int = 8000
    API_HOST: str = "0.0.0.0"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # ← THIS ALLOWS EXTRA ENV VARIABLES


settings = Settings()

if not settings.GEMINI_API_KEY:
    print("⚠️  WARNING: GEMINI_API_KEY not found in .env")
    print("   Some AI features may not work without a valid Gemini API key")
    print("   Add GEMINI_API_KEY=your_key to your .env file to enable AI screening")
    print("   You can still test the API without the key")
else:
    print(f" Gemini API Key loaded (prefix: {settings.GEMINI_API_KEY[:10]}...)")

print(f"MongoDB: {settings.MONGODB_URI}")
print(f" Frontend URL: {settings.FRONTEND_URL}")
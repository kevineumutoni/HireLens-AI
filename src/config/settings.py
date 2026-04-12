# src/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """HireLens configuration - no hardcoded values."""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    API_TIMEOUT_SECONDS = 30
    
    # Model Selection (NEVER hardcoded)
    PREFERRED_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    FALLBACK_MODEL = "gemini-2.0-flash"
    
    # Generation Config
    TEMPERATURE = 0.3  # Low = consistent, unbiased
    MAX_OUTPUT_TOKENS = 4000
    
    # Screening Config
    TOP_N_CANDIDATES = 10
    BATCH_SIZE = 3

settings = Settings()

# Validate on startup
if not settings.GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env")
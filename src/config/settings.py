# src/config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB = "hirelens"
class Settings:
    """HireLens configuration - no hardcoded values, using latest Gemini models."""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    API_TIMEOUT_SECONDS = 60
    
    # Model Selection - LATEST available models (2.0-flash is DEPRECATED)
    # Try in order: 2.5-flash (latest) -> 1.5-flash (stable) -> 1.5-pro (fallback)
    PREFERRED_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    FALLBACK_MODELS = ["gemini-1.5-flash", "gemini-1.5-pro"]
    
    # Generation Config - tuned for consistent JSON
    TEMPERATURE = 0.2  # Very low for deterministic output
    MAX_OUTPUT_TOKENS = 2000
    
    # Screening Config
    TOP_N_CANDIDATES = 10
    BATCH_SIZE = 3
    
    # Rate limiting
    REQUEST_DELAY_MS = 500  # 500ms between requests

settings = Settings()

# Validate on startup
if not settings.GEMINI_API_KEY:
    raise ValueError("❌ GEMINI_API_KEY not found in .env - Add GEMINI_API_KEY to your .env file")
"""
Load environment variables and configure AI settings.
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Centralized configuration for the AI module."""
    
    # Gemini API Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY")
    
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY not found in environment variables. Create .env file.")
    
    # AI Behavior Configuration
    TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", 0.1))
    MAX_OUTPUT_TOKENS: int = int(os.getenv("AI_MAX_TOKENS", 1024))
    TOP_N_SHORTLIST: int = int(os.getenv("AI_TOP_N_SHORTLIST", 10))
    
    # Scoring Weights (must sum to 1.0)
    MATCH_SCORE_WEIGHTS: dict = {
        "skills": 0.40,
        "experience": 0.30,
        "education": 0.15,
        "relevance": 0.15
    }
    
    # API Configuration
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta/models"
    API_TIMEOUT_SECONDS: int = 30
    MAX_RETRIES: int = 2

settings = Settings()
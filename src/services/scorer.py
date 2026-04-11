"""
Applies weighted scoring logic and normalizes AI outputs.
"""
from src.config.settings import settings


class Scorer:
    """Refines AI match scores with business rules and weights."""
    
    @staticmethod
    def apply_weights(ai_scores: list[dict], job_requirements: dict = None) -> list[dict]:
        """Apply configurable weights to AI-generated scores."""
        weights = job_requirements.get("weights", settings.MATCH_SCORE_WEIGHTS) if job_requirements else settings.MATCH_SCORE_WEIGHTS
        
        for score_entry in ai_scores:
            # For now, trust Gemini's matchScore (0-100)
            score_entry["finalScore"] = score_entry["matchScore"]
            
        return ai_scores
    
    @staticmethod
    def normalize_scores(scores: list[dict]) -> list[dict]:
        """Ensure all scores are integers 0-100 and handle edge cases."""
        for entry in scores:
            raw_score = entry.get("matchScore", 0)
            entry["matchScore"] = max(0, min(100, int(round(raw_score))))
            if "finalScore" not in entry:
                entry["finalScore"] = entry["matchScore"]
        return scores
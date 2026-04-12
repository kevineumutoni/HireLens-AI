# src/services/scorer.py
"""Score normalization and weighting."""

class Scorer:
    @staticmethod
    def apply_weights(scores: list) -> list:
        """Apply weighted scoring (currently flat weights, can be enhanced)."""
        for s in scores:
            # Ensure matchScore exists and is valid
            score = s.get("matchScore", 50)
            s["finalScore"] = max(0, min(100, int(score)))
        return scores
    
    @staticmethod
    def normalize_scores(scores: list) -> list:
        """Normalize scores to 0-100 range."""
        for entry in scores:
            score = entry.get("matchScore", 50)
            # Ensure it's an integer between 0-100
            entry["matchScore"] = max(0, min(100, int(score)))
        return scores
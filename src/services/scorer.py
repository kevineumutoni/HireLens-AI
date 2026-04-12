# src/services/scorer.py
"""Score normalization."""

class Scorer:
    @staticmethod
    def apply_weights(scores: list) -> list:
        for s in scores:
            s["finalScore"] = s.get("matchScore", 50)
        return scores
    
    @staticmethod
    def normalize_scores(scores: list) -> list:
        for entry in scores:
            score = entry.get("matchScore", 50)
            entry["matchScore"] = max(0, min(100, int(score)))
        return scores
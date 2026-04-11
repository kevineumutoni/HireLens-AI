"""
Ranks candidates and selects the top N for the shortlist.
"""
from src.config.settings import settings


class Ranker:
    """Sorts candidates and returns the top shortlist."""
    
    @staticmethod
    def create_shortlist(scored_candidates: list[dict], top_n: int = None) -> list[dict]:
        """Sort candidates by finalScore descending and return top N."""
        n = top_n or settings.TOP_N_SHORTLIST
        
        sorted_candidates = sorted(
            scored_candidates,
            key=lambda x: (x.get("finalScore", 0), x.get("matchScore", 0)),
            reverse=True
        )
        
        for rank, candidate in enumerate(sorted_candidates[:n], start=1):
            candidate["rank"] = rank
            
        return sorted_candidates[:n]
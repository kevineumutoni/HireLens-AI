# src/services/ranker.py
"""Rank candidates by score."""

class Ranker:
    @staticmethod
    def create_shortlist(candidates: list, top_n: int = 10) -> list:
        sorted_list = sorted(candidates, key=lambda x: x.get("matchScore", 0), reverse=True)
        for i, candidate in enumerate(sorted_list[:top_n], 1):
            candidate["rank"] = i
        return sorted_list[:top_n]
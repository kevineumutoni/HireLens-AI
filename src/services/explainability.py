# src/services/explainability.py
"""Generate explanations."""
from src.services.gemini_client import GeminiClient

class ExplainabilityGenerator:
    def __init__(self):
        self.gemini = GeminiClient()
    
    async def generate_explanation(self, job, candidate, match_result) -> str:
        prompt = f"""
Explain why {candidate.firstName} {candidate.lastName} ({match_result.get('matchScore', 0)}/100) is a good fit for {job.title}.
Key strengths: {', '.join(match_result.get('strengths', []))}
Gaps: {', '.join(match_result.get('gaps', []))}

Keep it 2-3 sentences, professional, recruiter-friendly. No markdown.
"""
        return await self.gemini.generate_text_response(prompt)
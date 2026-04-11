"""
Generates human-friendly explanations for AI screening decisions.
"""
from src.schemas.job_schema import Job
from src.schemas.talent_profile import TalentProfile
from src.prompts.templates import EXPLAIN_MATCH_PROMPT
from src.services.gemini_client import GeminiClient


class ExplainabilityGenerator:
    """Creates recruiter-friendly reasoning for shortlisted candidates."""
    
    def __init__(self):
        self.gemini = GeminiClient()
    
    async def generate_explanation(
        self, 
        job: Job, 
        candidate: TalentProfile, 
        match_result: dict
    ) -> str:
        """Generate a concise, natural-language explanation for a candidate's match."""
        strengths_str = "; ".join(match_result.get("strengths", []))
        gaps_str = "; ".join(match_result.get("gaps", []))
        
        prompt = EXPLAIN_MATCH_PROMPT.format(
            job_title=job.title,
            candidate_name=f"{candidate.firstName} {candidate.lastName}",
            candidate_headline=candidate.headline,
            match_score=match_result.get("matchScore", 0),
            strengths_list=strengths_str,
            gaps_list=gaps_str
        )
        
        explanation = await self.gemini.generate_text_response(prompt)
        explanation = explanation.strip().replace("\n", " ")
        
        return explanation
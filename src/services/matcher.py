"""
Core matching logic: compares candidates against job requirements using Gemini.
"""
from src.schemas.talent_profile import TalentProfile
from src.schemas.job_schema import Job
from src.prompts.templates import MATCH_CANDIDATE_PROMPT
from src.prompts.formatter import format_job_for_prompt, format_candidate_for_prompt
from src.services.gemini_client import GeminiClient


class CandidateMatcher:
    """Matches candidates to jobs using Gemini-powered analysis."""
    
    def __init__(self):
        self.gemini = GeminiClient()
    
    async def match_candidate(self, job: Job, candidate: TalentProfile) -> dict:
        """Analyze a single candidate against a job and return scored result."""
        job_text = format_job_for_prompt(job)
        candidate_text = format_candidate_for_prompt(candidate)
        
        prompt = MATCH_CANDIDATE_PROMPT.format(
            job_description=job_text,
            candidate_profile=candidate_text
        )
        
        expected_schema = {
            "required": ["matchScore", "strengths", "gaps", "recommendation"]
        }
        
        result = await self.gemini.generate_structured_response(prompt, expected_schema)
        
        # Add metadata for tracking
        result["candidateId"] = f"{candidate.firstName}_{candidate.lastName}_{candidate.email}"
        result["jobId"] = job.jobId
        
        return result
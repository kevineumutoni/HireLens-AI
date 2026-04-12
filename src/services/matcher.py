# src/services/matcher.py
"""Candidate-to-job matching with Gemini."""
from src.schemas.talent_profile import TalentProfile
from src.schemas.job_schema import Job
from src.services.gemini_client import GeminiClient

class CandidateMatcher:
    def __init__(self):
        self.gemini = GeminiClient()
    
    async def match_candidate(self, job: Job, candidate: TalentProfile) -> dict:
        """Score candidate against job."""
        prompt = self._build_prompt(job, candidate)
        
        result = await self.gemini.generate_structured_response(prompt)
        result["candidateId"] = f"{candidate.firstName}_{candidate.lastName}"
        result["jobId"] = job.jobId
        
        return result
    
    def _build_prompt(self, job: Job, candidate: TalentProfile) -> str:
        """Build unbiased screening prompt."""
        skills_str = "\n".join([f"  - {s.name} ({s.level}): {s.yearsOfExperience} yrs" for s in candidate.skills])
        exp_str = "\n".join([f"  - {e.role} at {e.company}" for e in candidate.experience[:2]])
        
        return f"""
You are an UNBIASED AI recruiter. Evaluate ONLY on qualifications and skills. IGNORE: name, age, location, gender.

JOB: {job.title}
Required Skills: {', '.join(job.requiredSkills)}
Min Experience: {job.minYearsExperience}+ years
Required Education: {job.requiredEducation}

CANDIDATE:
Headline: {candidate.headline}
Skills:
{skills_str}

Experience:
{exp_str}

Education: {candidate.education[0].degree if candidate.education else 'N/A'}

TASK: Return ONLY this JSON:
{{
    "matchScore": <0-100>,
    "strengths": [<string>, <string>],
    "gaps": [<string>, <string>],
    "recommendation": "Strong Yes|Yes|Maybe|No"
}}

Score 75+ if candidate has all required skills. Score 50-75 if missing 1-2 skills. Score <50 if major gaps.
"""
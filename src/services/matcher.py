"""Candidate-to-job matching with Gemini - SIMPLIFIED for reliability + clean output."""
from src.schemas.talent_profile import TalentProfile
from src.schemas.job_schema import Job
from src.services.gemini_client import GeminiClient


class CandidateMatcher:
    def __init__(self):
        self.gemini = GeminiClient(debug=False)

    async def match_candidate(self, job: Job, candidate: TalentProfile) -> dict:
        """Score candidate against job."""
        prompt = self._build_prompt(job, candidate)
        result = await self.gemini.generate_structured_response(prompt)

        # keep IDs regardless of success/failure
        result["candidateId"] = f"{candidate.firstName}_{candidate.lastName}"
        result["jobId"] = job.jobId
        return result

    def _build_prompt(self, job: Job, candidate: TalentProfile) -> str:
        """Build a strict-format screening prompt (easy parsing, no truncation)."""

        skills_lines = "\n".join(
            [f"- {s.name} | level={s.level} | years={s.yearsOfExperience}" for s in candidate.skills]
        )

        exp_lines = "\n".join(
            [
                f"- {e.role} @ {e.company} ({e.startDate} to {e.endDate}) tech={', '.join(e.technologies[:5])}"
                for e in (candidate.experience[:3] if candidate.experience else [])
            ]
        ) or "- None provided"

        if candidate.education:
            edu0 = candidate.education[0]
            education_line = f"{edu0.degree} in {edu0.fieldOfStudy} ({edu0.startYear}-{edu0.endYear})"
        else:
            education_line = "Not specified"

        return f"""
You are an unbiased recruiting assistant.
Evaluate ONLY job-related qualifications. Ignore name, gender, age, nationality, location.

JOB
Title: {job.title}
Required skills: {", ".join(job.requiredSkills)}
Preferred skills: {", ".join(job.preferredSkills)}
Min years experience: {job.minYearsExperience}
Education requirement: {job.requiredEducation}

CANDIDATE
Headline: {candidate.headline}
Education: {education_line}
Availability: {candidate.availability.status} ({candidate.availability.type})

Skills:
{skills_lines}

Experience (top 3):
{exp_lines}

SCORING RULES
- Score 80-100: has all required skills + relevant experience.
- Score 60-79: missing 1-2 required skills OR weaker experience, but solid foundation.
- Score 0-59: major gaps in required skills/experience.

Return EXACTLY this format (no extra text, no markdown):

Score: <0-100>/100
Strengths:
- <max 12 words>
- <max 12 words>
Gaps:
Gaps:
- <must name a missing required skill OR a missing experience area>
- <must name a missing required skill OR a missing experience area>
Recommendation: Strong Yes|Yes|Maybe|No
Reasoning: <2 sentences max, <= 240 characters>
""".strip()

    def _build_resume_prompt(self, job: Job, resume_text: str) -> str:
        """For resume screening."""
        return f"""Evaluate this resume for {job.title}.

Required skills: {', '.join(job.requiredSkills)}
Preferred skills: {', '.join(job.preferredSkills)}

Resume:
{resume_text}

Give a score 0-100 and a short explanation."""
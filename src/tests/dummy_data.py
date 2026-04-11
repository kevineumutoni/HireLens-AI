"""
Reusable dummy data for testing the AI module.
Import these in your tests or use for local development.
"""
from src.schemas.job_schema import Job
from src.schemas.talent_profile import TalentProfile, Skill, WorkExperience, Education, Project, Availability


def get_sample_job() -> Job:
    """Return a realistic sample job for testing."""
    return Job(
        jobId="TEST-JOB-001",
        title="AI Engineer – LLM Applications",
        description="Design and deploy LLM-powered features using Gemini API, RAG, and agent frameworks.",
        location="Remote (Africa)",
        employmentType="Full-time",
        requiredSkills=["Python", "LLM Integration", "Prompt Engineering", "API Design"],
        preferredSkills=["Gemini API", "LangChain", "Vector Databases", "Docker"],
        minYearsExperience=2,
        requiredEducation="Bachelor's in CS, AI, or related",
        softSkills=["Communication", "Problem-solving"],
        postedDate="2026-04-10"
    )


def get_strong_match_candidate() -> TalentProfile:
    """Candidate with high alignment to sample job."""
    return TalentProfile(
        firstName="Test",
        lastName="StrongMatch",
        email="strong@test.com",
        headline="AI Engineer | Gemini API & LLM Specialist",
        location="Kigali, Rwanda",
        skills=[
            Skill(name="Python", level="Expert", yearsOfExperience=4),
            Skill(name="Gemini API", level="Advanced", yearsOfExperience=2),
            Skill(name="Prompt Engineering", level="Advanced", yearsOfExperience=3),
            Skill(name="LangChain", level="Intermediate", yearsOfExperience=1),
        ],
        experience=[
            WorkExperience(
                company="AI Innovations Lab",
                role="AI Engineer",
                startDate="2023-01",
                endDate="Present",
                description="Built RAG pipelines and agent systems using Gemini API",
                technologies=["Python", "Gemini API", "LangChain", "Pinecone"],
                isCurrent=True
            )
        ],
        education=[
            Education(
                institution="African Leadership University",
                degree="Bachelor's",
                fieldOfStudy="Artificial Intelligence",
                startYear=2019,
                endYear=2023
            )
        ],
        projects=[
            Project(
                name="HR Screening Agent",
                description="AI agent that screens candidates using Gemini API and structured profiles",
                technologies=["Python", "Gemini API", "FastAPI", "MongoDB"],
                role="Lead AI Engineer",
                startDate="2025-09",
                endDate="2026-03"
            )
        ],
        availability=Availability(status="Available", type="Full-time")
    )


def get_weak_match_candidate() -> TalentProfile:
    """Candidate with low alignment to sample job (for testing edge cases)."""
    return TalentProfile(
        firstName="Test",
        lastName="WeakMatch",
        email="weak@test.com",
        headline="Frontend Developer | React & UI Specialist",
        location="Lagos, Nigeria",
        skills=[
            Skill(name="React", level="Expert", yearsOfExperience=5),
            Skill(name="CSS", level="Advanced", yearsOfExperience=4),
            Skill(name="JavaScript", level="Advanced", yearsOfExperience=5),
        ],
        experience=[
            WorkExperience(
                company="WebDev Studio",
                role="Frontend Developer",
                startDate="2021-06",
                endDate="Present",
                description="Built responsive UIs with React and modern CSS",
                technologies=["React", "TypeScript", "Tailwind CSS"],
                isCurrent=True
            )
        ],
        education=[
            Education(
                institution="University of Lagos",
                degree="Bachelor's",
                fieldOfStudy="Graphic Design",
                startYear=2017,
                endYear=2021
            )
        ],
        projects=[
            Project(
                name="E-commerce Storefront",
                description="Responsive React frontend for online retail platform",
                technologies=["React", "Redux", "Stripe API"],
                role="Frontend Lead",
                startDate="2024-01",
                endDate="2024-06"
            )
        ],
        availability=Availability(status="Available", type="Contract")
    )
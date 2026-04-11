"""
Main entry point for the Umurava AI screening module.
Includes example usage for testing the full pipeline.
"""
import asyncio
import json
from src.schemas.job_schema import Job
from src.schemas.talent_profile import TalentProfile, Skill, WorkExperience, Education, Project, Availability
from src.services.matcher import CandidateMatcher
from src.services.scorer import Scorer
from src.services.ranker import Ranker
from src.services.explainability import ExplainabilityGenerator
from src.utils.validators import validate_ai_match_response


async def run_screening_demo():
    """Demo: Screen 3 dummy candidates against a sample job."""
    print("🚀 Starting Umurava AI Screening Demo...\n")
    
    # Sample job
    sample_job = Job(
        jobId="JOB-001",
        title="Backend Engineer – Node.js & AI Systems",
        description="Build scalable APIs and AI-powered features for HR tech platform. Work with Node.js, MongoDB, Gemini API.",
        location="Kigali, Rwanda (Hybrid)",
        employmentType="Full-time",
        requiredSkills=["Node.js", "TypeScript", "MongoDB", "REST API"],
        preferredSkills=["Gemini API", "Python", "AWS"],
        minYearsExperience=2,
        requiredEducation="Bachelor's in Computer Science or related",
        softSkills=["Problem-solving", "Communication"],
        postedDate="2026-04-01"
    )
    
    # Candidate 1: Strong match
    candidate1 = TalentProfile(
        firstName="Jean",
        lastName="Mucyo",
        email="jean.mucyo@email.com",
        headline="Backend Engineer | Node.js & AI Integration Specialist",
        location="Kigali, Rwanda",
        skills=[
            Skill(name="Node.js", level="Advanced", yearsOfExperience=3),
            Skill(name="TypeScript", level="Advanced", yearsOfExperience=2),
            Skill(name="MongoDB", level="Intermediate", yearsOfExperience=2),
            Skill(name="Gemini API", level="Beginner", yearsOfExperience=1),
        ],
        experience=[
            WorkExperience(
                company="TechStart Rwanda",
                role="Backend Developer",
                startDate="2023-06",
                endDate="Present",
                description="Built REST APIs for HR platform using Node.js and MongoDB",
                technologies=["Node.js", "Express", "MongoDB"],
                isCurrent=True
            )
        ],
        education=[
            Education(
                institution="African Leadership University",
                degree="Bachelor's",
                fieldOfStudy="Computer Science",
                startYear=2020,
                endYear=2024
            )
        ],
        projects=[
            Project(
                name="AI Resume Parser",
                description="Built a tool to extract structured data from resumes using NLP",
                technologies=["Python", "spaCy", "FastAPI"],
                role="Lead Developer",
                startDate="2024-01",
                endDate="2024-03"
            )
        ],
        availability=Availability(status="Available", type="Full-time")
    )
    
    # Candidate 2: Partial match
    candidate2 = TalentProfile(
        firstName="Amina",
        lastName="Niyonzima", 
        email="amina.n@email.com",
        headline="Full-Stack Developer | React & Node.js",
        location="Nairobi, Kenya",
        skills=[
            Skill(name="React", level="Expert", yearsOfExperience=4),
            Skill(name="Node.js", level="Intermediate", yearsOfExperience=2),
            Skill(name="PostgreSQL", level="Advanced", yearsOfExperience=3),
        ],
        experience=[
            WorkExperience(
                company="DevHub Africa",
                role="Full-Stack Developer",
                startDate="2022-03",
                endDate="2024-12",
                description="Developed customer-facing web apps with React/Node",
                technologies=["React", "Node.js", "PostgreSQL"]
            )
        ],
        education=[
            Education(
                institution="University of Nairobi",
                degree="Bachelor's",
                fieldOfStudy="Software Engineering",
                startYear=2018,
                endYear=2022
            )
        ],
        projects=[
            Project(
                name="Job Board Platform",
                description="Full-stack job matching platform with search and applications",
                technologies=["Next.js", "Node.js", "PostgreSQL"],
                role="Full-Stack Developer",
                startDate="2023-09",
                endDate="2024-02"
            )
        ],
        availability=Availability(status="Open to Opportunities", type="Full-time")
    )
    
    # Candidate 3: Weak match (using valid "Internship" type)
    candidate3 = TalentProfile(
        firstName="David",
        lastName="Kamali",
        email="d.kamali@email.com", 
        headline="Junior Python Developer | Data & Automation",
        location="Kigali, Rwanda",
        skills=[
            Skill(name="Python", level="Intermediate", yearsOfExperience=2),
            Skill(name="Pandas", level="Intermediate", yearsOfExperience=1),
            Skill(name="SQL", level="Beginner", yearsOfExperience=1),
        ],
        experience=[
            WorkExperience(
                company="DataSolutions Ltd",
                role="Data Intern",
                startDate="2024-01",
                endDate="2024-06",
                description="Automated data cleaning pipelines with Python",
                technologies=["Python", "Pandas", "SQLite"]
            )
        ],
        education=[
            Education(
                institution="University of Rwanda",
                degree="Bachelor's",
                fieldOfStudy="Statistics",
                startYear=2021,
                endYear=2025
            )
        ],
        projects=[
            Project(
                name="Sales Dashboard",
                description="Automated reporting dashboard for sales team",
                technologies=["Python", "Streamlit", "SQLite"],
                role="Solo Developer",
                startDate="2024-03",
                endDate="2024-05"
            )
        ],
        # ✅ Fixed: Using valid "Internship" type
        availability=Availability(status="Available", type="Internship")
    )
    
    candidates = [candidate1, candidate2, candidate3]
    
    # Initialize services
    matcher = CandidateMatcher()
    scorer = Scorer()
    ranker = Ranker()
    explainer = ExplainabilityGenerator()
    
    # Match each candidate
    print("🔍 Analyzing candidates against job requirements...")
    match_results = []
    
    for candidate in candidates:
        print(f"  → Screening {candidate.firstName} {candidate.lastName}...")
        result = await matcher.match_candidate(sample_job, candidate)
        
        # Validate AI output
        is_valid, error = validate_ai_match_response(result)
        if not is_valid:
            print(f"    ⚠️  Validation failed: {error} – using fallback score")
            result["matchScore"] = 50
            result["strengths"] = ["Profile submitted"]
            result["gaps"] = ["AI analysis incomplete"]
            result["recommendation"] = "Manual review recommended"
        
        match_results.append(result)
        print(f"    ✓ Score: {result['matchScore']}/100")
    
    # Apply scoring logic and rank
    print("\n📊 Ranking candidates...")
    weighted_results = scorer.apply_weights(match_results)
    normalized_results = scorer.normalize_scores(weighted_results)
    shortlist = ranker.create_shortlist(normalized_results, top_n=2)
    
    # Generate explanations for shortlisted candidates
    print("\n✨ Generating AI explanations for shortlist...")
    for entry in shortlist:
        candidate = next(
            c for c in candidates 
            if f"{c.firstName}_{c.lastName}_{c.email}" == entry["candidateId"]
        )
        explanation = await explainer.generate_explanation(sample_job, candidate, entry)
        entry["explanation"] = explanation
        print(f"  Rank #{entry['rank']}: {candidate.firstName} – {explanation[:100]}...")
    
    # Output final shortlist
    print("\n🏆 FINAL SHORTLIST (Top 2):")
    print(json.dumps(shortlist, indent=2, default=str))
    
    return shortlist


if __name__ == "__main__":
    asyncio.run(run_screening_demo())
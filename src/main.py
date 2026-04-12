# src/main.py
"""
HireLens-AI: Unbiased Talent Screening
No deprecated APIs, no hardcoded values, fresh AI eval every time.
"""
import asyncio
import json
from datetime import datetime
from src.schemas.job_schema import Job
from src.dummy_data import DummyDataGenerator
from src.services.matcher import CandidateMatcher
from src.services.scorer import Scorer
from src.services.ranker import Ranker
from src.services.explainability import ExplainabilityGenerator

async def main():
    print("\n" + "=" * 80)
    print("🚀 HireLens-AI: Unbiased Talent Screening System")
    print("=" * 80)
    
    # Job posting
    job = Job(
        jobId="JOB-001",
        title="Backend Engineer - AI Systems",
        description="Build scalable APIs and AI-powered features for HR platform",
        location="Kigali, Rwanda",
        employmentType="Full-time",
        requiredSkills=["Node.js", "Python", "REST API", "Database Design"],
        preferredSkills=["Gemini API", "AWS", "Docker"],
        minYearsExperience=3,
        requiredEducation="Bachelor's in CS or related",
        softSkills=["Problem-solving", "Communication"],
        postedDate=datetime.now().strftime("%Y-%m-%d")
    )
    
    print(f"\n📋 JOB: {job.title}")
    print(f"   Required: {', '.join(job.requiredSkills)}")
    print(f"   Experience: {job.minYearsExperience}+ years")
    
    # Generate candidates
    print(f"\n👥 Generating diverse candidate pool...")
    candidates = DummyDataGenerator.generate_candidates_batch(50)
    print(f"   ✅ Generated {len(candidates)} candidates")
    
    # Initialize services
    matcher = CandidateMatcher()
    scorer = Scorer()
    ranker = Ranker()
    explainer = ExplainabilityGenerator()
    
    # Screen candidates
    print(f"\n🔍 Screening candidates (this calls Gemini API - fresh results)...")
    matches = []
    for i, candidate in enumerate(candidates, 1):
        print(f"   [{i}/{len(candidates)}] Analyzing {candidate.firstName} {candidate.lastName}...", end=" ")
        result = await matcher.match_candidate(job, candidate)
        matches.append(result)
        print(f"Score: {result.get('matchScore', 0)}/100")
    
    # Rank
    print(f"\n📊 Scoring and ranking...")
    weighted = scorer.apply_weights(matches)
    normalized = scorer.normalize_scores(weighted)
    shortlist = ranker.create_shortlist(normalized, top_n=10)
    
    # Explain
    print(f"\n✨ Generating explanations...")
    for entry in shortlist:
        cand_id = entry["candidateId"]
        candidate = next((c for c in candidates if f"{c.firstName}_{c.lastName}" == cand_id), None)
        if candidate:
            explanation = await explainer.generate_explanation(job, candidate, entry)
            entry["explanation"] = explanation
            print(f"   Rank #{entry['rank']}: {candidate.firstName} - {explanation[:70]}...")
    
    # Display results
    print("\n" + "=" * 80)
    print("🏆 TOP 10 CANDIDATES")
    print("=" * 80)
    for entry in shortlist:
        cand_id = entry["candidateId"]
        candidate = next((c for c in candidates if f"{c.firstName}_{c.lastName}" == cand_id), None)
        print(f"\n#{entry['rank']} | {candidate.firstName} {candidate.lastName}")
        print(f"    Score: {entry['matchScore']}/100 | {entry['recommendation']}")
        print(f"    Strengths: {', '.join(entry.get('strengths', [])[:2])}")
        print(f"    Explanation: {entry.get('explanation', 'N/A')[:100]}...")
    
    # Save
    with open("screening_results.json", "w") as f:
        json.dump({
            "job": job.dict(),
            "total_evaluated": len(candidates),
            "shortlist": shortlist
        }, f, indent=2, default=str)
    
    print(f"\n✅ Results saved to screening_results.json\n")

if __name__ == "__main__":
    asyncio.run(main())
# src/main.py
"""
HireLens-AI: Unbiased Talent Screening System
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
    print("HireLens-AI: Unbiased Talent Screening System")

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
        postedDate=datetime.now().strftime("%Y-%m-%d"),
    )

    print(f"\n JOB: {job.title}")
    print(f"   Required: {', '.join(job.requiredSkills)}")
    print(f"   Experience: {job.minYearsExperience}+ years")

    print(f"\n👥 Generating diverse candidate pool...")
    candidates = DummyDataGenerator.generate_candidates_batch(50)
    print(f"    Generated {len(candidates)} candidates")

    try:
        matcher = CandidateMatcher()
        scorer = Scorer()
        ranker = Ranker()
        explainer = ExplainabilityGenerator()
    except Exception as e:
        print(f" Failed to initialize services: {e}")
        return

    print(f"\n Screening candidates with Gemini AI...")
    matches = []
    for i, candidate in enumerate(candidates, 1):
        cid = f"{candidate.firstName}_{candidate.lastName}"

        print(f"   [{i:2d}/{len(candidates)}] {candidate.firstName} {candidate.lastName}...", end=" ", flush=True)

        try:
            result = await matcher.match_candidate(job, candidate)
            matches.append(result)

            if result.get("evaluationStatus") == "success":
                print(f" {result.get('matchScore')}/100")
            else:
                # failed evaluation: show error but do NOT assign fake score
                err = result.get("error", "unknown error")
                print(f" FAILED ({err[:60]})")

        except Exception as e:
            print(f" Exception ({str(e)[:60]})")
            matches.append(
                {
                    "candidateId": cid,
                    "jobId": job.jobId,
                    "evaluationStatus": "failed",
                    "error": f"Exception: {str(e)[:200]}",
                    "matchScore": None,
                    "strengths": [],
                    "gaps": [],
                    "recommendation": "Manual review",
                    "reasoning": "",
                }
            )

    successful = [
        m
        for m in matches
        if m.get("evaluationStatus") == "success" and isinstance(m.get("matchScore"), int)
    ]
    failed = [m for m in matches if m.get("evaluationStatus") != "success"]

    print(f"\n Evaluation summary:")
    print(f"    Successful evaluations: {len(successful)}")
    print(f"    Failed evaluations: {len(failed)}")

    if failed:
        print("   Sample failures (first 5):")
        for f in failed[:5]:
            print(f"   - {f.get('candidateId','?')}: {f.get('error','unknown error')[:120]}")

    if not successful:
        print("\n No successful Gemini evaluations. Check API key, quota, or model availability.")
        return

    print(f"\n Scoring and ranking (successful only)...")
    weighted = scorer.apply_weights(successful)
    normalized = scorer.normalize_scores(weighted)
    shortlist = ranker.create_shortlist(normalized, top_n=min(10, len(normalized)))

    print(f"\n Generating explanations for shortlist...")
    for entry in shortlist:
        cand_id = entry["candidateId"]
        candidate = next((c for c in candidates if f"{c.firstName}_{c.lastName}" == cand_id), None)

        if not candidate:
            entry["explanation"] = "Candidate profile not found in generated list."
            continue

        try:
            explanation = await explainer.generate_explanation(job, candidate, entry)
            entry["explanation"] = explanation
            print(f"   Rank #{entry['rank']}: {candidate.firstName} {candidate.lastName}")
        except Exception as e:
            entry["explanation"] = f"Explanation unavailable: {str(e)[:120]}"

    print(" TOP SHORTLISTED CANDIDATES")

    for entry in shortlist:
        cand_id = entry["candidateId"]
        candidate = next((c for c in candidates if f"{c.firstName}_{c.lastName}" == cand_id), None)

        if not candidate:
            continue

        print(f"\n#{entry['rank']} | {candidate.firstName} {candidate.lastName}")
        print(f"    Score: {entry['matchScore']}/100 | {entry.get('recommendation', 'N/A')}")

        strengths = entry.get("strengths", []) or []
        gaps = entry.get("gaps", []) or []
        reasoning = entry.get("reasoning", "") or ""
        explanation = entry.get("explanation", "") or ""

        if strengths:
            print("    Strengths:")
            for s in strengths[:2]:
                print(f"      - {s}")
        if gaps:
            print("    Gaps:")
            for g in gaps[:2]:
                print(f"      - {g}")

        if reasoning:
            print(f"    Reasoning: {reasoning}")
        if explanation:
            print(f"    Recruiter note: {explanation}")

    print(f"\n Saving results to MongoDB...")
    try:
        from src.db import jobs_col, candidates_col, results_col
        
        jobs_col.insert_one({
            **job.model_dump(),  # Pydantic v2
            "insertedAt": datetime.now().isoformat(),
            "source": "screening_run"
        })
        
        candidates_data = [c.model_dump() for c in candidates]
        if candidates_data:
            candidates_col.insert_many(candidates_data)
        
        results_col.insert_one({
            "job": job.model_dump(),
            "total_evaluated": len(candidates),
            "successful_evaluations": len(successful),
            "failed_evaluations": len(failed),
            "failed_examples": failed[:10],
            "shortlist": shortlist,
            "timestamp": datetime.now().isoformat(),
            "screeningRunId": f"RUN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        })
        
        print(f"   Saved to MongoDB!")
        print(f"      - Job: {job.jobId}")
        print(f"      - Candidates: {len(candidates)}")
        print(f"      - Results: 1 screening run")
        
    except Exception as e:
        print(f"    MongoDB save failed: {e}")
        print(f"   Falling back to JSON...")
        try:
            with open("screening_results.json", "w", encoding="utf-8") as f:
                json.dump({
                    "job": job.model_dump(),
                    "total_evaluated": len(candidates),
                    "successful_evaluations": len(successful),
                    "failed_evaluations": len(failed),
                    "failed_examples": failed[:10],
                    "shortlist": shortlist,
                    "timestamp": datetime.now().isoformat(),
                }, f, indent=2, ensure_ascii=False, default=str)
            print(f"    JSON fallback saved!")
        except Exception as e2:
            print(f"    JSON fallback also failed: {e2}")

    print(f"\n Screening complete!\n")


if __name__ == "__main__":
    asyncio.run(main())
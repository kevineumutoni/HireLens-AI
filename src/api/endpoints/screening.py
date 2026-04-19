# src/api/endpoints/screening.py
"""
Screening endpoint — fixed explanation generation.

Root cause fix: explanation was always "" because _parse_scoring_response
never generated it. Now we build a recruiter-friendly explanation inline
from the already-extracted strengths + gaps + reasoning — no extra Gemini
call needed, instant, always populated.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List, Any, Dict
from datetime import datetime
from bson import ObjectId
import asyncio

from src.db import results_col, jobs_col, candidates_col
from src.schemas.request_models import ScreeningRequest, ScreeningResultListResponse
from src.services.gemini_client import GeminiClient

router = APIRouter()

BATCH_SIZE = 5
CANDIDATE_TIMEOUT = 20


def _to_iso(dt: Any) -> Any:
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt


def serialize_screening_result(result: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(result)
    if "_id" in out:
        out["id"] = str(out.pop("_id"))
    if "timestamp" in out:
        out["timestamp"] = _to_iso(out["timestamp"])
    shortlist = out.get("shortlist")
    if isinstance(shortlist, list):
        fixed = []
        for item in shortlist:
            if not isinstance(item, dict):
                continue
            it = dict(item)
            if "candidateId" in it:
                it["candidateId"] = str(it["candidateId"])
            fixed.append(it)
        out["shortlist"] = fixed
    return out


def _build_explanation(
    candidate_name: str,
    score: int,
    recommendation: str,
    strengths: List[str],
    gaps: List[str],
    reasoning: str,
) -> str:
    """
    Build a recruiter-friendly explanation string from already-extracted fields.
    No extra Gemini call — assembled instantly from what we already have.
    Always returns a non-empty string.
    """
    parts = []

    # Opening: score + recommendation
    rec_map = {
        "Strong Yes": "a strong fit",
        "Yes":        "a good fit",
        "Maybe":      "a potential fit with reservations",
        "No":         "not a strong fit for this role",
    }
    fit_label = rec_map.get(recommendation, "a candidate to review")
    parts.append(f"{candidate_name} scored {score}/100 and is {fit_label}.")

    # Strengths sentence
    if strengths:
        top = strengths[0]
        # Truncate if very long
        if len(top) > 120:
            top = top[:117] + "…"
        if len(strengths) > 1:
            second = strengths[1]
            if len(second) > 80:
                second = second[:77] + "…"
            parts.append(f"Key strengths include: {top}; and {second}.")
        else:
            parts.append(f"Key strength: {top}.")

    # Gaps sentence
    if gaps:
        top_gap = gaps[0]
        if len(top_gap) > 120:
            top_gap = top_gap[:117] + "…"
        parts.append(f"Main gap: {top_gap}.")
    else:
        parts.append("No critical gaps identified.")

    if reasoning and len(reasoning) > 20:
        r = reasoning.strip()
        if len(r) > 200:
            r = r[:197] + "…"
        parts.append(r)

    return " ".join(parts)


def _build_screening_prompt(job: Dict[str, Any], candidate: Dict[str, Any]) -> str:
    raw_skills = candidate.get("skills") or []
    if raw_skills and isinstance(raw_skills[0], dict):
        skills_str = ", ".join(s.get("name", "") for s in raw_skills if s.get("name"))
    else:
        skills_str = ", ".join(str(s) for s in raw_skills if s)

    exp = candidate.get("experience") or []
    exp_lines = []
    for e in exp[:4]:
        if isinstance(e, dict):
            role = e.get("role") or e.get("title") or ""
            company = e.get("company") or ""
            if role or company:
                exp_lines.append(f"  - {role} at {company}".strip())
    exp_str = "\n".join(exp_lines) if exp_lines else "  Not provided"

    edu = candidate.get("education") or []
    edu_lines = []
    for ed in edu[:2]:
        if isinstance(ed, dict):
            degree = ed.get("degree") or ""
            institution = ed.get("institution") or ""
            if degree or institution:
                edu_lines.append(f"  - {degree} from {institution}".strip())
    edu_str = "\n".join(edu_lines) if edu_lines else "  Not provided"

    required_skills  = ", ".join(job.get("requiredSkills") or [])
    preferred_skills = ", ".join(job.get("preferredSkills") or [])

    return f"""You are an expert technical recruiter. Evaluate this candidate for the job below.

JOB:
  Title: {job.get("title", "")}
  Required Skills: {required_skills}
  Preferred Skills: {preferred_skills}
  Min. Experience: {job.get("minYearsExperience", 0)} years
  Required Education: {job.get("requiredEducation", "Any")}
  Description: {str(job.get("description", ""))[:300]}

CANDIDATE:
  Headline: {candidate.get("headline") or "N/A"}
  Location: {candidate.get("location") or "N/A"}
  Skills: {skills_str or "None listed"}
  Experience:
{exp_str}
  Education:
{edu_str}

Respond in this EXACT format (no markdown, no extra text):

Score: [0-100]/100
Strengths:
- [strength 1]
- [strength 2]
- [strength 3]
Gaps:
- [gap 1]
- [gap 2]
Recommendation: [Strong Yes / Yes / Maybe / No]
Reasoning: [One concise sentence]
"""


async def _evaluate_one(
    gemini: GeminiClient,
    job: Dict[str, Any],
    candidate: Dict[str, Any],
) -> Dict[str, Any]:
    cid  = str(candidate.get("_id", ""))
    name = f"{candidate.get('firstName', '')} {candidate.get('lastName', '')}".strip() or "Unknown"

    try:
        prompt = _build_screening_prompt(job, candidate)
        result = await asyncio.wait_for(
            gemini.generate_structured_response(prompt),
            timeout=CANDIDATE_TIMEOUT,
        )

        if result.get("evaluationStatus") == "success":
            result["candidateId"]   = cid
            result["candidateName"] = name

            # ── FIX: always generate a non-empty explanation ──
            result["explanation"] = _build_explanation(
                candidate_name = name,
                score          = result.get("matchScore", 0),
                recommendation = result.get("recommendation", ""),
                strengths      = result.get("strengths") or [],
                gaps           = result.get("gaps") or [],
                reasoning      = result.get("reasoning", ""),
            )
            return result

        return {
            "evaluationStatus": "failed",
            "candidateId":      cid,
            "candidateName":    name,
            "error":            result.get("error", "Gemini returned failed status"),
        }

    except asyncio.TimeoutError:
        return {
            "evaluationStatus": "failed",
            "candidateId":      cid,
            "candidateName":    name,
            "error":            f"Timeout after {CANDIDATE_TIMEOUT}s",
        }
    except Exception as e:
        return {
            "evaluationStatus": "failed",
            "candidateId":      cid,
            "candidateName":    name,
            "error":            str(e)[:200],
        }



@router.get("", response_model=ScreeningResultListResponse)
async def list_screening_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    job_id: Optional[str] = None,
):
    try:
        query_filter: Dict[str, Any] = {}
        if job_id:
            query_filter = {"job.jobId": job_id}
        total = results_col.count_documents(query_filter)
        results_list = list(
            results_col.find(query_filter).sort("timestamp", -1).skip(skip).limit(limit)
        )
        return {"total": total, "skip": skip, "limit": limit,
                "data": [serialize_screening_result(r) for r in results_list]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching results: {str(e)}")


@router.get("/{run_id}", response_model=dict)
async def get_screening_result(run_id: str):
    try:
        try:
            result = results_col.find_one({"_id": ObjectId(run_id)})
        except Exception:
            result = results_col.find_one({"screeningRunId": run_id})
        if not result:
            raise HTTPException(status_code=404, detail="Screening result not found")
        return serialize_screening_result(result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching result: {str(e)}")



@router.post("", response_model=dict)
async def trigger_screening(request: ScreeningRequest):
    try:
        # 1. Find job
        job = jobs_col.find_one({"jobId": request.job_id})
        if not job:
            try:
                job = jobs_col.find_one({"_id": ObjectId(request.job_id)})
            except Exception:
                job = None
        if not job:
            raise HTTPException(status_code=404, detail=f"Job '{request.job_id}' not found")

        # 2. Get candidates
        if request.candidate_ids:
            obj_ids = []
            for rid in request.candidate_ids:
                try:
                    obj_ids.append(ObjectId(rid))
                except Exception:
                    pass
            candidates_to_screen = list(candidates_col.find({"_id": {"$in": obj_ids}})) if obj_ids else []
        else:
            candidates_to_screen = list(candidates_col.find({}))

        if not candidates_to_screen:
            raise HTTPException(status_code=400, detail="No candidates found to screen")

        # 3. Init Gemini
        try:
            gemini = GeminiClient()
        except ValueError as e:
            raise HTTPException(status_code=500, detail=f"Gemini not configured: {str(e)}")

        # 4. Evaluate in concurrent batches
        screening_run_id = f"RUN-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        all_results: List[Dict[str, Any]] = []
        total = len(candidates_to_screen)

        for batch_start in range(0, total, BATCH_SIZE):
            batch = candidates_to_screen[batch_start : batch_start + BATCH_SIZE]
            batch_results = await asyncio.gather(
                *[_evaluate_one(gemini, job, c) for c in batch]
            )
            all_results.extend(batch_results)
            if batch_start + BATCH_SIZE < total:
                await asyncio.sleep(0.3)

        # 5. Split successful / failed
        successful = [r for r in all_results if r.get("evaluationStatus") == "success"]
        failed     = [r for r in all_results if r.get("evaluationStatus") != "success"]

        # 6. Rank
        successful.sort(key=lambda x: x.get("matchScore", 0), reverse=True)

        shortlist = []
        for rank, entry in enumerate(successful, start=1):
            shortlist.append({
                "rank":           rank,
                "candidateId":    entry["candidateId"],
                "candidateName":  entry.get("candidateName", ""),
                "matchScore":     entry.get("matchScore", 0),
                "finalScore":     entry.get("matchScore", 0),
                "strengths":      entry.get("strengths", []),
                "gaps":           entry.get("gaps", []),
                "recommendation": entry.get("recommendation", ""),
                "reasoning":      entry.get("reasoning", ""),
                "explanation":    entry.get("explanation", ""),
            })

        # 7. Save
        doc = {
            "job": {
                "jobId":          job.get("jobId"),
                "title":          job.get("title"),
                "location":       job.get("location"),
                "requiredSkills": job.get("requiredSkills", []),
            },
            "total_evaluated":        total,
            "successful_evaluations": len(successful),
            "failed_evaluations":     len(failed),
            "failed_examples":        failed[:5],
            "shortlist":              shortlist,
            "timestamp":              datetime.utcnow(),
            "screeningRunId":         screening_run_id,
        }
        inserted = results_col.insert_one(doc)

        jobs_col.update_one(
            {"jobId": job.get("jobId")},
            {"$set": {"status": "screening", "updatedAt": datetime.now()}}
        )

        return {
            "message":               "Screening completed",
            "id":                    str(inserted.inserted_id),
            "screeningRunId":        screening_run_id,
            "jobId":                 job.get("jobId"),
            "candidatesScreened":    total,
            "successfulEvaluations": len(successful),
            "failedEvaluations":     len(failed),
            "shortlistSize":         len(shortlist),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Screening error: {str(e)}")
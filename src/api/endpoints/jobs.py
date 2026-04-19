# src/api/endpoints/jobs.py
"""
Job-related API endpoints.
FIXES:
- POST /jobs: when includeMockCandidates=true, sets applicantCount = total candidates in DB
- PATCH /jobs/{id}/sync-candidates: update applicantCount for existing jobs
- GET /jobs: now returns real applicantCount synced from candidates_col
- All other endpoints unchanged.
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
from bson import ObjectId
import uuid

from src.db import jobs_col, candidates_col
from src.schemas.request_models import (
    JobResponse,
    JobListResponse,
    JobRequest
)

router = APIRouter()


def serialize_job(job: dict) -> dict:
    """Convert MongoDB document to API response."""
    if "_id" in job:
        job["id"] = str(job.pop("_id"))
    return job


@router.get("", response_model=JobListResponse)
async def list_jobs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = None,
    search: Optional[str] = None
):
    """List all jobs with pagination and filters."""
    try:
        query_filter = {}

        if status:
            query_filter["status"] = status

        if search:
            query_filter["$or"] = [
                {"title": {"$regex": search, "$options": "i"}},
                {"description": {"$regex": search, "$options": "i"}}
            ]

        total = jobs_col.count_documents(query_filter)

        jobs_list = list(
            jobs_col.find(query_filter)
            .sort("createdAt", -1)
            .skip(skip)
            .limit(limit)
        )

        # FIX: for each job that has useAllCandidates=True, always return
        # the live candidate count so it stays accurate even as candidates are added.
        total_candidates = candidates_col.count_documents({})
        for job in jobs_list:
            if job.get("useAllCandidates"):
                # Sync live count into the document before serializing
                job["applicantCount"] = total_candidates

        jobs_list = [serialize_job(j) for j in jobs_list]

        return JobListResponse(
            total=total,
            skip=skip,
            limit=limit,
            data=jobs_list
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching jobs: {str(e)}")


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    """Get a single job by ID."""
    try:
        try:
            obj_id = ObjectId(job_id)
            job = jobs_col.find_one({"_id": obj_id})
        except Exception:
            job = jobs_col.find_one({"jobId": job_id})

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        # FIX: return live candidate count for jobs using all candidates
        if job.get("useAllCandidates"):
            job["applicantCount"] = candidates_col.count_documents({})

        return JobResponse(**serialize_job(job))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching job: {str(e)}")


@router.post("", response_model=JobResponse)
async def create_job(job_data: JobRequest):
    """
    Create a new job posting.

    FIX: includeMockCandidates=True now:
      1. Sets applicantCount = total candidates currently in DB
      2. Sets useAllCandidates=True flag so future reads stay in sync
    """
    try:
        include_all = bool(getattr(job_data, "includeMockCandidates", False))

        # Count ALL candidates in the system (not just mock ones)
        total_candidates = candidates_col.count_documents({})
        applicant_count = total_candidates if include_all else 0

        job_doc = {
            **job_data.model_dump(exclude={"includeMockCandidates"}),
            "jobId": f"JOB-{uuid.uuid4().hex[:6].upper()}",
            "status": "open",
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "applicantCount": applicant_count,
            # Store the flag so GET endpoints can keep count live
            "useAllCandidates": include_all,
        }

        result = jobs_col.insert_one(job_doc)
        job_doc["_id"] = result.inserted_id
        return JobResponse(**serialize_job(job_doc))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating job: {str(e)}")


@router.patch("/{job_id}/sync-candidates")
async def sync_candidates(job_id: str):
    """
    NEW endpoint: attach all candidates in the system to an existing job.
    Call this from the frontend "Use all candidates" toggle on existing jobs.
    Returns the updated applicantCount.
    """
    try:
        try:
            filter_doc = {"_id": ObjectId(job_id)}
        except Exception:
            filter_doc = {"jobId": job_id}

        job = jobs_col.find_one(filter_doc)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        total_candidates = candidates_col.count_documents({})

        jobs_col.update_one(
            filter_doc,
            {"$set": {
                "applicantCount": total_candidates,
                "useAllCandidates": True,
                "updatedAt": datetime.now(),
            }}
        )

        return {
            "message": f"Job now uses all {total_candidates} candidates",
            "applicantCount": total_candidates,
            "useAllCandidates": True,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing candidates: {str(e)}")


@router.patch("/{job_id}/unsync-candidates")
async def unsync_candidates(job_id: str):
    """Remove the 'use all candidates' flag — reset applicantCount to 0."""
    try:
        try:
            filter_doc = {"_id": ObjectId(job_id)}
        except Exception:
            filter_doc = {"jobId": job_id}

        result = jobs_col.update_one(
            filter_doc,
            {"$set": {
                "applicantCount": 0,
                "useAllCandidates": False,
                "updatedAt": datetime.now(),
            }}
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")

        return {"message": "Candidates unlinked from job", "applicantCount": 0}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error unsyncing candidates: {str(e)}")


@router.put("/{job_id}")
async def update_job(job_id: str, job_data: JobRequest):
    """Update a job posting."""
    try:
        try:
            obj_id = ObjectId(job_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid job ID format")

        update_data = {
            **job_data.model_dump(),
            "updatedAt": datetime.now()
        }

        result = jobs_col.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")

        updated_job = jobs_col.find_one({"_id": obj_id})
        return JobResponse(**serialize_job(updated_job))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating job: {str(e)}")


@router.delete("/{job_id}")
async def delete_job(job_id: str):
    """Delete a job posting."""
    try:
        try:
            filter_doc = {"_id": ObjectId(job_id)}
        except Exception:
            filter_doc = {"jobId": job_id}

        result = jobs_col.delete_one(filter_doc)

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Job not found")

        return {"message": "Job deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting job: {str(e)}")
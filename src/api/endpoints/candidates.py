# src/api/endpoints/candidates.py
"""
Candidate-related API endpoints.
- GET /candidates - List all candidates (paginated)
- GET /candidates/{id} - Get single candidate
- POST /candidates - Create candidate (from form)
- POST /candidates/upload - Upload CSV/PDF (upsert by email)
- DELETE /candidates/{id} - Delete candidate
"""

from fastapi import APIRouter, Query, HTTPException, UploadFile, File
from typing import Optional, Any, Dict, List, Tuple
from datetime import datetime
from bson import ObjectId

from src.db import candidates_col
from src.schemas.request_models import (
    CandidateResponse,
    CandidateListResponse,
    FileUploadResponse,
)
from src.services.file_parser import FileParser

router = APIRouter()


def serialize_candidate(candidate: dict) -> dict:
    """Convert MongoDB document to API response."""
    if "_id" in candidate:
        candidate["id"] = str(candidate.pop("_id"))
    return candidate


@router.get("", response_model=CandidateListResponse)
async def list_candidates(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
):
    """List all candidates with pagination."""
    try:
        query_filter = {}
        if search:
            query_filter = {
                "$or": [
                    {"firstName": {"$regex": search, "$options": "i"}},
                    {"lastName": {"$regex": search, "$options": "i"}},
                    {"email": {"$regex": search, "$options": "i"}},
                ]
            }

        total = candidates_col.count_documents(query_filter)

        candidates_list = list(
            candidates_col.find(query_filter)
            .skip(skip)
            .limit(limit)
        )

        candidates_list = [serialize_candidate(c) for c in candidates_list]

        return CandidateListResponse(
            total=total,
            skip=skip,
            limit=limit,
            data=candidates_list,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candidates: {str(e)}")


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(candidate_id: str):
    """Get a single candidate by ID."""
    try:
        try:
            obj_id = ObjectId(candidate_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid candidate ID format")

        candidate = candidates_col.find_one({"_id": obj_id})
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")

        return CandidateResponse(**serialize_candidate(candidate))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching candidate: {str(e)}")


@router.post("", response_model=dict)
async def create_candidate(payload: Dict[str, Any]):
    """
    Create a candidate from a form payload.

    Expected minimum:
      - email
      - firstName (recommended)
      - lastName (recommended)
    """
    try:
        email = (payload.get("email") or "").strip().lower()
        if not email:
            raise HTTPException(status_code=400, detail="Email is required")

        existing = candidates_col.find_one({"email": email})
        if existing:
            raise HTTPException(status_code=409, detail="Candidate with this email already exists")

        payload["email"] = email
        now = datetime.utcnow().isoformat()
        payload["createdAt"] = payload.get("createdAt") or now
        payload["updatedAt"] = now
        payload.setdefault("source", "form")

        ins = candidates_col.insert_one(payload)
        return {"message": "Candidate created", "id": str(ins.inserted_id)}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating candidate: {str(e)}")


def _normalize_candidate_dict(c: Dict[str, Any], now: str) -> Dict[str, Any]:
    """Normalize candidate dict: email lower, timestamps, defaults."""
    out = dict(c)

    email = str(out.get("email") or "").strip().lower()
    out["email"] = email

    out["updatedAt"] = now
    out["createdAt"] = out.get("createdAt") or now

    out["firstName"] = str(out.get("firstName") or "Unknown").strip() or "Unknown"
    out["lastName"] = str(out.get("lastName") or "").strip()

    for k in ["skills", "languages", "experience", "education", "projects"]:
        if k in out and out[k] is None:
            out[k] = []
        if k in out and not isinstance(out[k], list):
            out[k] = []

    return out


@router.post("/upload", response_model=FileUploadResponse)
async def upload_candidates(file: UploadFile = File(...)):
    """
    Upload candidates from CSV or PDF file.
    Supported formats: CSV, PDF

    Behavior:
    - CSV: parse many candidates
    - PDF: parse single candidate (Gemini)
    - Upsert by email (update duplicates)
    """
    try:
        filename = (file.filename or "").lower()
        content = await file.read()

        candidates_data: List[Dict[str, Any]] = []
        errors: List[str] = []

        if filename.endswith(".csv"):
            candidates_data, errors = FileParser.parse_csv(content)

        elif filename.endswith(".pdf"):
            candidate, pdf_errors = await FileParser.parse_pdf(content)  # ✅ async now
            if candidate:
                candidates_data = [candidate]
            errors.extend(pdf_errors)

        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or PDF.")

        now = datetime.utcnow().isoformat()

        uploaded_count = 0
        updated_count = 0

        for c in candidates_data:
            if not isinstance(c, dict):
                errors.append("Invalid candidate object; skipped")
                continue

            normalized = _normalize_candidate_dict(c, now)
            email = normalized.get("email") or ""
            if not email:
                errors.append("Candidate missing email; skipped")
                continue

            res = candidates_col.update_one(
                {"email": email},
                {"$set": normalized},
                upsert=True,
            )

            if res.upserted_id is not None:
                uploaded_count += 1
            else:
                updated_count += 1

        return FileUploadResponse(
            message=f"Uploaded {uploaded_count}, updated {updated_count}",
            uploaded_count=uploaded_count,
            updated_count=updated_count,
            failed_count=len(errors),
            errors=errors,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.delete("/{candidate_id}")
async def delete_candidate(candidate_id: str):
    """Delete a candidate."""
    try:
        try:
            obj_id = ObjectId(candidate_id)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid candidate ID format")

        result = candidates_col.delete_one({"_id": obj_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Candidate not found")

        return {"message": "Candidate deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting candidate: {str(e)}")
# src/schemas/request_models.py
"""
Request/Response Pydantic models for API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime



class CandidateResponse(BaseModel):
    """Response model for candidate."""
    id: str = Field(alias="_id")
    firstName: str
    lastName: str
    email: str
    headline: Optional[str] = None
    bio: Optional[str] = None
    location: Optional[str] = None
    skills: List[dict] = []
    experience: List[dict] = []
    education: List[dict] = []
    projects: List[dict] = []
    languages: List[dict] = []
    availability: Optional[dict] = None
    socialLinks: Optional[dict] = None
    
    class Config:
        populate_by_name = True


class CandidateListResponse(BaseModel):
    """Response for paginated candidate list."""
    total: int
    skip: int
    limit: int
    data: List[CandidateResponse]


class FileUploadResponse(BaseModel):
    """Response after file upload."""
    message: str
    uploaded_count: int
    updated_count: int = 0  # ✅ NEW
    failed_count: int
    errors: List[str] = []



class JobRequest(BaseModel):
    """Request model for creating a job."""
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10)
    location: str
    employmentType: str
    requiredSkills: List[str]
    preferredSkills: Optional[List[str]] = []
    minYearsExperience: int = 0
    requiredEducation: Optional[str] = None
    softSkills: Optional[List[str]] = []
    includeMockCandidates: Optional[bool] = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "title": "Backend Engineer",
                "description": "Build scalable APIs...",
                "location": "Kigali, Rwanda",
                "employmentType": "Full-time",
                "requiredSkills": ["Node.js", "Python", "REST API"],
                "preferredSkills": ["AWS", "Docker"],
                "minYearsExperience": 3,
                "requiredEducation": "Bachelor's in CS"
            }
        }


class JobResponse(BaseModel):
    """Response model for job."""
    id: str = Field(alias="_id")
    jobId: Optional[str] = None
    title: str
    description: str
    location: str
    employmentType: str
    requiredSkills: List[str]
    preferredSkills: Optional[List[str]] = []
    minYearsExperience: int
    requiredEducation: Optional[str] = None
    softSkills: Optional[List[str]] = []
    status: Optional[str] = "open"
    applicantCount: Optional[int] = 0        
    useAllCandidates: Optional[bool] = False  
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        populate_by_name = True


class JobListResponse(BaseModel):
    """Response for paginated job list."""
    total: int
    skip: int
    limit: int
    data: List[JobResponse]



class ScreeningRequest(BaseModel):
    """Request to trigger screening."""
    job_id: str = Field(..., description="Job ID to screen candidates for")
    candidate_ids: Optional[List[str]] = None
    use_all_candidates: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "JOB-001",
                "candidate_ids": ["id1", "id2"],
                "use_all_candidates": False
            }
        }


class ShortlistEntry(BaseModel):
    """Single shortlisted candidate."""
    rank: int
    candidateId: str
    matchScore: int
    strengths: List[str]
    gaps: List[str]
    recommendation: str
    explanation: Optional[str] = None
    finalScore: Optional[int] = None


class ScreeningResultResponse(BaseModel):
    """Response model for screening result."""
    id: str = Field(alias="_id")
    job: dict
    total_evaluated: int
    successful_evaluations: int
    failed_evaluations: int
    shortlist: List[ShortlistEntry]
    timestamp: Optional[datetime] = None
    screeningRunId: Optional[str] = None
    
    class Config:
        populate_by_name = True


class ScreeningResultListResponse(BaseModel):
    """Response for screening results list."""
    total: int
    skip: int
    limit: int
    data: List[dict]



class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: datetime
    mongodb_connected: bool
    message: str
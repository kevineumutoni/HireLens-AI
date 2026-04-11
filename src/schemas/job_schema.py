"""
Pydantic models for Job Requirements.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class JobRequirement(BaseModel):
    name: str
    category: str = Field(..., pattern="^(skill|experience|education|soft_skill)$")
    required: bool = Field(default=True)
    preferredLevel: Optional[str] = Field(None, pattern="^(Beginner|Intermediate|Advanced|Expert)$")
    weight: Optional[float] = Field(None, ge=0, le=1)


class Job(BaseModel):
    jobId: str
    title: str
    description: str
    location: str
    employmentType: str = Field(..., pattern="^(Full-time|Part-time|Contract|Internship)$")
    
    requiredSkills: List[str] = Field(..., min_length=1)
    preferredSkills: Optional[List[str]] = Field(default_factory=list)
    minYearsExperience: int = Field(..., ge=0)
    requiredEducation: Optional[str] = None
    softSkills: Optional[List[str]] = Field(default_factory=list)
    
    requirements: Optional[List[JobRequirement]] = None
    
    postedDate: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    isActive: bool = Field(default=True)
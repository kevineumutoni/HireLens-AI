"""
Pydantic models for the Talent Profile Schema (Umurava spec).
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class Skill(BaseModel):
    name: str
    level: str = Field(..., pattern="^(Beginner|Intermediate|Advanced|Expert)$")
    yearsOfExperience: int = Field(..., ge=0)


class Language(BaseModel):
    name: str
    proficiency: str = Field(..., pattern="^(Basic|Conversational|Fluent|Native)$")


class WorkExperience(BaseModel):
    company: str
    role: str
    startDate: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    endDate: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$|^Present$")
    description: str
    technologies: List[str] = Field(default_factory=list)
    isCurrent: bool = Field(default=False)


class Education(BaseModel):
    institution: str
    degree: str
    fieldOfStudy: str
    startYear: int = Field(..., ge=1900, le=2100)
    endYear: Optional[int] = Field(None, ge=1900, le=2100)


class Certification(BaseModel):
    name: str
    issuer: str
    issueDate: str = Field(..., pattern=r"^\d{4}-\d{2}$")


class Project(BaseModel):
    name: str
    description: str
    technologies: List[str] = Field(default_factory=list)
    role: str
    link: Optional[str] = None
    startDate: str = Field(..., pattern=r"^\d{4}-\d{2}$")
    endDate: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}$")


class Availability(BaseModel):
    status: str = Field(..., pattern="^(Available|Open to Opportunities|Not Available)$")
    # ✅ Added Internship to allowed values
    type: str = Field(..., pattern="^(Full-time|Part-time|Contract|Internship)$")
    startDate: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")


class SocialLinks(BaseModel):
    linkedin: Optional[str] = None
    github: Optional[str] = None
    portfolio: Optional[str] = None


class TalentProfile(BaseModel):
    # Basic Information (Required)
    firstName: str
    lastName: str
    email: str = Field(..., pattern=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    headline: str
    bio: Optional[str] = None
    location: str
    
    # Skills & Languages
    skills: List[Skill] = Field(..., min_length=1)
    languages: Optional[List[Language]] = Field(default_factory=list)
    
    # Work Experience (Required)
    experience: List[WorkExperience] = Field(..., min_length=1)
    
    # Education (Required)
    education: List[Education] = Field(..., min_length=1)
    
    # Certifications (Optional)
    certifications: Optional[List[Certification]] = Field(default_factory=list)
    
    # Projects (Required)
    projects: List[Project] = Field(..., min_length=1)
    
    # Availability (Required)
    availability: Availability
    
    # Social Links (Optional)
    socialLinks: Optional[SocialLinks] = None
    
    # AI-generated fields (added post-screening)
    aiMatchScore: Optional[float] = Field(None, ge=0, le=100)
    aiReasoning: Optional[dict] = None
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        return v.lower()
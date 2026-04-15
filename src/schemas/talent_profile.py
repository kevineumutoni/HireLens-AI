# src/schemas/talent_profile.py
# Matches the Umurava Talent Profile Schema specification exactly.
from pydantic import BaseModel
from typing import Optional, List

class Skill(BaseModel):
    name: str
    level: str  # Beginner | Intermediate | Advanced | Expert
    yearsOfExperience: int

class Language(BaseModel):
    name: str
    proficiency: str  # Basic | Conversational | Fluent | Native

class WorkExperience(BaseModel):
    company: str
    role: str
    startDate: str        # YYYY-MM
    endDate: str          # YYYY-MM or "Present"
    description: str = ""
    technologies: List[str] = []
    isCurrent: bool = False

class Education(BaseModel):
    institution: str
    degree: str
    fieldOfStudy: str
    startYear: int
    endYear: int

class Certification(BaseModel):
    name: str
    issuer: str
    issueDate: str  # YYYY-MM

class Project(BaseModel):
    name: str
    description: str
    technologies: List[str] = []
    role: str
    link: Optional[str] = None
    startDate: str
    endDate: str

class Availability(BaseModel):
    status: str   # Available | Open to Opportunities | Not Available
    type: str     # Full-time | Part-time | Contract | Internship
    startDate: Optional[str] = None

class TalentProfile(BaseModel):
    firstName: str
    lastName: str
    email: str
    headline: str
    bio: Optional[str] = None
    location: str
    skills: List[Skill] = []
    languages: Optional[List[Language]] = None
    experience: List[WorkExperience] = []
    education: List[Education] = []
    certifications: Optional[List[Certification]] = None
    projects: List[Project] = []
    availability: Availability
    socialLinks: Optional[dict] = None
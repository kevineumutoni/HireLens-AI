# src/schemas/job_schema.py
from pydantic import BaseModel
from typing import List, Optional

class Job(BaseModel):
    jobId: str
    title: str
    description: str
    location: str
    employmentType: str
    requiredSkills: List[str]
    preferredSkills: List[str] = []
    minYearsExperience: int
    requiredEducation: str
    softSkills: List[str] = []
    postedDate: str
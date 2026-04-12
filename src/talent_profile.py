# src/talent_profile.py
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class TalentProfile:
    """
    Talent profile validator following Umurava schema specification.
    Ensures data consistency and AI-readiness.
    """
    
    REQUIRED_FIELDS = {
        "firstName", "lastName", "email", "headline", "location",
        "skills", "experience", "education", "projects", "availability"
    }
    
    OPTIONAL_FIELDS = {
        "bio", "languages", "certifications", "socialLinks"
    }
    
    def __init__(self, profile_data: Dict[str, Any]):
        """Initialize and validate talent profile."""
        self.profile = profile_data
        self.validation_errors = []
        self.validate()
    
    def validate(self) -> bool:
        """Validate profile against schema."""
        # Check required fields
        missing_fields = self.REQUIRED_FIELDS - set(self.profile.keys())
        if missing_fields:
            self.validation_errors.append(f"Missing required fields: {missing_fields}")
            return False
        
        # Validate email format
        if "@" not in self.profile.get("email", ""):
            self.validation_errors.append("Invalid email format")
            return False
        
        # Validate skills structure
        if not isinstance(self.profile.get("skills"), list):
            self.validation_errors.append("Skills must be a list")
            return False
        
        for skill in self.profile.get("skills", []):
            if not all(k in skill for k in ["name", "level", "yearsOfExperience"]):
                self.validation_errors.append(f"Invalid skill structure: {skill}")
                return False
        
        # Validate experience structure
        if not isinstance(self.profile.get("experience"), list):
            self.validation_errors.append("Experience must be a list")
            return False
        
        # Validate education structure
        if not isinstance(self.profile.get("education"), list):
            self.validation_errors.append("Education must be a list")
            return False
        
        return len(self.validation_errors) == 0
    
    def to_ai_ready_format(self) -> Dict[str, Any]:
        """Convert to optimized format for AI screening."""
        return {
            "id": self.profile.get("id", ""),
            "full_name": f"{self.profile['firstName']} {self.profile['lastName']}",
            "headline": self.profile.get("headline", ""),
            "location": self.profile.get("location", ""),
            "summary": self._build_summary(),
            "skills": self.profile.get("skills", []),
            "experience_years": self._calculate_experience_years(),
            "highest_education": self._get_highest_education(),
            "certifications": self.profile.get("certifications", []),
            "projects": self.profile.get("projects", []),
            "languages": self.profile.get("languages", []),
            "availability": self.profile.get("availability", {})
        }
    
    def _build_summary(self) -> str:
        """Build a professional summary from profile data."""
        bio = self.profile.get("bio", "")
        headline = self.profile.get("headline", "")
        return f"{headline}. {bio}".strip()
    
    def _calculate_experience_years(self) -> float:
        """Calculate total years of professional experience."""
        total_months = 0
        for exp in self.profile.get("experience", []):
            start = datetime.strptime(exp.get("Start Date", "2020-01"), "%Y-%m")
            end_str = exp.get("End Date", "Present")
            end = datetime.now() if end_str == "Present" else datetime.strptime(end_str, "%Y-%m")
            total_months += (end.year - start.year) * 12 + (end.month - start.month)
        
        return round(total_months / 12, 1)
    
    def _get_highest_education(self) -> Dict[str, Any]:
        """Extract highest level of education."""
        education = self.profile.get("education", [])
        if not education:
            return {}
        
        degree_hierarchy = {
            "PhD": 5,
            "Master's": 4,
            "Bachelor's": 3,
            "Associate": 2,
            "High School": 1
        }
        
        highest = max(
            education,
            key=lambda x: degree_hierarchy.get(x.get("degree", ""), 0)
        )
        
        return {
            "degree": highest.get("degree", ""),
            "field": highest.get("Field of Study", ""),
            "institution": highest.get("institution", "")
        }
    
    def get_errors(self) -> List[str]:
        """Get validation errors."""
        return self.validation_errors
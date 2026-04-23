import pandas as pd
import fitz  # PyMuPDF
from typing import List, Optional
from src.schemas.talent_profile import TalentProfile, Skill, WorkExperience, Education, Project, Availability

def load_candidates_from_csv(csv_path: str) -> List[TalentProfile]:
    """
    Minimal CSV ingestion.
    Expected columns example: firstName,lastName,email,headline,location,skills
    skills can be "Python:Intermediate:3;Node.js:Advanced:4"
    """
    df = pd.read_csv(csv_path)
    candidates: List[TalentProfile] = []

    for _, row in df.iterrows():
        raw_skills = str(row.get("skills", "") or "")
        skills: List[Skill] = []
        for item in raw_skills.split(";"):
            item = item.strip()
            if not item:
                continue
            parts = [p.strip() for p in item.split(":")]
            if len(parts) >= 3:
                skills.append(Skill(name=parts[0], level=parts[1], yearsOfExperience=int(parts[2])))

        candidates.append(
            TalentProfile(
                firstName=str(row.get("firstName", "Unknown")),
                lastName=str(row.get("lastName", "Unknown")),
                email=str(row.get("email", "unknown@example.com")),
                headline=str(row.get("headline", "Candidate")),
                bio=None,
                location=str(row.get("location", "Unknown")),
                skills=skills,
                languages=None,
                experience=[],     # you can extend later
                education=[],      # you can extend later
                certifications=None,
                projects=[],
                availability=Availability(status="Open to Opportunities", type="Full-time", startDate=None),
                socialLinks=None,
            )
        )

    return candidates

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF resume."""
    doc = fitz.open(pdf_path)
    chunks = []
    for page in doc:
        chunks.append(page.get_text("text"))
    return "\n".join(chunks).strip()
# src/services/file_parser.py
"""
Service for parsing uploaded files (CSV, PDF).
Converts files to candidate profiles matching TalentProfile schema.

Updates:
- CSV parsing: same as before, but normalizes email + sets timestamps
- PDF parsing: uses GeminiClient.extract_candidate_profile(resume_text)
  (falls back to basic extraction if Gemini fails)
- IMPORTANT: converts Gemini skills list[str] -> list[dict] to match CandidateResponse/UI
"""

import io
import pandas as pd
from typing import List, Dict, Tuple, Any
from datetime import datetime
import PyPDF2


class FileParser:
    """Parse CSV and PDF files into candidate data."""

    @staticmethod
    def parse_csv(file_content: bytes) -> Tuple[List[Dict], List[str]]:
        """
        Parse CSV file into candidate dictionaries.

        Returns:
            (candidates, errors)
        """
        try:
            df = pd.read_csv(io.BytesIO(file_content))

            candidates: List[Dict] = []
            errors: List[str] = []
            now = datetime.utcnow().isoformat()

            for idx, row in df.iterrows():
                try:
                    email = str(row.get("email", row.get("Email", ""))).strip().lower()

                    candidate = {
                        "firstName": str(row.get("firstName", row.get("First Name", "Unknown"))).strip(),
                        "lastName": str(row.get("lastName", row.get("Last Name", ""))).strip(),
                        "email": email,
                        "headline": str(row.get("headline", row.get("Headline", ""))).strip(),
                        "bio": str(row.get("bio", row.get("Bio", ""))).strip(),
                        "location": str(row.get("location", row.get("Location", ""))).strip(),
                        "skills": FileParser._parse_skills(row.get("skills", row.get("Skills", ""))),
                        "languages": FileParser._parse_languages(row.get("languages", row.get("Languages", ""))),
                        "experience": FileParser._parse_experience(row.get("experience", row.get("Experience", ""))),
                        "education": FileParser._parse_education(row.get("education", row.get("Education", ""))),
                        "availability": {
                            "status": str(row.get("status", "Open to Opportunities")).strip(),
                            "type": str(row.get("type", "Full-time")).strip(),
                            "startDate": None,
                        },
                        "createdAt": now,
                        "updatedAt": now,
                        "source": "csv",
                    }

                    if candidate["firstName"] and candidate["email"]:
                        candidates.append(candidate)
                    else:
                        errors.append(f"Row {idx + 1}: Missing firstName or email")

                except Exception as e:
                    errors.append(f"Row {idx + 1}: {str(e)}")

            return candidates, errors

        except Exception as e:
            return [], [f"CSV parsing error: {str(e)}"]

    @staticmethod
    async def parse_pdf(file_content: bytes) -> Tuple[Dict, List[str]]:
        """
        Parse PDF resume into candidate data.
        Uses Gemini extraction. If Gemini fails, falls back to basic heuristics.

        Returns:
            (candidate_dict, errors)
        """
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""

            for page in pdf_reader.pages:
                text += (page.extract_text() or "") + "\n"

            text = text.strip()
            if not text:
                return {}, ["PDF parsing error: could not extract text from PDF"]

            now = datetime.utcnow().isoformat()

            # ---- Gemini extraction ----
            try:
                from src.services.gemini_client import GeminiClient

                gemini = GeminiClient(debug=True)
                result = await gemini.extract_candidate_profile(text)

                if result.get("success") and isinstance(result.get("candidate"), dict):
                    candidate: Dict[str, Any] = result["candidate"]

                    # Normalize core fields
                    candidate["email"] = str(candidate.get("email") or "").strip().lower()
                    candidate["firstName"] = str(candidate.get("firstName") or "Unknown").strip() or "Unknown"
                    candidate["lastName"] = str(candidate.get("lastName") or "").strip()
                    candidate["headline"] = str(candidate.get("headline") or "").strip()
                    candidate["location"] = str(candidate.get("location") or "").strip()

                    # ✅ Convert skills format if Gemini returned list[str]
                    skills = candidate.get("skills") or []
                    if isinstance(skills, list):
                        if len(skills) == 0 or isinstance(skills[0], str):
                            candidate["skills"] = [
                                {"name": str(s).strip(), "level": "Intermediate", "yearsOfExperience": 1}
                                for s in skills
                                if str(s).strip()
                            ]
                        elif isinstance(skills[0], dict):
                            # already list[dict]
                            candidate["skills"] = skills
                        else:
                            candidate["skills"] = []
                    else:
                        candidate["skills"] = []

                    for k in ["languages", "experience", "education", "projects"]:
                        if k not in candidate or candidate[k] is None:
                            candidate[k] = []
                        if not isinstance(candidate[k], list):
                            candidate[k] = []

                    candidate["createdAt"] = candidate.get("createdAt") or now
                    candidate["updatedAt"] = now
                    candidate["source"] = "pdf_gemini"

                    if not candidate.get("email"):
                        candidate["email"] = FileParser._extract_email(text)

                    return candidate, []

                gemini_error = result.get("error") or "Gemini extraction failed"
                partial = result.get("candidate") if isinstance(result.get("candidate"), dict) else {}
                if partial:
                    partial["createdAt"] = partial.get("createdAt") or now
                    partial["updatedAt"] = now
                    partial["source"] = "pdf_gemini_partial"
                    if not partial.get("email"):
                        partial["email"] = FileParser._extract_email(text)
                    if not partial.get("firstName"):
                        partial["firstName"] = "Unknown"
                    return partial, [gemini_error]

            except Exception as e:
                gemini_error = f"Gemini error: {str(e)}"

            lines = text.split("\n")
            candidate = {
                "firstName": "FromPDF",
                "lastName": "Resume",
                "email": FileParser._extract_email(text),
                "headline": FileParser._extract_headline(lines),
                "bio": FileParser._extract_summary(text),
                "location": FileParser._extract_location(text),
                "skills": FileParser._extract_skills_from_text(text),
                "experience": FileParser._extract_experience_from_text(text),
                "education": FileParser._extract_education_from_text(text),
                "availability": {"status": "Open to Opportunities", "type": "Full-time", "startDate": None},
                "createdAt": now,
                "updatedAt": now,
                "source": "pdf_fallback",
            }

            if "gemini_error" in locals():
                return candidate, [gemini_error]

            return candidate, []

        except Exception as e:
            return {}, [f"PDF parsing error: {str(e)}"]


    @staticmethod
    def _parse_skills(skills_str: str) -> List[Dict]:
        """Parse comma-separated skills."""
        if not skills_str or pd.isna(skills_str):
            return []

        skills = []
        for skill in str(skills_str).split(","):
            skill = skill.strip()
            if skill:
                skills.append({"name": skill, "level": "Intermediate", "yearsOfExperience": 1})

        return skills

    @staticmethod
    def _parse_languages(lang_str: str) -> List[Dict]:
        """Parse comma-separated languages."""
        if not lang_str or pd.isna(lang_str):
            return []

        languages = []
        for lang in str(lang_str).split(","):
            lang = lang.strip()
            if lang:
                languages.append({"name": lang, "proficiency": "Fluent"})

        return languages

    @staticmethod
    def _parse_experience(exp_str: str) -> List[Dict]:
        """Parse experience from string."""
        if not exp_str or pd.isna(exp_str):
            return []

        return [
            {
                "company": "Previous Company",
                "role": "Developer",
                "description": str(exp_str).strip(),
                "technologies": [],
                "isCurrent": False,
            }
        ]

    @staticmethod
    def _parse_education(edu_str: str) -> List[Dict]:
        """Parse education from string."""
        if not edu_str or pd.isna(edu_str):
            return []

        return [
            {
                "institution": str(edu_str).strip(),
                "degree": "Bachelor's",
                "fieldOfStudy": "Computer Science",
                "startYear": 2015,
                "endYear": 2019,
            }
        ]

    @staticmethod
    def _extract_email(text: str) -> str:
        """Extract email from text."""
        import re

        emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
        return emails[0].strip().lower() if emails else ""

    @staticmethod
    def _extract_headline(lines: List[str]) -> str:
        """Extract headline (usually first non-empty line)."""
        for line in lines[:5]:
            line = line.strip()
            if 10 < len(line) < 200:
                return line
        return "Professional"

    @staticmethod
    def _extract_summary(text: str) -> str:
        """Extract summary from resume."""
        lines = text.split("\n")
        summary = " ".join(lines[1:5])
        return summary[:500] if summary else "Experienced professional"

    @staticmethod
    def _extract_location(text: str) -> str:
        """Extract location from text."""
        locations = ["Kigali", "Nairobi", "Kampala", "Lagos", "Rwanda", "Kenya", "Uganda"]
        for location in locations:
            if location.lower() in text.lower():
                return location
        return "Remote"

    @staticmethod
    def _extract_skills_from_text(text: str) -> List[Dict]:
        """Extract technical skills from resume text."""
        skill_keywords = [
            "Python",
            "Node.js",
            "React",
            "TypeScript",
            "JavaScript",
            "MongoDB",
            "PostgreSQL",
            "AWS",
            "Docker",
            "REST API",
            "FastAPI",
            "SQL",
            "GraphQL",
            "Git",
            "Redis",
        ]

        skills = []
        for skill in skill_keywords:
            if skill.lower() in text.lower():
                skills.append({"name": skill, "level": "Intermediate", "yearsOfExperience": 1})

        return skills[:8]

    @staticmethod
    def _extract_experience_from_text(text: str) -> List[Dict]:
        """Extract experience from resume."""
        return [
            {
                "company": "Previous Role",
                "role": "Developer",
                "description": "Experienced developer",
                "technologies": [],
                "isCurrent": False,
            }
        ]

    @staticmethod
    def _extract_education_from_text(text: str) -> List[Dict]:
        """Extract education from resume."""
        return [
            {
                "institution": "University",
                "degree": "Bachelor's",
                "fieldOfStudy": "Computer Science",
                "startYear": 2015,
                "endYear": 2019,
            }
        ]
"""
Utilities to format Python objects into prompt-ready strings.
"""
from src.schemas.talent_profile import TalentProfile
from src.schemas.job_schema import Job


def format_job_for_prompt(job: Job) -> str:
    """Convert Job object into AI-friendly description."""
    requirements_text = []
    
    if job.requiredSkills:
        requirements_text.append(f"• Required skills: {', '.join(job.requiredSkills)}")
    if job.preferredSkills:
        requirements_text.append(f"• Preferred skills: {', '.join(job.preferredSkills)}")
    if job.minYearsExperience:
        requirements_text.append(f"• Minimum experience: {job.minYearsExperience} years")
    if job.requiredEducation:
        requirements_text.append(f"• Education: {job.requiredEducation}")
    if job.softSkills:
        requirements_text.append(f"• Soft skills: {', '.join(job.softSkills)}")
    
    return f"""
Role: {job.title}
Location: {job.location}
Type: {job.employmentType}

Description:
{job.description}

Key Requirements:
{chr(10).join(requirements_text)}
""".strip()


def format_candidate_for_prompt(candidate: TalentProfile) -> str:
    """Convert TalentProfile into AI-friendly summary."""
    skills_summary = [f"{s.name} ({s.level}, {s.yearsOfExperience}y)" for s in candidate.skills[:10]]
    experience_summary = [f"{e.role} at {e.company} ({e.startDate}–{e.endDate or 'Present'})" for e in candidate.experience[:3]]
    
    return f"""
Name: {candidate.firstName} {candidate.lastName}
Headline: {candidate.headline}
Location: {candidate.location}

Top Skills: {', '.join(skills_summary)}
Recent Experience:
{chr(10).join(f"  • {exp}" for exp in experience_summary)}

Education: {candidate.education[0].degree} in {candidate.education[0].fieldOfStudy} ({candidate.education[0].institution})
Key Projects: {', '.join([p.name for p in candidate.projects[:2]])}
Availability: {candidate.availability.status} – {candidate.availability.type}
""".strip()


def format_resume_text_for_prompt(resume_text: str) -> str:
    """Sanitize and truncate resume text for parsing prompt."""
    cleaned = " ".join(resume_text.split())
    max_length = 8000
    return cleaned[:max_length] + ("..." if len(cleaned) > max_length else "")
# src/dummy_data.py
"""
Generate realistic dummy candidates matching Umurava schema.
NO hardcoded dates, NO random crashes, DIVERSE profiles.
FIXED: randint edge case when years_exp=0
"""
import random
from datetime import datetime, timedelta
from typing import List
from src.schemas.talent_profile import TalentProfile, Skill, WorkExperience, Education, Project, Availability, Language

class DummyDataGenerator:
    """Generate diverse candidate profiles for screening tests."""
    
    # Predefined pools for realistic variety
    FIRST_NAMES = [
        "Jean", "Amina", "David", "Marie", "Khalid", "Fatima",
        "Emmanuel", "Nadia", "Ibrahim", "Sophia", "Claude",
        "Pascale", "Innocent", "Diane", "Joseph", "Beatrice"
    ]
    
    LAST_NAMES = [
        "Mukama", "Niyonzima", "Kamali", "Habimana", "Rutayisire",
        "Nyonzima", "Kayihura", "Kabangu", "Ntezimana", "Muhire",
        "Byamugisha", "Mukunzi", "Gitonga", "Okonkwo", "Mensah"
    ]
    
    LOCATIONS = [
        "Kigali, Rwanda",
        "Nairobi, Kenya",
        "Kampala, Uganda",
        "Dar es Salaam, Tanzania",
        "Lagos, Nigeria",
        "Remote",
        "Kigali (Remote)",
        "Nairobi (Remote)"
    ]
    
    SKILLS = [
        {"name": "Node.js", "levels": ["Beginner", "Intermediate", "Advanced", "Expert"]},
        {"name": "Python", "levels": ["Beginner", "Intermediate", "Advanced", "Expert"]},
        {"name": "TypeScript", "levels": ["Beginner", "Intermediate", "Advanced"]},
        {"name": "MongoDB", "levels": ["Beginner", "Intermediate", "Advanced"]},
        {"name": "PostgreSQL", "levels": ["Beginner", "Intermediate", "Advanced"]},
        {"name": "React", "levels": ["Beginner", "Intermediate", "Advanced", "Expert"]},
        {"name": "REST API", "levels": ["Intermediate", "Advanced", "Expert"]},
        {"name": "AWS", "levels": ["Beginner", "Intermediate", "Advanced"]},
        {"name": "Docker", "levels": ["Beginner", "Intermediate", "Advanced"]},
        {"name": "Gemini API", "levels": ["Beginner", "Intermediate"]},
        {"name": "GraphQL", "levels": ["Beginner", "Intermediate", "Advanced"]},
        {"name": "Redis", "levels": ["Beginner", "Intermediate", "Advanced"]},
        {"name": "FastAPI", "levels": ["Beginner", "Intermediate", "Advanced"]},
        {"name": "Git", "levels": ["Intermediate", "Advanced", "Expert"]},
        {"name": "SQL", "levels": ["Beginner", "Intermediate", "Advanced"]},
    ]
    
    COMPANIES = [
        "TechStart Rwanda", "DevHub Africa", "Innovation Lab", "DataSolutions Ltd",
        "CloudTech Africa", "AI Ventures", "StartupHub Kigali", "Tech Alliance",
        "Digital Africa", "Software Forge", "Code Factory", "ByteWorks"
    ]
    
    TITLES = [
        "Backend Engineer",
        "Full-Stack Developer",
        "Senior Developer",
        "Junior Developer",
        "ML Engineer",
        "Data Engineer",
        "API Developer",
        "DevOps Engineer"
    ]
    
    UNIVERSITIES = [
        "University of Rwanda",
        "African Leadership University",
        "Ashesi University",
        "University of Nairobi",
        "Makerere University",
        "University of Ghana",
        "Cape Peninsula University of Technology",
        "Strathmore University"
    ]
    
    LANGUAGES = [
        "English", "French", "Swahili", "Kinyarwanda", "Luganda", "Amharic"
    ]
    
    @staticmethod
    def _generate_valid_date_range(years_of_exp: int) -> tuple:
        """Generate realistic start/end dates for work experience."""
        # FIXED: Handle edge case where years_of_exp might be 0 or negative
        years_of_exp = max(1, years_of_exp)  # Minimum 1 year
        
        # End date is today or up to 3 months ago
        end_days_ago = random.randint(0, 90)
        end_date = datetime.now() - timedelta(days=end_days_ago)
        
        # Start date is years_of_exp ago, plus random variance
        start_days_ago = random.randint(
            int(365 * years_of_exp),
            int(365 * years_of_exp) + 180
        )
        start_date = datetime.now() - timedelta(days=start_days_ago)
        
        return start_date.strftime("%Y-%m"), end_date.strftime("%Y-%m")
    
    @staticmethod
    def generate_candidate(candidate_id: str, profile_type: str = "balanced") -> TalentProfile:
        """
        Generate a single realistic candidate.
        profile_type: "strong", "moderate", "weak", "balanced"
        """
        first_name = random.choice(DummyDataGenerator.FIRST_NAMES)
        last_name = random.choice(DummyDataGenerator.LAST_NAMES)
        location = random.choice(DummyDataGenerator.LOCATIONS)
        
        # Determine experience level based on profile
        if profile_type == "strong":
            years_exp = random.randint(4, 8)
            num_skills = random.randint(6, 10)
            skill_level_dist = ["Advanced", "Advanced", "Expert", "Intermediate"]
        elif profile_type == "moderate":
            years_exp = random.randint(2, 4)
            num_skills = random.randint(4, 6)
            skill_level_dist = ["Intermediate", "Intermediate", "Advanced", "Beginner"]
        elif profile_type == "weak":
            years_exp = random.randint(1, 2)  # FIXED: Changed from (0, 2) to (1, 2)
            num_skills = random.randint(2, 4)
            skill_level_dist = ["Beginner", "Beginner", "Intermediate"]
        else:  # balanced
            years_exp = random.randint(1, 6)
            num_skills = random.randint(3, 7)
            skill_level_dist = ["Intermediate", "Advanced", "Beginner", "Expert"]
        
        # SAFETY: Ensure years_exp is always >= 1
        years_exp = max(1, years_exp)
        
        # Generate skills
        selected_skills = random.sample(DummyDataGenerator.SKILLS, min(num_skills, len(DummyDataGenerator.SKILLS)))
        skills = []
        for skill in selected_skills:
            level = random.choice(skill_level_dist)
            if level in skill["levels"]:
                # FIXED: Ensure years_of_experience is always valid (1 to years_exp)
                skill_years = random.randint(1, max(1, years_exp))
                skills.append(Skill(
                    name=skill["name"],
                    level=level,
                    yearsOfExperience=skill_years
                ))
        
        # Generate languages
        languages = []
        for _ in range(random.randint(1, 2)):
            languages.append(Language(
                name=random.choice(DummyDataGenerator.LANGUAGES),
                proficiency=random.choice(["Basic", "Conversational", "Fluent", "Native"])
            ))
        
        # Generate work experience
        experiences = []
        for _ in range(random.randint(1, 3)):
            start, end = DummyDataGenerator._generate_valid_date_range(years_exp)
            experiences.append(WorkExperience(
                company=random.choice(DummyDataGenerator.COMPANIES),
                role=random.choice(DummyDataGenerator.TITLES),
                startDate=start,
                endDate=end if random.random() > 0.3 else "Present",
                description=f"Developed scalable solutions, led technical initiatives, mentored junior developers",
                technologies=[s.name for s in random.sample(skills, min(3, len(skills))) if skills],
                isCurrent=True if random.random() > 0.5 else False
            ))
        
        # Generate education - FIXED: endYear must be after startYear
        start_year = datetime.now().year - random.randint(6, 12)
        end_year = start_year + random.randint(3, 5)  # FIXED: Ensure endYear > startYear
        
        education = [
            Education(
                institution=random.choice(DummyDataGenerator.UNIVERSITIES),
                degree=random.choice(["Bachelor's", "Master's"]),
                fieldOfStudy=random.choice(["Computer Science", "Software Engineering", "Information Technology"]),
                startYear=start_year,
                endYear=end_year
            )
        ]
        
        # Generate projects
        projects = []
        for _ in range(random.randint(1, 3)):
            start, end = DummyDataGenerator._generate_valid_date_range(random.randint(1, 3))
            projects.append(Project(
                name=f"Project {random.choice(['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon'])}",
                description="Full-stack application with modern tech stack and API integration",
                technologies=[s.name for s in random.sample(skills, min(3, len(skills))) if skills],
                role=random.choice(["Lead Developer", "Backend Engineer", "Full-Stack Developer"]),
                startDate=start,
                endDate=end,
                link=f"https://github.com/{first_name.lower()}-{last_name.lower()}/{candidate_id}"
            ))
        
        # Availability
        availability = Availability(
            status=random.choice(["Available", "Open to Opportunities", "Available"]),
            type=random.choice(["Full-time", "Full-time", "Contract"]),
            startDate=None
        )
        
        return TalentProfile(
            firstName=first_name,
            lastName=last_name,
            email=f"{first_name.lower()}.{last_name.lower()}@{candidate_id}.com",
            headline=f"{random.choice(DummyDataGenerator.TITLES)} | Specialized in {random.choice([s.name for s in skills[:2]] if skills else ['Backend'])}",
            bio=f"Passionate developer with {years_exp} years of experience in building scalable systems.",
            location=location,
            skills=skills,
            languages=languages,
            experience=experiences,
            education=education,
            projects=projects,
            availability=availability,
            socialLinks={
                "linkedin": f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
                "github": f"https://github.com/{first_name.lower()}-{last_name.lower()}",
                "portfolio": f"https://{first_name.lower()}-{last_name.lower()}.dev"
            }
        )
    
    @staticmethod
    def generate_candidates_batch(count: int = 50) -> List[TalentProfile]:
        """Generate diverse candidate pool."""
        candidates = []
        
        # Distribute across profile types for diversity
        strong_count = int(count * 0.3)      # 30% strong
        moderate_count = int(count * 0.4)    # 40% moderate
        weak_count = count - strong_count - moderate_count  # 30% weak/balanced
        
        for i in range(strong_count):
            candidates.append(DummyDataGenerator.generate_candidate(f"cand_{i:03d}", "strong"))
        
        for i in range(moderate_count):
            candidates.append(DummyDataGenerator.generate_candidate(f"cand_{strong_count + i:03d}", "moderate"))
        
        for i in range(weak_count):
            candidates.append(DummyDataGenerator.generate_candidate(f"cand_{strong_count + moderate_count + i:03d}", "weak"))
        
        random.shuffle(candidates)
        return candidates
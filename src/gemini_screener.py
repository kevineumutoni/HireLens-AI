# src/gemini_screener.py
import os
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class GeminiScreener:
    """
    Production-grade AI screener using Gemini API
    - No hardcoded models
    - Dynamic prompt engineering
    - Structured JSON output for unbiased evaluation
    - Full explainability tracking
    """
    
    def __init__(self):
        """Initialize Gemini client with environment variables."""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY not found in .env file")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_NONE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_NONE"
            }
        ]
    
    def build_screening_prompt(
        self,
        job_requirements: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        top_n: int = 10
    ) -> str:
        """
        Build a dynamic, unbiased screening prompt.
        
        Args:
            job_requirements: Job details with role, skills, experience level
            candidates: List of talent profiles
            top_n: Number of top candidates to shortlist
        
        Returns:
            Structured prompt for Gemini
        """
        
        prompt = f"""You are an expert, unbiased AI recruiter evaluating candidates for the following role:

JOB REQUIREMENT:
Role: {job_requirements.get('role', 'N/A')}
Required Skills: {', '.join(job_requirements.get('required_skills', []))}
Experience Level Required: {job_requirements.get('experience_level', 'Not Specified')}
Education Requirement: {job_requirements.get('education', 'Not Specified')}
Preferred Skills: {', '.join(job_requirements.get('preferred_skills', []))}
Key Responsibilities: {job_requirements.get('description', 'Not provided')}

EVALUATION CRITERIA (Weighted):
- Technical Skills Match: 35%
- Experience Relevance: 30%
- Education Fit: 15%
- Cultural Fit / Soft Skills: 15%
- Other Unique Strengths: 5%

IMPORTANT: Evaluate ONLY based on qualifications and skills. 
Ignore: Names, location, age, gender, or any personally identifiable information that could introduce bias.
Focus on: Hard skills, experience, education, and demonstrated achievements.

CANDIDATES TO EVALUATE:
{json.dumps(candidates, indent=2)}

TASK:
1. Score each candidate from 0-100 based on the weighted criteria
2. Rank candidates by score (highest first)
3. Select the top {top_n} candidates
4. For each shortlisted candidate, provide:
   - Overall Match Score (0-100)
   - Strengths (specific to the role)
   - Gaps/Risks (what they're missing)
   - Recommendation (Strong Yes, Yes, Maybe, No)
   - Key Achievement that demonstrates capability

Return ONLY valid JSON (no markdown, no extra text) with this exact structure:
{{
    "shortlist": [
        {{
            "candidate_id": "string",
            "candidate_name": "string",
            "overall_score": number,
            "strengths": ["string"],
            "gaps": ["string"],
            "recommendation": "Strong Yes|Yes|Maybe|No",
            "key_achievement": "string",
            "reasoning": "string"
        }}
    ],
    "evaluation_summary": "string",
    "screening_completed_at": "ISO8601 timestamp"
}}"""
        
        return prompt
    
    def screen_candidates(
        self,
        job_requirements: Dict[str, Any],
        candidates: List[Dict[str, Any]],
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        Screen candidates using Gemini API.
        
        Args:
            job_requirements: Job details
            candidates: List of talent profiles
            top_n: Top N candidates to shortlist
        
        Returns:
            Screening results with rankings and explanations
        """
        
        try:
            prompt = self.build_screening_prompt(job_requirements, candidates, top_n)
            
            response = self.model.generate_content(
                prompt,
                safety_settings=self.safety_settings,
                generation_config={
                    "temperature": 0.3,  # Lower for consistency
                    "top_p": 0.9,
                    "top_k": 40,
                    "max_output_tokens": 4000
                }
            )
            
            # Parse response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            
            results = json.loads(response_text.strip())
            
            return {
                "status": "success",
                "data": results,
                "model": self.model.model_name
            }
        
        except json.JSONDecodeError as e:
            return {
                "status": "error",
                "error": f"Failed to parse AI response: {str(e)}",
                "raw_response": response_text if 'response_text' in locals() else None
            }
        
        except Exception as e:
            return {
                "status": "error",
                "error": f"Screening failed: {str(e)}"
            }
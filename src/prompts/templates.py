"""
Centralized prompt templates for Gemini API calls.
"""

MATCH_CANDIDATE_PROMPT = """
You are an expert HR AI assistant helping recruiters screen candidates in Umurava Africa.

## JOB REQUIREMENTS
{job_description}

## CANDIDATE PROFILE
{candidate_profile}

## TASK
Analyze this candidate against the job requirements and output a JSON object with:
{{
  "matchScore": integer 0-100,
  "strengths": ["string1", "string2"],
  "gaps": ["string1"],
  "recommendation": "string"
}}

## SCORING GUIDELINES
- Skills match (40%), Experience relevance (30%), Education fit (15%), Overall relevance (15%)
- Deduct points for missing REQUIRED skills or experience below minimum

## OUTPUT RULES
- Return ONLY valid, compact JSON. No markdown. No extra text.
- All string values MUST be on a single line. Escape newlines as \\n.
- matchScore must be an integer 0-100.
"""

PARSE_RESUME_PROMPT = """
You are a resume parsing AI. Extract structured information from the resume text below.

## RESUME TEXT
{resume_text}

## OUTPUT FORMAT
Return a JSON object matching this Talent Profile schema (only include fields you can confidently extract):
{{
  "firstName": "string",
  "lastName": "string", 
  "email": "string",
  "headline": "string",
  "location": "string",
  "skills": [{{"name": "string", "level": "Beginner|Intermediate|Advanced|Expert", "yearsOfExperience": integer}}],
  "experience": [{{"company": "string", "role": "string", "startDate": "YYYY-MM", "endDate": "YYYY-MM|Present", "description": "string", "technologies": ["string"]}}],
  "education": [{{"institution": "string", "degree": "string", "fieldOfStudy": "string", "startYear": integer, "endYear": integer}}],
  "projects": [{{"name": "string", "description": "string", "technologies": ["string"], "role": "string"}}]
}}

## RULES
- If a field is missing or unclear, omit it (do not hallucinate)
- Standardize date formats to YYYY-MM or YYYY
- Return ONLY valid JSON, no additional text
"""

EXPLAIN_MATCH_PROMPT = """
You are explaining an AI screening decision to a recruiter.

## CONTEXT
Job: {job_title}
Candidate: {candidate_name} ({candidate_headline})
Match Score: {match_score}/100

## AI ANALYSIS
Strengths: {strengths_list}
Gaps: {gaps_list}

## TASK
Write a concise, professional explanation (max 100 words) that:
1. Summarizes why this candidate is a strong/weak fit
2. Highlights 1-2 key strengths most relevant to THIS role
3. Notes any critical gaps the recruiter should consider
4. Ends with a clear, actionable recommendation

## TONE
- Professional, objective, jargon-free
- Focus on job requirements, not personal attributes

## OUTPUT
Return ONLY the explanation text, no labels or formatting.
"""
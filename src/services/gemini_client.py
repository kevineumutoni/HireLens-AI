# src/services/gemini_client.py
"""
Gemini API client - SIMPLIFIED + RELIABLE
- Request plain text (not JSON mode)
- Parse text into structured data
- Retry transient failures (429/503) with exponential backoff
- Mark failures so ranking can exclude them (fairness)

Updates for resume extraction:
- Increase maxOutputTokens to reduce truncation
- Print head + tail of Gemini output when debug=True
- More robust JSON parsing (handles code fences, extra text, trailing commas, single quotes)
- Resume extraction prompt reduced to key fields to avoid truncation (name/email/headline/location/skills)
"""
from __future__ import annotations

import re
import time
import requests
from src.config.settings import settings


class GeminiClient:
    """Simplified Gemini client - text response mode."""

    def __init__(self, debug: bool = False):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError(" GEMINI_API_KEY not in .env")

        self.base_url = settings.GEMINI_BASE_URL
        self.timeout = settings.API_TIMEOUT_SECONDS
        self.model = settings.PREFERRED_MODEL
        self.debug = debug

        # You can tune these if needed
        self.max_attempts = 5
        self.base_backoff_seconds = 1.0

    def _make_api_call(self, prompt: str) -> dict:
        """Call Gemini API in TEXT mode (more reliable than JSON mime type)."""
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"

        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                # bigger output so JSON doesn't cut off mid-way
                "maxOutputTokens": 4096,
            },
        }

        last_error = "Unknown error"

        for attempt in range(1, self.max_attempts + 1):
            try:
                resp = requests.post(url, json=body, timeout=self.timeout)

                # Transient errors: retry with backoff
                if resp.status_code in (429, 503):
                    wait = min(12.0, self.base_backoff_seconds * (2 ** (attempt - 1)))
                    last_error = f"HTTP {resp.status_code}"
                    if self.debug:
                        print(
                            f"⚠️ Gemini transient error {resp.status_code}. "
                            f"attempt={attempt}/{self.max_attempts}, waiting {wait:.1f}s"
                        )
                    time.sleep(wait)
                    continue

                if resp.status_code == 403:
                    return {
                        "success": False,
                        "error": "HTTP 403: API key invalid or API not enabled for this key/project.",
                    }

                if resp.status_code != 200:
                    return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text[:200]}"}

                result = resp.json()

                # Extract text
                try:
                    text = result["candidates"][0]["content"]["parts"][0].get("text", "")
                except Exception:
                    return {"success": False, "error": f"Malformed response structure: {str(result)[:200]}"}

                if not text or not text.strip():
                    return {"success": False, "error": "Empty text response (no model output)."}

                return {"success": True, "text": text}

            except requests.exceptions.Timeout:
                last_error = f"Timeout after {self.timeout}s"
                wait = min(12.0, self.base_backoff_seconds * (2 ** (attempt - 1)))
                if self.debug:
                    print(f"⚠️ Gemini timeout. attempt={attempt}/{self.max_attempts}, waiting {wait:.1f}s")
                time.sleep(wait)
                continue

            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)[:120]}"
                wait = min(12.0, self.base_backoff_seconds * (2 ** (attempt - 1)))
                if self.debug:
                    print(
                        f"⚠️ Gemini connection error. attempt={attempt}/{self.max_attempts}, waiting {wait:.1f}s"
                    )
                time.sleep(wait)
                continue

            except Exception as e:
                return {"success": False, "error": f"Request error: {str(e)[:200]}"}

        return {"success": False, "error": f"{last_error} after {self.max_attempts} attempts"}

    # ---------------------------
    # Scoring parsing helpers
    # ---------------------------

    def _extract_score(self, text: str) -> int | None:
        patterns = [
            r"Score\s*:\s*(\d{1,3})\s*/\s*100",
            r"Match\s*Score\s*:\s*(\d{1,3})",
            r"\b(\d{1,3})\s*/\s*100\b",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                val = int(m.group(1))
                return max(0, min(100, val))
        return None

    def _extract_section_lines(self, text: str, header: str) -> list[str]:
        m = re.search(
            rf"{re.escape(header)}\s*:\s*(.*?)(?:\n[A-Za-z][A-Za-z ]{{0,30}}\s*:\s*|$)",
            text,
            re.IGNORECASE | re.DOTALL,
        )
        if not m:
            return []

        block = m.group(1).strip()
        if not block:
            return []

        items: list[str] = []
        for line in block.splitlines():
            line = line.strip()
            if not line:
                continue
            line = re.sub(r"^[\-\*\•\u2022\d\)\.]+\s*", "", line).strip()
            if not line:
                continue
            line = re.sub(r"\s+", " ", line).strip()
            if 4 <= len(line) <= 180:
                items.append(line)

        return items

    def _extract_reasoning(self, text: str) -> str:
        m = re.search(r"Reasoning\s*:\s*(.+)", text, re.IGNORECASE)
        if m:
            reasoning = m.group(1).strip()
            reasoning = re.sub(r"\s+", " ", reasoning)
            return reasoning[:260]
        compact = re.sub(r"\s+", " ", text).strip()
        return compact[:260]

    def _extract_recommendation(self, text: str, score: int | None) -> str:
        m = re.search(r"Recommendation\s*:\s*(Strong Yes|Yes|Maybe|No)", text, re.IGNORECASE)
        if m:
            return m.group(1).title()

        if score is None:
            return "Manual review"
        if score >= 80:
            return "Strong Yes"
        if score >= 70:
            return "Yes"
        if score >= 60:
            return "Maybe"
        return "No"

    def _parse_scoring_response(self, text: str) -> dict:
        score = self._extract_score(text)
        strengths = self._extract_section_lines(text, "Strengths")
        gaps = self._extract_section_lines(text, "Gaps")
        reasoning = self._extract_reasoning(text)
        recommendation = self._extract_recommendation(text, score)

        if score is None:
            score = 50

        return {
            "evaluationStatus": "success",
            "matchScore": score,
            "strengths": strengths[:3],
            "gaps": gaps[:3],
            "recommendation": recommendation,
            "reasoning": reasoning,
        }

    # ---------------------------
    # Resume -> Candidate extraction
    # ---------------------------

    def _extract_email_from_text_fallback(self, text: str) -> str:
        emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text or "")
        return emails[0].strip().lower() if emails else ""

    def _try_parse_json_object(self, text: str) -> dict | None:
        """
        Parse JSON even if Gemini returns extra text or "almost JSON".
        Handles:
        - ```json fences
        - extra text before/after
        - trailing commas
        - single quotes
        """
        import json

        if not text:
            return None

        t = text.strip()

        # strip code fences
        if t.startswith("```"):
            t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
            t = re.sub(r"\s*```$", "", t).strip()

        # find json object boundaries
        start = t.find("{")
        end = t.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return None

        candidate = t[start : end + 1].strip()

        # strict parse
        try:
            obj = json.loads(candidate)
            return obj if isinstance(obj, dict) else None
        except Exception:
            pass

        # light repair: remove trailing commas before } or ]
        repaired = re.sub(r",\s*([}\]])", r"\1", candidate)

        # light repair: convert single quotes to double quotes (best-effort)
        repaired = re.sub(r"(?<!\\)'", '"', repaired)

        try:
            obj = json.loads(repaired)
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    async def extract_candidate_profile(self, resume_text: str) -> dict:
        """
        Extract candidate info from resume text.
        IMPORTANT: keep the output small to reduce truncation.

        Returns:
          { success: bool, error: str, candidate: dict|None }
        """
        resume_text = (resume_text or "").strip()
        if not resume_text:
            return {"success": False, "error": "Empty resume text", "candidate": None}

        # Smaller schema to avoid truncation (this is what your table needs)
        prompt = f"""
Extract candidate info from the resume below.

Return ONLY JSON (no markdown, no backticks, no explanation).

Schema:
{{
  "firstName": "string",
  "lastName": "string",
  "email": "string",
  "headline": "string",
  "location": "string",
  "skills": ["string"]
}}

Rules:
- skills: list up to 20 items (skill names only)
- headline <= 120 chars
- location <= 80 chars
- If unknown, use "" or [].

Resume:
\"\"\"{resume_text[:20000]}\"\"\"
"""

        result = self._make_api_call(prompt)
        if not result.get("success"):
            return {"success": False, "error": result.get("error", "Gemini extraction failed"), "candidate": None}

        raw = result.get("text", "")

        if self.debug:
            print("----- GEMINI RAW OUTPUT START -----")
            print(raw[:2000])
            print("----- GEMINI RAW OUTPUT END -----")
            print("----- GEMINI RAW OUTPUT TAIL -----")
            print(raw[-400:])
            print("----- GEMINI RAW OUTPUT TAIL END -----")

        obj = self._try_parse_json_object(raw)
        if not obj:
            email = self._extract_email_from_text_fallback(resume_text)
            return {
                "success": False,
                "error": "Gemini returned non-JSON output (likely truncated or extra text)",
                "candidate": {"email": email},
            }

        # Normalize fields
        email = str(obj.get("email") or "").strip().lower()
        if not email:
            email = self._extract_email_from_text_fallback(resume_text)
        obj["email"] = email

        obj["firstName"] = str(obj.get("firstName") or "Unknown").strip() or "Unknown"
        obj["lastName"] = str(obj.get("lastName") or "").strip()
        obj["headline"] = str(obj.get("headline") or "").strip()[:120]
        obj["location"] = str(obj.get("location") or "").strip()[:80]

        # Normalize skills -> list[str]
        skills = obj.get("skills") or []
        if not isinstance(skills, list):
            skills = []
        cleaned = []
        for s in skills[:20]:
            s = str(s or "").strip()
            if s:
                cleaned.append(s)
        obj["skills"] = cleaned

        return {"success": True, "error": "", "candidate": obj}

    async def generate_structured_response(self, prompt: str) -> dict:
        """Get scoring response in structured format."""
        result = self._make_api_call(prompt)

        if not result.get("success"):
            error = result.get("error", "Evaluation failed")
            if self.debug:
                print(f"   ❌ API Error: {error}")

            return {
                "evaluationStatus": "failed",
                "error": error,
                "matchScore": None,
                "strengths": [],
                "gaps": [],
                "recommendation": "Manual review",
                "reasoning": "",
            }

        return self._parse_scoring_response(result["text"])

    async def generate_text_response(self, prompt: str) -> str:
        """Get text response."""
        result = self._make_api_call(prompt)
        if result.get("success"):
            return result["text"].strip()
        return f"Unable to generate explanation: {result.get('error', 'unknown error')}"
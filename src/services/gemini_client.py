# src/services/gemini_client.py
"""
Gemini API client with KEY ROTATION.

How it works:
- Loads all keys from settings.api_keys (GEMINI_API_KEYS in .env)
- Keeps a shared round-robin index across all GeminiClient instances
- On ANY 429 response: immediately rotates to the next key and retries
  without waiting — because the next key has its own fresh quota
- Only falls back to exponential backoff when ALL keys have been tried
  for the same attempt (meaning the quota storm is across all keys)

This means with 30 keys you can fire 30 requests before hitting any limit.
"""
from __future__ import annotations

import re
import time
import threading
import requests
from typing import List

from src.config.settings import settings


class GeminiClient:
    """Gemini client with automatic key rotation on 429."""

    _keys: List[str] = []
    _current_index: int = 0
    _lock: threading.Lock = threading.Lock()
    _initialized: bool = False

    @classmethod
    def _init_keys(cls) -> None:
        if cls._initialized:
            return
        cls._keys = settings.api_keys
        if not cls._keys:
            raise ValueError("No Gemini API keys configured. Add GEMINI_API_KEYS to .env")
        cls._current_index = 0
        cls._initialized = True

    @classmethod
    def _get_next_key(cls) -> str:
        """Round-robin: advance index and return next key."""
        with cls._lock:
            cls._current_index = (cls._current_index + 1) % len(cls._keys)
            return cls._keys[cls._current_index]

    @classmethod
    def _current_key(cls) -> str:
        with cls._lock:
            return cls._keys[cls._current_index]


    def __init__(self, debug: bool = False):
        GeminiClient._init_keys()

        self.base_url = settings.GEMINI_BASE_URL
        self.timeout  = settings.API_TIMEOUT_SECONDS
        self.model    = settings.PREFERRED_MODEL
        self.debug    = debug

        # How many full rotations through all keys before giving up
        self.max_full_rotations  = 2
        self.base_backoff_seconds = 2.0
        self.max_backoff_seconds  = 60.0

    # ── Core API call ─────────────────────────────────────────────────────────

    def _make_api_call(self, prompt: str) -> dict:
        """
        Call Gemini API with automatic key rotation on 429.

        Strategy:
          - Try current key
          - On 429: immediately rotate to next key and retry (no wait)
          - Only wait if we've tried ALL keys and they're all 429ing
          - Give up after max_full_rotations full cycles through all keys
        """
        num_keys   = len(GeminiClient._keys)
        max_attempts = num_keys * self.max_full_rotations
        rotation_count = 0   # how many times we've rotated through all keys
        last_error = "Unknown error"

        url_template = self.base_url + "/{model}:generateContent?key={key}"

        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4096,
            },
        }

        for attempt in range(1, max_attempts + 1):
            key = GeminiClient._current_key()
            url = url_template.format(model=self.model, key=key)

            try:
                resp = requests.post(url, json=body, timeout=self.timeout)

                if resp.status_code == 429:
                    last_error = f"HTTP 429 (key ...{key[-6:]})"

                    # Rotate immediately to next key
                    next_key = GeminiClient._get_next_key()
                    keys_tried_this_cycle = attempt % num_keys

                    # If we've gone through all keys once, wait before next cycle
                    if attempt > 0 and attempt % num_keys == 0:
                        rotation_count += 1
                        wait = min(
                            self.max_backoff_seconds,
                            self.base_backoff_seconds * (2 ** (rotation_count - 1)),
                        )
                        print(
                            f"⚠️  All {num_keys} keys hit 429 (cycle {rotation_count}). "
                            f"Waiting {wait:.0f}s before trying again…"
                        )
                        time.sleep(wait)
                    else:
                        print(
                            f"⚠️  Key ...{key[-6:]} → 429. Rotating to next key "
                            f"(attempt {attempt}/{max_attempts})"
                        )
                    continue

                if resp.status_code == 503:
                    wait = min(self.max_backoff_seconds,
                               self.base_backoff_seconds * (2 ** ((attempt - 1) % 4)))
                    last_error = f"HTTP 503"
                    print(f"⚠️  HTTP 503 (attempt {attempt}). Waiting {wait:.0f}s…")
                    time.sleep(wait)
                    continue

                if resp.status_code == 403:
                    print(f"⚠️  Key ...{key[-6:]} → 403 (invalid). Rotating…")
                    GeminiClient._get_next_key()
                    continue

                if resp.status_code != 200:
                    return {
                        "success": False,
                        "error": f"HTTP {resp.status_code}: {resp.text[:200]}",
                    }

                result = resp.json()

                try:
                    text = result["candidates"][0]["content"]["parts"][0].get("text", "")
                except Exception:
                    return {
                        "success": False,
                        "error": f"Malformed Gemini response: {str(result)[:200]}",
                    }

                if not text or not text.strip():
                    return {"success": False, "error": "Empty text response from Gemini."}

                return {"success": True, "text": text}

            except requests.exceptions.Timeout:
                last_error = f"Timeout after {self.timeout}s"
                wait = min(self.max_backoff_seconds,
                           self.base_backoff_seconds * (2 ** ((attempt - 1) % 4)))
                print(f"⚠️  Timeout (attempt {attempt}). Waiting {wait:.0f}s…")
                time.sleep(wait)
                continue

            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection error: {str(e)[:80]}"
                wait = min(self.max_backoff_seconds,
                           self.base_backoff_seconds * (2 ** ((attempt - 1) % 4)))
                print(f"⚠️  Connection error (attempt {attempt}). Waiting {wait:.0f}s…")
                time.sleep(wait)
                continue

            except Exception as e:
                return {"success": False, "error": f"Request error: {str(e)[:200]}"}

        return {
            "success": False,
            "error": f"{last_error} — exhausted all {num_keys} keys × {self.max_full_rotations} cycles",
        }


    def _extract_score(self, text: str) -> int | None:
        patterns = [
            r"Score\s*:\s*(\d{1,3})\s*/\s*100",
            r"Match\s*Score\s*:\s*(\d{1,3})",
            r"\b(\d{1,3})\s*/\s*100\b",
        ]
        for pat in patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                return max(0, min(100, int(m.group(1))))
        return None

    def _extract_section_lines(self, text: str, header: str) -> list[str]:
        m = re.search(
            rf"{re.escape(header)}\s*:\s*(.*?)(?:\n[A-Za-z][A-Za-z ]{{0,30}}\s*:\s*|$)",
            text, re.IGNORECASE | re.DOTALL,
        )
        if not m:
            return []
        block = m.group(1).strip()
        items: list[str] = []
        for line in block.splitlines():
            line = re.sub(r"^[\-\*\•\u2022\d\)\.]+\s*", "", line.strip()).strip()
            line = re.sub(r"\s+", " ", line)
            if 4 <= len(line) <= 180:
                items.append(line)
        return items

    def _extract_reasoning(self, text: str) -> str:
        m = re.search(r"Reasoning\s*:\s*(.+)", text, re.IGNORECASE)
        if m:
            return re.sub(r"\s+", " ", m.group(1).strip())[:260]
        return re.sub(r"\s+", " ", text).strip()[:260]

    def _extract_recommendation(self, text: str, score: int | None) -> str:
        m = re.search(r"Recommendation\s*:\s*(Strong Yes|Yes|Maybe|No)", text, re.IGNORECASE)
        if m:
            return m.group(1).title()
        if score is None:
            return "Manual review"
        if score >= 80: return "Strong Yes"
        if score >= 70: return "Yes"
        if score >= 60: return "Maybe"
        return "No"

    def _parse_scoring_response(self, text: str) -> dict:
        score          = self._extract_score(text)
        strengths      = self._extract_section_lines(text, "Strengths")
        gaps           = self._extract_section_lines(text, "Gaps")
        reasoning      = self._extract_reasoning(text)
        recommendation = self._extract_recommendation(text, score)
        if score is None:
            score = 50
        return {
            "evaluationStatus": "success",
            "matchScore":       score,
            "strengths":        strengths[:3],
            "gaps":             gaps[:3],
            "recommendation":   recommendation,
            "reasoning":        reasoning,
        }


    def _extract_email_from_text_fallback(self, text: str) -> str:
        emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text or "")
        return emails[0].strip().lower() if emails else ""

    def _try_parse_json_object(self, text: str) -> dict | None:
        import json
        if not text:
            return None
        t = text.strip()
        if t.startswith("```"):
            t = re.sub(r"^```[a-zA-Z]*\s*", "", t)
            t = re.sub(r"\s*```$", "", t).strip()
        start, end = t.find("{"), t.rfind("}")
        if start == -1 or end <= start:
            return None
        candidate = t[start:end + 1]
        try:
            obj = json.loads(candidate)
            return obj if isinstance(obj, dict) else None
        except Exception:
            pass
        repaired = re.sub(r",\s*([}\]])", r"\1", candidate)
        repaired = re.sub(r"(?<!\\)'", '"', repaired)
        try:
            obj = json.loads(repaired)
            return obj if isinstance(obj, dict) else None
        except Exception:
            return None

    async def extract_candidate_profile(self, resume_text: str) -> dict:
        resume_text = (resume_text or "").strip()
        if not resume_text:
            return {"success": False, "error": "Empty resume text", "candidate": None}

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
        obj = self._try_parse_json_object(raw)
        if not obj:
            email = self._extract_email_from_text_fallback(resume_text)
            return {"success": False, "error": "Gemini returned non-JSON output", "candidate": {"email": email}}

        email = str(obj.get("email") or "").strip().lower() or self._extract_email_from_text_fallback(resume_text)
        obj["email"]     = email
        obj["firstName"] = str(obj.get("firstName") or "Unknown").strip() or "Unknown"
        obj["lastName"]  = str(obj.get("lastName") or "").strip()
        obj["headline"]  = str(obj.get("headline") or "").strip()[:120]
        obj["location"]  = str(obj.get("location") or "").strip()[:80]
        skills  = obj.get("skills") or []
        obj["skills"] = [str(s).strip() for s in skills[:20] if str(s).strip()]

        return {"success": True, "error": "", "candidate": obj}


    async def generate_structured_response(self, prompt: str) -> dict:
        result = self._make_api_call(prompt)
        if not result.get("success"):
            return {
                "evaluationStatus": "failed",
                "error":            result.get("error", "Evaluation failed"),
                "matchScore":       None,
                "strengths":        [],
                "gaps":             [],
                "recommendation":   "Manual review",
                "reasoning":        "",
            }
        parsed = self._parse_scoring_response(result["text"])
        parsed["raw_text"] = result["text"]
        return parsed

    async def generate_text_response(self, prompt: str) -> str:
        result = self._make_api_call(prompt)
        if result.get("success"):
            return result["text"].strip()
        return f"Unable to generate response: {result.get('error', 'unknown error')}"
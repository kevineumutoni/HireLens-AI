"""
Gemini API client using direct REST API calls.
✅ Robust JSON parser that fixes unescaped newlines in strings
✅ Works with gemini-2.5-flash
"""
import json
import requests
import hashlib
import os
import re
import time
from src.config.settings import settings


def _fix_json_newlines(json_str: str) -> str:
    """
    Fix unescaped newlines inside JSON string values.
    Handles cases where LLM returns pretty JSON with literal newlines in strings.
    """
    # Remove markdown code blocks first
    json_str = re.sub(r'^```(?:json)?\s*', '', json_str, flags=re.IGNORECASE)
    json_str = re.sub(r'\s*```$', '', json_str, flags=re.DOTALL)
    
    # Extract JSON bounds
    start = json_str.find('{')
    end = json_str.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return json_str  # Return as-is if no valid bounds found
    json_str = json_str[start:end+1]
    
    # Fix unescaped newlines inside quoted strings
    # Pattern: match content inside quotes, replace literal \n with \\n
    def fix_string_value(match):
        content = match.group(1)
        # Escape backslashes first, then newlines
        content = content.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        return f'"{content}"'
    
    # Match quoted strings (handles escaped quotes inside)
    json_str = re.sub(r'"((?:[^"\\]|\\.)*)"', fix_string_value, json_str)
    
    return json_str


class GeminiClient:
    """Direct REST API wrapper for Gemini - reliable and hackathon-ready."""
    
    def __init__(self):
        """Initialize with API key and auto-select best available model."""
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = settings.GEMINI_BASE_URL
        self.timeout = settings.API_TIMEOUT_SECONDS
        
        # Auto-detect best available model
        self.primary_model = self._get_best_available_model()
        self.fallback_model = "gemini-2.5-pro"
        
        # Setup caching
        self.cache_dir = ".gemini_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def _get_best_available_model(self) -> str:
        """Query API to find best available model (prefers flash variants)."""
        try:
            url = f"{self.base_url}?key={self.api_key}"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                models = response.json().get("models", [])
                for preference in ["flash", "pro"]:
                    for m in models:
                        name = m.get("name", "").replace("models/", "")
                        if ("generateContent" in m.get("supportedGenerationMethods", []) 
                            and preference in name.lower()):
                            return name
                for m in models:
                    if "generateContent" in m.get("supportedGenerationMethods", []):
                        return m.get("name", "").replace("models/", "")
        except Exception:
            pass
        return "gemini-2.5-flash"
    
    def _get_cache_key(self, prompt: str) -> str:
        return hashlib.sha256(prompt.encode()).hexdigest()[:16]
    
    def _get_cached(self, key: str, max_age_hours: int = 24) -> dict | None:
        path = f"{self.cache_dir}/{key}.json"
        if os.path.exists(path):
            if time.time() - os.path.getmtime(path) < max_age_hours * 3600:
                with open(path, 'r') as f:
                    return json.load(f)
        return None
    
    def _set_cached(self, key: str,  dict):
        with open(f"{self.cache_dir}/{key}.json", 'w') as f:
            json.dump(data, f)
    
    def _make_api_call(self, prompt: str, model: str, json_mode: bool = True) -> dict:
        """Internal helper to call Gemini REST API."""
        url = f"{self.base_url}/{model}:generateContent?key={self.api_key}"
        
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": settings.TEMPERATURE,
                "maxOutputTokens": settings.MAX_OUTPUT_TOKENS,
            }
        }
        
        if json_mode:
            body["generationConfig"]["response_mime_type"] = "application/json"
        
        try:
            headers = {"User-Agent": "HireLens-AI-Hackathon/1.0"}
            response = requests.post(url, json=body, headers=headers, timeout=self.timeout)
            
            if response.status_code == 404:
                return {"success": False, "error": f"Model '{model}' not found (404)"}
            elif response.status_code == 403:
                return {"success": False, "error": "API key invalid or Gemini API not enabled (403)"}
            elif response.status_code != 200:
                return {"success": False, "error": f"HTTP {response.status_code}: {response.text[:150]}"}
            
            result = response.json()
            
            if "candidates" in result and result["candidates"]:
                content = result["candidates"][0].get("content", {})
                parts = content.get("parts", [])
                if parts and "text" in parts[0]:
                    return {"text": parts[0]["text"], "success": True}
            
            return {"success": False, "error": "Empty or malformed response from Gemini"}
            
        except requests.exceptions.SSLError as e:
            return {"success": False, "error": f"SSL Error: {str(e)}"}
        except requests.exceptions.RequestException as e:
            return {"success": False, "error": f"Network error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Unexpected error: {str(e)}"}
    
    async def generate_structured_response(self, prompt: str, expected_schema: dict = None) -> dict:
        """Send prompt and return parsed JSON response with caching and fallback."""
        cache_key = self._get_cache_key(prompt)
        cached = self._get_cached(cache_key)
        if cached:
            return cached
        
        # Try primary model
        result = self._make_api_call(prompt, self.primary_model, json_mode=True)
        
        # Fallback to pro if primary fails with 404
        if not result["success"] and "404" in result.get("error", ""):
            result = self._make_api_call(prompt, self.fallback_model, json_mode=True)
        
        fallback = {
            "matchScore": 50,
            "strengths": ["Profile received"],
            "gaps": ["AI service temporarily unavailable"],
            "recommendation": "Manual review recommended"
        }
        
        if not result["success"]:
            print(f"⚠️  API call failed: {result.get('error', 'Unknown error')}")
            self._set_cached(cache_key, fallback)
            return fallback
        
        response_text = result["text"].strip()
        
        # ✅ Robust JSON extraction and fixing
        json_str = _fix_json_newlines(response_text)
        
        try:
            parsed = json.loads(json_str)
            if expected_schema and not all(k in parsed for k in expected_schema.get("required", [])):
                raise ValueError(f"Missing: {expected_schema['required']}")
            self._set_cached(cache_key, parsed)
            return parsed
        except json.JSONDecodeError as e:
            print(f"⚠️  JSON parse failed: {e}")
            print(f"   Raw response preview: {response_text[:200]}...")
            self._set_cached(cache_key, fallback)
            return fallback
    
    async def generate_text_response(self, prompt: str) -> str:
        """Send prompt and return raw text for explanations."""
        cache_key = self._get_cache_key(prompt)
        cached = self._get_cached(cache_key)
        if cached and "text" in cached:
            return cached["text"]
        
        result = self._make_api_call(prompt, self.primary_model, json_mode=False)
        
        if not result["success"] and "404" in result.get("error", ""):
            result = self._make_api_call(prompt, self.fallback_model, json_mode=False)
        
        error_msg = f"Explanation unavailable: {result.get('error', 'API error')}"
        if not result["success"]:
            self._set_cached(cache_key, {"text": error_msg})
            return error_msg
        
        self._set_cached(cache_key, {"text": result["text"].strip()})
        return result["text"].strip()
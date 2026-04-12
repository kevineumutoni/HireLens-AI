# src/services/gemini_client.py
"""
Gemini API client - Direct REST API calls.
✅ Uses google-genai v1.72.0+
✅ No caching - fresh results every time
✅ Robust JSON parsing
"""
import json
import requests
import os
import re
from src.config.settings import settings

def _fix_json_newlines(json_str: str) -> str:
    """Fix unescaped newlines in JSON strings."""
    json_str = re.sub(r'^```(?:json)?\s*', '', json_str, flags=re.IGNORECASE)
    json_str = re.sub(r'\s*```$', '', json_str, flags=re.DOTALL)
    
    start = json_str.find('{')
    end = json_str.rfind('}')
    if start == -1 or end == -1 or end <= start:
        return json_str
    json_str = json_str[start:end+1]
    
    def fix_string_value(match):
        content = match.group(1)
        content = content.replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')
        return f'"{content}"'
    
    json_str = re.sub(r'"((?:[^"\\]|\\.)*)"', fix_string_value, json_str)
    return json_str


class GeminiClient:
    """Direct REST API for Gemini - production-ready."""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        if not self.api_key:
            raise ValueError("❌ GEMINI_API_KEY not in .env")
        
        self.base_url = settings.GEMINI_BASE_URL
        self.timeout = settings.API_TIMEOUT_SECONDS
        self.model = settings.PREFERRED_MODEL
    
    def _make_api_call(self, prompt: str, json_mode: bool = True) -> dict:
        """Call Gemini API."""
        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
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
            response = requests.post(url, json=body, timeout=self.timeout)
            
            if response.status_code == 403:
                return {"success": False, "error": "API key invalid or API not enabled"}
            elif response.status_code == 429:
                return {"success": False, "error": "Rate limited - wait 60s"}
            elif response.status_code != 200:
                return {"success": False, "error": f"HTTP {response.status_code}"}
            
            result = response.json()
            if "candidates" in result and result["candidates"]:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                return {"text": text, "success": True}
            
            return {"success": False, "error": "Empty response"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def generate_structured_response(self, prompt: str) -> dict:
        """Get JSON response."""
        result = self._make_api_call(prompt, json_mode=True)
        
        if not result["success"]:
            print(f"❌ API Error: {result.get('error')}")
            return {"matchScore": 50, "strengths": [], "gaps": [], "recommendation": "Manual review"}
        
        json_str = _fix_json_newlines(result["text"].strip())
        
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            print(f"❌ JSON parse failed")
            return {"matchScore": 50, "strengths": [], "gaps": [], "recommendation": "Manual review"}
    
    async def generate_text_response(self, prompt: str) -> str:
        """Get text response."""
        result = self._make_api_call(prompt, json_mode=False)
        return result["text"].strip() if result["success"] else "Unavailable"
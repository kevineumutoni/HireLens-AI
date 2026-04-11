# test_api.py - Test your Gemini API key
import requests
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("❌ GEMINI_API_KEY not found in .env")
    exit(1)

print(f"🔑 API Key loaded (prefix: {API_KEY[:10]}...)")

# Correct endpoints
list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
generate_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"

print("\n📋 Testing API key...")

# Test 1: List models
print("\n1️⃣  Testing model listing...")
try:
    response = requests.get(list_url, timeout=10)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        models = data.get("models", [])
        generate_models = [
            m.get("name", "").replace("models/", "") 
            for m in models 
            if "generateContent" in m.get("supportedGenerationMethods", [])
        ]
        print(f"   ✅ Success! Found {len(generate_models)} models with generateContent:")
        for m in generate_models[:5]:
            print(f"      - {m}")
        if generate_models:
            print(f"\n💡 Using in gemini_client.py: self.primary_model = \"{generate_models[0]}\"")
    elif response.status_code == 403:
        print("   ❌ 403: API key invalid or Gemini API not enabled")
        print("   👉 Fix: https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com → ENABLE")
    else:
        print(f"   ⚠️  Unexpected: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 2: Generate content
print("\n2️⃣  Testing content generation...")
test_prompt = "Reply with only: OK"
payload = {
    "contents": [{"role": "user", "parts": [{"text": test_prompt}]}],
    "generationConfig": {"temperature": 0.1, "maxOutputTokens": 10}
}

try:
    response = requests.post(generate_url, json=payload, timeout=15)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
        print(f"   ✅ Success! Response: \"{text}\"")
    elif response.status_code == 404:
        print("   ⚠️  404: Model 'gemini-2.5-flash' not available - check available models above")
    elif response.status_code == 400:
        print(f"   ❌ 400: Bad request - {response.json().get('error', {}).get('message', 'Unknown')}")
    elif response.status_code == 429:
        print("   ❌ 429: Rate limit exceeded - wait 1 minute and retry")
    else:
        print(f"   ⚠️  Unexpected: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✨ Test complete!")
# Umurava AI Screening Module

AI-powered talent screening for the Umurava Hackathon, built with Google ADK (Agent Development Kit) and Gemini API.

## 🚀 Quick Start (Windows)

### Prerequisites
- Python 3.10 or later
- pip package manager
- Gemini API key from [Google AI Studio](https://aistudio.google.com/)

### Setup
```bash
# 1. Clone or create project folder
mkdir umurava_ai && cd umurava_ai

# 2. Create virtual environment
python -m venv venv

# 3. Activate environment
# PowerShell:
.\venv\Scripts\Activate.ps1
# CMD:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure environment
# Create .env file and add your Gemini API key:
echo "GEMINI_API_KEY=your_key_here" > .env
<div align="Left">

<br/>

# 🔍 HireLens AI

### *Screen smarter. Hire better.*

**AI-powered talent screening that ranks 150+ candidates in minutes with full explainability and zero bias.**

Built for the **Umurava AI Hackathon 2026** · Team HireLens

<div align="left">
<br/>

## Links
1. Live Demo: https://hire-lens-frontend-seven.vercel.app/
2. Backend Repo: https://github.com/kevineumutoni/HireLens-AI
3. Video Demo: https://drive.google.com/file/d/1DzjCoAZW_Y8TQjuHCXVuUTn6tHlMKrkk/view?usp=sharing
4. Figma Design: https://www.figma.com/design/rbEwtGnfPKUqqg5vIcH1P5/HireLens?node-id=0-1&t=iqFJQCJP2xM1SP14-1
5. Frontend Repo: https://github.com/kevineumutoni/HireLens-Frontend
6. API documentation: https://hirelens-hh2zui6bcq-ew.a.run.app/docs
7. Google Slides Link: https://docs.google.com/presentation/d/1eeWqC_I0Gg6y2RQdlJGaZCxuHGEDY7vtc_H_7W77chM/edit?usp=sharing

---

### Quick Access

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Visit%20App-2C7CF2?style=for-the-badge&logo=vercel)](https://hire-lens-frontend-seven.vercel.app/)

[![Backend Repo](https://img.shields.io/badge/Backend-Repository-0F172A?style=for-the-badge&logo=github)](https://github.com/kevineumutoni/HireLens-AI)

[![Video Demo](https://img.shields.io/badge/Video%20Demo-Watch-DC2626?style=for-the-badge&logo=youtube)](https://drive.google.com/file/d/1DzjCoAZW_Y8TQjuHCXVuUTn6tHlMKrkk/view?usp=sharing)

[![Figma Design](https://img.shields.io/badge/Figma-Design-A855F7?style=for-the-badge&logo=figma)](https://www.figma.com/design/rbEwtGnfPKUqqg5vIcH1P5/HireLens?node-id=0-1&t=iqFJQCJP2xM1SP14-1)

[![Frontend Repo](https://img.shields.io/badge/Frontend-Repository-0F172A?style=for-the-badge&logo=github)](https://github.com/kevineumutoni/HireLens-Frontend)

[![API Docs](https://img.shields.io/badge/API%20Docs-Open-16A34A?style=for-the-badge)](https://hirelens-hh2zui6bcq-ew.a.run.app/docs)

[![Pitch Deck](https://img.shields.io/badge/Pitch%20Deck-Google%20Slides-FBBC04?style=for-the-badge&logo=googleslides&logoColor=black)](https://docs.google.com/presentation/d/1eeWqC_I0Gg6y2RQdlJGaZCxuHGEDY7vtc_H_7W77chM/edit?usp=sharing)

---

### Video Demo (click on the image to view the demo)

[<img width="537" alt="Video Demo Thumbnail" src="https://github.com/user-attachments/assets/afc914c4-545e-40d1-b793-f0b6389ab45a" />](https://drive.google.com/file/d/1DzjCoAZW_Y8TQjuHCXVuUTn6tHlMKrkk/view?usp=sharing)

---

### HireLens Dashboard (image)

<img width="1512" alt="HireLens Dashboard" src="https://github.com/user-attachments/assets/5f6de626-9118-467d-8def-df4d2c7e997a" />

---

### Design Guideline (click image)

[<img width="900" alt="HireLens Figma Design" src="https://github.com/user-attachments/assets/64eea049-dc8e-42e9-95b1-e094bdc7a881" />](https://www.figma.com/design/rbEwtGnfPKUqqg5vIcH1P5/HireLens?node-id=0-1&t=iqFJQCJP2xM1SP14-1)

---
</div>

## The Problem

Screening over 150 candidates for a single opening means recruiters spend roughly 23 hours manually reviewing applications, with the majority of that time spent on profiles that don’t actually match. It’s exhausting work and it’s where bias creeps in, strong candidates slip through the cracks, and time-to-hire stretches out unnecessarily.

## Our Solution

HireLens connects to your candidate pool, takes your job requirements, and hands every profile to **Gemini AI** for objective evaluation. In 1–2 minutes you get a ranked shortlist; each candidate with a match score, strengths, gaps, and a plain-English recruiter note explaining *why* they were ranked where they are.

The recruiter stays in control. The AI does the reading.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| **AI Screening** | Gemini evaluates every candidate against the job's required skills, experience, and education |
| **Ranked Shortlist** | Candidates sorted 1–N by match score (0–100). Configurable top 5 / 10 / 20 / all |
| **Full Explainability** | Each result shows strengths, gaps, AI reasoning, and a plain-English recruiter note |
| **Unbiased Evaluation** | Names, location, age, nationality never factor into scoring — only qualifications |
| **PDF & CSV Ingestion** | Upload PDF resumes or bulk CSV/Excel files — Gemini parses them automatically |
| **Real-time Progress** | Live progress modal shows screening status as batches complete |
| **Recruiter Decisions** | Accept, reject, or flag candidates directly from the shortlist |
| **Job Management** | Full CRUD for job postings with skill tagging and applicant tracking |
| **Secure Auth** | JWT + bcrypt signup/signin. Google OAuth via Firebase |

---

## 🎬 Demo

> **Video walkthrough (9.18 mins):** [Watch on YouTube →](https://youtu.be/arWW5hBTotQ)

What the demo covers:
1. Creating a job posting with required skills
2. Uploading candidate profiles (CSV bulk + PDF resume)
3. Triggering AI screening — watching the live progress modal
4. Reviewing the ranked shortlist with strengths, gaps, and AI notes
5. Making recruiter decisions (accept / reject / flag)

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                             │
│  Next.js 14 · TypeScript · Inline CSS · Zustand · Axios     │
│                                                             │
│  Pages: Dashboard · Jobs · Candidates · Screening           │
│  Components: JobDetailModal · CandidateResultCard           │
│              ScreeningProgressModal · CandidateModal        │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (JSON)
                         │ Axios · 15min timeout for screening
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                              │
│  FastAPI · Python 3.12 · Uvicorn · Pydantic v2              │
│                                                             │
│  Routes:                                                    │
│    POST /api/auth/signup|signin                             │
│    GET|POST|PATCH|DELETE /api/jobs                          │
│    GET|POST|DELETE /api/candidates                          │
│    POST /api/candidates/upload  (CSV / PDF)                 │
│    POST /api/screening          (trigger AI run)            │
│    GET  /api/screening          (list results)              │
│                                                             │
│  AI Pipeline:                                               │
│    GeminiClient (key rotation) → Matcher → Scorer           │
│    → Ranker → Explainability → MongoDB                      │
└────────────────────────┬────────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          ▼                             ▼
┌──────────────────┐         ┌──────────────────────┐
│   MongoDB Atlas  │         │    Gemini API Pool   │
│                  │         │                      │
│  collections:    │         │  gemini-2.5-flash-   │
│  · jobs          │         │  (primary)           │
│  · candidates    │         │                      │
│  · screening_    │         │                      │
│    results       │         │                      │
│  · users         │         │                      │
└──────────────────┘         └──────────────────────┘
```
<img width="680" height="780" alt="hirelens_architecture 1" src="https://github.com/user-attachments/assets/1f5bb6c0-8089-4e7d-b17b-33a97fa73d75" />

## HireLens Product Requirements Document
<img width="680" height="900" alt="hirelens_prd 1 (1)" src="https://github.com/user-attachments/assets/4b4588ef-0f2a-46da-9571-0644ccc4e55f" />

## Hirelens System Requirements Document
<img width="680" height="820" alt="hirelens_srd 1 (1)" src="https://github.com/user-attachments/assets/97d13af3-d75c-47c6-a42b-0389ff236d3c" />

---

## 🤖 AI Decision Flow

```
Job Requirements
      │
      ▼
For each candidate (batches of 5, parallel):
      │
      ├─► Build prompt
      │     • Job title, required skills, preferred skills
      │     • Min experience, education requirement
      │     • Candidate headline, skills, experience, education
      │     • Bias guardrail: "Ignore name, gender, age, nationality"
      │
      ├─► Gemini API call (async, httpx, 30s timeout)
      │     • Temperature: 0.2 (consistent, low creativity)
      │     • Returns: Score/100, Strengths[], Gaps[], Recommendation, Reasoning
      │
      ├─► Parse structured response
      │     • Regex extraction for score, strengths, gaps, reasoning
      │     • Fallback defaults if parsing incomplete
      │
      └─► Build explanation (inline, no extra API call)
            • "{name} scored {N}/100 and is {fit_label}."
            • "{top strength}; {second strength}."
            • "Main gap: {gap}. {reasoning}"

      ▼
Rank all successful evaluations by matchScore (descending)
      ▼
Save shortlist to MongoDB (screening_results collection)
      ▼
Return to frontend → display ranked cards with expand/collapse
```

**Scoring weights (prompt-engineered):**
- Technical skills match — 35%
- Experience relevance — 30%
- Education fit — 15%
- Soft skills & cultural fit — 15%
- Unique strengths — 5%

**Score bands:**
- 80–100 → Strong Yes (has all required skills + experience)
- 60–79 → Yes / Maybe (1–2 gaps but solid foundation)
- 0–59 → No (major gaps in required skills or experience)

---

## 🗂 Project Structure

```
hirelens/
├── hirelens-frontend/               # Next.js 14 app
│   ├── src/
│   │   ├── app/
│   │   │   ├── (protected)/
│   │   │   │   ├── dashboard/page.tsx
│   │   │   │   ├── jobs/page.tsx
│   │   │   │   ├── candidates/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── CandidateModal.tsx
│   │   │   │   │   └── AddCandidateModal.tsx
│   │   │   │   └── screening/
│   │   │   │       ├── page.tsx
│   │   │   │       ├── CandidateResultCard.tsx
│   │   │   │       └── ScreeningProgressModal.tsx
│   │   │   ├── login/page.tsx
│   │   │   └── signup/page.tsx
│   │   ├── components/
│   │   │   ├── layout/AppShell.tsx
│   │   │   ├── LensLogo.tsx
│   │   │   ├── JobDetailModal.tsx
│   │   │   └── ScreeningResultsModal.tsx
│   │   ├── lib/
│   │   │   ├── api.ts               # Axios client, all API functions
│   │   │   ├── firebaseAuth.ts      # Google OAuth
│   │   │   └── mockData.ts          # Dev/offline fallback data
│   │   ├── store/
│   │   │   └── authStore.ts         # Zustand auth state
│   │   └── types/index.ts           # TypeScript interfaces
│   ├── .env.local                   # Frontend env vars
│   └── package.json
│
└── hirelens-backend/                # FastAPI Python backend
    ├── src/
    │   ├── api/endpoints/
    │   │   ├── auth.py              # Signup / signin (bcrypt + JWT)
    │   │   ├── jobs.py              # Jobs CRUD + sync-candidates
    │   │   ├── candidates.py        # Candidates CRUD + file upload
    │   │   └── screening.py         # AI screening trigger + results
    │   ├── services/
    │   │   ├── gemini_client.py     # Gemini API w/ key rotation
    │   │   ├── gemini_screener.py   # Batch screening orchestration
    │   │   ├── matcher.py           # Prompt builder + per-candidate eval
    │   │   ├── scorer.py            # Score normalization
    │   │   ├── ranker.py            # Sort + assign ranks
    │   │   ├── explainability.py    # Recruiter note generation
    │   │   └── file_parser.py       # CSV + PDF parsing
    │   ├── schemas/
    │   │   ├── job_schema.py
    │   │   ├── request_models.py
    │   │   └── talent_profile.py
    │   ├── config/
    │   │   └── settings.py          # Pydantic settings + key pool
    │   └── db.py                    # MongoDB collections
    ├── .env                         # Backend env vars
    ├── requirements.txt
    └── .github/workflows/deploy.yml # CI/CD → Cloud Run
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.12+
- MongoDB (local or Atlas)
- Gemini API key(s) — [get one free at ai.google.dev](https://aistudio.google.com/api-keys)

---

### Backend Setup

```bash
# 1. Clone the repo
git clone https://github.com/kevineumutoni/HireLens-AI
cd HireLens-AI

# 2. Create virtual environment
python -m venv env
source env/bin/activate        # Windows: env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and fill in environment variables
cp .env.example .env
```

Edit `.env`:

```env
# Gemini — add your API key
GEMINI_API_KEYS=AIzaSy_key
GEMINI_MODEL=gemini-2.5-flash-lite

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=hirelens

# Server
API_PORT=8000
API_HOST=0.0.0.0
DEBUG=true
TOP_CANDIDATES=10

# Auth
JWT_SECRET=your-secret-key-here
JWT_EXPIRES_HOURS=24

# Frontend
FRONTEND_URL=http://localhost:3000
```

```bash
# 5. Start the backend
python -m uvicorn src.app:app --reload --port 8000

# API docs available at:
http://localhost:8000/docs
```

---

### Frontend Setup

```bash
# 1. Clone the repo
git clone https://github.com/kevineumutoni/HireLens-Frontend
cd HireLens-Frontend

# 1. Install dependencies
npm install

# 2. Copy and fill in environment variables
cp .env.local.example .env.local
```

Edit `.env.local`:

```env
# Backend API
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Firebase (optional — for Google OAuth)
NEXT_PUBLIC_FIREBASE_API_KEY=your-firebase-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id

# Set to true to use mock data without a running backend
NEXT_PUBLIC_USE_MOCK_API=false
```

```bash
# 3. Start the frontend
npm run dev

# App available at http://localhost:3000
```

---

### Quick Start (both together)

```bash
# Terminal 1 — MongoDB (if running locally)
mongod --dbpath ./data/db

# Terminal 2 — Backend
cd HireLens-AI && python -m uvicorn src.app:app --reload --port 8000

# Terminal 3 — Frontend
cd HireLens-Frontend && npm run dev
```

---

## 🔌 API Reference

### Auth
| Method  | Endpoint          | Description                    |
|--------|--------------------|--------------------------------|
| `POST` | `/api/auth/signup` | Register new recruiter account |
| `POST` | `/api/auth/signin` | Login, returns JWT token       |

### Jobs
| Method  | Endpoint                          | Description                  |
|---------|-----------------------------------|------------------------------|
| `GET`   | `/api/jobs`                       | List all jobs (paginated)    |
| `POST`  | `/api/jobs`                       | Create a job posting         |
| `GET`   | `/api/jobs/:id`                   | Get single job               |
| `PATCH` | `/api/jobs/:id`                   | Update job (partial)         |
| `DELETE`| `/api/jobs/:id`                   | Delete job                   |
| `PATCH` | `/api/jobs/:id/sync-candidates`   | Attach all candidates to job |
| `PATCH` | `/api/jobs/:id/unsync-candidates` | Detach candidates from job   |

### Candidates
| Method   | Endpoint                 | Description                             |
|----------|--------------------------|-----------------------------------------|
| `GET`    | `/api/candidates`        | List candidates (paginated, searchable) |
| `POST`   | `/api/candidates`        | Add candidate manually                  |
| `GET`    | `/api/candidates/:id`    | Get candidate profile                   |
| `DELETE` | `/api/candidates/:id`    | Remove candidate                        |
| `POST`   | `/api/candidates/upload` | Upload CSV or PDF (Gemini parses PDF)   |

### Screening
| Method    | Endpoint             | Description                        |
|-----------|----------------------|------------------------------------|
| `POST`    | `/api/screening`     | Trigger AI screening run for a job |
| `GET`     | `/api/screening`     | List all screening results         |
| `GET`     | `/api/screening/:id` | Get specific screening run         |
| `DELETE`  | `/api/screening/:id` | Delete a screening run             |
| `DELETE`  | `/api/screening`     | Delete all runs (or by job_id)     |

---

## ⚙️ Environment Variables Reference

### Backend (`.env`)

| Variable               | Required| Description |
|------------------------|-----|---------------------------------------------------|
| `GEMINI_API_KEYS`      | ✅ | Comma-separated Gemini API keys (for key rotation)  |
| `GEMINI_API_KEY`       | ✅  | Single key fallback if GEMINI_API_KEYS not set     |
| `GEMINI_MODEL`         |     | Model name (default: `gemini-2.5-flash-lite`)       |
| `MONGODB_URI`          | ✅ | MongoDB connection string                            |
| `MONGODB_DB`           |     | Database name (default: `hirelens`)                 |
| `JWT_SECRET`           | ✅ | Secret key for JWT signing                            |
| `JWT_EXPIRES_HOURS`    |     | Token expiry in hours (default: `24`)                |
| `FRONTEND_URL`         |     | CORS allowed origin (default: `http://localhost:3000`) |
| `API_PORT`             |     | Server port (default: `8000`)                        |
| `DEBUG`                |     | Enable debug logs (default: `true`)                  |
| `TOP_CANDIDATES`       |     | Default shortlist size (default: `10`)               |

### Frontend (`.env.local`)

| Variable                     | Required     | Description |
|------------------------------|--------------|-------------|
| `NEXT_PUBLIC_API_BASE_URL`   | ✅           | Backend API URL |
| `NEXT_PUBLIC_USE_MOCK_API` |                | Use mock data offline (`true`/`false`) |
| `NEXT_PUBLIC_FIREBASE_API_KEY` |            | Firebase API key (Google OAuth) |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` |        | Firebase auth domain |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` |         | Firebase project ID |
| `NEXT_PUBLIC_FIREBASE_APP_ID` |             | Firebase app ID |

---

## 📦 Tech Stack

### Frontend
| Layer     | Technology                         |
|-----------|------------------------------------|
| Framework | Next.js 14 (App Router)            |
| Language  | TypeScript                         |
| Styling   | Inline CSS with design tokens      |
| State     | Zustand                            |
| HTTP      | Axios (15min timeout for screening)|
| Auth      | Firebase Google OAuth + JWT        |
| Toast     | react-hot-toast                    |

### Backend
| Layer       | Technology                      |
|-------------|---------------------------------|
| Framework   | FastAPI                         |
| Language    | Python 3.12                     |
| Server      | Uvicorn                         |
| Validation  | Pydantic v2                     |
| Database    | MongoDB (Motor async driver)    |
| Auth        | bcrypt + python-jose (JWT)      |
| AI          | Google Gemini API               |
| HTTP Client | httpx (async)                   |
| File Parsing| PyPDF2, pandas                  |

### Infrastructure
| Service          | Provider         |
|------------------|------------------|
| Frontend Hosting | Vercel           |
| Backend Hosting  | Google Cloud Run |
| Database         | MongoDB Atlas    |
| CI/CD            | GitHub Actions   |
| Container        | Docker           |

---

## 🧠 AI Design Decisions

**Why Gemini over other models?**
Gemini API is mandatory per hackathon rules and the `gemini-2.5-flash-lite` model gives fast, consistent structured outputs ideal for batch screening.

### Why not Gemini 1.5 Flash or 1.5 Pro?

`gemini-1.5-flash` and `gemini-1.5-pro` are previous-generation models. 
2.5 Flash is Google's latest production model as of April 2026 and outperforms 
both on reasoning benchmarks while maintaining the same speed profile. 
For a screening task that requires interpreting nuanced skill descriptions, 
inferring experience relevance from job history, and producing structured JSON 
reliably — better reasoning directly translates to more accurate match scores. 
1.5 Pro is slower and more expensive. 1.5 Flash produces less consistent 
structured output. 2.5 Flash gives us the best of both.

### Why not Gemini 2.5 Pro?

`gemini-2.5-pro` is more powerful but significantly slower — average response 
times of 8–15 seconds per candidate versus 2–4 seconds for 2.5 Flash. 
At 155 candidates in batches of 5, that difference compounds into minutes of 
extra wall-clock time per screening run. The screening task does not require 
deep multi-step reasoning or long-context analysis — it requires fast, 
consistent structured evaluation of a single candidate profile against fixed 
criteria. 2.5 Flash is the right tool for that job.

### Why not GPT-4o, Claude, or another LLM entirely?

Beyond the hackathon requirement, Gemini has practical advantages for this 
use case specifically:

- **Free tier with key rotation.** Gemini's free tier allows 15 requests/minute 
  per API key. By rotating across multiple keys with round-robin load balancing, 
  we can screen 155 candidates without hitting quota walls mid-run — at zero cost. 
  GPT-4o and Claude Sonnet have no meaningful free tier for batch workloads.

- **JSON output reliability.** Gemini 2.5 Flash at temperature 0.2 produces 
  clean, parseable JSON on over 95% of calls in our testing. The low temperature 
  setting trades creativity for determinism — exactly what you want when the 
  output feeds a ranking algorithm and a single malformed response would break 
  a candidate's evaluation.

- **No vendor lock-in beyond the API.** The `GeminiClient` in 
  `src/services/gemini_client.py` is a thin wrapper around a REST call. 
  Swapping to a different model or provider requires changing one URL and one 
  model string — the rest of the pipeline is model-agnostic.

### The one real tradeoff

Gemini's free tier rate limits (15 RPM per key) mean throughput scales with 
the number of API keys available, not with compute. This is why multi-key 
rotation is a first-class feature of HireLens rather than an afterthought — 
adding a second key doubles throughput, a third triples it. In a production 
deployment with a paid tier, the batch size and concurrency settings in 
`src/config/settings.py` can be increased accordingly.

**Why key rotation?**
Gemini free tier is 15 requests/minute per key. With 20 candidates in batches of 5, that's 4 API calls. Multiple keys let us screen the full pool without hitting quota walls mid-run.

**Why `httpx` instead of `requests`?**
`requests` is synchronous/blocking. When FastAPI calls `asyncio.gather()` to run 5 candidates in parallel, a blocking HTTP call freezes the entire event loop — meaning all 5 run sequentially. `httpx.AsyncClient` with `await` is truly async, so parallelism actually works. This reduced screening time from ~77 minutes to ~5 minutes for 155 candidates.

**Why inline explanation generation?**
The original design made a second Gemini API call per candidate to generate the recruiter note — doubling API usage and time. The current approach assembles the explanation from already-parsed fields (strengths, gaps, score, recommendation) instantly, with no extra call. Quality is equivalent for the recruiter's use case.

**Bias mitigation:**
Every screening prompt explicitly instructs Gemini: *"Evaluate ONLY job-related qualifications. Ignore name, gender, age, nationality, location."* Candidates are identified by MongoDB ObjectId during evaluation, not by name.

---

## 🚢 Deployment

### Frontend → Vercel

```bash
# From the frontend directory
npm run build

# Deploy via Vercel CLI
npx vercel --prod
```

Set environment variables in Vercel dashboard under Project → Settings → Environment Variables.

### Backend → Google Cloud Run (automated)

Push to `main` branch. GitHub Actions (`.github/workflows/deploy.yml`) will:
1. Build Docker image
2. Push to Docker Hub
3. Deploy to Cloud Run with all env vars from GitHub Secrets

Required GitHub Secrets:
```
GCP_PROJECT_ID
GCP_SA_KEY
DOCKERHUB_USERNAME
DOCKERHUB_TOKEN
MONGODB_URI
GEMINI_API_KEY
FRONTEND_URL
```

### Manual Cloud Run deploy

```bash
# Build and push image
docker build -t your-dockerhub/HireLens-AI.
docker push your-dockerhub/HireLens-AI

# Deploy to Cloud Run
gcloud run deploy hirelens \
  --image your-dockerhub/hirelens-backend:latest \
  --region europe-west1 \
  --memory 2Gi \
  --timeout 3600 \
  --set-env-vars "MONGODB_URI=...,GEMINI_API_KEY=..."
```

---

## 📋 CSV Upload Format

To bulk-import candidates via CSV, use these column headers:

```csv
firstName,lastName,email,headline,location,skills,bio
Jean,Mukama,jean@example.com,Backend Engineer | Node.js + Python,Kigali Rwanda,Node.js:Advanced:5;Python:Advanced:4;REST API:Expert:5,Passionate backend engineer...
Amina,Niyonzima,amina@example.com,Full-Stack Developer,Nairobi Kenya,React:Advanced:3;TypeScript:Advanced:2;Node.js:Intermediate:2,Product-focused developer...
```

Skills format: `SkillName:Level:YearsExp` separated by semicolons. Level must be one of: `Beginner`, `Intermediate`, `Advanced`, `Expert`.

---

## 🔒 Security Notes

- Passwords hashed with bcrypt (72-byte limit enforced, preventing bcrypt truncation attacks)
- JWT tokens expire in 24 hours (configurable)
- API keys never exposed to frontend — all Gemini calls are server-side only
- CORS restricted to configured `FRONTEND_URL`
- MongoDB ObjectIds used as candidate identifiers during AI evaluation (name not in scope)

---

## Every shortlisted candidate includes:
- **Match Score** — 0–100 numerical score
- **Recommendation** — Strong Yes / Yes / Maybe / No  
- **Strengths** — specific qualifications that match the role
- **Gaps** — specific missing requirements
- **Reasoning** — Gemini's plain-English explanation of the score
- **Recruiter Note** — assembled explanation ready to share with hiring managers


## 🏆 Team

**HireLens** — Umurava AI Hackathon 2026

| Name            | Role                                       |
|-----------------|---|
| Kevine Umutoni  | ML Engineer · AI Integration               |
| Berissa Muyizere| Full-Stack Engineer . Backend Engineer     |
| Bonnette Umutoni| Full-Stack Engineer . Frontend Engineer    |

---

## 📄 Assumptions & Limitations

- **Candidate data quality** — AI scoring accuracy depends on how complete candidate profiles are. Profiles with missing skills or experience dates may score lower than expected.
- **PDF parsing** — Works best on text-based PDFs. Scanned image PDFs are not supported.
- **Screening time** — 155 candidates takes approximately 1–2 minutes depending on Gemini response latency and number of API keys available.
- **Bias guardrails** — Prompt-level instructions reduce but do not eliminate all potential bias. Human review of AI outputs is always recommended before final hiring decisions.
- **No real-time streaming** — Progress modal simulates progress with fake increments. Actual screening runs server-side as a single HTTP request.

---

## Why should you trust HireLens amongst other recruiting systems
<img width="2181" height="1869" alt="image 1" src="https://github.com/user-attachments/assets/112e50a2-d26f-4c96-960b-34fc3cdffdda" />


<div align="center">

Built with intention and ❤️ in Kigali for the **Umurava AI Hackathon 2026**

*Powered by Gemini AI · FastAPI · Next.js · MongoDB*

</div>

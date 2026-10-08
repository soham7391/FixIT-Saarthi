# FixIT Saarthi

A hybrid expert system for structured Windows computer troubleshooting.

## Overview

FixIT Saarthi guides users through common computer problems using natural-language input, targeted questions, deterministic diagnostic rules, safe troubleshooting steps, and explicit resolution verification.

The system uses AI for natural-language understanding and supported screenshot interpretation. Final diagnosis and cause ranking are controlled by domain-specific expert rules rather than generated directly by the AI model.

## Core Features

- Four troubleshooting domains
- Natural-language problem description
- Deterministic expert diagnosis with ranked causes and explanations
- Targeted diagnostic questions with Yes, No, and Skip handling
- Optional Task Manager screenshot analysis for performance problems
- Domain-intent detection with user-controlled domain switching
- Safety-labelled troubleshooting steps: Safe, Caution, Advanced
- Explicit user confirmation before a session is marked resolved
- Supabase-based session persistence
- Resolved diagnosis report with Print / Save PDF support
- AI provider failover and output validation
- Progressive Web App support

## Supported Domains

1. Performance and Freezing
2. Boot Failures and Startup
3. Network and Connectivity
4. Driver and Peripheral Problems

## System Architecture

```mermaid
graph TD
    U[User] --> F[React PWA]
    F -->|Problem text, answers, screenshot| B[FastAPI Backend]
    B --> S[Safety and Validation]
    S --> A[AI Assistance Layer]
    A -->|Structured observations| E[Deterministic Expert Engine]
    E --> K[Domain Knowledge Bases]
    E --> R[Ranked Causes and Explanations]
    R --> F
    F --> T[Troubleshooting and Resolution Verification]
    T --> B
    B --> DB[(Supabase PostgreSQL)]
```

## Diagnostic Flow

```text
Problem description
        |
        v
Domain intent detection
        |
        v
AI or heuristic symptom parsing
        |
        v
Safety validation
        |
        v
Targeted questions
        |
        v
Structured observations
        |
        v
Domain-specific expert evaluation
        |
        v
Ranked causes and explanations
        |
        v
Safety-labelled troubleshooting
        |
        v
User verification
        |
        v
Resolved session and report
```

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite, Tailwind CSS |
| App model | Progressive Web App |
| Backend | Python, FastAPI |
| Expert engine | Python rule-based evaluation and ranking |
| AI | Google Gemini with Groq fallback |
| Database | Supabase PostgreSQL |
| Validation | Pydantic, frontend TypeScript types |
| Testing | Pytest, Vitest |

## Project Structure

```text
backend/
├── app/
│   ├── api/             # FastAPI routes
│   ├── db/              # Supabase session persistence
│   ├── expert_engine/   # Rule evaluation, ranking, explanations
│   ├── gemini/          # AI providers, parsing and safety validation
│   ├── knowledge_base/  # Domain-specific symptoms, rules and fixes
│   ├── schemas/         # Backend request and response models
│   └── main.py          # FastAPI application entry point
├── tests/               # Backend test suite
├── frontend/
│   ├── src/
│   │   ├── components/  # Workflow and UI components
│   │   ├── api/         # Backend API client
│   │   ├── types/       # Shared frontend types
│   │   └── utils/       # Domain intent and UI utilities
│   └── ...
├── requirements.txt
└── .env.example
```

## Local Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm
- Supabase project
- Gemini API key
- Groq API key for provider fallback

### Backend

From the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend

From `backend/frontend`:

**Planned for Future Releases**:
- 🔄 **Boot Failure / Slow Startup** domain
- 🌐 **Network / Connectivity** domain
- 🗄️ **Supabase PostgreSQL** session persistence & diagnostic history
- 📱 **QR Code Cross-Device Session Sync**

---

- **Docker Validation**: Builds and validates Docker images for both `backend` and `frontend` services using BuildKit without pushing to a registry.

---

## 🚀 Production Deployment (CD on Render)

FixIT Saarthi uses an automated **CI → CD → Render** pipeline (`.github/workflows/cd.yml`).

### Workflow & Trigger
1. **GitHub Actions CI** runs on every push or PR to `main`.
2. Upon **CI success on `main`**, the **CD workflow** (`FixIT Saarthi CD`) triggers automatically.
3. CD sends HTTP POST requests to Render **Deploy Hooks** to deploy the latest commit seamlessly.

### Render Services Architecture
1. **Backend Web Service** (Render Free Web Service):
   - **Environment**: Docker (uses root `Dockerfile`).
   - **Required Render Environment Variables**:
     - `GEMINI_API_KEY`: Google GenAI API Key.
     - `GEMINI_MODEL`: `gemini-2.5-flash`
     - `SUPABASE_URL`: Supabase project URL.
     - `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key.

2. **Frontend Static Site** (Render Free Static Site):
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Publish Directory**: `dist`
   - **Required Render Environment Variable**:
     - `VITE_API_BASE_URL`: Deployed backend API URL (e.g., `https://fixit-saarthi-backend.onrender.com/api`).

### Required GitHub Actions Secrets
In your GitHub repository under **Settings > Secrets and variables > Actions**, configure:
- `RENDER_BACKEND_DEPLOY_HOOK_URL`: Render Backend Deploy Hook URL.
- `RENDER_FRONTEND_DEPLOY_HOOK_URL`: Render Frontend Deploy Hook URL.

> [!NOTE]
> On Render's Free Tier, backend Web Services spin down after 15 minutes of inactivity. The first request after sleep may take ~30–50 seconds while the container wakes up.



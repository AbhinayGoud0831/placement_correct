# AI-Powered Placement Intelligence & Career Preparation Platform

An AI-driven career prep system that helps students analyze resumes, discover job opportunities, and prepare for interviews—all powered by local LLMs and semantic AI.

## Quick Start

1. Extract ZIP
2. Read **SETUP_FIRST_TIME.md**
3. Follow the setup steps

## Features

- 📄 **Resume Upload** — Parse PDF/DOCX, auto-extract skills/education/experience
- 🎯 **Job Fit Analysis** — Semantic matching + weighted scoring
- 💼 **Job Discovery** — Browse and get AI-powered job recommendations
- 📊 **Skill Gaps** — See missing skills vs. required
- 🎓 **Learning Recommendations** — Personalized career development plan
- 🎤 **Interview Prep** — Technical & behavioral questions + revision topics
- 📈 **Analysis History** — Track your progress over time

## Architecture

```
React Frontend → FastAPI Backend → PostgreSQL Database
                       ↓
        Ollama + Qwen2.5 (Resume/JD extraction)
        sentence-transformers (Semantic matching)
```

**Scoring Formula:**
- Skills: 50%
- Experience: 30% (including years comparison)
- Education: 20%

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL (via Docker or local)
- Ollama + Qwen2.5 model

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic, PostgreSQL
- **Frontend**: React, Axios, React Router
- **AI/ML**: Ollama, Qwen2.5, sentence-transformers
- **File Handling**: pdfplumber, python-docx
- **Auth**: JWT (no external OAuth)

## Database

- `students` — Registered users
- `resumes` — Uploaded resumes + extracted data
- `job_descriptions` — Analyzed job descriptions
- `sample_jobs` — Pre-populated job listings
- `analyses` — Analysis results (fit scores, gaps, recommendations, interview prep)

## Status

**⚠️ PROJECT RELEASE** — Core features are implemented. Discovery supports public job APIs (Remotive + Arbeitnow) with an offline fallback catalog.

## Important implementation notes

- **Job discovery:** public APIs from Remotive and Arbeitnow can be refreshed from the Discovery page; the app keeps an offline fallback catalog when external sources are unavailable.
- **Source attribution:** live listings retain their original source and application URL so users can open the original posting.
- **Analysis workflow:** selecting a discovery job automatically creates a student-owned job-description record before analysis, preserving the existing history schema and user isolation.
- **Security:** the destructive sample-job seed endpoint has been removed. Discovery is authenticated and refresh never deletes existing jobs.
- **Scoring:** Skills 50%, Experience 30% and Education 20%. Experience includes explicit years comparison.

## For Developers

- Backend tests: `cd backend && python3 tests/test_scoring_formula.py`
- Frontend: Uses React 18, React Router v6, Axios for HTTP
- Database migrations: `cd backend && alembic upgrade head`
- API docs: http://localhost:8000/docs

## Files You Submitted

```
placement_correct/
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   │   ├── discovery.py          ← Job discovery & recommendations
│   │   │   ├── analyses.py           ← Run & retrieve analyses
│   │   │   ├── auth.py               ← JWT login/register
│   │   │   ├── resumes.py            ← Resume upload & parsing
│   │   │   └── jobs.py               ← Job description creation
│   │   ├── services/
│   │   │   ├── matching.py           ← Weighted scoring (with year extraction)
│   │   │   ├── llm_extraction.py     ← Qwen2.5 integration
│   │   │   ├── recommendations.py    ← Learning plans + interview prep
│   │   │   └── file_parser.py        ← PDF/DOCX parsing
│   │   ├── models.py                 ← SQLAlchemy schemas
│   │   ├── schemas.py                ← Pydantic schemas
│   │   ├── auth.py                   ← Password hashing + JWT
│   │   ├── main.py                   ← FastAPI app
│   │   └── config.py                 ← Settings from .env
│   ├── alembic/                      ← Database migrations
│   ├── tests/                        ← Unit tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Discovery.jsx         ← Job discovery + recommendations
│   │   │   ├── JobAnalysis.jsx       ← Analyze resume vs job
│   │   │   ├── AnalysisDetail.jsx    ← View results + recommendations
│   │   │   ├── History.jsx           ← Past analyses
│   │   │   ├── Dashboard.jsx         ← Home page
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── UploadResume.jsx
│   │   ├── components/
│   │   │   ├── Navbar.jsx
│   │   │   └── ScoreGauge.jsx
│   │   ├── App.jsx                   ← Router setup
│   │   ├── api.js                    ← Axios client
│   │   ├── index.js
│   │   └── index.css                 ← Styling
│   └── package.json
├── docker-compose.yml                ← PostgreSQL
├── setup.sh                          ← Auto-setup script
├── README.md                         ← This file
├── SETUP_FIRST_TIME.md              ← Important: Read this!
├── DEPLOYMENT.md                    ← Production checklist
├── VERIFICATION.md                  ← Compliance checklist
└── .gitignore
```

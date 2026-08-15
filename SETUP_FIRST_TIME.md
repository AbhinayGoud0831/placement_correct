# First-Time Setup Guide

## 1. Start PostgreSQL
```bash
docker compose up -d
```

## 2. Start Ollama + Qwen2.5
```bash
ollama pull qwen2.5
ollama serve
```

## 3. Start Backend
```bash
cd backend
# Windows: venv\\Scripts\\activate
# Linux/macOS: source venv/bin/activate
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000 and Swagger at http://localhost:8000/docs.

## 4. Start Frontend
```bash
cd frontend
npm install
npm start
```

Open http://localhost:3000.

## 5. Job Discovery
The application automatically creates an offline fallback catalog on first use, so there is **no public seed endpoint** and no manual database seeding step.

On the Discovery page, click **Refresh Live Jobs** to pull public listings from Remotive and Arbeitnow. If the external APIs are unavailable, cached/live jobs and the fallback catalog remain usable.

## 6. Test the workflow
1. Register a student account.
2. Upload a PDF/DOCX resume.
3. Open **Job Discovery**.
4. Browse jobs or select a resume and click **Get Recommendations**.
5. Click **Analyze My Match / View Full Analysis**.
6. The discovery job is automatically imported into the student's job-description history and analyzed using the same 50/30/20 scoring model.
7. Review skill gaps, learning recommendations, interview preparation and history.

## Troubleshooting

### Live jobs do not refresh
This is normally an external API/network issue. The platform intentionally keeps its fallback catalog available. Try Refresh Live Jobs again later.

### Ollama connection refused
Run `ollama serve` and verify `OLLAMA_HOST` in `backend/.env`.

### PostgreSQL connection refused
Run `docker compose up -d` and wait for PostgreSQL to become healthy.

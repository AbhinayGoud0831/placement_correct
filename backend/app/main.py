from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, resumes, jobs, analyses, discovery

app = FastAPI(
    title="AI-Powered Placement Intelligence & Career Preparation Platform",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(resumes.router)
app.include_router(jobs.router)
app.include_router(analyses.router)
app.include_router(discovery.router)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}

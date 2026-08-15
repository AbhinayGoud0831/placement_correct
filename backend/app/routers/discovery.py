from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.config import settings
from app.database import get_db
from app.services.builtin_jobs import builtin_rows
from app.services.job_sources import fetch_live_jobs
from app.services.matching import compute_fit_score

router = APIRouter(prefix="/api/discovery", tags=["discovery"])


def _ensure_fallback_jobs(db: Session) -> None:
    """Keep the app usable offline without exposing a destructive seed endpoint."""
    if db.query(models.SampleJob).count() > 0:
        return
    for row in builtin_rows():
        db.add(models.SampleJob(**row))
    db.commit()


def _upsert_jobs(db: Session, rows: list[dict]) -> int:
    count = 0
    for row in rows:
        job = (
            db.query(models.SampleJob)
            .filter(models.SampleJob.external_id == row["external_id"])
            .first()
        )
        if job is None:
            job = models.SampleJob(**row)
            db.add(job)
        else:
            for key, value in row.items():
                setattr(job, key, value)
        count += 1
    db.commit()
    return count


@router.post("/refresh", response_model=schemas.JobRefreshOut)
def refresh_live_jobs(
    search: str = "",
    limit: int = 50,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    """Refresh discovery from public job APIs; never deletes existing jobs."""
    del current_student
    limit = max(1, min(limit, settings.LIVE_JOB_LIMIT))
    rows, errors = fetch_live_jobs(search=search, limit=limit)
    added_or_updated = _upsert_jobs(db, rows) if rows else 0
    _ensure_fallback_jobs(db)
    return schemas.JobRefreshOut(
        source_count=len(rows),
        added_or_updated=added_or_updated,
        sources=["Remotive", "Arbeitnow"],
        warnings=errors,
    )


@router.get("/recommend", response_model=list[schemas.JobRecommendationOut])
def get_recommendations(
    resume_id: str,
    top_k: int = 5,
    min_fit: float = 30.0,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    """Return jobs ranked by the same 50/30/20 fit model used for analysis."""
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.id == resume_id, models.Resume.student_id == current_student.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    _ensure_fallback_jobs(db)
    recommendations = []
    for job in db.query(models.SampleJob).all():
        result = compute_fit_score(resume.extracted_data or {}, job.extracted_data or {})
        if result["fit_score"] >= min_fit:
            recommendations.append({
                "job_id": job.id,
                "title": job.title,
                "company": job.company,
                "level": job.level,
                "fit_score": result["fit_score"],
                "reason": (
                    f"Matches {len(result['matching_skills'])} skills: "
                    f"{', '.join(result['matching_skills'][:4]) or 'none'}. "
                    f"Experience: {result['experience_score']:.0f}%, "
                    f"Education: {result['education_score']:.0f}%.",
                )
            })
    recommendations.sort(key=lambda x: x["fit_score"], reverse=True)
    return recommendations[: max(1, min(top_k, 20))]


@router.get("", response_model=list[schemas.SampleJobOut])
def list_jobs(
    search: str = "",
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    del current_student
    _ensure_fallback_jobs(db)
    query = db.query(models.SampleJob)
    if search.strip():
        search_term = f"%{search.lower()}%"
        query = query.filter(
            models.SampleJob.title.ilike(search_term)
            | models.SampleJob.company.ilike(search_term)
            | models.SampleJob.description.ilike(search_term)
        )
    return query.order_by(models.SampleJob.created_at.desc()).all()


@router.get("/{job_id}", response_model=schemas.SampleJobOut)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    del current_student
    job = db.query(models.SampleJob).filter(models.SampleJob.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

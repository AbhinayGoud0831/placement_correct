from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db
from app.services.matching import compute_fit_score
from app.services.recommendations import generate_recommendations, generate_interview_prep

router = APIRouter(prefix="/api/analyses", tags=["analyses"])


def _resolve_job(req: schemas.AnalysisRequest, db: Session, student_id: str):
    """Resolve a personal JD or transparently import a discovery job for analysis."""
    job = (
        db.query(models.JobDescription)
        .filter(models.JobDescription.id == req.job_id, models.JobDescription.student_id == student_id)
        .first()
    )
    if job:
        return job

    sample = db.query(models.SampleJob).filter(models.SampleJob.id == req.job_id).first()
    if not sample:
        return None

    # Discovery jobs are converted into a student-owned JobDescription so the
    # existing analysis/history schema remains normalized and isolated per user.
    job = models.JobDescription(
        student_id=student_id,
        title=sample.title,
        raw_text=sample.description,
        extracted_data=sample.extracted_data or {},
    )
    db.add(job)
    db.flush()
    return job


@router.post("", response_model=schemas.AnalysisOut, status_code=201)
def run_analysis(
    req: schemas.AnalysisRequest,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.id == req.resume_id, models.Resume.student_id == current_student.id)
        .first()
    )
    job = _resolve_job(req, db, current_student.id)
    if not resume or not job:
        raise HTTPException(status_code=404, detail="Resume or job description not found")

    result = compute_fit_score(resume.extracted_data or {}, job.extracted_data or {})
    recommendations = generate_recommendations(
        result["missing_skills"], (job.extracted_data or {}).get("required_skills", [])
    )
    interview_prep = generate_interview_prep(job.raw_text, resume.extracted_data or {})

    analysis = models.Analysis(
        student_id=current_student.id,
        resume_id=resume.id,
        job_id=job.id,
        fit_score=result["fit_score"],
        skills_score=result["skills_score"],
        experience_score=result["experience_score"],
        education_score=result["education_score"],
        matching_skills=result["matching_skills"],
        missing_skills=result["missing_skills"],
        recommendations=recommendations,
        interview_prep=interview_prep,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    return analysis


@router.get("", response_model=list[schemas.AnalysisOut])
def list_analyses(
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    return (
        db.query(models.Analysis)
        .filter(models.Analysis.student_id == current_student.id)
        .order_by(models.Analysis.created_at.desc())
        .all()
    )


@router.get("/{analysis_id}", response_model=schemas.AnalysisOut)
def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    analysis = (
        db.query(models.Analysis)
        .filter(models.Analysis.id == analysis_id, models.Analysis.student_id == current_student.id)
        .first()
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return analysis

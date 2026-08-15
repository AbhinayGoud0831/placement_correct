from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db
from app.services.llm_extraction import extract_job_data

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=schemas.JobDescriptionOut, status_code=201)
def create_job(
    job_in: schemas.JobDescriptionCreate,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    try:
        extracted_data = extract_job_data(job_in.raw_text)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI extraction service unavailable: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to extract job description data: {str(e)}"
        )
    
    job = models.JobDescription(
        student_id=current_student.id,
        title=job_in.title,
        raw_text=job_in.raw_text,
        extracted_data=extracted_data,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("", response_model=list[schemas.JobDescriptionOut])
def list_jobs(
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    return (
        db.query(models.JobDescription)
        .filter(models.JobDescription.student_id == current_student.id)
        .order_by(models.JobDescription.created_at.desc())
        .all()
    )


@router.get("/{job_id}", response_model=schemas.JobDescriptionOut)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    job = (
        db.query(models.JobDescription)
        .filter(models.JobDescription.id == job_id, models.JobDescription.student_id == current_student.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return job

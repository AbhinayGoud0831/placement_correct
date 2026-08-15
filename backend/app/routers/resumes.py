import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.config import settings
from app.database import get_db
from app.services.file_parser import extract_text
from app.services.llm_extraction import extract_resume_data

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@router.post("/upload", response_model=schemas.ResumeOut, status_code=201)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")

    student_dir = os.path.join(settings.UPLOAD_DIR, current_student.id)
    os.makedirs(student_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(student_dir, stored_name)

    with open(file_path, "wb") as f:
        f.write(file.file.read())

    raw_text = extract_text(file_path)
    
    try:
        extracted_data = extract_resume_data(raw_text)
    except RuntimeError as e:
        raise HTTPException(
            status_code=503,
            detail=f"AI extraction service unavailable: {str(e)}. Resume file saved but extraction failed."
        )
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail=f"Failed to extract resume data: {str(e)}"
        )

    resume = models.Resume(
        student_id=current_student.id,
        original_filename=file.filename,
        file_path=file_path,
        raw_text=raw_text,
        extracted_data=extracted_data,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return resume


@router.get("", response_model=list[schemas.ResumeOut])
def list_resumes(
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    return (
        db.query(models.Resume)
        .filter(models.Resume.student_id == current_student.id)
        .order_by(models.Resume.uploaded_at.desc())
        .all()
    )


@router.get("/{resume_id}", response_model=schemas.ResumeOut)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_student: models.Student = Depends(auth.get_current_student),
):
    resume = (
        db.query(models.Resume)
        .filter(models.Resume.id == resume_id, models.Resume.student_id == current_student.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

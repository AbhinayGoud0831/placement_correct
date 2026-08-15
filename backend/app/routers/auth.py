from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import models, schemas, auth
from app.database import get_db

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def register(student_in: schemas.StudentCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Student).filter(models.Student.email == student_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    student = models.Student(
        full_name=student_in.full_name,
        email=student_in.email,
        hashed_password=auth.hash_password(student_in.password),
    )
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.email == form_data.username).first()
    if not student or not auth.verify_password(form_data.password, student.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = auth.create_access_token({"sub": student.id})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.StudentOut)
def get_me(current_student: models.Student = Depends(auth.get_current_student)):
    return current_student

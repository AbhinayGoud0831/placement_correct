from datetime import datetime
from typing import Optional, List, Dict, Any

from pydantic import BaseModel, EmailStr


# ---------- Auth ----------
class StudentCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str


class StudentLogin(BaseModel):
    email: EmailStr
    password: str


class StudentOut(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Resume ----------
class ResumeOut(BaseModel):
    id: str
    original_filename: str
    extracted_data: Optional[Dict[str, Any]] = None
    uploaded_at: datetime

    class Config:
        from_attributes = True


# ---------- Job Description ----------
class JobDescriptionCreate(BaseModel):
    title: Optional[str] = None
    raw_text: str


class JobDescriptionOut(BaseModel):
    id: str
    title: Optional[str]
    raw_text: str
    extracted_data: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Analysis ----------
class AnalysisRequest(BaseModel):
    resume_id: str
    job_id: str


class AnalysisOut(BaseModel):
    id: str
    resume_id: str
    job_id: str
    fit_score: float
    skills_score: float
    experience_score: float
    education_score: float
    matching_skills: Optional[List[str]] = None
    missing_skills: Optional[List[str]] = None
    recommendations: Optional[Dict[str, Any]] = None
    interview_prep: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class SampleJobOut(BaseModel):
    id: str
    title: str
    company: str
    level: Optional[str] = None
    description: str
    extracted_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    source: str = "demo"
    url: Optional[str] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    remote: bool = True

    class Config:
        from_attributes = True


class JobRefreshOut(BaseModel):
    source_count: int
    added_or_updated: int
    sources: List[str]
    warnings: List[str] = []


class JobRecommendationOut(BaseModel):
    job_id: str
    title: str
    company: str
    level: Optional[str] = None
    fit_score: float
    reason: str  # Why this job matches

    class Config:
        from_attributes = True

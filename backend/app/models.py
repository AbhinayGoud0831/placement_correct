import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Float, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


def gen_uuid():
    return str(uuid.uuid4())


class Student(Base):
    __tablename__ = "students"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    resumes = relationship("Resume", back_populates="student", cascade="all, delete-orphan")
    jobs = relationship("JobDescription", back_populates="student", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="student", cascade="all, delete-orphan")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    student_id = Column(UUID(as_uuid=False), ForeignKey("students.id"), nullable=False)
    original_filename = Column(String(500), nullable=False)
    file_path = Column(String(1000), nullable=False)
    raw_text = Column(Text, nullable=True)
    extracted_data = Column(JSON, nullable=True)  # skills, education, experience, projects
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="resumes")
    analyses = relationship("Analysis", back_populates="resume", cascade="all, delete-orphan")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    student_id = Column(UUID(as_uuid=False), ForeignKey("students.id"), nullable=False)
    title = Column(String(500), nullable=True)
    raw_text = Column(Text, nullable=False)
    extracted_data = Column(JSON, nullable=True)  # required skills, qualifications, experience
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="jobs")
    analyses = relationship("Analysis", back_populates="job", cascade="all, delete-orphan")


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    student_id = Column(UUID(as_uuid=False), ForeignKey("students.id"), nullable=False)
    resume_id = Column(UUID(as_uuid=False), ForeignKey("resumes.id"), nullable=False)
    job_id = Column(UUID(as_uuid=False), ForeignKey("job_descriptions.id"), nullable=False)

    fit_score = Column(Float, nullable=False)
    skills_score = Column(Float, nullable=False)
    experience_score = Column(Float, nullable=False)
    education_score = Column(Float, nullable=False)

    matching_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)  # learning resources / plan
    interview_prep = Column(JSON, nullable=True)  # interview questions & tips

    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="analyses")
    resume = relationship("Resume", back_populates="analyses")
    job = relationship("JobDescription", back_populates="analyses")


class SampleJob(Base):
    """Pre-loaded sample jobs for discovery/recommendations."""
    __tablename__ = "sample_jobs"

    id = Column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    title = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=False)
    level = Column(String(50), nullable=True)  # entry, mid, senior
    description = Column(Text, nullable=False)
    extracted_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    external_id = Column(String(500), nullable=True, unique=True, index=True)
    source = Column(String(100), nullable=False, default="demo")
    url = Column(String(2000), nullable=True)
    location = Column(String(255), nullable=True)
    employment_type = Column(String(80), nullable=True)
    remote = Column(Boolean, nullable=False, default=True)

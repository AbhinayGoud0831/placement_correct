"""
Integration tests for all core workflows:
- Authentication (login, register)
- Resume upload & extraction with error handling
- Job analysis & matching
- Job discovery
- Analysis history
"""
import json
import os
import tempfile
from unittest.mock import patch, MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import models, auth


# Setup in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

# Test credentials
TEST_EMAIL = "student@test.com"
TEST_PASSWORD = "TestPassword123!"


class TestAuth:
    """Test authentication workflows."""
    
    def test_register_success(self):
        """Test student registration."""
        response = client.post(
            "/api/auth/register",
            json={
                "full_name": "Test Student",
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
            },
        )
        assert response.status_code == 201
        assert response.json()["email"] == TEST_EMAIL
        print("✅ Registration successful")

    def test_register_duplicate_email(self):
        """Test duplicate email rejected."""
        client.post(
            "/api/auth/register",
            json={
                "full_name": "Test Student",
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
            },
        )
        response = client.post(
            "/api/auth/register",
            json={
                "full_name": "Test Student 2",
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
            },
        )
        assert response.status_code == 400
        print("✅ Duplicate email rejected")

    def test_login_success(self):
        """Test successful login."""
        # Register first
        client.post(
            "/api/auth/register",
            json={
                "full_name": "Test Student",
                "email": "login@test.com",
                "password": TEST_PASSWORD,
            },
        )
        
        # Login
        response = client.post(
            "/api/auth/login",
            data={"username": "login@test.com", "password": TEST_PASSWORD},
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        assert token is not None
        print("✅ Login successful")
        return token

    def test_get_current_student(self):
        """Test fetching current student info."""
        token = self.test_login_success()
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert response.json()["email"] == "login@test.com"
        print("✅ Get current student successful")


class TestResumeWorkflow:
    """Test resume upload and extraction."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup auth for each test."""
        client.post(
            "/api/auth/register",
            json={
                "full_name": "Test Student",
                "email": "resume@test.com",
                "password": TEST_PASSWORD,
            },
        )
        response = client.post(
            "/api/auth/login",
            data={"username": "resume@test.com", "password": TEST_PASSWORD},
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_upload_resume_with_mock_extraction(self):
        """Test resume upload with mocked Ollama extraction."""
        # Create a temporary text file (simulating PDF/DOCX parsing)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("Test PDF content")
            temp_file = f.name
        
        try:
            # Mock extract_text to return sample text
            with patch('app.routers.resumes.extract_text') as mock_extract:
                mock_extract.return_value = "Python, Django, React skills"
                
                # Mock extract_resume_data to return valid structure
                with patch('app.routers.resumes.extract_resume_data') as mock_llm:
                    mock_llm.return_value = {
                        "skills": ["Python", "Django", "React"],
                        "education": [{"degree": "B.Tech", "institution": "Test Uni"}],
                        "experience": [{"role": "Intern", "company": "TestCorp", "duration": "1 year"}],
                        "projects": [],
                    }
                    
                    with open(temp_file, 'rb') as f:
                        response = client.post(
                            "/api/resumes/upload",
                            files={"file": ("test.pdf", f, "application/pdf")},
                            headers=self.headers,
                        )
            
            assert response.status_code == 201
            data = response.json()
            assert data["extracted_data"]["skills"] == ["Python", "Django", "React"]
            print("✅ Resume upload with extraction successful")
        finally:
            os.unlink(temp_file)

    def test_upload_resume_extraction_failure_connection(self):
        """Test resume upload fails gracefully when Ollama unreachable."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("Test PDF content")
            temp_file = f.name
        
        try:
            with patch('app.routers.resumes.extract_text') as mock_extract:
                mock_extract.return_value = "Test content"
                
                # Mock extract_resume_data to simulate Ollama connection error
                with patch('app.routers.resumes.extract_resume_data') as mock_llm:
                    mock_llm.side_effect = RuntimeError(
                        "Failed to connect to Ollama at http://localhost:11434. Is it running?"
                    )
                    
                    with open(temp_file, 'rb') as f:
                        response = client.post(
                            "/api/resumes/upload",
                            files={"file": ("test.pdf", f, "application/pdf")},
                            headers=self.headers,
                        )
            
            assert response.status_code == 503
            assert "AI extraction service unavailable" in response.json()["detail"]
            print("✅ Resume upload error handling (connection) successful")
        finally:
            os.unlink(temp_file)

    def test_upload_resume_extraction_failure_parsing(self):
        """Test resume upload fails gracefully when LLM response unparseable."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write("Test PDF content")
            temp_file = f.name
        
        try:
            with patch('app.routers.resumes.extract_text') as mock_extract:
                mock_extract.return_value = "Test content"
                
                # Mock extract_resume_data to simulate JSON parsing error
                with patch('app.routers.resumes.extract_resume_data') as mock_llm:
                    mock_llm.side_effect = ValueError("Could not parse Ollama response as JSON")
                    
                    with open(temp_file, 'rb') as f:
                        response = client.post(
                            "/api/resumes/upload",
                            files={"file": ("test.pdf", f, "application/pdf")},
                            headers=self.headers,
                        )
            
            assert response.status_code == 422
            assert "Failed to extract resume data" in response.json()["detail"]
            print("✅ Resume upload error handling (parsing) successful")
        finally:
            os.unlink(temp_file)

    def test_list_resumes(self):
        """Test listing student's resumes."""
        response = client.get(
            "/api/resumes",
            headers=self.headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✅ List resumes successful")


class TestJobAnalysisWorkflow:
    """Test job analysis and scoring."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup auth and sample data for each test."""
        client.post(
            "/api/auth/register",
            json={
                "full_name": "Test Student",
                "email": "analysis@test.com",
                "password": TEST_PASSWORD,
            },
        )
        response = client.post(
            "/api/auth/login",
            data={"username": "analysis@test.com", "password": TEST_PASSWORD},
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_create_job_description(self):
        """Test creating a job description."""
        with patch('app.routers.jobs.extract_job_data') as mock_llm:
            mock_llm.return_value = {
                "required_skills": ["Python", "PostgreSQL"],
                "preferred_skills": ["Docker"],
                "qualifications": ["Bachelor's degree"],
                "min_experience_years": 2,
                "responsibilities": ["Build APIs", "Optimize databases"],
            }
            
            response = client.post(
                "/api/jobs",
                json={
                    "title": "Senior Python Engineer",
                    "raw_text": "We are looking for a Python engineer with 5+ years experience...",
                },
                headers=self.headers,
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Senior Python Engineer"
        assert data["extracted_data"]["required_skills"] == ["Python", "PostgreSQL"]
        print("✅ Job description creation successful")

    def test_create_job_extraction_failure(self):
        """Test job creation fails gracefully when Ollama fails."""
        with patch('app.routers.jobs.extract_job_data') as mock_llm:
            mock_llm.side_effect = RuntimeError(
                "Failed to connect to Ollama at http://localhost:11434"
            )
            
            response = client.post(
                "/api/jobs",
                json={
                    "title": "Test Job",
                    "raw_text": "Test job description...",
                },
                headers=self.headers,
            )
        
        assert response.status_code == 503
        assert "AI extraction service unavailable" in response.json()["detail"]
        print("✅ Job creation error handling successful")

    def test_list_jobs(self):
        """Test listing student's job descriptions."""
        response = client.get(
            "/api/jobs",
            headers=self.headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✅ List jobs successful")


class TestDiscovery:
    """Test job discovery and recommendations."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup auth."""
        client.post(
            "/api/auth/register",
            json={
                "full_name": "Test Student",
                "email": "discovery@test.com",
                "password": TEST_PASSWORD,
            },
        )
        response = client.post(
            "/api/auth/login",
            data={"username": "discovery@test.com", "password": TEST_PASSWORD},
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_browse_jobs(self):
        """Test browsing available jobs."""
        response = client.get(
            "/api/discovery",
            headers=self.headers,
        )
        assert response.status_code == 200
        jobs = response.json()
        assert isinstance(jobs, list)
        # Should have builtin fallback jobs
        assert len(jobs) > 0
        print(f"✅ Job discovery successful ({len(jobs)} jobs available)")

    def test_search_jobs(self):
        """Test searching for jobs."""
        response = client.get(
            "/api/discovery?search=Python",
            headers=self.headers,
        )
        assert response.status_code == 200
        print("✅ Job search successful")


class TestAnalyses:
    """Test analysis creation and history."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup auth and create sample resume/job."""
        client.post(
            "/api/auth/register",
            json={
                "full_name": "Test Student",
                "email": "analyses@test.com",
                "password": TEST_PASSWORD,
            },
        )
        response = client.post(
            "/api/auth/login",
            data={"username": "analyses@test.com", "password": TEST_PASSWORD},
        )
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def test_list_analyses(self):
        """Test listing past analyses."""
        response = client.get(
            "/api/analyses",
            headers=self.headers,
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
        print("✅ List analyses successful")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RUNNING INTEGRATION TESTS")
    print("="*60 + "\n")
    
    # Run tests manually
    test_auth = TestAuth()
    test_auth.test_register_success()
    test_auth.test_register_duplicate_email()
    test_auth.test_login_success()
    test_auth.test_get_current_student()
    
    test_resume = TestResumeWorkflow()
    test_resume.setup()
    test_resume.test_upload_resume_with_mock_extraction()
    test_resume.test_upload_resume_extraction_failure_connection()
    test_resume.test_upload_resume_extraction_failure_parsing()
    test_resume.test_list_resumes()
    
    test_job = TestJobAnalysisWorkflow()
    test_job.setup()
    test_job.test_create_job_description()
    test_job.test_create_job_extraction_failure()
    test_job.test_list_jobs()
    
    test_discovery = TestDiscovery()
    test_discovery.setup()
    test_discovery.test_browse_jobs()
    test_discovery.test_search_jobs()
    
    test_analyses = TestAnalyses()
    test_analyses.setup()
    test_analyses.test_list_analyses()
    
    print("\n" + "="*60)
    print("ALL INTEGRATION TESTS PASSED ✅")
    print("="*60 + "\n")

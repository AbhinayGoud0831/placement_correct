"""
Test that API endpoints properly handle and return LLM extraction errors to clients.
"""
import sys
sys.path.insert(0, '.')

from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tempfile
import os

from app.main import app
from app.database import Base, get_db

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
TEST_EMAIL = "apitest@test.com"
TEST_PASSWORD = "TestPass123!"


def setup_auth():
    """Register and login a test student."""
    client.post(
        "/api/auth/register",
        json={
            "full_name": "API Test Student",
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
        },
    )
    response = client.post(
        "/api/auth/login",
        data={"username": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_resume_upload_returns_503_on_ollama_failure():
    """Test that resume upload returns 503 when Ollama is unreachable."""
    headers = setup_auth()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
        f.write("Test resume")
        temp_file = f.name
    
    try:
        with patch('app.routers.resumes.extract_text') as mock_text:
            mock_text.return_value = "Test content"
            
            with patch('app.routers.resumes.extract_resume_data') as mock_llm:
                mock_llm.side_effect = RuntimeError(
                    "Failed to connect to Ollama at http://localhost:11434. Is it running?"
                )
                
                with open(temp_file, 'rb') as f:
                    response = client.post(
                        "/api/resumes/upload",
                        files={"file": ("test.pdf", f, "application/pdf")},
                        headers=headers,
                    )
        
        assert response.status_code == 503, f"Expected 503, got {response.status_code}"
        assert "AI extraction service unavailable" in response.json()["detail"]
        print("✅ API: Resume upload returns 503 on Ollama connection failure")
    finally:
        os.unlink(temp_file)


def test_resume_upload_returns_422_on_parse_failure():
    """Test that resume upload returns 422 when LLM response cannot be parsed."""
    headers = setup_auth()
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
        f.write("Test resume")
        temp_file = f.name
    
    try:
        with patch('app.routers.resumes.extract_text') as mock_text:
            mock_text.return_value = "Test content"
            
            with patch('app.routers.resumes.extract_resume_data') as mock_llm:
                mock_llm.side_effect = ValueError("Could not parse response as JSON")
                
                with open(temp_file, 'rb') as f:
                    response = client.post(
                        "/api/resumes/upload",
                        files={"file": ("test.pdf", f, "application/pdf")},
                        headers=headers,
                    )
        
        assert response.status_code == 422, f"Expected 422, got {response.status_code}"
        assert "Failed to extract resume data" in response.json()["detail"]
        print("✅ API: Resume upload returns 422 on JSON parsing failure")
    finally:
        os.unlink(temp_file)


def test_job_creation_returns_503_on_ollama_failure():
    """Test that job creation returns 503 when Ollama is unreachable."""
    headers = setup_auth()
    
    with patch('app.routers.jobs.extract_job_data') as mock_llm:
        mock_llm.side_effect = RuntimeError(
            "Failed to connect to Ollama at http://localhost:11434"
        )
        
        response = client.post(
            "/api/jobs",
            json={
                "title": "Test Job",
                "raw_text": "Job description here...",
            },
            headers=headers,
        )
    
    assert response.status_code == 503, f"Expected 503, got {response.status_code}"
    assert "AI extraction service unavailable" in response.json()["detail"]
    print("✅ API: Job creation returns 503 on Ollama connection failure")


def test_job_creation_returns_422_on_parse_failure():
    """Test that job creation returns 422 when LLM response cannot be parsed."""
    headers = setup_auth()
    
    with patch('app.routers.jobs.extract_job_data') as mock_llm:
        mock_llm.side_effect = ValueError("Could not parse response as JSON")
        
        response = client.post(
            "/api/jobs",
            json={
                "title": "Test Job",
                "raw_text": "Job description here...",
            },
            headers=headers,
        )
    
    assert response.status_code == 422, f"Expected 422, got {response.status_code}"
    assert "Failed to extract job description data" in response.json()["detail"]
    print("✅ API: Job creation returns 422 on JSON parsing failure")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("TESTING API ERROR RESPONSES")
    print("="*70 + "\n")
    
    test_resume_upload_returns_503_on_ollama_failure()
    test_resume_upload_returns_422_on_parse_failure()
    test_job_creation_returns_503_on_ollama_failure()
    test_job_creation_returns_422_on_parse_failure()
    
    print("\n" + "="*70)
    print("ALL API ERROR RESPONSE TESTS PASSED ✅")
    print("="*70 + "\n")

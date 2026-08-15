"""
Test error handling for LLM extraction failures.
Verifies that exceptions are properly propagated instead of silent failures.
"""
import sys
sys.path.insert(0, '.')

from app.services.llm_extraction import extract_resume_data, extract_job_data
from unittest.mock import patch, MagicMock
import requests


def test_resume_extraction_ollama_connection_failure():
    """Test that Ollama connection errors are propagated."""
    with patch('app.services.llm_extraction._call_ollama') as mock_call:
        mock_call.side_effect = requests.ConnectionError("Connection refused")
        
        try:
            extract_resume_data("Test resume text")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Failed to connect to Ollama" in str(e)
            assert "localhost:11434" in str(e)
            print("✅ Resume extraction: Ollama connection error properly propagated")


def test_resume_extraction_json_parsing_failure():
    """Test that JSON parsing errors are propagated."""
    with patch('app.services.llm_extraction._call_ollama') as mock_call:
        mock_call.return_value = "This is not valid JSON {broken"
        
        try:
            extract_resume_data("Test resume text")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Could not parse Ollama response as JSON" in str(e)
            print("✅ Resume extraction: JSON parsing error properly propagated")


def test_job_extraction_ollama_connection_failure():
    """Test that Ollama connection errors are propagated for jobs."""
    with patch('app.services.llm_extraction._call_ollama') as mock_call:
        mock_call.side_effect = requests.ConnectionError("Connection refused")
        
        try:
            extract_job_data("Test job description")
            assert False, "Should have raised RuntimeError"
        except RuntimeError as e:
            assert "Failed to connect to Ollama" in str(e)
            print("✅ Job extraction: Ollama connection error properly propagated")


def test_job_extraction_json_parsing_failure():
    """Test that JSON parsing errors are propagated for jobs."""
    with patch('app.services.llm_extraction._call_ollama') as mock_call:
        mock_call.return_value = "Not JSON {invalid:"
        
        try:
            extract_job_data("Test job description")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "Could not parse Ollama response as JSON" in str(e)
            print("✅ Job extraction: JSON parsing error properly propagated")


def test_resume_extraction_success():
    """Test that successful extraction still works."""
    with patch('app.services.llm_extraction._call_ollama') as mock_call:
        mock_call.return_value = """{
            "skills": ["Python", "Django"],
            "education": [{"degree": "B.Tech", "institution": "Test"}],
            "experience": [{"role": "Dev", "company": "TestCorp", "duration": "2 years"}],
            "projects": []
        }"""
        
        result = extract_resume_data("Test resume text")
        assert result["skills"] == ["Python", "Django"]
        assert result["education"][0]["degree"] == "B.Tech"
        print("✅ Resume extraction: Success case works correctly")


def test_job_extraction_success():
    """Test that successful job extraction still works."""
    with patch('app.services.llm_extraction._call_ollama') as mock_call:
        mock_call.return_value = """{
            "required_skills": ["Python", "PostgreSQL"],
            "preferred_skills": ["Docker"],
            "qualifications": ["Bachelor's"],
            "min_experience_years": 3,
            "responsibilities": ["Build APIs"]
        }"""
        
        result = extract_job_data("Test job description")
        assert result["required_skills"] == ["Python", "PostgreSQL"]
        assert result["min_experience_years"] == 3
        print("✅ Job extraction: Success case works correctly")


def test_secret_key_validation():
    """Test that SECRET_KEY is required from environment."""
    import os
    import subprocess
    
    # Try to import config without SECRET_KEY set
    env = os.environ.copy()
    env.pop('SECRET_KEY', None)  # Remove if exists
    
    result = subprocess.run(
        [sys.executable, '-c', 'from app.config import settings'],
        cwd='.',
        capture_output=True,
        text=True,
        env=env,
    )
    
    assert result.returncode != 0, "Should fail if SECRET_KEY not set"
    assert "SECRET_KEY must be set" in result.stderr
    print("✅ Config: SECRET_KEY validation works (fails without env var)")


if __name__ == "__main__":
    print("\n" + "="*70)
    print("RUNNING ERROR HANDLING TESTS")
    print("="*70 + "\n")
    
    test_resume_extraction_ollama_connection_failure()
    test_resume_extraction_json_parsing_failure()
    test_job_extraction_ollama_connection_failure()
    test_job_extraction_json_parsing_failure()
    test_resume_extraction_success()
    test_job_extraction_success()
    test_secret_key_validation()
    
    print("\n" + "="*70)
    print("ALL ERROR HANDLING TESTS PASSED ✅")
    print("="*70 + "\n")

"""
Uses a local Ollama server running Qwen2.5 to turn free-form resume / job
description text into structured JSON. Requires `ollama serve` running
locally and the model pulled: `ollama pull qwen2.5`.
"""
import json
import re
import requests

from app.config import settings

RESUME_PROMPT = """You are an information-extraction engine. Read the resume text
below and return ONLY a JSON object (no markdown, no commentary) with this shape:

{{
  "skills": ["skill1", "skill2", ...],
  "education": [{{"degree": "...", "institution": "...", "year": "..."}}],
  "experience": [{{"role": "...", "company": "...", "duration": "...", "description": "..."}}],
  "projects": [{{"name": "...", "description": "...", "technologies": ["..."]}}]
}}

Resume text:
---
{text}
---
JSON:"""

JD_PROMPT = """You are an information-extraction engine. Read the job description
below and return ONLY a JSON object (no markdown, no commentary) with this shape:

{{
  "required_skills": ["skill1", "skill2", ...],
  "preferred_skills": ["skill1", ...],
  "qualifications": ["..."],
  "min_experience_years": 0,
  "responsibilities": ["..."]
}}

Job description text:
---
{text}
---
JSON:"""


def _call_ollama(prompt: str) -> str:
    response = requests.post(
        f"{settings.OLLAMA_HOST}/api/generate",
        json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    return response.json().get("response", "")


def _extract_json(raw: str) -> dict:
    """Qwen sometimes wraps JSON in markdown fences; strip and parse defensively."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^```json\s*|^```\s*|```$", "", cleaned, flags=re.MULTILINE).strip()
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM response")
    return json.loads(match.group(0))


def extract_resume_data(resume_text: str) -> dict:
    """Extract structured resume data using Ollama.
    
    Raises:
        requests.RequestException: If Ollama is unreachable
        ValueError: If Ollama response cannot be parsed as JSON
    """
    try:
        raw = _call_ollama(RESUME_PROMPT.format(text=resume_text[:12000]))
        return _extract_json(raw)
    except requests.RequestException as e:
        raise RuntimeError(
            f"Failed to connect to Ollama at {settings.OLLAMA_HOST}. "
            f"Is it running? Error: {str(e)}"
        ) from e
    except (ValueError, json.JSONDecodeError) as e:
        raise ValueError(
            f"Could not parse Ollama response as JSON. "
            f"Resume extraction failed. Please try again or check Ollama logs. "
            f"Error: {str(e)}"
        ) from e


def extract_job_data(job_text: str) -> dict:
    """Extract structured job description data using Ollama.
    
    Raises:
        requests.RequestException: If Ollama is unreachable
        ValueError: If Ollama response cannot be parsed as JSON
    """
    try:
        raw = _call_ollama(JD_PROMPT.format(text=job_text[:12000]))
        return _extract_json(raw)
    except requests.RequestException as e:
        raise RuntimeError(
            f"Failed to connect to Ollama at {settings.OLLAMA_HOST}. "
            f"Is it running? Error: {str(e)}"
        ) from e
    except (ValueError, json.JSONDecodeError) as e:
        raise ValueError(
            f"Could not parse Ollama response as JSON. "
            f"Job extraction failed. Please try again or check Ollama logs. "
            f"Error: {str(e)}"
        ) from e

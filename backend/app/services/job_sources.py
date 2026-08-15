"""External job-source integration with a deterministic fallback catalog.

The application never scrapes protected job boards. It consumes public APIs and
keeps the source URL so students can apply on the original listing.
"""
import html
import re
from typing import Any

import requests

from app.config import settings

SKILL_VOCAB = [
    "python", "java", "javascript", "typescript", "react", "node.js", "node", "django",
    "fastapi", "flask", "sql", "postgresql", "mysql", "mongodb", "docker", "kubernetes",
    "aws", "azure", "gcp", "git", "linux", "rest", "graphql", "pytorch", "tensorflow",
    "scikit-learn", "machine learning", "deep learning", "nlp", "computer vision", "pandas",
    "numpy", "spark", "airflow", "tableau", "power bi", "html", "css", "figma", "c++",
    "c#", ".net", "spring", "spring boot", "redis", "kafka", "terraform", "jenkins",
]


def _clean_html(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    return re.sub(r"\s+", " ", html.unescape(value)).strip()


def _extract_skills(text: str) -> list[str]:
    lowered = text.lower()
    found = []
    for skill in SKILL_VOCAB:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, lowered):
            found.append(skill)
    return found


def _extract_years(text: str) -> int:
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", text.lower())
    return int(max((float(x) for x in matches), default=0))


def normalize_job(raw: dict[str, Any], source: str) -> dict[str, Any] | None:
    """Normalize a public job API item into our SampleJob representation."""
    title = raw.get("title") or raw.get("position")
    company = raw.get("company_name") or raw.get("company") or raw.get("companyName")
    description = raw.get("description") or raw.get("job_description") or raw.get("description_text")
    url = raw.get("url") or raw.get("job_url") or raw.get("apply_url")
    if not title or not company or not description or not url:
        return None

    description = _clean_html(description)
    text = f"{title} {description}"
    years = _extract_years(text)
    skills = _extract_skills(text)
    level = "entry" if years <= 1 else "mid" if years <= 3 else "senior"
    remote = bool(raw.get("remote", True))
    location = raw.get("candidate_required_location") or raw.get("location") or "Remote"

    external_id = str(raw.get("id") or url)
    return {
        "external_id": external_id,
        "source": source,
        "title": str(title)[:255],
        "company": str(company)[:255],
        "level": level,
        "description": description[:12000],
        "url": str(url),
        "location": str(location)[:255],
        "employment_type": str(raw.get("job_type") or raw.get("employment_type") or "")[:80] or None,
        "remote": remote,
        "extracted_data": {
            "required_skills": skills,
            "preferred_skills": [],
            "qualifications": [],
            "min_experience_years": years,
            "responsibilities": [description[:2000]],
        },
    }


def fetch_remotive(search: str = "", limit: int = 50) -> list[dict[str, Any]]:
    params = {"limit": min(limit, 100)}
    if search.strip():
        params["search"] = search.strip()
    response = requests.get(settings.REMOTIVE_API_URL, params=params, timeout=settings.JOB_SOURCE_TIMEOUT)
    response.raise_for_status()
    jobs = response.json().get("jobs", [])
    return [j for j in (normalize_job(item, "Remotive") for item in jobs) if j]


def fetch_arbeitnow(search: str = "", limit: int = 50) -> list[dict[str, Any]]:
    response = requests.get(settings.ARBEITNOW_API_URL, timeout=settings.JOB_SOURCE_TIMEOUT)
    response.raise_for_status()
    jobs = response.json().get("data", [])
    if search.strip():
        needle = search.lower()
        jobs = [j for j in jobs if needle in f"{j.get('title','')} {j.get('company_name','')} {j.get('description','')}".lower()]
    return [j for j in (normalize_job(item, "Arbeitnow") for item in jobs[:limit]) if j]


def fetch_live_jobs(search: str = "", limit: int = 50) -> tuple[list[dict[str, Any]], list[str]]:
    """Fetch from both public sources; one source failing must not break discovery."""
    jobs: list[dict[str, Any]] = []
    errors: list[str] = []
    for name, loader in (("Remotive", fetch_remotive), ("Arbeitnow", fetch_arbeitnow)):
        try:
            jobs.extend(loader(search, limit))
        except Exception as exc:
            errors.append(f"{name}: {exc.__class__.__name__}")
    # De-duplicate by source + external id and cap the result.
    unique = {}
    for job in jobs:
        unique[(job["source"], job["external_id"])] = job
    return list(unique.values())[:limit], errors

"""
Semantic matching + weighted scoring with robust experience extraction.
"""
from functools import lru_cache
from typing import List, Tuple
import re

from sentence_transformers import SentenceTransformer, util

from app.config import settings


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    return SentenceTransformer(settings.EMBEDDING_MODEL)


def _semantic_similarity(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    model = get_model()
    emb = model.encode([a, b], convert_to_tensor=True)
    score = util.cos_sim(emb[0], emb[1]).item()
    return max(0.0, min(1.0, (score + 1) / 2))


def extract_years_of_experience(resume_data: dict) -> float:
    """
    Extract total years of experience from resume with robust heuristics.
    
    1. Look for explicit "X years" in duration field
    2. Parse date ranges (e.g., "2020-2023" or "Jan 2020 - Dec 2023")
    3. Fall back to counting roles (1 year each) if no explicit data
    """
    experience = resume_data.get("experience", [])
    if not experience:
        return 0.0

    total_years = 0.0
    
    for exp in experience:
        duration = exp.get("duration", "")
        if not duration:
            # No explicit duration; skip instead of defaulting to 1 year
            continue
        
        # Pattern 1: "X years" or "X yrs"
        match = re.search(r"(\d+)\s*(?:years?|yrs?)", str(duration), re.IGNORECASE)
        if match:
            total_years += float(match.group(1))
            continue
        
        # Pattern 2: "2020 - 2024" or "2020-2024"
        match = re.search(r"(\d{4})\s*[-–]\s*(\d{4})", str(duration))
        if match:
            start_year = int(match.group(1))
            end_year = int(match.group(2))
            total_years += max(0, end_year - start_year)
            continue
        
        # Pattern 3: "Jan 2020 - Dec 2023" or similar
        months_years = re.findall(r"(\d{4})", str(duration))
        if len(months_years) >= 2:
            start_year = int(months_years[0])
            end_year = int(months_years[-1])
            total_years += max(0, end_year - start_year)
            continue

    return max(0.0, total_years)  # Ensure non-negative


def match_skills(resume_skills: List[str], required_skills: List[str]) -> Tuple[List[str], List[str], float]:
    """Semantic set matching: each required skill matched to closest resume skill."""
    if not required_skills:
        return [], [], 1.0

    model = get_model()
    resume_skills = resume_skills or []
    matching, missing = [], []

    if resume_skills:
        resume_emb = model.encode(resume_skills, convert_to_tensor=True)

    for req_skill in required_skills:
        if not resume_skills:
            missing.append(req_skill)
            continue
        req_emb = model.encode(req_skill, convert_to_tensor=True)
        sims = util.cos_sim(req_emb, resume_emb)[0]
        best_score = float(sims.max())
        if best_score >= 0.6:
            matching.append(req_skill)
        else:
            missing.append(req_skill)

    skills_score = len(matching) / len(required_skills) if required_skills else 0.0
    return matching, missing, skills_score


def score_experience(resume_experience: list, jd_data: dict) -> float:
    """
    Score based on semantic match + years of experience comparison.
    
    Semantic (60%): Compares role descriptions and responsibilities
    Years (40%): Compares resume years against min_experience_years requirement
    """
    # Semantic match on role descriptions
    exp_text = " ".join(
        f"{e.get('role', '')} {e.get('description', '')}" for e in (resume_experience or [])
    )
    responsibilities = " ".join(jd_data.get("responsibilities", []))
    semantic_score = _semantic_similarity(exp_text, responsibilities)

    # Years comparison
    resume_data = {"experience": resume_experience or []}
    resume_years = extract_years_of_experience(resume_data)
    required_years = jd_data.get("min_experience_years", 0)

    # Years scoring: full points if meets/exceeds, scale down otherwise
    if resume_years >= required_years:
        years_score = 1.0
    elif required_years > 0:
        years_score = max(0.0, resume_years / required_years)
    else:
        years_score = 0.5 if resume_years > 0 else 0.3  # Some credit for any experience

    # Weighted combination
    return round(semantic_score * 0.6 + years_score * 0.4, 2)


def score_education(resume_education: list, jd_data: dict) -> float:
    """Score education match using semantic similarity on qualifications."""
    edu_text = " ".join(
        f"{e.get('degree', '')} {e.get('institution', '')}" for e in (resume_education or [])
    )
    qual_text = " ".join(jd_data.get("qualifications", []))
    return _semantic_similarity(edu_text, qual_text)


def compute_fit_score(resume_data: dict, jd_data: dict) -> dict:
    """Compute weighted fit score: Skills 50%, Experience 30%, Education 20%."""
    required_skills = list(
        set((jd_data.get("required_skills") or []) + (jd_data.get("preferred_skills") or []))
    )
    matching, missing, skills_score = match_skills(resume_data.get("skills", []), required_skills)
    experience_score = score_experience(resume_data.get("experience", []), jd_data)
    education_score = score_education(resume_data.get("education", []), jd_data)

    fit_score = (
        skills_score * settings.WEIGHT_SKILLS
        + experience_score * settings.WEIGHT_EXPERIENCE
        + education_score * settings.WEIGHT_EDUCATION
    ) * 100

    return {
        "fit_score": round(fit_score, 2),
        "skills_score": round(skills_score * 100, 2),
        "experience_score": round(experience_score * 100, 2),
        "education_score": round(education_score * 100, 2),
        "matching_skills": matching,
        "missing_skills": missing,
    }

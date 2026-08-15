import json

from app.services.llm_extraction import _call_ollama, _extract_json

RECOMMENDATION_PROMPT = """You are a career coach AI. A student is missing these skills
for a job: {missing_skills}. The job requires: {required_skills}.

Return ONLY a JSON object:
{{
  "learning_plan": [
    {{"skill": "...", "suggestion": "...", "estimated_weeks": 0}}
  ],
  "priority_order": ["skill1", "skill2"]
}}
JSON:"""

INTERVIEW_PROMPT = """You are a technical interview coach. The job description is:
---
{job_text}
---
The candidate's resume summary is: {resume_summary}

Return ONLY a JSON object:
{{
  "technical_questions": ["...", "..."],
  "behavioral_questions": ["...", "..."],
  "topics_to_revise": ["...", "..."],
  "tips": ["...", "..."]
}}
JSON:"""


def generate_recommendations(missing_skills: list, required_skills: list) -> dict:
    if not missing_skills:
        return {"learning_plan": [], "priority_order": []}
    prompt = RECOMMENDATION_PROMPT.format(
        missing_skills=json.dumps(missing_skills), required_skills=json.dumps(required_skills)
    )
    raw = _call_ollama(prompt)
    try:
        return _extract_json(raw)
    except (ValueError, json.JSONDecodeError):
        return {"learning_plan": [], "priority_order": missing_skills, "_raw": raw}


def generate_interview_prep(job_text: str, resume_data: dict) -> dict:
    resume_summary = ", ".join(resume_data.get("skills", [])[:15])
    prompt = INTERVIEW_PROMPT.format(job_text=job_text[:6000], resume_summary=resume_summary)
    raw = _call_ollama(prompt)
    try:
        return _extract_json(raw)
    except (ValueError, json.JSONDecodeError):
        return {
            "technical_questions": [],
            "behavioral_questions": [],
            "topics_to_revise": [],
            "tips": [],
            "_raw": raw,
        }

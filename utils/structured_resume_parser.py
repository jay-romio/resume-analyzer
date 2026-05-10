"""
Structured resume parsing: extract profile fields from raw resume text.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from utils.resume_analyzer import ResumeAnalyzer


def parse_resume_text(text: str, analyzer: Optional[ResumeAnalyzer] = None) -> Dict[str, Any]:
    """
    Extract name, contact, summary, skills, education, experience, and qualifications.
    """
    ra = analyzer or ResumeAnalyzer()
    personal = ra.extract_personal_info(text)
    return {
        "name": personal.get("name") or "",
        "email": personal.get("email") or "",
        "phone": personal.get("phone") or "",
        "linkedin": personal.get("linkedin") or "",
        "github": personal.get("github") or "",
        "portfolio": personal.get("portfolio") or "",
        "summary": ra.extract_summary(text) or "",
        "skills": list(ra.extract_skills(text)),
        "education": ra.extract_education(text),
        "experience": ra.extract_experience(text),
        "qualifications": ra.extract_qualifications(text),
    }


def profile_from_analysis(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """Build a display profile dict from analyze_resume() output."""
    return {
        "name": analysis.get("name") or "",
        "email": analysis.get("email") or "",
        "phone": analysis.get("phone") or "",
        "linkedin": analysis.get("linkedin") or "",
        "github": analysis.get("github") or "",
        "portfolio": analysis.get("portfolio") or "",
        "summary": analysis.get("summary") or "",
        "skills": list(analysis.get("skills") or []),
        "education": list(analysis.get("education") or []),
        "experience": list(analysis.get("experience") or []),
        "qualifications": list(analysis.get("qualifications") or []),
    }

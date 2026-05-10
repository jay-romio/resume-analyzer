"""Generate interview questions from resume text using Gemini when API key is available."""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional


def generate_questions_from_resume(
    resume_text: str,
    role: str,
    num_questions: int = 6,
) -> List[Dict[str, Any]]:
    """
    Return extra tailored questions [{question, type, tips}, ...].
    Empty list if unavailable or on error.
    """
    if not resume_text or len(resume_text.strip()) < 80:
        return []
    key = os.getenv("GOOGLE_API_KEY")
    if not key:
        return []
    try:
        import google.generativeai as genai

        genai.configure(api_key=key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""You are an expert hiring manager. Target role: {role}.
Read the resume excerpt and output EXACTLY {num_questions} interview questions tailored to this candidate's experience.
Mix behavioral and technical. Return ONLY valid JSON array of objects with keys: "question" (string), "type" (string: behavioral|technical|situational), "tips" (short string).

Resume excerpt:
{resume_text[:12000]}
"""
        resp = model.generate_content(prompt)
        text = (resp.text or "").strip()
        m = re.search(r"\[[\s\S]*\]", text)
        if not m:
            return []
        data = json.loads(m.group(0))
        out = []
        for item in data[: num_questions]:
            if isinstance(item, dict) and item.get("question"):
                out.append(
                    {
                        "question": str(item["question"]).strip(),
                        "type": str(item.get("type", "behavioral")),
                        "tips": str(item.get("tips", "Answer clearly and cite examples.")),
                        "section": "Resume-tailored",
                    }
                )
        return out
    except Exception:
        return []

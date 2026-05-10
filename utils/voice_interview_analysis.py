"""Heuristic analysis of spoken interview answers: clarity, confidence, keyword relevance."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Set


HESITATION = (
    "um", "uh", "erm", "uhm", "like", "you know", "sort of", "kind of",
    "maybe", "perhaps", "i think", "i guess", "probably",
)

POSITIVE = (
    "achieved", "delivered", "improved", "led", "owned", "solved", "result",
    "impact", "success", "learned", "collaborated", "clearly", "confidently",
)

NEGATIVE_EMOTION = (
    "failed", "terrible", "worst", "hate", "awful", "panic", "scared",
)


def _word_tokens(text: str) -> List[str]:
    return re.findall(r"[A-Za-z][A-Za-z'\-]+", text.lower())


def analyze_spoken_answer(
    answer: str,
    question: str,
    keyword_pool: List[str],
) -> Dict[str, Any]:
    """
    Score clarity, confidence (linguistic proxy), keyword relevance vs question + resume keywords.
    """
    if not answer or not answer.strip():
        return {
            "clarity_score": 0,
            "confidence_score": 0,
            "keyword_relevance_score": 0,
            "overall_score": 0,
            "hesitation_hits": 0,
            "keyword_hits": [],
            "emotion_hint": "neutral",
            "tips": ["Provide a spoken answer to receive feedback."],
        }

    words = _word_tokens(answer)
    sentences = [s.strip() for s in re.split(r"[.!?]+", answer) if s.strip()]
    wc = len(words)

    # Clarity: sentence structure + length sweet spot
    avg_len = wc / max(len(sentences), 1)
    clarity = 55.0
    if 8 <= avg_len <= 22:
        clarity += 15
    elif avg_len > 35:
        clarity -= 15
    if wc < 15:
        clarity -= 20
    if wc > 180:
        clarity -= 10
    # Filler words
    text_low = answer.lower()
    hesitation_hits = sum(text_low.count(h) for h in HESITATION)
    clarity -= min(25, hesitation_hits * 3)
    clarity = max(0, min(100, clarity))

    # Confidence proxy: fewer hedges, more positive career language
    conf = 50.0
    conf += min(20, sum(10 for p in POSITIVE if p in text_low))
    conf -= min(25, hesitation_hits * 2)
    conf -= min(15, sum(5 for n in NEGATIVE_EMOTION if n in text_low))
    if re.search(r"\bi\s+(?:think|guess|believe)\b", text_low):
        conf -= 8
    conf = max(0, min(100, conf))

    # Keyword relevance
    pool: Set[str] = {k.lower().strip() for k in keyword_pool if k and len(k) > 1}
    qwords = {w for w in _word_tokens(question) if len(w) > 3}
    pool |= qwords
    hits = [w for w in words if w in pool]
    unique_hits = list(dict.fromkeys(hits))
    relevance = min(100, 30 + len(unique_hits) * 12)

    overall = round(clarity * 0.35 + conf * 0.35 + relevance * 0.3)

    emotion_hint = "neutral"
    if sum(text_low.count(p) for p in POSITIVE) >= 3:
        emotion_hint = "positive"
    if sum(text_low.count(n) for n in NEGATIVE_EMOTION) >= 2:
        emotion_hint = "negative"

    tips: List[str] = []
    if hesitation_hits > 4:
        tips.append("Reduce filler words (um, like) — pause briefly instead.")
    if wc < 30:
        tips.append("Elaborate with a concrete example (STAR: situation, task, action, result).")
    if len(unique_hits) < 3 and keyword_pool:
        tips.append("Weave in role-relevant keywords from your resume naturally.")
    if avg_len > 40:
        tips.append("Break long sentences into shorter ones for clearer delivery.")
    if not tips:
        tips.append("Solid answer — keep practicing with varied questions.")

    return {
        "clarity_score": round(clarity, 1),
        "confidence_score": round(conf, 1),
        "keyword_relevance_score": round(relevance, 1),
        "overall_score": overall,
        "hesitation_hits": hesitation_hits,
        "keyword_hits": unique_hits[:15],
        "emotion_hint": emotion_hint,
        "tips": tips[:5],
    }


def merge_with_coach_feedback(
    voice_metrics: Dict[str, Any],
    coach_feedback: Dict[str, Any],
) -> Dict[str, Any]:
    """Blend heuristic voice metrics with AIInterviewCoach criteria scores."""
    out = dict(coach_feedback)
    oa = coach_feedback.get("overall_score", 0)
    vo = voice_metrics.get("overall_score", 0)
    blended = round(oa * 0.65 + vo * 0.35)
    out["overall_score"] = min(100, max(0, blended))
    out["voice_metrics"] = voice_metrics
    out["criteria_scores"] = dict(out.get("criteria_scores") or {})
    out["criteria_scores"]["clarity"] = voice_metrics.get("clarity_score", oa)
    out["criteria_scores"]["confidence"] = voice_metrics.get("confidence_score", oa)
    if "keyword_relevance_score" in voice_metrics:
        out["criteria_scores"]["relevance"] = float(
            max(
                float(out["criteria_scores"].get("relevance", 0) or 0),
                float(voice_metrics["keyword_relevance_score"]) * 0.85,
            )
        )
    return out

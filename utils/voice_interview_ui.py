"""
Voice-Based Mock Interview — Streamlit UI (TTS, STT, controls, feedback, report).
"""
from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components

from utils.interview_coach import AIInterviewCoach
from utils.voice_interview_analysis import analyze_spoken_answer, merge_with_coach_feedback
from utils.voice_interview_resume import generate_questions_from_resume
from utils.voice_stt import transcribe_openai_whisper_optional, transcribe_with_google
from utils.voice_tts import list_voice_options, synthesize_interviewer_speech

try:
    from streamlit_extras.st_autorefresh import st_autorefresh

    _HAS_AUTOREFRESH = True
except ImportError:
    _HAS_AUTOREFRESH = False


def _waveform_html(active: bool) -> str:
    bars = "".join(
        f'<span class="bar" style="animation-delay:{i * 0.08}s"></span>' for i in range(12)
    )
    disp = "flex" if active else "none"
    return f"""
<style>
@keyframes barwave {{
  0%, 100% {{ height: 6px; opacity: 0.4; }}
  50% {{ height: 22px; opacity: 1; }}
}}
.voice-wave-wrap {{ display: {disp}; align-items: flex-end; gap: 4px; height: 28px; padding: 8px 0; }}
.voice-wave-wrap .bar {{
  width: 5px; background: linear-gradient(180deg,#4CAF50,#2196F3);
  border-radius: 2px; animation: barwave 0.9s ease-in-out infinite;
}}
</style>
<div class="voice-wave-wrap" id="wave">{bars}</div>
"""


def _live_speech_browser_html() -> None:
    """Chrome/Edge: live SpeechRecognition transcript (supplement to server STT)."""
    html = """
<div style="font-family:sans-serif;color:#eee;padding:8px;">
  <p style="margin:0 0 8px 0;font-size:13px;">Live caption (browser — Chrome/Edge). Allow mic. Paste into answer box if needed.</p>
  <div id="t" style="min-height:64px;background:#1e1e1e;border-radius:8px;padding:10px;font-size:14px;white-space:pre-wrap;"></div>
  <button type="button" id="b" style="margin-top:8px;padding:8px 12px;border-radius:6px;cursor:pointer;">Start / Stop listening</button>
</div>
<script>
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const out = document.getElementById('t');
const btn = document.getElementById('b');
let rec = null; let on = false;
if (!SpeechRecognition) {
  out.textContent = "Web Speech API not available in this browser.";
  btn.disabled = true;
} else {
  btn.onclick = () => {
    if (!on) {
      rec = new SpeechRecognition();
      rec.continuous = true; rec.interimResults = true; rec.lang = 'en-US';
      rec.onresult = (e) => {
        let txt = '';
        for (let i = e.resultIndex; i < e.results.length; i++)
          txt += e.results[i][0].transcript;
        out.textContent = txt;
      };
      rec.onerror = () => { out.textContent += '\\n[recognition paused]'; };
      rec.start(); on = true; btn.textContent = 'Stop listening';
    } else { rec && rec.stop(); on = false; btn.textContent = 'Start / Stop listening'; }
  };
}
</script>
"""
    components.html(html, height=220)


def _keyword_pool_from_session(skills: Dict[str, Any], role: str) -> List[str]:
    pool: List[str] = [role.lower()]
    if not skills:
        return pool
    for k in ("technical_skills", "soft_skills", "tools_software"):
        for s in skills.get(k) or []:
            if s:
                pool.append(str(s).lower())
    return pool


def _build_report_md(
    coach: AIInterviewCoach,
    role: str,
    extras: Dict[str, Any],
) -> str:
    lines = [
        "# Voice mock interview report",
        f"Generated: {datetime.now().isoformat()}",
        f"Role: {role}",
        "",
        "## Summary",
    ]
    summ = coach.get_session_summary()
    if "error" in summ:
        lines.append(str(summ))
    else:
        ss = summ.get("session_summary", {})
        lines.append(f"- Average score: {ss.get('average_score')}")
        lines.append(f"- Grade: {ss.get('grade')}")
        lines.append(f"- Questions completed: {ss.get('total_questions')}")
        lines.append("")
        lines.append("## Per-answer notes")
        for i, h in enumerate(coach.conversation_history):
            lines.append(f"### Q{i+1}")
            lines.append(f"**Q:** {h.get('question','')}")
            lines.append(f"**Your answer:** {h.get('answer','')}")
            fb = h.get("feedback") or {}
            vm = (fb.get("voice_metrics") or {})
            if vm:
                lines.append(
                    f"- Voice clarity: {vm.get('clarity_score')} | "
                    f"confidence: {vm.get('confidence_score')} | "
                    f"keywords: {vm.get('keyword_relevance_score')}"
                )
            lines.append("")
    lines.append("## Settings")
    lines.append(str(extras))
    return "\n".join(lines)


def render_voice_mock_interview() -> None:
    st.markdown("## 🎙️ Voice Mock Interview")
    st.caption(
        "Simulated interview with AI voice prompts, speech-to-text answers, and blended feedback. "
        "Use Chrome or Edge for best results. Allow microphone access when prompted."
    )

    if "voice_settings" not in st.session_state:
        st.session_state.voice_settings = {
            "voice_id": "female_us",
            "speech_speed": 1.0,
            "tone": 0.0,
            "answer_timer_sec": 120,
            "thinking_pause": 1.2,
        }

    if "voice_coach" not in st.session_state:
        st.session_state.voice_coach = AIInterviewCoach()
    if "voice_session_meta" not in st.session_state:
        st.session_state.voice_session_meta = None
    if "vi_phase" not in st.session_state:
        st.session_state.vi_phase = "main"
    if "vi_followup" not in st.session_state:
        st.session_state.vi_followup = ""
    if "vi_main_buf" not in st.session_state:
        st.session_state.vi_main_buf = ""
    if "voice_paused" not in st.session_state:
        st.session_state.voice_paused = False
    if "voice_last_mp3" not in st.session_state:
        st.session_state.voice_last_mp3 = None
    if "voice_last_question_text" not in st.session_state:
        st.session_state.voice_last_question_text = ""

    coach = st.session_state.voice_coach

    with st.expander("⚙️ Voice & interview settings", expanded=not st.session_state.voice_session_meta):
        opts = list_voice_options()
        voice_id = st.selectbox(
            "Interviewer voice",
            [o["id"] for o in opts],
            format_func=lambda x: next(o["label"] for o in opts if o["id"] == x),
            key="vi_voice",
        )
        c1, c2, c3 = st.columns(3)
        with c1:
            speech_speed = st.slider("Speech speed", 0.7, 1.4, 1.0, 0.05, key="vi_speed")
        with c2:
            tone = st.slider("Tone (pitch)", -1.0, 1.0, 0.0, 0.1, key="vi_tone")
        with c3:
            answer_timer_sec = st.number_input("Answer timer (seconds, 0 = off)", 0, 600, 120, key="vi_timer")

        thinking_pause = st.slider("Interviewer thinking pause (seconds)", 0.0, 3.0, 1.2, 0.1, key="vi_think")
        use_resume_ai = st.checkbox(
            "Tailor questions from resume (needs GOOGLE_API_KEY)",
            value=True,
            key="vi_resume_ai",
        )
    st.session_state.voice_settings = {
        "voice_id": st.session_state.get("vi_voice", "female_us"),
        "speech_speed": float(st.session_state.get("vi_speed", 1.0)),
        "tone": float(st.session_state.get("vi_tone", 0.0)),
        "answer_timer_sec": int(st.session_state.get("vi_timer", 120)),
        "thinking_pause": float(st.session_state.get("vi_think", 1.2)),
    }

    # --- Setup ---
    if not st.session_state.voice_session_meta:
        st.subheader("Start a session")
        r1, r2 = st.columns(2)
        with r1:
            role = st.selectbox(
                "Target role",
                [
                    "Software Engineer",
                    "Web Developer",
                    "Data Analyst",
                    "Product Manager",
                    "DevOps Engineer",
                ],
                key="vi_role",
            )
        with r2:
            resume_ctx = st.text_area(
                "Resume text (optional — improves questions)",
                value=st.session_state.get("voice_resume_text", "")
                or _default_resume_text(),
                height=120,
                key="vi_resume_ta",
            )

        if st.button("🚀 Start voice interview", type="primary", key="vi_start"):
            skills = st.session_state.get("resume_analysis", {}).get("extracted_skills") or {
                "technical_skills": ["Python", "SQL"],
                "soft_skills": ["Communication"],
                "tools_software": ["Git"],
            }
            meta = coach.start_interview_session(skills, role)
            use_ai = st.session_state.get("vi_resume_ai", True)
            if use_ai and resume_ctx and len(resume_ctx.strip()) > 80:
                extra = generate_questions_from_resume(resume_ctx, role, num_questions=5)
                for j, eq in enumerate(extra):
                    coach.interview_questions.insert(
                        1 + j,
                        {
                            "question": eq["question"],
                            "section": eq.get("section", "Resume-tailored"),
                            "type": eq.get("type", "behavioral"),
                            "tips": eq.get("tips", ""),
                            "duration_minutes": 2,
                        },
                    )
            st.session_state.voice_session_meta = meta
            st.session_state.voice_resume_text = resume_ctx
            st.session_state.vi_phase = "main"
            st.session_state.vi_followup = ""
            st.session_state.vi_main_buf = ""
            st.rerun()
        return

    # --- Active session ---
    meta = st.session_state.voice_session_meta
    st.success(
        f"Session: **{meta.get('role')}** — {meta.get('total_questions', 0)} questions · "
        f"~{meta.get('estimated_duration', 0)} min"
    )

    flash = st.session_state.get("vi_feedback_flash")
    if flash:
        with st.expander("📊 Latest feedback", expanded=True):
            _render_feedback_inner(flash.get("fb", {}), flash.get("vm", {}))
            if flash.get("note"):
                st.caption(flash["note"])
        if st.button("Dismiss feedback", key="vi_flash_dismiss"):
            st.session_state.vi_feedback_flash = None
            st.rerun()

    if _HAS_AUTOREFRESH and st.session_state.voice_settings.get("answer_timer_sec", 0) > 0:
        st_autorefresh(interval=1000, key="vi_timer_refresh")

    # Current question text
    if st.session_state.vi_phase == "followup" and st.session_state.vi_followup:
        qtext = st.session_state.vi_followup
        qobj: Optional[Dict[str, Any]] = None
        section = "Follow-up"
        tips = "Keep this answer short and specific."
    else:
        qobj = coach.get_current_question()
        if not qobj:
            st.balloons()
            st.success("Interview complete!")
            summary = coach.get_session_summary()
            if "error" not in summary:
                st.subheader("📈 Session summary")
                st.metric("Average score", summary["session_summary"]["average_score"])
                st.metric("Grade", summary["session_summary"]["grade"])
                cr = summary.get("criteria_performance", {})
                if cr:
                    st.bar_chart(cr)
            report = _build_report_md(
                coach,
                meta.get("role", ""),
                st.session_state.get("voice_settings", {}),
            )
            st.download_button(
                "Download interview report (.md)",
                data=report,
                file_name=f"voice_interview_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                mime="text/markdown",
            )
            if st.button("New session", key="vi_new"):
                st.session_state.voice_session_meta = None
                st.session_state.voice_coach = AIInterviewCoach()
                st.session_state.voice_last_mp3 = None
                st.rerun()
            return

        qtext = qobj["question"]
        section = qobj.get("section", "")
        tips = qobj.get("tips", "")

    st.markdown(
        f"""
<div style="background:#1a2332;padding:16px;border-radius:12px;border-left:4px solid #4CAF50;margin-bottom:12px;">
  <div style="color:#8bc34a;font-size:12px;text-transform:uppercase;">{section}</div>
  <div style="color:#fff;font-size:18px;font-weight:600;">{qtext}</div>
  {f'<div style="color:#aaa;margin-top:8px;font-size:14px;">💡 {tips}</div>' if tips else ''}
</div>
""",
        unsafe_allow_html=True,
    )

    ctrl1, ctrl2, ctrl3, ctrl4, ctrl5 = st.columns(5)
    with ctrl1:
        if st.button("⏸ Pause" if not st.session_state.voice_paused else "▶ Resume", key="vi_pause"):
            st.session_state.voice_paused = not st.session_state.voice_paused
            st.rerun()
    with ctrl2:
        if st.button("🔁 Replay question (TTS)", key="vi_replay"):
            st.session_state.voice_force_tts = True
            st.rerun()
    with ctrl3:
        if st.button("⏭ Skip question", key="vi_skip"):
            if st.session_state.vi_phase == "followup":
                coach.submit_answer(st.session_state.vi_main_buf)
                st.session_state.vi_phase = "main"
                st.session_state.vi_followup = ""
                st.session_state.vi_main_buf = ""
            else:
                coach.current_question_index += 1
            st.session_state.voice_last_mp3 = None
            st.rerun()
    with ctrl4:
        if st.button("🔂 Repeat question text", key="vi_repeat"):
            st.rerun()
    with ctrl5:
        if st.button("⏹ Stop session", key="vi_stop"):
            st.session_state.voice_session_meta = None
            st.session_state.voice_coach = AIInterviewCoach()
            st.session_state.voice_last_mp3 = None
            st.rerun()

    # TTS play
    settings = st.session_state.get("voice_settings", {})
    force = st.session_state.pop("voice_force_tts", False)
    same_q = st.session_state.voice_last_question_text == qtext
    if not st.session_state.voice_paused and (not same_q or force or not st.session_state.voice_last_mp3):
        with st.spinner("Interviewer is preparing audio…"):
            mp3 = synthesize_interviewer_speech(
                qtext,
                voice_id=settings.get("voice_id", "female_us"),
                speech_speed=float(settings.get("speech_speed", 1.0)),
                tone=float(settings.get("tone", 0.0)),
            )
            st.session_state.voice_last_mp3 = mp3
            st.session_state.voice_last_question_text = qtext
        if not same_q or force:
            tp = float(settings.get("thinking_pause", 1.0))
            if tp > 0:
                time.sleep(min(tp, 3.0))

    if st.session_state.voice_last_mp3:
        st.audio(st.session_state.voice_last_mp3, format="audio/mp3")

    st.markdown(_waveform_html(not st.session_state.voice_paused), unsafe_allow_html=True)

    # Timer
    tsec = int(settings.get("answer_timer_sec", 0) or 0)
    if "vi_answer_start" not in st.session_state:
        st.session_state.vi_answer_start = time.time()
    if tsec > 0:
        elapsed = int(time.time() - st.session_state.vi_answer_start)
        rem = max(0, tsec - elapsed)
        st.metric("Answer timer remaining", f"{rem}s")
        st.caption("Timer updates when you interact with the page (Streamlit limitation).")
        if rem <= 0:
            st.warning("Time is up — submit your answer when ready.")

    st.subheader("Your spoken answer")
    try:
        audio = st.audio_input("Record your answer", key="vi_audio")
    except Exception:
        audio = None
        st.warning(
            "Audio recording needs a recent Streamlit version. Type or paste your answer below."
        )

    c1, c2 = st.columns([2, 1])
    with c1:
        _live_speech_browser_html()
    with c2:
        st.caption("Server STT uses Google (or set OPENAI_API_KEY for Whisper).")

    manual = st.text_area(
        "Transcript (edit if needed)",
        height=120,
        key="vi_transcript",
        placeholder="Record audio above, or type / paste your answer here.",
    )

    if st.button("📝 Transcribe recording", key="vi_tr"):
        if audio:
            data = audio.getvalue()
            fn = getattr(audio, "name", "clip.wav") or "clip.wav"
            alt = transcribe_openai_whisper_optional(data)
            if alt:
                st.session_state.vi_transcript = alt
                st.success("Whisper transcription applied.")
            else:
                text, err = transcribe_with_google(data, fn)
                if text:
                    st.session_state.vi_transcript = text
                    st.success("Transcription applied.")
                else:
                    st.error(err or "Transcription failed.")
            st.rerun()
        else:
            st.warning("Record audio first.")

    transcript = (manual or "").strip()

    if st.button("✅ Submit answer", type="primary", key="vi_submit"):
        if not transcript:
            st.error("Provide a transcript or record your answer.")
            return

        skills = st.session_state.get("resume_analysis", {}).get("extracted_skills") or {}
        kpool = _keyword_pool_from_session(skills, meta.get("role", ""))

        if st.session_state.vi_phase == "followup":
            combined = (
                st.session_state.vi_main_buf + "\n\n(Follow-up response) " + transcript
            )
            result = coach.submit_answer(combined)
            fb = result.get("feedback") or {}
            cq = coach.interview_questions[max(0, coach.current_question_index - 1)]
            vm = analyze_spoken_answer(combined, cq.get("question", ""), kpool)
            fb2 = merge_with_coach_feedback(vm, fb)
            if coach.feedback_scores:
                coach.feedback_scores[-1] = fb2
            st.session_state.vi_phase = "main"
            st.session_state.vi_followup = ""
            st.session_state.vi_main_buf = ""
            st.session_state.vi_answer_start = time.time()
            st.session_state.voice_last_mp3 = None
            st.session_state.vi_feedback_flash = {"fb": fb2, "vm": vm, "note": None}
            st.rerun()
            return

        cq = coach.get_current_question()
        if not cq:
            return
        fb = coach._generate_feedback(transcript, cq)
        vm = analyze_spoken_answer(transcript, cq["question"], kpool)
        fb2 = merge_with_coach_feedback(vm, fb)

        if fb.get("follow_up_questions") and st.session_state.vi_phase == "main":
            st.session_state.vi_phase = "followup"
            st.session_state.vi_followup = fb["follow_up_questions"][0]
            st.session_state.vi_main_buf = transcript
            st.session_state.vi_answer_start = time.time()
            st.session_state.voice_last_mp3 = None
            st.session_state.vi_feedback_flash = {
                "fb": fb2,
                "vm": vm,
                "note": "Follow-up question loaded — answer it next.",
            }
            st.rerun()
            return

        result = coach.submit_answer(transcript)
        fb = result.get("feedback") or {}
        vm = analyze_spoken_answer(transcript, cq["question"], kpool)
        fb2 = merge_with_coach_feedback(vm, fb)
        if coach.feedback_scores:
            coach.feedback_scores[-1] = fb2
        st.session_state.vi_answer_start = time.time()
        st.session_state.voice_last_mp3 = None
        st.session_state.vi_feedback_flash = {"fb": fb2, "vm": vm, "note": None}
        st.rerun()


def _default_resume_text() -> str:
    ra = st.session_state.get("resume_analysis")
    if not ra:
        return ""
    parts = []
    if ra.get("summary"):
        parts.append(ra["summary"])
    if ra.get("skills"):
        parts.append("Skills: " + ", ".join(str(s) for s in ra["skills"][:40]))
    return "\n".join(parts)


def _render_feedback_inner(fb: Dict[str, Any], vm: Dict[str, Any]) -> None:
    st.markdown(
        f"**Overall:** {fb.get('overall_score', 0)}/100 | "
        f"Clarity: {vm.get('clarity_score')} | "
        f"Confidence: {vm.get('confidence_score')} | "
        f"Keywords: {vm.get('keyword_relevance_score')}"
    )
    if vm.get("emotion_hint") and vm.get("emotion_hint") != "neutral":
        st.caption(f"Tone hint (text-based): {vm['emotion_hint']}")
    if vm.get("keyword_hits"):
        st.caption("Keywords matched: " + ", ".join(vm["keyword_hits"][:12]))
    for t in vm.get("tips", []):
        st.write(f"• {t}")
    if fb.get("strengths"):
        st.write("**Strengths**")
        for s in fb["strengths"][:5]:
            st.write(f"✅ {s}")
    if fb.get("improvements"):
        st.write("**Improvements**")
        for i in fb["improvements"][:5]:
            st.write(f"⚠️ {i}")


def render_voice_interview_page() -> None:
    render_voice_mock_interview()

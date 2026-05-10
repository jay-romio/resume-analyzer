"""Speech-to-text from recorded audio (browser upload / streamlit audio_input)."""
from __future__ import annotations

import io
import os
import tempfile
import speech_recognition as sr
from typing import Optional, Tuple

# Tunable: pause length before phrase ends (seconds)
DEFAULT_PAUSE_THRESHOLD = 0.9
DEFAULT_ENERGY_THRESHOLD = 280


def _load_audio_segment(data: bytes, suffix: str = ".wav"):
    try:
        from pydub import AudioSegment
    except ImportError:
        raise RuntimeError("pydub not installed")

    buf = io.BytesIO(data)
    fmt = "wav" if suffix.lower().endswith(".wav") else suffix.lstrip(".")
    try:
        return AudioSegment.from_file(buf, format=fmt)
    except Exception:
        buf.seek(0)
        return AudioSegment.from_file(buf)


def _to_wav_bytes(data: bytes, suffix: str = ".wav") -> bytes:
    """Normalize various browser formats to WAV for SpeechRecognition."""
    try:
        seg = _load_audio_segment(data, suffix)
        seg = seg.set_channels(1).set_frame_rate(16000)
        out = io.BytesIO()
        seg.export(out, format="wav")
        return out.getvalue()
    except Exception:
        return data


def transcribe_with_google(audio_bytes: bytes, filename_hint: str = "clip.wav") -> Tuple[str, Optional[str]]:
    """
    Transcribe using Google Web Speech API via SpeechRecognition.
    Returns (text, error_message_if_any).
    """
    import speech_recognition as sr

    if not audio_bytes:
        return "", "No audio captured"

    wav = audio_bytes
    lower = filename_hint.lower()
    if not lower.endswith(".wav"):
        try:
            ext = os.path.splitext(filename_hint)[1] or ".webm"
            wav = _to_wav_bytes(audio_bytes, ext)
        except Exception:
            wav = audio_bytes

    r = sr.Recognizer()
    r.energy_threshold = DEFAULT_ENERGY_THRESHOLD
    r.dynamic_energy_threshold = True
    r.pause_threshold = DEFAULT_PAUSE_THRESHOLD
    r.non_speaking_duration = 0.5

    try:
        with sr.AudioFile(io.BytesIO(wav)) as source:
            r.adjust_for_ambient_noise(source, duration=0.3)
            audio = r.record(source)
        text = r.recognize_google(audio, language="en-US")
        return (text.strip(), None)
    except sr.UnknownValueError:
        return "", "Could not understand audio — try speaking more clearly or reduce background noise."
    except sr.RequestError as e:
        return "", f"Speech service error: {e}"
    except Exception as e:
        return "", f"Transcription failed: {e}"


def transcribe_openai_whisper_optional(audio_bytes: bytes) -> Optional[str]:
    """If OPENAI_API_KEY is set, use OpenAI Whisper API (good accuracy)."""
    key = os.getenv("OPENAI_API_KEY")
    if not key or not audio_bytes:
        return None
    try:
        import requests

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            path = tmp.name
        try:
            with open(path, "rb") as fh:
                r = requests.post(
                    "https://api.openai.com/v1/audio/transcriptions",
                    headers={"Authorization": f"Bearer {key}"},
                    files={"file": ("audio.wav", fh, "audio/wav")},
                    data={"model": "whisper-1"},
                    timeout=120,
                )
            r.raise_for_status()
            return r.json().get("text", "").strip()
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass
    except Exception:
        return None

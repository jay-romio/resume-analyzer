"""Text-to-speech for mock interviews using Microsoft Edge TTS (no API key)."""
from __future__ import annotations

import asyncio
import io
from typing import Dict, List, Optional

# Neural voices: natural, low latency via edge-tts
VOICE_PRESETS: Dict[str, str] = {
    "female_us": "en-US-JennyNeural",
    "male_us": "en-US-GuyNeural",
    "female_uk": "en-GB-SoniaNeural",
    "male_uk": "en-GB-RyanNeural",
    "female_in": "en-IN-NeerjaNeural",
    "male_in": "en-IN-PrabhatNeural",
    "female_es": "es-ES-ElviraNeural",
    "male_es": "es-ES-AlvaroNeural",
}


def list_voice_options() -> List[Dict[str, str]]:
    return [
        {"id": "female_us", "label": "Female — US English (Jenny)"},
        {"id": "male_us", "label": "Male — US English (Guy)"},
        {"id": "female_uk", "label": "Female — UK English (Sonia)"},
        {"id": "male_uk", "label": "Male — UK English (Ryan)"},
        {"id": "female_in", "label": "Female — English India (Neerja)"},
        {"id": "male_in", "label": "Male — English India (Prabhat)"},
        {"id": "female_es", "label": "Female — Spanish (Elvira)"},
        {"id": "male_es", "label": "Male — Spanish (Alvaro)"},
    ]


def _rate_percent(speed: float) -> str:
    """speed 0.5–2.0 -> Edge rate string e.g. +15% or -10%."""
    # Edge uses relative to default; map 1.0 -> +0%
    pct = int(round((speed - 1.0) * 100))
    if pct >= 0:
        return f"+{pct}%"
    return f"{pct}%"


def _pitch_hz(tone: float) -> str:
    """tone -1..1 -> pitch string."""
    hz = int(round(tone * 12))
    if hz >= 0:
        return f"+{hz}Hz"
    return f"{hz}Hz"


async def _synthesize_async(
    text: str,
    voice_id: str,
    rate: str,
    pitch: str,
) -> bytes:
    import edge_tts

    voice = VOICE_PRESETS.get(voice_id, VOICE_PRESETS["female_us"])
    communicate = edge_tts.Communicate(text.strip(), voice, rate=rate, pitch=pitch)
    out = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            out.extend(chunk["data"])
    return bytes(out)


def synthesize_interviewer_speech(
    text: str,
    voice_id: str = "female_us",
    speech_speed: float = 1.0,
    tone: float = 0.0,
) -> bytes:
    """
    Generate MP3 audio bytes for interviewer prompt.
    speech_speed: 0.5 (slow) to 2.0 (fast), default 1.0
    tone: -1.0 lower ... +1.0 higher
    """
    if not text.strip():
        return b""
    rate = _rate_percent(max(0.5, min(2.0, speech_speed)))
    pitch = _pitch_hz(max(-1.0, min(1.0, tone)))
    return asyncio.run(_synthesize_async(text, voice_id, rate, pitch))


def mp3_to_wav_bytes(mp3_bytes: bytes) -> Optional[bytes]:
    """Optional WAV conversion for players that prefer WAV (requires pydub + ffmpeg)."""
    try:
        from pydub import AudioSegment

        seg = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
        buf = io.BytesIO()
        seg.export(buf, format="wav")
        return buf.getvalue()
    except Exception:
        return None

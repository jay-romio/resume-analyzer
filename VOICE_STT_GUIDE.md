# 🎤 Voice STT Interface - Complete Usage Guide

## 📋 Overview

The `voice_stt.py` module provides **Speech-to-Text (STT)** functionality with two transcription methods:
- **Google Speech API** (Free, built-in)
- **OpenAI Whisper API** (Requires API key, higher accuracy)

## 🔧 Installation & Setup

### 1. Install Dependencies
```bash
pip install SpeechRecognition pydub openai
```

### 2. Optional: Set OpenAI API Key
```python
import os
os.environ["OPENAI_API_KEY"] = "your-openai-api-key-here"
```

## 🚀 Quick Start

### Basic Usage
```python
from utils.voice_stt import transcribe_with_google, transcribe_openai_whisper_optional

# Get audio bytes (from file, microphone, etc.)
audio_bytes = get_your_audio_data()

# Method 1: Google Speech API (Free)
text, error = transcribe_with_google(audio_bytes, "audio.wav")
if error:
    print(f"Error: {error}")
else:
    print(f"Transcription: {text}")

# Method 2: OpenAI Whisper (Higher accuracy)
text = transcribe_openai_whisper_optional(audio_bytes)
if text:
    print(f"Whisper transcription: {text}")
```

## 🎯 Integration with Resume Analyzer

The voice STT is already integrated into the **Voice Interview Coach** feature. Here's how to access it:

### Method 1: Through Main Application
1. Run the main application:
   ```bash
   streamlit run app.py
   ```
2. Navigate to **"🎤 INTERVIEW COACH"** in the sidebar
3. The voice interface is automatically available

### Method 2: Standalone Voice Interview
```python
from utils.voice_interview_ui import render_voice_interview_page

# In your Streamlit app
st.sidebar.button("Voice Interview", on_click=render_voice_interview_page)
```

## 🎙️ Audio Input Methods

### 1. File Upload
```python
import streamlit as st
from utils.voice_stt import transcribe_with_google

uploaded_file = st.file_uploader(
    "Upload audio",
    type=['wav', 'mp3', 'webm', 'm4a', 'ogg']
)

if uploaded_file:
    audio_bytes = uploaded_file.getvalue()
    text, error = transcribe_with_google(audio_bytes, uploaded_file.name)
    
    if not error:
        st.success(f"Transcription: {text}")
    else:
        st.error(f"Error: {error}")
```

### 2. Microphone Recording
```python
# Streamlit audio input (requires recent Streamlit version)
audio_data = st.audio_input("Record your answer")

if audio_data:
    audio_bytes = audio_data.getvalue()
    text, error = transcribe_with_google(audio_bytes, "recording.wav")
    
    st.text_area("Transcription:", text or error)
```

## 🔧 Advanced Configuration

### Custom Thresholds
```python
from utils.voice_stt import DEFAULT_PAUSE_THRESHOLD, DEFAULT_ENERGY_THRESHOLD

# You can modify these in the module or pass custom values
# Energy threshold: Lower = more sensitive, Higher = less sensitive
# Pause threshold: Shorter = faster response, Longer = avoids false triggers

# Custom transcription with adjusted parameters
import speech_recognition as sr

r = sr.Recognizer()
r.energy_threshold = 200  # Custom energy threshold
r.pause_threshold = 0.8   # Custom pause threshold
r.dynamic_energy_threshold = True
```

### Audio Format Support
The module automatically converts between formats:
- **Input**: WAV, MP3, WebM, M4A, OGG
- **Processing**: Converts to WAV (16kHz, mono)
- **Best quality**: WAV → WAV (no conversion needed)

## 🎤 Interview Coach Integration

The voice STT is fully integrated into the interview coach system:

### Features Available:
1. **Voice Settings**
   - Voice selection (male/female, different accents)
   - Speech speed control
   - Tone/pitch adjustment
   - Answer timer

2. **Real-time Transcription**
   - Live microphone input
   - Google Speech API (free)
   - OpenAI Whisper (premium)
   - Manual text fallback

3. **Interview Flow**
   - AI-generated questions
   - Voice answers with transcription
   - Real-time feedback
   - Follow-up questions
   - Performance scoring

4. **Session Management**
   - Start/stop controls
   - Pause/resume functionality
   - Question replay (TTS)
   - Progress tracking
   - Report generation

### Accessing Voice Interview:
1. **In the main app**: Click "🎤 INTERVIEW COACH" in sidebar
2. **Configure settings**: Expand "⚙️ Voice & interview settings"
3. **Start session**: Select role and click "🚀 Start voice interview"
4. **Answer questions**: 
   - Listen to AI question
   - Record your answer
   - Click "📝 Transcribe recording"
   - Review transcription
   - Submit answer

## 📊 Performance Considerations

### Google Speech API
- **Speed**: ~2-5 seconds per audio clip
- **Accuracy**: Good for clear speech
- **Cost**: Free
- **Limits**: Standard API quotas apply
- **Best for**: Real-time applications, quick responses

### OpenAI Whisper
- **Speed**: ~10-30 seconds per audio clip
- **Accuracy**: Excellent, handles noise well
- **Cost**: ~$0.006 per minute of audio
- **Best for**: High-accuracy requirements, noisy environments

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### 1. "Could not understand audio"
**Cause**: Background noise, unclear speech
**Solution**: 
- Speak clearly and closer to microphone
- Reduce background noise
- Use higher quality audio format (WAV)

#### 2. "Speech service error"
**Cause**: Network issues, API limits
**Solution**:
- Check internet connection
- Try shorter audio clips
- Use OpenAI Whisper as fallback

#### 3. Module import errors
**Cause**: Missing dependencies
**Solution**:
```bash
pip install SpeechRecognition pydub openai
```

#### 4. Audio format issues
**Cause**: Unsupported format
**Solution**:
- Use WAV format when possible
- Convert audio to standard format first
- Check file integrity

## 🎯 Best Practices

### For Interview Scenarios
1. **Answer Length**: 45-90 seconds per response
2. **Audio Quality**: Use quiet environment
3. **Microphone Position**: 6-12 inches from mouth
4. **Speech Rate**: Moderate, clear pace
5. **Content**: Direct answers to questions asked

### For Technical Integration
1. **Error Handling**: Always check return tuples `(text, error)`
2. **Fallback**: Use Google as primary, Whisper as backup
3. **User Feedback**: Show transcriptions for user editing
4. **Performance**: Cache results when possible

## 📱 Browser Compatibility

### Supported Browsers for Microphone Input
- ✅ **Chrome**: Full support
- ✅ **Edge**: Full support  
- ✅ **Firefox**: Limited support
- ❌ **Safari**: Limited support
- ⚠️ **Mobile**: Varies by device

### Alternative Input Methods
1. **File Upload**: Works in all browsers
2. **Text Input**: Always available as fallback
3. **Copy-Paste**: For manual transcription corrections

## 🔗 Example Applications

### 1. Voice Resume Analysis
```python
def analyze_voice_resume():
    st.title("Voice Resume Analysis")
    
    # Upload audio resume
    audio_file = st.file_uploader("Upload spoken resume", type=['wav'])
    
    if audio_file:
        text, error = transcribe_with_google(audio_file.getvalue())
        
        if not error:
            # Process transcribed text with resume analyzer
            analysis = analyze_resume_text(text)
            st.write(analysis)
```

### 2. Language Learning Practice
```python
def language_practice():
    st.title("Voice Language Practice")
    
    target_language = st.selectbox("Language", ["en-US", "es-ES", "fr-FR"])
    
    audio_input = st.audio_input(f"Practice in {target_language}")
    
    if audio_input:
        text, error = transcribe_with_google(
            audio_input.getvalue(), 
            target_language
        )
        
        st.text_area("Your pronunciation:", text)
```

### 3. Meeting Transcription
```python
def meeting_transcriber():
    st.title("Meeting Transcriber")
    
    if st.button("Start Transcription"):
        # Continuous transcription loop
        while True:
            audio = record_audio_segment(duration=30)  # 30-second chunks
            text, error = transcribe_with_google(audio)
            
            if text:
                st.write(f"[{datetime.now()}] {text}")
```

## 🚀 Getting Started

1. **Run the demo**:
   ```bash
   streamlit run voice_stt_example.py
   ```

2. **Access in main app**:
   - Start: `streamlit run app.py`
   - Navigate to: "🎤 INTERVIEW COACH"
   - Configure settings and start session

3. **Integrate into your code**:
   ```python
   from utils.voice_stt import transcribe_with_google, transcribe_openai_whisper_optional
   ```

The voice STT interface is now ready for use! 🎉

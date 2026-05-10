"""
Example Usage of voice_stt.py Interface
Demonstrates how to use the Speech-to-Text functionality
"""
import os
import streamlit as st
import speech_recognition as sr
from utils.voice_stt import transcribe_with_google, transcribe_openai_whisper_optional

def main():
    st.title("🎤 Voice STT Interface Demo")
    st.write("This demo shows how to use the voice_stt.py module")
    
    # API Key Configuration
    st.sidebar.header("⚙️ Configuration")
    
    # OpenAI API Key (optional, for Whisper)
    openai_key = st.sidebar.text_input(
        "OpenAI API Key (for Whisper)",
        type="password",
        help="Optional: If provided, uses OpenAI Whisper for higher accuracy"
    )
    
    if openai_key:
        os.environ["OPENAI_API_KEY"] = st.sidebar.success("✅ OpenAI API Key set")
    
    st.sidebar.markdown("---")
    
    # Audio Input Methods
    st.header("🎙️ Audio Input Methods")
    
    method = st.radio(
        "Choose Input Method:",
        ["Upload Audio File", "Use Microphone"],
        help="Select how you want to provide audio input"
    )
    
    if method == "Upload Audio File":
        # File Upload Method
        st.subheader("📁 Upload Audio File")
        
        uploaded_file = st.file_uploader(
            "Upload audio file",
            type=['wav', 'mp3', 'webm', 'm4a', 'ogg'],
            help="Supported formats: WAV, MP3, WebM, M4A, OGG"
        )
        
        if uploaded_file is not None:
            st.audio(uploaded_file, format="audio/wav")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔍 Transcribe with Google", type="primary"):
                    with st.spinner("Transcribing with Google Speech API..."):
                        audio_bytes = uploaded_file.getvalue()
                        text, error = transcribe_with_google(audio_bytes, uploaded_file.name)
                        
                        if error:
                            st.error(f"❌ Error: {error}")
                        else:
                            st.success("✅ Transcription successful!")
                            st.text_area("Transcription:", text, height=200)
            
            with col2:
                if openai_key and st.button("🧠 Transcribe with Whisper (OpenAI)", type="primary"):
                    with st.spinner("Transcribing with OpenAI Whisper..."):
                        audio_bytes = uploaded_file.getvalue()
                        text = transcribe_openai_whisper_optional(audio_bytes)
                        
                        if text:
                            st.success("✅ Whisper transcription successful!")
                            st.text_area("Transcription:", text, height=200)
                        else:
                            st.error("❌ Whisper transcription failed")
    
    else:
        # Microphone Method (using Streamlit's audio_input)
        st.subheader("🎤 Record with Microphone")
        st.write("Click the microphone button below to record your answer:")
        
        audio_data = st.audio_input(
            "Record your voice",
            help="Click to start recording, click again to stop"
        )
        
        if audio_data is not None:
            st.audio(audio_data, format="audio/wav")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔍 Transcribe with Google", type="primary"):
                    with st.spinner("Transcribing with Google Speech API..."):
                        audio_bytes = audio_data.getvalue()
                        text, error = transcribe_with_google(audio_bytes, "recording.wav")
                        
                        if error:
                            st.error(f"❌ Error: {error}")
                        else:
                            st.success("✅ Transcription successful!")
                            st.text_area("Transcription:", text, height=200)
            
            with col2:
                if openai_key and st.button("🧠 Transcribe with Whisper (OpenAI)", type="primary"):
                    with st.spinner("Transcribing with OpenAI Whisper..."):
                        audio_bytes = audio_data.getvalue()
                        text = transcribe_openai_whisper_optional(audio_bytes)
                        
                        if text:
                            st.success("✅ Whisper transcription successful!")
                            st.text_area("Transcription:", text, height=200)
                        else:
                            st.error("❌ Whisper transcription failed")
    
    # Usage Instructions
    st.sidebar.markdown("---")
    st.sidebar.subheader("📖 Usage Instructions")
    
    instructions = """
    ### 🔧 **Setup Requirements**
    1. Install dependencies: `pip install SpeechRecognition pydub openai`
    2. Set OpenAI API key (optional, for better accuracy)
    
    ### 🎤 **How to Use**
    
    **Method 1: Upload Audio File**
    1. Click "Upload Audio File"
    2. Select an audio file (WAV, MP3, WebM, etc.)
    3. Choose transcription service:
       - **Google Speech API**: Free, good accuracy
       - **OpenAI Whisper**: Requires API key, excellent accuracy
    4. Click transcribe button
    5. View results in text area
    
    **Method 2: Record with Microphone**
    1. Click "Use Microphone"
    2. Click the microphone button in audio widget
    3. Speak clearly into your microphone
    4. Click again to stop recording
    5. Choose transcription service
    6. Click transcribe button
    7. View results in text area
    
    ### 📋 **Technical Details**
    
    **Google Speech API:**
    - Free to use
    - Supports multiple languages
    - Real-time transcription
    - Energy threshold: 280 (adjustable)
    - Pause threshold: 0.9s (adjustable)
    
    **OpenAI Whisper:**
    - Requires API key
    - Higher accuracy, especially for noisy audio
    - Supports 99 languages
    - Better handling of accents and background noise
    - Processing time: ~10-30 seconds per audio clip
    
    ### 🎯 **Best Practices**
    - Speak clearly and at moderate pace
    - Minimize background noise
    - Keep recordings under 2 minutes for best results
    - Use WAV format when possible (highest quality)
    - For interviews: 45-60 seconds per answer is ideal
    """
    
    st.sidebar.markdown(instructions)
    
    # Code Example
    st.sidebar.markdown("---")
    st.sidebar.subheader("💻 Code Example")
    
    code_example = '''
```python
from utils.voice_stt import transcribe_with_google, transcribe_openai_whisper_optional

# Method 1: Google Speech API (Free)
audio_bytes = get_audio_bytes()  # Your audio data
text, error = transcribe_with_google(audio_bytes, "filename.wav")

if error:
    print(f"Error: {error}")
else:
    print(f"Transcription: {text}")

# Method 2: OpenAI Whisper (Requires API Key)
import os
os.environ["OPENAI_API_KEY"] = "your-api-key-here"

text = transcribe_openai_whisper_optional(audio_bytes)
if text:
    print(f"Whisper transcription: {text}")
else:
    print("Whisper transcription failed")
```
    '''
    
    st.sidebar.code(code_example, language='python')

if __name__ == "__main__":
    main()

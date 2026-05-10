"""
Enhanced Voice Interview UI - ChatGPT-like Interface
Real-time conversation, live scoring, and natural interaction
"""
from __future__ import annotations

import time
import json
from datetime import datetime
from typing import Dict, List, Optional

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from utils.enhanced_voice_interview import EnhancedVoiceInterview, InterviewState
from utils.voice_stt import transcribe_openai_whisper_optional, transcribe_with_google
from utils.voice_tts import synthesize_interviewer_speech


def render_enhanced_voice_interview():
    """Render enhanced voice interview interface with ChatGPT-like experience"""
    st.title("AI Interview Coach - Conversational Experience")
    st.markdown("---")
    
    # Initialize interview session
    if 'enhanced_interview' not in st.session_state:
        st.session_state.enhanced_interview = EnhancedVoiceInterview()
    
    interview = st.session_state.enhanced_interview
    
    # Interview setup
    if not st.session_state.get('interview_active', False):
        render_interview_setup(interview)
    else:
        render_active_interview(interview)


def render_interview_setup(interview: EnhancedVoiceInterview):
    """Render interview setup interface"""
    st.markdown("### Interview Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        job_role = st.selectbox(
            "Target Role",
            ["Software Engineer", "Data Scientist", "Product Manager", "DevOps Engineer", "UI/UX Designer"],
            help="Select the role you're interviewing for"
        )
        
        experience_level = st.selectbox(
            "Experience Level",
            ["Entry Level", "Mid Level", "Senior Level", "Lead/Manager"],
            help="Select your experience level"
        )
    
    with col2:
        st.markdown("### Interview Features")
        st.markdown("""
        - **Natural Conversation**: ChatGPT-like dialogue flow
        - **Real-time Analysis**: Live scoring and feedback
        - **Dynamic Questions**: Context-aware question generation
        - **Voice Interaction**: Speech-to-text and text-to-speech
        - **Performance Metrics**: Fluency, relevance, clarity scores
        """)
    
    # Voice settings
    with st.expander("Voice Settings", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            voice_speed = st.slider("Speech Speed", 0.5, 2.0, 1.0, 0.1)
        with col2:
            voice_pitch = st.slider("Voice Pitch", 0.5, 2.0, 1.0, 0.1)
    
    # Start interview button
    if st.button("Start Interview", type="primary", use_container_width=True):
        greeting = interview.initialize_session(job_role, experience_level)
        st.session_state.current_question = greeting
        st.session_state.voice_speed = voice_speed
        st.session_state.voice_pitch = voice_pitch
        st.rerun()


def render_active_interview(interview: EnhancedVoiceInterview):
    """Render active interview interface"""
    # Interview status
    render_interview_status(interview)
    
    # Conversation display
    render_conversation_display(interview)
    
    # Live metrics
    render_live_metrics(interview)
    
    # Voice controls
    render_voice_controls(interview)
    
    # Interview controls
    render_interview_controls(interview)


def render_interview_status(interview: EnhancedVoiceInterview):
    """Render interview status bar"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("State", interview.current_state.value.title())
    
    with col2:
        if interview.session_start_time:
            duration = datetime.now() - interview.session_start_time
            st.metric("Duration", f"{duration.seconds // 60}:{duration.seconds % 60:02d}")
    
    with col3:
        response_count = len([turn for turn in interview.conversation_history if turn.speaker == "candidate"])
        st.metric("Responses", response_count)
    
    with col4:
        if interview.interview_metrics.overall_score > 0:
            st.metric("Current Score", f"{interview.interview_metrics.overall_score:.1f}/100")


def render_conversation_display(interview: EnhancedVoiceInterview):
    """Render conversation history with ChatGPT-like interface"""
    st.markdown("### Conversation")
    
    # Chat-like display
    conversation_container = st.container()
    
    with conversation_container:
        for turn in interview.conversation_history:
            if turn.speaker == "interviewer":
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           color: white; padding: 15px; border-radius: 15px; 
                           margin: 10px 0; max-width: 80%; margin-left: auto;">
                    <strong>AI Interviewer:</strong> {turn.text}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Candidate response with analysis
                confidence_emoji = " confidence" if turn.confidence_score > 0.8 else " moderate" if turn.confidence_score > 0.6 else " low"
                
                st.markdown(f"""
                <div style="background: #f0f2f5; color: #333; padding: 15px; 
                           border-radius: 15px; margin: 10px 0; max-width: 80%; 
                           border-left: 4px solid #4CAF50;">
                    <strong>You:</strong> {turn.text}
                    <br><small style="color: #666;">
                        Confidence: {confidence_emoji} 
                        {f'| Score: {turn.analysis_score:.1f}/100' if turn.analysis_score else ''}
                    </small>
                </div>
                """, unsafe_allow_html=True)
                
                # Show feedback if available
                if turn.feedback:
                    st.markdown(f"""
                    <div style="background: #e8f5e8; color: #2e7d32; padding: 10px; 
                               border-radius: 10px; margin: 5px 0; font-size: 0.9em;">
                        <strong>Feedback:</strong> {turn.feedback}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Auto-scroll to latest
    if interview.conversation_history:
        st.markdown('<div id="conversation-end"></div>', unsafe_allow_html=True)
        st.markdown("""
        <script>
            document.getElementById('conversation-end').scrollIntoView({behavior: 'smooth'});
        </script>
        """, unsafe_allow_html=True)


def render_live_metrics(interview: EnhancedVoiceInterview):
    """Render live performance metrics"""
    if interview.interview_metrics.overall_score > 0:
        st.markdown("### Live Performance Analysis")
        
        # Metrics grid
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            fluency_color = "green" if interview.interview_metrics.fluency_score > 70 else "orange" if interview.interview_metrics.fluency_score > 50 else "red"
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border-radius: 10px; background: #f8f9fa;">
                <div style="font-size: 24px; color: {fluency_color};"> 
                    {interview.interview_metrics.fluency_score:.0f}
                </div>
                <div style="font-size: 12px; color: #666;">Fluency</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            relevance_color = "green" if interview.interview_metrics.relevance_score > 70 else "orange" if interview.interview_metrics.relevance_score > 50 else "red"
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border-radius: 10px; background: #f8f9fa;">
                <div style="font-size: 24px; color: {relevance_color};"> 
                    {interview.interview_metrics.relevance_score:.0f}
                </div>
                <div style="font-size: 12px; color: #666;">Relevance</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            clarity_color = "green" if interview.interview_metrics.clarity_score > 70 else "orange" if interview.interview_metrics.clarity_score > 50 else "red"
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border-radius: 10px; background: #f8f9fa;">
                <div style="font-size: 24px; color: {clarity_color};"> 
                    {interview.interview_metrics.clarity_score:.0f}
                </div>
                <div style="font-size: 12px; color: #666;">Clarity</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            overall_color = "green" if interview.interview_metrics.overall_score > 70 else "orange" if interview.interview_metrics.overall_score > 50 else "red"
            st.markdown(f"""
            <div style="text-align: center; padding: 10px; border-radius: 10px; background: #f8f9fa;">
                <div style="font-size: 24px; color: {overall_color}; font-weight: bold;"> 
                    {interview.interview_metrics.overall_score:.0f}
                </div>
                <div style="font-size: 12px; color: #666;">Overall</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Progress bars
        st.markdown("#### Detailed Metrics")
        
        metrics_data = {
            "Fluency": interview.interview_metrics.fluency_score,
            "Confidence": interview.interview_metrics.confidence_score,
            "Relevance": interview.interview_metrics.relevance_score,
            "Clarity": interview.interview_metrics.clarity_score
        }
        
        fig = go.Figure()
        
        for metric, score in metrics_data.items():
            color = "#4CAF50" if score > 70 else "#FF9800" if score > 50 else "#F44336"
            fig.add_trace(go.Bar(
                x=[metric],
                y=[score],
                marker_color=color,
                text=f"{score:.1f}",
                textposition='auto'
            ))
        
        fig.update_layout(
            title="Performance Breakdown",
            yaxis=dict(range=[0, 100]),
            showlegend=False,
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Words Spoken", interview.interview_metrics.word_count)
        with col2:
            st.metric("Filler Words", interview.interview_metrics.filler_words)


def render_voice_controls(interview: EnhancedVoiceInterview):
    """Render voice interaction controls"""
    st.markdown("### Voice Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Speech-to-text button
        if st.button("Speak Response", type="primary", use_container_width=True):
            with st.spinner("Listening..."):
                # Simulate voice input (replace with actual STT)
                time.sleep(2)
                response = "This is a simulated response for testing purposes."
                
                # Add response to conversation
                interview._add_conversation_turn("candidate", response, confidence=0.85)
                
                # Generate follow-up question
                follow_up = interview.generate_follow_up_question(response)
                interview._add_conversation_turn("interviewer", follow_up)
                
                # Provide feedback
                feedback = interview.provide_real_time_feedback(response)
                if feedback:
                    st.info(f"Feedback: {feedback}")
                
                st.rerun()
    
    with col2:
        # Text input alternative
        user_input = st.text_input("Or type your response:", key="text_response")
        if st.button("Send Response", use_container_width=True) and user_input:
            interview._add_conversation_turn("candidate", user_input, confidence=0.95)
            
            # Generate follow-up
            follow_up = interview.generate_follow_up_question(user_input)
            interview._add_conversation_turn("interviewer", follow_up)
            
            # Provide feedback
            feedback = interview.provide_real_time_feedback(user_input)
            if feedback:
                st.info(f"Feedback: {feedback}")
            
            st.rerun()
    
    with col3:
        # TTS for interviewer questions
        if st.button("Play Question", use_container_width=True):
            if interview.conversation_history and interview.conversation_history[-1].speaker == "interviewer":
                last_question = interview.conversation_history[-1].text
                st.info(f"Playing: {last_question}")
                # TTS would be implemented here
                time.sleep(1)  # Simulate TTS playback


def render_interview_controls(interview: EnhancedVoiceInterview):
    """Render interview control buttons"""
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Pause Interview", use_container_width=True):
            st.session_state.interview_paused = True
            st.info("Interview paused. Click 'Resume' to continue.")
    
    with col2:
        if st.button("End Interview", type="secondary", use_container_width=True):
            results = interview.end_interview()
            st.session_state.interview_results = results
            st.session_state.show_results = True
            st.rerun()
    
    with col3:
        if st.button("Get Hint", use_container_width=True):
            hint = "Try to structure your response with the STAR method: Situation, Task, Action, Result."
            st.info(f"Hint: {hint}")


def render_interview_results():
    """Render final interview results"""
    if 'interview_results' in st.session_state:
        results = st.session_state.interview_results
        
        st.markdown("### Interview Complete! ")
        st.markdown("---")
        
        # Overall score
        score = results["final_score"]["overall_score"]
        
        # Score visualization
        col1, col2 = st.columns(2)
        
        with col1:
            # Gauge chart for overall score
            fig = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = score,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Overall Score"},
                delta = {'reference': 70},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#4CAF50" if score > 70 else "#FF9800" if score > 50 else "#F44336"},
                    'steps': [
                        {'range': [0, 50], 'color': "lightgray"},
                        {'range': [50, 70], 'color': "yellow"},
                        {'range': [70, 100], 'color': "lightgreen"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Score breakdown
            breakdown = results["final_score"]["breakdown"]
            
            st.markdown("#### Performance Breakdown")
            
            for metric, score in breakdown.items():
                color = "green" if score > 70 else "orange" if score > 50 else "red"
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; 
                           padding: 8px; margin: 5px 0; background: #f8f9fa; border-radius: 5px;">
                    <span>{metric.title()}</span>
                    <span style="color: {color}; font-weight: bold;">{score:.1f}/100</span>
                </div>
                """, unsafe_allow_html=True)
        
        # Conversation summary
        st.markdown("### Conversation Summary")
        
        conversation_df = []
        for turn in results["conversation_history"]:
            conversation_df.append({
                "Speaker": turn.speaker.title(),
                "Message": turn.text[:100] + "..." if len(turn.text) > 100 else turn.text,
                "Time": turn.timestamp.strftime("%H:%M:%S")
            })
        
        if conversation_df:
            df = pd.DataFrame(conversation_df)
            st.dataframe(df, use_container_width=True)
        
        # Recommendations
        st.markdown("### Recommendations")
        
        score = results["final_score"]["overall_score"]
        
        if score >= 85:
            st.success("Excellent performance! You're ready for real interviews.")
        elif score >= 70:
            st.info("Good performance! Focus on reducing filler words and providing more specific examples.")
        elif score >= 55:
            st.warning("Fair performance. Practice structuring your responses and work on fluency.")
        else:
            st.error("Needs improvement. Consider practicing with mock interviews and working on communication skills.")
        
        # Download report
        if st.button("Download Interview Report", type="primary"):
            report_data = {
                "interview_date": datetime.now().isoformat(),
                "final_score": results["final_score"],
                "conversation": [
                    {
                        "speaker": turn.speaker,
                        "text": turn.text,
                        "timestamp": turn.timestamp.isoformat()
                    }
                    for turn in results["conversation_history"]
                ]
            }
            
            st.download_button(
                label="Download JSON Report",
                data=json.dumps(report_data, indent=2),
                file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )


# Main render function
def render_enhanced_voice_interview_page():
    """Main entry point for enhanced voice interview"""
    render_enhanced_voice_interview()
    
    # Show results if interview ended
    if st.session_state.get('show_results', False):
        render_interview_results()

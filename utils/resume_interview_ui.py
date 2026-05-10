"""
Resume-Based Interview UI
Complete interface for resume analysis, voice synthesis, and answer scoring
"""
from __future__ import annotations

import time
import json
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils.resume_based_interview import (
    ResumeBasedInterview, ResumeSkill, GeneratedQuestion, AnswerAnalysis,
    QuestionCategory, QuestionDifficulty
)


def render_resume_based_interview():
    """Render complete resume-based interview interface"""
    st.title("Resume-Based Voice Interview")
    st.markdown("*AI-powered interview system that analyzes your resume and generates personalized questions*")
    st.markdown("---")
    
    # Initialize interview system
    if 'resume_interview' not in st.session_state:
        st.session_state.resume_interview = ResumeBasedInterview()
        st.session_state.resume_uploaded = False
        st.session_state.resume_analyzed = False
        st.session_state.questions_generated = False
        st.session_state.interview_active = False
    
    interview = st.session_state.resume_interview
    
    # Main interface tabs
    tab_upload, tab_questions, tab_interview, tab_results = st.tabs([
        "Upload Resume", "Generated Questions", "Voice Interview", "Results"
    ])
    
    with tab_upload:
        render_resume_upload_tab(interview)
    
    with tab_questions:
        render_questions_tab(interview)
    
    with tab_interview:
        render_interview_tab(interview)
    
    with tab_results:
        render_results_tab(interview)


def render_resume_upload_tab(interview: ResumeBasedInterview):
    """Render resume upload and analysis tab"""
    st.markdown("### Upload and Analyze Resume")
    
    # Resume upload
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF or DOCX)",
            type=['pdf', 'docx'],
            help="Upload your resume to generate personalized interview questions"
        )
        
        if uploaded_file is not None:
            # Extract text from resume
            try:
                from utils.ai_resume_analyzer import AIResumeAnalyzer
                analyzer = AIResumeAnalyzer()
                
                if uploaded_file.type == "application/pdf":
                    resume_text = analyzer.extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = analyzer.extract_text_from_docx(uploaded_file)
                
                st.session_state.resume_text = resume_text
                st.session_state.resume_uploaded = True
                
                st.success("Resume uploaded successfully!")
                
                # Display resume preview
                with st.expander("Preview Resume Text", expanded=False):
                    st.text_area("Resume Content", resume_text, height=200, disabled=True)
                
            except Exception as e:
                st.error(f"Error reading resume: {e}")
    
    with col2:
        st.markdown("#### Resume Analysis")
        
        if st.session_state.get('resume_uploaded', False):
            if st.button("Analyze Resume", type="primary", use_container_width=True):
                with st.spinner("Analyzing resume skills..."):
                    resume_text = st.session_state.resume_text
                    skills = interview.analyze_resume(resume_text)
                    
                    if skills:
                        st.session_state.resume_analyzed = True
                        st.success(f"Found {len(skills)} skills!")
                        st.rerun()
                    else:
                        st.error("No skills found in resume")
        else:
            st.info("Please upload a resume first")
    
    # Display analyzed skills
    if st.session_state.get('resume_analyzed', False):
        st.markdown("#### Extracted Skills")
        
        skills = interview.resume_skills
        
        # Categorize skills
        categories = {}
        for skill in skills:
            if skill.category not in categories:
                categories[skill.category] = []
            categories[skill.category].append(skill)
        
        # Display skills by category
        for category, category_skills in categories.items():
            with st.expander(f"{category.title()} ({len(category_skills)} skills)", expanded=True):
                for skill in category_skills:
                    col_skill_name, col_level, col_exp = st.columns([3, 2, 2])
                    
                    with col_skill_name:
                        st.markdown(f"**{skill.name}**")
                    
                    with col_level:
                        st.markdown(f"Level: {skill.proficiency_level}")
                    
                    with col_exp:
                        if skill.years_of_experience > 0:
                            st.markdown(f"Exp: {skill.years_of_experience}y")
                        else:
                            st.markdown("Exp: N/A")
                    
                    # Display keywords
                    if skill.keywords:
                        st.markdown(f"*Keywords:* {', '.join(skill.keywords[:5])}")
        
        # Generate questions button
        st.markdown("---")
        if st.button("Generate Interview Questions", type="primary", use_container_width=True):
            with st.spinner("Generating personalized questions..."):
                questions = interview.generate_skill_based_questions(num_questions=10)
                
                if questions:
                    st.session_state.questions_generated = True
                    st.success(f"Generated {len(questions)} personalized questions!")
                    st.rerun()
                else:
                    st.error("Failed to generate questions")


def render_questions_tab(interview: ResumeBasedInterview):
    """Render generated questions tab"""
    st.markdown("### Generated Interview Questions")
    
    if not st.session_state.get('questions_generated', False):
        st.warning("Please upload and analyze a resume first to generate questions.")
        return
    
    questions = interview.generated_questions
    
    if not questions:
        st.error("No questions available")
        return
    
    # Question statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Questions", len(questions))
    
    with col2:
        categories = set(q.category.value for q in questions)
        st.metric("Categories", len(categories))
    
    with col3:
        difficulties = set(q.difficulty.value for q in questions)
        st.metric("Difficulty Levels", len(difficulties))
    
    with col4:
        total_skills = len(set(skill for q in questions for skill in q.target_skills))
        st.metric("Skills Covered", total_skills)
    
    # Filter questions
    st.markdown("#### Filter Questions")
    
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    
    with col_filter1:
        selected_category = st.selectbox(
            "Filter by Category",
            ["All"] + list(set(q.category.value for q in questions)),
            index=0
        )
    
    with col_filter2:
        selected_difficulty = st.selectbox(
            "Filter by Difficulty",
            ["All"] + list(set(q.difficulty.value for q in questions)),
            index=0
        )
    
    with col_filter3:
        search_keyword = st.text_input("Search by Keyword")
    
    # Display questions
    st.markdown("#### Question List")
    
    filtered_questions = []
    
    for i, question in enumerate(questions):
        # Apply filters
        if selected_category != "All" and question.category.value != selected_category:
            continue
        if selected_difficulty != "All" and question.difficulty.value != selected_difficulty:
            continue
        if search_keyword and search_keyword.lower() not in question.text.lower():
            continue
        
        filtered_questions.append((i + 1, question))
    
    if not filtered_questions:
        st.info("No questions match your filters")
        return
    
    for question_num, question in filtered_questions:
        with st.expander(f"Question {question_num}: {question.category.value.title()} - {question.difficulty.value.title()}", expanded=False):
            # Question text
            st.markdown(f"**Question:** {question.text}")
            
            # Question details
            col_detail1, col_detail2, col_detail3 = st.columns(3)
            
            with col_detail1:
                st.markdown(f"**Category:** {question.category.value.title()}")
            
            with col_detail2:
                st.markdown(f"**Difficulty:** {question.difficulty.value.title()}")
            
            with col_detail3:
                st.markdown(f"**Max Time:** {question.max_response_time}s")
            
            # Target skills
            if question.target_skills:
                st.markdown(f"**Target Skills:** {', '.join(question.target_skills)}")
            
            # Expected keywords
            if question.expected_keywords:
                st.markdown(f"**Expected Keywords:** {', '.join(question.expected_keywords[:8])}")
                if len(question.expected_keywords) > 8:
                    st.markdown(f"*... and {len(question.expected_keywords) - 8} more*")
            
            # Scoring criteria
            if question.scoring_criteria:
                st.markdown("**Scoring Criteria:**")
                for criterion, weight in question.scoring_criteria.items():
                    st.markdown(f"- {criterion.title()}: {weight:.1%}")
            
            # Follow-up suggestions
            if question.follow_up_suggestions:
                st.markdown("**Follow-up Suggestions:**")
                for suggestion in question.follow_up_suggestions:
                    st.markdown(f"- {suggestion}")
            
            # Play question audio
            if st.button(f"Play Question {question_num} Audio", key=f"play_{question.id}"):
                with st.spinner("Generating audio..."):
                    audio_data = interview.synthesize_question_audio(question.text)
                    if audio_data:
                        st.success("Audio generated successfully!")
                        # In real implementation, would play audio here
                    else:
                        st.error("Failed to generate audio")
    
    # Start interview button
    st.markdown("---")
    if st.button("Start Voice Interview", type="primary", use_container_width=True):
        st.session_state.interview_active = True
        interview.current_question_index = 0
        st.success("Interview started! Go to the Voice Interview tab.")
        st.rerun()


def render_interview_tab(interview: ResumeBasedInterview):
    """Render voice interview tab"""
    st.markdown("### Voice Interview")
    
    if not st.session_state.get('questions_generated', False):
        st.warning("Please generate questions first in the Questions tab.")
        return
    
    if not st.session_state.get('interview_active', False):
        st.info("Click 'Start Voice Interview' in the Questions tab to begin.")
        return
    
    # Interview status
    current_q_index = interview.current_question_index
    total_questions = len(interview.generated_questions)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Current Question", f"{current_q_index + 1}/{total_questions}")
    
    with col2:
        answered = len(interview.answer_analyses)
        st.metric("Answered", answered)
    
    with col3:
        if answered > 0:
            avg_score = sum(a.overall_score for a in interview.answer_analyses) / answered
            st.metric("Average Score", f"{avg_score:.1f}")
        else:
            st.metric("Average Score", "N/A")
    
    with col4:
        st.metric("Status", "Active" if interview.interview_active else "Inactive")
    
    st.markdown("---")
    
    # Current question
    current_question = interview.get_next_question()
    
    if current_question:
        # Display current question
        st.markdown("#### Current Question")
        
        # Question card
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                   color: white; padding: 20px; border-radius: 15px; 
                   margin: 20px 0; box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);">
            <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 10px;">
                Question {current_q_index + 1}
            </div>
            <div style="font-size: 1.1em; line-height: 1.6;">
                {current_question.text}
            </div>
            <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.9;">
                Category: {current_question.category.value.title()} | 
                Difficulty: {current_question.difficulty.value.title()} | 
                Max Time: {current_question.max_response_time}s
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Voice controls
        st.markdown("#### Voice Controls")
        
        col_play, col_record, col_skip = st.columns(3)
        
        with col_play:
            if st.button("Play Question", type="primary", use_container_width=True):
                with st.spinner("Generating audio..."):
                    audio_data = interview.synthesize_question_audio(current_question.text)
                    if audio_data:
                        st.success("Question audio playing...")
                        time.sleep(2)  # Simulate playback
                    else:
                        st.error("Failed to generate audio")
        
        with col_record:
            if st.button("Record Response", type="secondary", use_container_width=True):
                with st.spinner("Recording your response..."):
                    user_response, confidence = interview.capture_user_response()
                    
                    if user_response:
                        st.session_state.current_response = user_response
                        st.session_state.response_confidence = confidence
                        st.success(f"Response captured! (Confidence: {confidence:.1%})")
                        
                        # Show response preview
                        st.text_area("Your Response", user_response, height=100, disabled=True)
                    else:
                        st.error("Failed to capture response")
        
        with col_skip:
            if st.button("Skip Question", use_container_width=True):
                st.warning("Question skipped")
                # Move to next question
                if current_q_index < total_questions - 1:
                    interview.current_question_index += 1
                    st.rerun()
        
        # Analyze response
        if 'current_response' in st.session_state:
            st.markdown("#### Analyze Response")
            
            if st.button("Analyze Response", type="primary", use_container_width=True):
                with st.spinner("Analyzing your response..."):
                    response_time = 30.0  # Simulated response time
                    analysis = interview.analyze_answer(
                        current_question, 
                        st.session_state.current_response, 
                        response_time
                    )
                    
                    st.session_state.current_analysis = analysis
                    
                    # Clear response
                    del st.session_state.current_response
                    del st.session_state.response_confidence
                    
                    st.success("Analysis complete!")
                    st.rerun()
        
        # Display analysis
        if 'current_analysis' in st.session_state:
            analysis = st.session_state.current_analysis
            
            st.markdown("#### Response Analysis")
            
            # Score overview
            col_score1, col_score2, col_score3, col_score4 = st.columns(4)
            
            with col_score1:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=analysis.overall_score,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Overall Score"},
                    gauge={'axis': {'range': [None, 100]}, 'bar': {'color': "#4CAF50"}}
                ))
                fig.update_layout(height=200, margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
            
            with col_score2:
                st.metric("Relevance", f"{analysis.relevance_score:.1f}%")
                st.metric("Completeness", f"{analysis.completeness_score:.1f}%")
            
            with col_score3:
                st.metric("Technical", f"{analysis.technical_accuracy_score:.1f}%")
                st.metric("Communication", f"{analysis.communication_score:.1f}%")
            
            with col_score4:
                st.metric("Response Time", f"{analysis.response_time:.1f}s")
                st.metric("Grade", interview._calculate_grade(analysis.overall_score))
            
            # Detailed feedback
            st.markdown("##### Detailed Feedback")
            st.info(analysis.detailed_feedback)
            
            # Keywords analysis
            col_keywords1, col_keywords2 = st.columns(2)
            
            with col_keywords1:
                if analysis.matched_keywords:
                    st.markdown("**Matched Keywords:**")
                    for keyword in analysis.matched_keywords:
                        st.success(f" {keyword}")
            
            with col_keywords2:
                if analysis.missing_keywords:
                    st.markdown("**Missing Keywords:**")
                    for keyword in analysis.missing_keywords:
                        st.warning(f" {keyword}")
            
            # Strengths and improvements
            col_feedback1, col_feedback2 = st.columns(2)
            
            with col_feedback1:
                if analysis.strengths:
                    st.markdown("**Strengths:**")
                    for strength in analysis.strengths:
                        st.success(f" {strength}")
            
            with col_feedback2:
                if analysis.improvements:
                    st.markdown("**Areas for Improvement:**")
                    for improvement in analysis.improvements:
                        st.warning(f" {improvement}")
            
            # Next question button
            if st.button("Next Question", type="primary", use_container_width=True):
                del st.session_state.current_analysis
                if current_q_index < total_questions - 1:
                    st.rerun()
                else:
                    st.session_state.interview_complete = True
                    st.success("Interview completed! Check the Results tab for your report.")
                    st.rerun()
    
    else:
        # Interview complete
        st.markdown("#### Interview Complete!")
        st.success("Congratulations! You've completed all the questions.")
        st.info("Check the Results tab for your comprehensive interview report.")


def render_results_tab(interview: ResumeBasedInterview):
    """Render interview results tab"""
    st.markdown("### Interview Results")
    
    if not interview.answer_analyses:
        st.warning("No interview data available. Please complete the interview first.")
        return
    
    # Generate summary
    summary = interview.get_interview_summary()
    
    # Overview section
    st.markdown("#### Interview Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Questions Answered", summary["interview_overview"]["questions_answered"])
    
    with col2:
        st.metric("Skills Analyzed", summary["interview_overview"]["resume_skills_analyzed"])
    
    with col3:
        st.metric("Average Score", f"{summary['performance_summary']['average_overall']:.1f}")
    
    with col4:
        st.metric("Final Grade", summary['performance_summary']['final_grade'])
    
    # Performance breakdown
    st.markdown("#### Performance Breakdown")
    
    perf = summary["performance_summary"]
    
    col_perf1, col_perf2 = st.columns(2)
    
    with col_perf1:
        # Overall score gauge
        fig_overall = go.Figure(go.Indicator(
            mode="gauge+number",
            value=perf["average_overall"],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Overall Performance"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#4CAF50"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 70], 'color': "yellow"},
                    {'range': [70, 85], 'color': "lightgreen"},
                    {'range': [85, 100], 'color': "green"}
                ]
            }
        ))
        fig_overall.update_layout(height=250, margin=dict(l=0, r=0, t=30, b=0))
        st.plotly_chart(fig_overall, use_container_width=True)
    
    with col_perf2:
        # Individual metrics
        st.metric("Relevance", f"{perf['average_relevance']:.1f}%")
        st.metric("Completeness", f"{perf['average_completeness']:.1f}%")
        st.metric("Technical", f"{perf['average_technical']:.1f}%")
        st.metric("Communication", f"{perf['average_communication']:.1f}%")
    
    # Performance distribution
    st.markdown("#### Performance Distribution")
    
    dist = summary["performance_distribution"]
    labels = list(dist.keys())
    values = list(dist.values())
    
    fig_dist = px.pie(
        values=values,
        names=labels,
        title="Response Quality Distribution",
        color_discrete_map={
            "Excellent": "#4CAF50",
            "Good": "#8BC34A",
            "Fair": "#FFC107",
            "Poor": "#F44336"
        }
    )
    st.plotly_chart(fig_dist, use_container_width=True)
    
    # Category performance
    if summary["category_performance"]:
        st.markdown("#### Performance by Category")
        
        cat_perf = summary["category_performance"]
        categories = list(cat_perf.keys())
        scores = list(cat_perf.values())
        
        fig_cat = px.bar(
            x=categories,
            y=scores,
            title="Performance by Question Category",
            labels={"x": "Category", "y": "Average Score"},
            color=scores,
            color_continuous_scale="viridis"
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    # Common strengths and improvements
    col_common1, col_common2 = st.columns(2)
    
    with col_common1:
        if summary["common_strengths"]:
            st.markdown("#### Common Strengths")
            for strength_data in summary["common_strengths"]:
                st.success(f" {strength_data['strength']} ({strength_data['count']} times)")
    
    with col_common2:
        if summary["common_improvements"]:
            st.markdown("#### Common Areas for Improvement")
            for improvement_data in summary["common_improvements"]:
                st.warning(f" {improvement_data['improvement']} ({improvement_data['count']} times)")
    
    # Detailed responses
    if summary["detailed_responses"]:
        st.markdown("#### Detailed Response Analysis")
        
        # Create dataframe
        df = pd.DataFrame(summary["detailed_responses"])
        
        # Display with custom formatting
        for i, row in df.iterrows():
            with st.expander(f"Question {i+1} - Score: {row['overall_score']:.1f}", expanded=False):
                st.markdown(f"**Question:** {row['question']}")
                st.markdown(f"**Your Response:** {row['user_response']}")
                st.markdown(f"**Score:** {row['overall_score']:.1f}")
                st.markdown(f"**Feedback:** {row['feedback']}")
    
    # Export options
    st.markdown("#### Export Results")
    
    col_export1, col_export2, col_export3 = st.columns(3)
    
    with col_export1:
        if st.button("Export as JSON", use_container_width=True):
            json_data = json.dumps(summary, indent=2, default=str)
            st.download_button(
                label="Download JSON Report",
                data=json_data,
                file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col_export2:
        if st.button("Export as CSV", use_container_width=True):
            csv_data = pd.DataFrame(summary["detailed_responses"]).to_csv(index=False)
            st.download_button(
                label="Download CSV Report",
                data=csv_data,
                file_name=f"interview_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    with col_export3:
        if st.button("Reset Interview", use_container_width=True):
            interview.reset_interview()
            
            # Reset session states
            st.session_state.resume_uploaded = False
            st.session_state.resume_analyzed = False
            st.session_state.questions_generated = False
            st.session_state.interview_active = False
            
            if 'current_analysis' in st.session_state:
                del st.session_state.current_analysis
            
            if 'current_response' in st.session_state:
                del st.session_state.current_response
            
            st.success("Interview reset successfully!")
            st.rerun()

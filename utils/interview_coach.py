"""
AI Interview Coach - Interactive Interview Simulation
"""
import streamlit as st
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from utils.interview_generator import InterviewQuestionGenerator

class AIInterviewCoach:
    """Interactive AI-powered interview coach"""
    
    def __init__(self):
        self.question_generator = InterviewQuestionGenerator()
        self.conversation_history = []
        self.current_question_index = 0
        self.interview_questions = []
        self.user_answers = []
        self.feedback_scores = []
        
        # Feedback criteria
        self.feedback_criteria = {
            'clarity': {
                'weight': 0.25,
                'indicators': ['clear', 'well-structured', 'easy to understand', 'coherent'],
                'negative_indicators': ['unclear', 'confusing', 'rambling', 'disorganized']
            },
            'relevance': {
                'weight': 0.25,
                'indicators': ['relevant', 'on-topic', 'directly addresses', 'focused'],
                'negative_indicators': ['irrelevant', 'off-topic', 'avoided question', 'unrelated']
            },
            'depth': {
                'weight': 0.25,
                'indicators': ['detailed', 'thorough', 'comprehensive', 'insightful'],
                'negative_indicators': ['superficial', 'brief', 'lacking detail', 'shallow']
            },
            'confidence': {
                'weight': 0.25,
                'indicators': ['confident', 'assured', 'poised', 'articulate'],
                'negative_indicators': ['hesitant', 'uncertain', 'nervous', 'apologetic']
            }
        }
    
    def start_interview_session(self, skills: Dict[str, Any], role: str = "Software Engineer") -> Dict[str, Any]:
        """Start a new interview session"""
        
        # Reset session state
        self.conversation_history = []
        self.current_question_index = 0
        self.interview_questions = []
        self.user_answers = []
        self.feedback_scores = []
        
        # Generate interview questions
        mock_interview = self.question_generator.generate_mock_interview(
            skills, role, duration_minutes=30
        )
        
        # Flatten all questions
        all_questions = []
        for section in mock_interview['sections']:
            for question_data in section['questions']:
                all_questions.append({
                    'question': question_data['question'],
                    'section': section['section'],
                    'type': question_data.get('type', 'general'),
                    'tips': question_data.get('tips', ''),
                    'duration_minutes': section['duration_minutes']
                })
        
        self.interview_questions = all_questions
        
        return {
            'session_id': f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'role': role,
            'total_questions': len(all_questions),
            'estimated_duration': mock_interview['duration_minutes'],
            'tips': mock_interview['tips'],
            'evaluation_criteria': mock_interview['evaluation_criteria'],
            'first_question': all_questions[0] if all_questions else None
        }
    
    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """Get the current question"""
        if self.current_question_index < len(self.interview_questions):
            return self.interview_questions[self.current_question_index]
        return None
    
    def submit_answer(self, answer: str) -> Dict[str, Any]:
        """Submit an answer and get feedback"""
        if self.current_question_index >= len(self.interview_questions):
            return {'error': 'Interview session ended'}
        
        current_question = self.interview_questions[self.current_question_index]
        
        # Store answer
        answer_data = {
            'question': current_question['question'],
            'answer': answer,
            'timestamp': datetime.now().isoformat(),
            'question_type': current_question['type'],
            'section': current_question['section']
        }
        self.user_answers.append(answer_data)
        
        # Generate feedback
        feedback = self._generate_feedback(answer, current_question)
        self.feedback_scores.append(feedback)
        
        # Add to conversation history
        self.conversation_history.append({
            'question': current_question['question'],
            'answer': answer,
            'feedback': feedback,
            'timestamp': datetime.now().isoformat()
        })
        
        # Move to next question
        self.current_question_index += 1
        
        return {
            'feedback': feedback,
            'next_question': self.get_current_question(),
            'progress': {
                'current': self.current_question_index,
                'total': len(self.interview_questions),
                'percentage': (self.current_question_index / len(self.interview_questions)) * 100
            },
            'is_complete': self.current_question_index >= len(self.interview_questions)
        }
    
    def _generate_feedback(self, answer: str, question: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI feedback for the answer"""
        feedback = {
            'overall_score': 0,
            'criteria_scores': {},
            'strengths': [],
            'improvements': [],
            'suggestions': [],
            'follow_up_questions': []
        }
        
        # Analyze answer for each criterion
        answer_lower = answer.lower()
        total_score = 0
        
        for criterion, config in self.feedback_criteria.items():
            score = self._score_criterion(answer_lower, criterion, config)
            feedback['criteria_scores'][criterion] = score
            total_score += score * config['weight']
        
        feedback['overall_score'] = min(100, max(0, total_score))
        
        # Generate strengths and improvements
        feedback['strengths'] = self._identify_strengths(answer_lower, question)
        feedback['improvements'] = self._identify_improvements(answer_lower, question)
        feedback['suggestions'] = self._generate_suggestions(feedback, question)
        feedback['follow_up_questions'] = self.question_generator.generate_followup_questions(
            answer, question.get('type', 'general')
        )
        
        return feedback
    
    def _score_criterion(self, answer: str, criterion: str, config: Dict[str, Any]) -> float:
        """Score answer for a specific criterion"""
        score = 50  # Base score
        
        # Check for positive indicators
        positive_count = sum(1 for indicator in config['indicators'] if indicator in answer)
        score += positive_count * 10
        
        # Check for negative indicators
        negative_count = sum(1 for indicator in config['negative_indicators'] if indicator in answer)
        score -= negative_count * 15
        
        # Length analysis
        word_count = len(answer.split())
        if criterion == 'depth':
            if word_count > 100:
                score += 10
            elif word_count < 30:
                score -= 20
        elif criterion == 'clarity':
            if 50 <= word_count <= 150:
                score += 10
            elif word_count > 200:
                score -= 10
        
        return min(100, max(0, score))
    
    def _identify_strengths(self, answer: str, question: Dict[str, Any]) -> List[str]:
        """Identify strengths in the answer"""
        strengths = []
        
        # Check for STAR method (Situation, Task, Action, Result)
        star_indicators = ['situation', 'task', 'action', 'result', 'outcome']
        star_count = sum(1 for indicator in star_indicators if indicator in answer)
        if star_count >= 3:
            strengths.append("Good use of STAR method for structured storytelling")
        
        # Check for specific examples
        if any(word in answer for word in ['example', 'project', 'time when', 'instance']):
            strengths.append("Provides specific examples and concrete details")
        
        # Check for quantification
        if any(char.isdigit() for char in answer):
            strengths.append("Uses quantifiable metrics and data")
        
        # Check for problem-solving approach
        problem_words = ['problem', 'challenge', 'solution', 'approach', 'strategy']
        if sum(1 for word in problem_words if word in answer) >= 2:
            strengths.append("Demonstrates problem-solving thinking")
        
        # Check for learning/growth
        learning_words = ['learned', 'improved', 'grew', 'developed', 'enhanced']
        if any(word in answer for word in learning_words):
            strengths.append("Shows learning and growth mindset")
        
        return strengths[:3]  # Return top 3 strengths
    
    def _identify_improvements(self, answer: str, question: Dict[str, Any]) -> List[str]:
        """Identify areas for improvement"""
        improvements = []
        
        # Check answer length
        word_count = len(answer.split())
        if word_count < 30:
            improvements.append("Consider providing more detailed responses")
        elif word_count > 200:
            improvements.append("Try to be more concise and focused")
        
        # Check for structure
        if not any(indicator in answer for indicator in ['first', 'then', 'finally', 'next']):
            improvements.append("Consider structuring your answer with clear progression")
        
        # Check for results/outcomes
        if not any(word in answer for word in ['result', 'outcome', 'impact', 'achieved']):
            improvements.append("Include the results and impact of your actions")
        
        # Check for specificity
        vague_words = ['thing', 'stuff', 'something', 'anything', 'everything']
        if sum(1 for word in vague_words if word in answer) > 1:
            improvements.append("Be more specific and avoid vague language")
        
        # Check for confidence indicators
        hesitant_words = ['maybe', 'perhaps', 'probably', 'might', 'could', 'try']
        if sum(1 for word in hesitant_words if word in answer) > 2:
            improvements.append("Speak with more confidence and conviction")
        
        return improvements[:3]  # Return top 3 improvements
    
    def _generate_suggestions(self, feedback: Dict[str, Any], question: Dict[str, Any]) -> List[str]:
        """Generate specific suggestions for improvement"""
        suggestions = []
        
        # Based on overall score
        if feedback['overall_score'] < 60:
            suggestions.append("Practice structuring your answers using the STAR method")
            suggestions.append("Prepare specific examples from your experience")
        elif feedback['overall_score'] < 80:
            suggestions.append("Add more quantifiable results to your answers")
            suggestions.append("Focus on the impact and outcomes of your actions")
        
        # Based on specific criteria
        if feedback['criteria_scores'].get('relevance', 0) < 70:
            suggestions.append("Ensure your answer directly addresses the question asked")
        
        if feedback['criteria_scores'].get('depth', 0) < 70:
            suggestions.append("Provide more detailed explanations and context")
        
        if feedback['criteria_scores'].get('clarity', 0) < 70:
            suggestions.append("Organize your thoughts before speaking for better clarity")
        
        # Question-specific suggestions
        question_type = question.get('type', 'general')
        if question_type == 'technical':
            suggestions.append("Be ready to discuss technical concepts in detail")
        elif question_type == 'behavioral':
            suggestions.append("Use specific examples from your work experience")
        elif question_type == 'situational':
            suggestions.append("Walk through your thought process step by step")
        
        return suggestions[:4]  # Return top 4 suggestions
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary"""
        if not self.user_answers:
            return {'error': 'No interview data available'}
        
        # Calculate overall performance
        overall_scores = [f['overall_score'] for f in self.feedback_scores]
        average_score = sum(overall_scores) / len(overall_scores)
        
        # Calculate criteria averages
        criteria_averages = {}
        for criterion in self.feedback_criteria.keys():
            scores = [f['criteria_scores'].get(criterion, 0) for f in self.feedback_scores]
            criteria_averages[criterion] = sum(scores) / len(scores)
        
        # Identify strengths and weaknesses
        all_strengths = []
        all_improvements = []
        for feedback in self.feedback_scores:
            all_strengths.extend(feedback['strengths'])
            all_improvements.extend(feedback['improvements'])
        
        # Count frequency of strengths and improvements
        strength_counts = {}
        for strength in all_strengths:
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        
        improvement_counts = {}
        for improvement in all_improvements:
            improvement_counts[improvement] = improvement_counts.get(improvement, 0) + 1
        
        # Get top strengths and improvements
        top_strengths = sorted(strength_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_improvements = sorted(improvement_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate grade
        grade = self._get_performance_grade(average_score)
        
        return {
            'session_summary': {
                'total_questions': len(self.user_answers),
                'average_score': round(average_score, 1),
                'grade': grade,
                'duration_minutes': len(self.conversation_history) * 2,  # Estimate
                'completion_time': datetime.now().isoformat()
            },
            'criteria_performance': criteria_averages,
            'top_strengths': [s[0] for s in top_strengths],
            'top_improvements': [i[0] for i in top_improvements],
            'detailed_feedback': self.feedback_scores,
            'recommendations': self._generate_final_recommendations(average_score, criteria_averages),
            'next_steps': self._generate_next_steps(grade, criteria_averages)
        }
    
    def _get_performance_grade(self, score: float) -> str:
        """Get performance grade based on score"""
        if score >= 90:
            return "Excellent"
        elif score >= 80:
            return "Good"
        elif score >= 70:
            return "Satisfactory"
        elif score >= 60:
            return "Needs Improvement"
        else:
            return "Significant Improvement Needed"
    
    def _generate_final_recommendations(self, overall_score: float, criteria_scores: Dict[str, float]) -> List[str]:
        """Generate final recommendations"""
        recommendations = []
        
        if overall_score < 70:
            recommendations.append("Practice more interview questions to build confidence")
            recommendations.append("Consider recording yourself to identify areas for improvement")
        
        # Criteria-specific recommendations
        if criteria_scores.get('clarity', 0) < 70:
            recommendations.append("Work on structuring your answers more clearly")
        
        if criteria_scores.get('relevance', 0) < 70:
            recommendations.append("Practice staying focused on the question asked")
        
        if criteria_scores.get('depth', 0) < 70:
            recommendations.append("Prepare more detailed examples from your experience")
        
        if criteria_scores.get('confidence', 0) < 70:
            recommendations.append("Practice speaking confidently about your achievements")
        
        return recommendations
    
    def _generate_next_steps(self, grade: str, criteria_scores: Dict[str, float]) -> List[str]:
        """Generate next steps for improvement"""
        next_steps = []
        
        if grade in ["Excellent", "Good"]:
            next_steps.extend([
                "Continue practicing with more advanced questions",
                "Focus on industry-specific knowledge",
                "Practice with mock interviews with peers"
            ])
        else:
            next_steps.extend([
                "Review fundamental interview techniques",
                "Practice with common behavioral questions",
                "Work on communication and presentation skills"
            ])
        
        # Add specific next steps based on weakest criteria
        weakest_criteria = min(criteria_scores.items(), key=lambda x: x[1])
        if weakest_criteria[0] == 'clarity':
            next_steps.append("Practice storytelling and structured communication")
        elif weakest_criteria[0] == 'depth':
            next_steps.append("Prepare detailed case studies from your experience")
        elif weakest_criteria[0] == 'relevance':
            next_steps.append("Practice active listening and question analysis")
        elif weakest_criteria[0] == 'confidence':
            next_steps.append("Practice positive self-talk and visualization techniques")
        
        return next_steps
    
    def export_session_data(self) -> Dict[str, Any]:
        """Export complete session data for analysis"""
        return {
            'session_info': {
                'start_time': self.conversation_history[0]['timestamp'] if self.conversation_history else None,
                'end_time': datetime.now().isoformat(),
                'total_questions': len(self.interview_questions),
                'completed_questions': len(self.user_answers)
            },
            'questions': self.interview_questions,
            'answers': self.user_answers,
            'feedback': self.feedback_scores,
            'conversation_history': self.conversation_history
        }

def render_interview_coach_interface():
    """Render the interview coach interface in Streamlit"""
    st.title("🎤 AI Interview Coach")
    st.write("Practice your interview skills with AI-powered feedback")
    
    # Initialize session state
    if 'interview_coach' not in st.session_state:
        st.session_state.interview_coach = AIInterviewCoach()
    if 'interview_session' not in st.session_state:
        st.session_state.interview_session = None
    if 'current_answer' not in st.session_state:
        st.session_state.current_answer = ""
    
    coach = st.session_state.interview_coach
    
    # Start new interview section
    if not st.session_state.interview_session:
        st.subheader("🚀 Start New Interview Session")
        
        col1, col2 = st.columns(2)
        with col1:
            role = st.selectbox(
                "Select Role",
                ["Software Engineer", "Web Developer", "Data Analyst", "Product Manager", "DevOps Engineer"]
            )
        
        with col2:
            # Get skills from previous analysis if available
            skills = st.session_state.get('resume_analysis', {}).get('extracted_skills', {})
            if not skills:
                skills = {'technical_skills': ['Python', 'JavaScript', 'SQL'], 'soft_skills': ['Communication']}
        
        if st.button("Start Interview", type="primary"):
            session_data = coach.start_interview_session(skills, role)
            st.session_state.interview_session = session_data
            st.rerun()
    
    # Active interview session
    elif st.session_state.interview_session:
        session = st.session_state.interview_session
        
        # Progress bar
        progress = coach.current_question_index / len(coach.interview_questions) * 100
        st.progress(progress / 100)
        st.write(f"Question {coach.current_question_index + 1} of {len(coach.interview_questions)}")
        
        # Current question
        current_question = coach.get_current_question()
        if current_question:
            st.subheader(f"📋 {current_question['section']}")
            st.write(f"**{current_question['question']}**")
            
            if current_question.get('tips'):
                st.info(f"💡 **Tip:** {current_question['tips']}")
            
            # Answer input
            answer = st.text_area(
                "Your Answer:",
                value=st.session_state.current_answer,
                height=150,
                help="Provide a detailed answer using the STAR method when applicable"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Submit Answer", type="primary"):
                    if answer.strip():
                        result = coach.submit_answer(answer)
                        
                        # Show feedback
                        feedback = result['feedback']
                        st.subheader("📊 AI Feedback")
                        
                        # Overall score
                        score_color = "green" if feedback['overall_score'] >= 80 else "orange" if feedback['overall_score'] >= 60 else "red"
                        st.markdown(f"**Overall Score:** <span style='color:{score_color}'>{feedback['overall_score']}/100</span>", unsafe_allow_html=True)
                        
                        # Criteria scores
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**Criteria Breakdown:**")
                            for criterion, score in feedback['criteria_scores'].items():
                                st.write(f"• {criterion.title()}: {score}/100")
                        
                        with col2:
                            if feedback['strengths']:
                                st.write("**Strengths:**")
                                for strength in feedback['strengths']:
                                    st.write(f"✅ {strength}")
                        
                        # Improvements and suggestions
                        if feedback['improvements']:
                            st.write("**Areas for Improvement:**")
                            for improvement in feedback['improvements']:
                                st.write(f"⚠️ {improvement}")
                        
                        if feedback['suggestions']:
                            st.write("**Suggestions:**")
                            for suggestion in feedback['suggestions']:
                                st.write(f"💡 {suggestion}")
                        
                        # Follow-up questions
                        if feedback['follow_up_questions']:
                            st.write("**Follow-up Questions to Consider:**")
                            for question in feedback['follow_up_questions']:
                                st.write(f"❓ {question}")
                        
                        # Check if interview is complete
                        if result['is_complete']:
                            st.success("🎉 Interview Complete! Generating your summary...")
                            summary = coach.get_session_summary()
                            
                            # Show summary
                            st.subheader("📈 Interview Summary")
                            st.write(f"**Overall Performance:** {summary['session_summary']['grade']} ({summary['session_summary']['average_score']}/100)")
                            
                            # Performance charts
                            import plotly.express as px
                            import pandas as pd
                            
                            # Criteria performance
                            criteria_df = pd.DataFrame(list(summary['criteria_performance'].items()), columns=['Criterion', 'Score'])
                            fig = px.bar(criteria_df, x='Criterion', y='Score', title='Performance by Criteria')
                            st.plotly_chart(fig)
                            
                            # Top strengths and improvements
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("**Top Strengths:**")
                                for strength in summary['top_strengths']:
                                    st.write(f"✅ {strength}")
                            
                            with col2:
                                st.write("**Key Improvements:**")
                                for improvement in summary['top_improvements']:
                                    st.write(f"🎯 {improvement}")
                            
                            # Recommendations
                            if summary['recommendations']:
                                st.write("**Recommendations:**")
                                for rec in summary['recommendations']:
                                    st.write(f"📚 {rec}")
                            
                            # Next steps
                            if summary['next_steps']:
                                st.write("**Next Steps:**")
                                for step in summary['next_steps']:
                                    st.write(f"🚀 {step}")
                            
                            if st.button("Start New Interview"):
                                st.session_state.interview_session = None
                                st.session_state.current_answer = ""
                                st.rerun()
                        
                        else:
                            # Continue to next question
                            if st.button("Next Question"):
                                st.session_state.current_answer = ""
                                st.rerun()
                    
                    else:
                        st.error("Please provide an answer before submitting")
            
            with col2:
                if st.button("Skip Question"):
                    coach.current_question_index += 1
                    st.session_state.current_answer = ""
                    st.rerun()
                
                if st.button("End Interview"):
                    summary = coach.get_session_summary()
                    st.session_state.interview_summary = summary
                    st.session_state.interview_session = None
                    st.rerun()
        
        else:
            st.error("No more questions available")
    
    # Show interview summary if available
    if 'interview_summary' in st.session_state:
        summary = st.session_state.interview_summary
        st.subheader("📊 Interview Summary")
        st.json(summary)
        
        if st.button("Start New Interview"):
            st.session_state.interview_summary = None
            st.session_state.current_answer = ""
            st.rerun()

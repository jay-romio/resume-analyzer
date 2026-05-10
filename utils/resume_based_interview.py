"""
Resume-Based Interview System
Analyzes resumes to generate skill-based questions with voice synthesis and answer analysis
"""
from __future__ import annotations

import time
import json
import re
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

from utils.ai_resume_analyzer import AIResumeAnalyzer
from utils.voice_stt import transcribe_openai_whisper_optional, transcribe_with_google
from utils.voice_tts import synthesize_interviewer_speech


class QuestionCategory(Enum):
    """Question categories based on resume skills"""
    TECHNICAL_SKILLS = "technical_skills"
    EXPERIENCE = "experience"
    PROJECTS = "projects"
    EDUCATION = "education"
    SOFT_SKILLS = "soft_skills"
    CERTIFICATIONS = "certifications"


class QuestionDifficulty(Enum):
    """Question difficulty levels"""
    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class ResumeSkill:
    """Skill extracted from resume"""
    name: str
    category: str
    experience_level: str
    years_of_experience: float = 0.0
    proficiency_level: str = "intermediate"
    projects_count: int = 0
    keywords: List[str] = field(default_factory=list)


@dataclass
class GeneratedQuestion:
    """Generated question based on resume skills"""
    id: str
    text: str
    category: QuestionCategory
    difficulty: QuestionDifficulty
    target_skills: List[str]
    expected_keywords: List[str]
    scoring_criteria: Dict[str, float]
    follow_up_suggestions: List[str]
    max_response_time: int = 120  # seconds


@dataclass
class AnswerAnalysis:
    """Analysis of user's answer"""
    question_id: str
    user_response: str
    response_time: float
    relevance_score: float
    completeness_score: float
    technical_accuracy_score: float
    communication_score: float
    overall_score: float
    matched_keywords: List[str]
    missing_keywords: List[str]
    strengths: List[str]
    improvements: List[str]
    detailed_feedback: str


class ResumeBasedInterview:
    """Resume-based interview system with voice synthesis and analysis"""
    
    def __init__(self):
        self.ai_analyzer = AIResumeAnalyzer()
        self.resume_skills: List[ResumeSkill] = []
        self.generated_questions: List[GeneratedQuestion] = []
        self.answer_analyses: List[AnswerAnalysis] = []
        self.current_question_index = 0
        self.interview_active = False
        
        # Voice synthesis settings
        self.tts_settings = {
            "voice": "professional",
            "rate": 1.0,
            "pitch": 1.0,
            "volume": 0.9
        }
        
        # Speech recognition settings
        self.stt_settings = {
            "engine": "whisper",
            "language": "en-US",
            "confidence_threshold": 0.8
        }
        
        # Question templates
        self.question_templates = self._load_question_templates()
        
        # Scoring weights
        self.scoring_weights = {
            "relevance": 0.30,
            "completeness": 0.25,
            "technical_accuracy": 0.30,
            "communication": 0.15
        }
    
    def _load_question_templates(self) -> Dict[str, Dict[str, List[str]]]:
        """Load question templates for different skill categories"""
        return {
            "technical_skills": {
                "basic": [
                    "Can you explain your experience with {skill}?",
                    "How would you rate your proficiency in {skill}?",
                    "What projects have you worked on using {skill}?"
                ],
                "intermediate": [
                    "Describe a challenging problem you solved using {skill}.",
                    "How do you stay updated with {skill} best practices?",
                    "What are the key considerations when working with {skill}?"
                ],
                "advanced": [
                    "Can you discuss the architecture of a system you built using {skill}?",
                    "How would you optimize performance for {skill} applications?",
                    "What are common pitfalls when implementing {skill} solutions?"
                ],
                "expert": [
                    "How would you design a scalable system using {skill}?",
                    "What are your thoughts on the future of {skill} in the industry?",
                    "Can you compare different approaches to {skill} implementation?"
                ]
            },
            "experience": {
                "basic": [
                    "Tell me about your role at {company}.",
                    "What were your main responsibilities at {company}?",
                    "How long did you work at {company}?"
                ],
                "intermediate": [
                    "Describe your biggest achievement at {company}.",
                    "What challenges did you face at {company}?",
                    "How did you contribute to team success at {company}?"
                ],
                "advanced": [
                    "How did your experience at {company} prepare you for this role?",
                    "What leadership opportunities did you have at {company}?",
                    "How did you drive innovation at {company}?"
                ],
                "expert": [
                    "What strategic decisions did you influence at {company}?",
                    "How did you measure your impact at {company}?",
                    "What lessons from {company} will you apply to future roles?"
                ]
            },
            "projects": {
                "basic": [
                    "Can you describe the {project} project?",
                    "What was your role in {project}?",
                    "What technologies did you use in {project}?"
                ],
                "intermediate": [
                    "What were the main challenges in {project}?",
                    "How did you ensure quality in {project}?",
                    "What was the outcome of {project}?"
                ],
                "advanced": [
                    "How did you approach the architecture of {project}?",
                    "What trade-offs did you make in {project}?",
                    "How would you improve {project} now?"
                ],
                "expert": [
                    "What was the business impact of {project}?",
                    "How did {project} align with organizational goals?",
                    "What innovations did you introduce in {project}?"
                ]
            },
            "soft_skills": {
                "basic": [
                    "How do you handle {skill} situations?",
                    "Can you give an example of your {skill}?",
                    "How important is {skill} in your role?"
                ],
                "intermediate": [
                    "Describe a time you demonstrated {skill} under pressure.",
                    "How do you develop your {skill} abilities?",
                    "What feedback have you received about your {skill}?"
                ],
                "advanced": [
                    "How do you measure the effectiveness of your {skill}?",
                    "How do you balance {skill} with other priorities?",
                    "How do you teach {skill} to others?"
                ],
                "expert": [
                    "How has your approach to {skill} evolved over your career?",
                    "What frameworks do you use for {skill} development?",
                    "How do you create a culture of {skill} in your team?"
                ]
            }
        }
    
    def analyze_resume(self, resume_text: str) -> List[ResumeSkill]:
        """Analyze resume text to extract skills"""
        try:
            # Use AI analyzer to extract skills
            analysis_result = self.ai_analyzer.analyze_resume(resume_text)
            
            # Extract skills from analysis
            extracted_skills = []
            
            # Extract skills from strengths (this is what the analyzer actually returns)
            if 'strengths' in analysis_result and analysis_result['strengths']:
                for strength in analysis_result['strengths']:
                    # Clean up the strength name
                    skill_name = strength.strip().lower()
                    
                    # Determine category based on skill content
                    category = self._categorize_skill(skill_name)
                    
                    # Determine experience level and proficiency based on content
                    experience_level, proficiency_level = self._assess_skill_level(skill_name)
                    
                    # Extract keywords from the skill name
                    keywords = [skill_name] + skill_name.split()
                    
                    skill = ResumeSkill(
                        name=skill_name,
                        category=category,
                        experience_level=experience_level,
                        years_of_experience=0.0,  # Can't determine from current analysis
                        proficiency_level=proficiency_level,
                        keywords=keywords
                    )
                    extracted_skills.append(skill)
            
            # Also extract from the full analysis text for more skills
            if 'full_response' in analysis_result:
                full_text = analysis_result['full_response'].lower()
                
                # Look for common technical skills
                technical_skills = self._extract_technical_skills_from_text(full_text)
                for tech_skill in technical_skills:
                    if not any(s.name.lower() == tech_skill.lower() for s in extracted_skills):
                        skill = ResumeSkill(
                            name=tech_skill,
                            category="technical",
                            experience_level="intermediate",
                            proficiency_level="intermediate",
                            keywords=[tech_skill]
                        )
                        extracted_skills.append(skill)
                
                # Look for soft skills
                soft_skills = self._extract_soft_skills_from_text(full_text)
                for soft_skill in soft_skills:
                    if not any(s.name.lower() == soft_skill.lower() for s in extracted_skills):
                        skill = ResumeSkill(
                            name=soft_skill,
                            category="soft_skills",
                            experience_level="intermediate",
                            proficiency_level="intermediate",
                            keywords=[soft_skill]
                        )
                        extracted_skills.append(skill)
            
            # FALLBACK: If no skills found, extract directly from resume text
            if not extracted_skills:
                extracted_skills = self._fallback_skill_extraction(resume_text)
            
            # If still no skills, add some default skills based on common patterns
            if not extracted_skills:
                extracted_skills = self._add_default_skills(resume_text)
            
            self.resume_skills = extracted_skills
            return extracted_skills
            
        except Exception as e:
            st.error(f"Error analyzing resume: {e}")
            return []
    
    def _fallback_skill_extraction(self, resume_text: str) -> List[ResumeSkill]:
        """Fallback skill extraction directly from resume text"""
        extracted_skills = []
        text_lower = resume_text.lower()
        
        # Enhanced technical skills patterns
        technical_patterns = {
            'programming_languages': [
                r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\btypescript\b',
                r'\bc\+\+\b', r'\bc#\b', r'\bphp\b', r'\bruby\b', r'\bscala\b',
                r'\bgo\b', r'\brust\b', r'\bswift\b', r'\bkotlin\b', r'\bperl\b'
            ],
            'web_technologies': [
                r'\breact\b', r'\bvue\b', r'\bangular\b', r'\bnode\.?js\b', r'\bexpress\b',
                r'\bdjango\b', r'\bflask\b', r'\bspring\b', r'\blaravel\b',
                r'\bhtml\b', r'\bcss\b', r'\bsass\b', r'\bless\b', r'\bbootstrap\b',
                r'\btailwind\b', r'\bjquery\b', r'\bwebpack\b'
            ],
            'databases': [
                r'\bsql\b', r'\bmysql\b', r'\bpostgresql\b', r'\bmongodb\b',
                r'\bredis\b', r'\belasticsearch\b', r'\bcassandra\b', r'\bdynamodb\b',
                r'\boracle\b', r'\bsqlite\b', r'\bfirebase\b'
            ],
            'cloud_devops': [
                r'\baws\b', r'\bazure\b', r'\bgcp\b', r'\bdocker\b', r'\bkubernetes\b',
                r'\bjenkins\b', r'\bgitlab\b', r'\bcircleci\b', r'\btower\b',
                r'\bterraform\b', r'\bansible\b', r'\bpuppet\b', r'\bchef\b'
            ],
            'tools_frameworks': [
                r'\bgit\b', r'\bgithub\b', r'\bgitlab\b', r'\bbitbucket\b',
                r'\bjira\b', r'\btrello\b', r'\bslack\b', r'\bvs code\b',
                r'\bintellij\b', r'\beclipse\b', r'\bvisual studio\b'
            ],
            'data_science': [
                r'\bmachine learning\b', r'\bdata science\b', r'\bdeep learning\b',
                r'\btensorflow\b', r'\bpytorch\b', r'\bscikit-learn\b', r'\bnumpy\b',
                r'\bpandas\b', r'\bmatplotlib\b', r'\bseaborn\b', r'\btableau\b',
                r'\bpower bi\b', r'\bspark\b', r'\bhadoop\b'
            ],
            'mobile': [
                r'\bandroid\b', r'\bios\b', r'\breact native\b', r'\bflutter\b',
                r'\bswift\b', r'\bkotlin\b', r'\bobjective-c\b', r'\bxamarin\b'
            ]
        }
        
        import re
        # Extract technical skills
        for category, patterns in technical_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                for match in matches:
                    skill_name = match.strip()
                    if skill_name and not any(s.name.lower() == skill_name.lower() for s in extracted_skills):
                        skill = ResumeSkill(
                            name=skill_name,
                            category="technical",
                            experience_level="intermediate",
                            proficiency_level="intermediate",
                            keywords=[skill_name]
                        )
                        extracted_skills.append(skill)
        
        # Extract soft skills
        soft_skill_patterns = [
            r'\bleadership\b', r'\bcommunication\b', r'\bteamwork\b', r'\bcollaboration\b',
            r'\bproblem solving\b', r'\banalytical thinking\b', r'\bcritical thinking\b',
            r'\bproject management\b', r'\btime management\b', r'\badaptability\b',
            r'\bcreativity\b', r'\binnovation\b', r'\borganization\b', r'\bplanning\b',
            r'\battention to detail\b', r'\bmultitasking\b', r'\bdecision making\b',
            r'\bnegotiation\b', r'\bconflict resolution\b', r'\bmentoring\b', r'\bcoaching\b'
        ]
        
        for pattern in soft_skill_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                skill_name = match.strip()
                if skill_name and not any(s.name.lower() == skill_name.lower() for s in extracted_skills):
                    skill = ResumeSkill(
                        name=skill_name,
                        category="soft_skills",
                        experience_level="intermediate",
                        proficiency_level="intermediate",
                        keywords=[skill_name]
                    )
                    extracted_skills.append(skill)
        
        return extracted_skills
    
    def _add_default_skills(self, resume_text: str) -> List[ResumeSkill]:
        """Add default skills based on resume content analysis"""
        extracted_skills = []
        text_lower = resume_text.lower()
        
        # Check for common job titles and add relevant skills
        job_title_skills = {
            'software engineer': ['python', 'javascript', 'git', 'problem solving'],
            'data scientist': ['python', 'machine learning', 'data analysis', 'statistics'],
            'web developer': ['html', 'css', 'javascript', 'react', 'web development'],
            'mobile developer': ['mobile development', 'app development'],
            'devops engineer': ['docker', 'kubernetes', 'ci/cd', 'cloud computing'],
            'project manager': ['project management', 'leadership', 'communication'],
            'business analyst': ['business analysis', 'requirements gathering', 'stakeholder management']
        }
        
        for job_title, skills in job_title_skills.items():
            if job_title in text_lower:
                for skill in skills:
                    if not any(s.name.lower() == skill.lower() for s in extracted_skills):
                        category = "technical" if skill in ['python', 'javascript', 'git', 'docker', 'kubernetes', 'html', 'css'] else "soft_skills"
                        skill_obj = ResumeSkill(
                            name=skill,
                            category=category,
                            experience_level="intermediate",
                            proficiency_level="intermediate",
                            keywords=[skill]
                        )
                        extracted_skills.append(skill_obj)
        
        # If still no skills, add some basic ones
        if not extracted_skills:
            basic_skills = [
                ResumeSkill("communication", "soft_skills", "intermediate", 0.0, "intermediate", ["communication"]),
                ResumeSkill("problem solving", "soft_skills", "intermediate", 0.0, "intermediate", ["problem solving"]),
                ResumeSkill("teamwork", "soft_skills", "intermediate", 0.0, "intermediate", ["teamwork"])
            ]
            
            # Add some technical skills based on common patterns
            if any(word in text_lower for word in ['software', 'developer', 'engineer', 'programming']):
                basic_skills.extend([
                    ResumeSkill("software development", "technical", "intermediate", 0.0, "intermediate", ["software", "development"]),
                    ResumeSkill("programming", "technical", "intermediate", 0.0, "intermediate", ["programming"])
                ])
            
            extracted_skills = basic_skills
        
        return extracted_skills
    
    def _categorize_skill(self, skill_name: str) -> str:
        """Categorize skill based on content"""
        skill_lower = skill_name.lower()
        
        # Technical skills indicators
        technical_indicators = [
            'python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'azure', 'docker',
            'kubernetes', 'machine learning', 'ai', 'data science', 'tensorflow', 'pytorch',
            'git', 'github', 'ci/cd', 'devops', 'microservices', 'api', 'rest',
            'mongodb', 'postgresql', 'mysql', 'redis', 'elasticsearch', 'spark',
            'hadoop', 'big data', 'analytics', 'visualization', 'tableau', 'power bi',
            'html', 'css', 'typescript', 'angular', 'vue', 'django', 'flask',
            'algorithms', 'data structures', 'system design', 'architecture'
        ]
        
        # Soft skills indicators
        soft_indicators = [
            'leadership', 'communication', 'teamwork', 'problem solving', 'analytical',
            'collaboration', 'project management', 'time management', 'adaptability',
            'creativity', 'critical thinking', 'attention to detail', 'organization'
        ]
        
        # Check for technical skills
        for tech in technical_indicators:
            if tech in skill_lower or tech in skill_name:
                return "technical"
        
        # Check for soft skills
        for soft in soft_indicators:
            if soft in skill_lower or soft in skill_name:
                return "soft_skills"
        
        # Default to general
        return "general"
    
    def _assess_skill_level(self, skill_name: str) -> Tuple[str, str]:
        """Assess skill level based on name and context"""
        skill_lower = skill_name.lower()
        
        # Look for expertise indicators
        expert_indicators = ['expert', 'senior', 'lead', 'principal', 'architect']
        advanced_indicators = ['advanced', 'experienced', 'senior', 'specialized']
        intermediate_indicators = ['intermediate', 'proficient', 'skilled']
        
        if any(indicator in skill_lower for indicator in expert_indicators):
            return "expert", "expert"
        elif any(indicator in skill_lower for indicator in advanced_indicators):
            return "advanced", "advanced"
        elif any(indicator in skill_lower for indicator in intermediate_indicators):
            return "intermediate", "intermediate"
        else:
            return "basic", "basic"
    
    def _extract_technical_skills_from_text(self, text: str) -> List[str]:
        """Extract technical skills from analysis text"""
        technical_skills = []
        
        # Common technical skill patterns
        tech_patterns = [
            r'\bpython\b', r'\bjava\b', r'\bjavascript\b', r'\breact\b', r'\bnode\.?js\b',
            r'\bsql\b', r'\baws\b', r'\bazure\b', r'\bdocker\b',
            r'\bkubernetes\b', r'\bgit\b', r'\bgithub\b',
            r'\bapi\b', r'\brest\b', r'\bgraphql\b',
            r'\bmongodb\b', r'\bpostgresql\b', r'\bmysql\b',
            r'\bredis\b', r'\belasticsearch\b',
            r'\bmachine learning\b', r'\bai\b', r'\bdata science\b',
            r'\btensorflow\b', r'\bpytorch\b', r'\bscikit-learn\b',
            r'\bhtml\b', r'\bcss\b', r'\btypescript\b',
            r'\bangular\b', r'\bvue\b', r'\bdjango\b', r'\bflask\b',
            r'\balgorithms\b', r'\bdata structures\b', r'\bsystem design\b'
        ]
        
        import re
        for pattern in tech_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                found_skill = match.strip()
                if found_skill and found_skill not in technical_skills:
                    technical_skills.append(found_skill)
        
        return technical_skills
    
    def _extract_soft_skills_from_text(self, text: str) -> List[str]:
        """Extract soft skills from analysis text"""
        soft_skills = []
        
        # Common soft skill patterns
        soft_patterns = [
            r'\bleadership\b', r'\bcommunication\b', r'\bteamwork\b', r'\bcollaboration\b',
            r'\bproblem solving\b', r'\banalytical\b', r'\bcritical thinking\b',
            r'\bproject management\b', r'\btime management\b', r'\badaptability\b',
            r'\bcreativity\b', r'\borganization\b', r'\battention to detail\b'
        ]
        
        import re
        for pattern in soft_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                found_skill = match.strip()
                if found_skill and found_skill not in soft_skills:
                    soft_skills.append(found_skill)
        
        return soft_skills
    
    def _determine_experience_level(self, skill_data: Dict[str, Any]) -> str:
        """Determine experience level from skill data"""
        if 'proficiency' in skill_data:
            proficiency = skill_data['proficiency'].lower()
            if 'expert' in proficiency or 'advanced' in proficiency:
                return "advanced"
            elif 'intermediate' in proficiency:
                return "intermediate"
            else:
                return "basic"
        return "intermediate"
    
    def _extract_years_experience(self, skill_data: Dict[str, Any]) -> float:
        """Extract years of experience from skill data"""
        if 'years' in skill_data:
            return float(skill_data['years'])
        elif 'duration' in skill_data:
            # Extract years from duration string
            duration_str = str(skill_data['duration'])
            years_match = re.search(r'(\d+)\s*year', duration_str)
            if years_match:
                return float(years_match.group(1))
        return 0.0
    
    def _extract_proficiency(self, skill_data: Dict[str, Any]) -> str:
        """Extract proficiency level from skill data"""
        if 'proficiency' in skill_data:
            return skill_data['proficiency']
        return "intermediate"
    
    def _extract_keywords(self, skill_data: Dict[str, Any]) -> List[str]:
        """Extract keywords from skill data"""
        keywords = []
        
        # Add skill name
        if 'name' in skill_data:
            keywords.append(skill_data['name'])
        
        # Add technologies
        if 'technologies' in skill_data:
            keywords.extend(skill_data['technologies'])
        
        # Add description keywords
        if 'description' in skill_data:
            desc_words = skill_data['description'].split()
            keywords.extend([word for word in desc_words if len(word) > 3])
        
        return list(set(keywords))  # Remove duplicates
    
    def generate_skill_based_questions(self, num_questions: int = 10) -> List[GeneratedQuestion]:
        """Generate questions based on extracted skills"""
        questions = []
        
        if not self.resume_skills:
            return questions
        
        # Categorize skills
        categorized_skills = {}
        for skill in self.resume_skills:
            if skill.category not in categorized_skills:
                categorized_skills[skill.category] = []
            categorized_skills[skill.category].append(skill)
        
        # Generate questions for each category
        question_id = 1
        
        for category, skills in categorized_skills.items():
            # Determine number of questions for this category
            category_questions = min(len(skills), max(1, num_questions // len(categorized_skills)))
            
            for i, skill in enumerate(skills[:category_questions]):
                # Determine difficulty based on experience level
                difficulty = self._determine_question_difficulty(skill)
                
                # Generate question
                question = self._generate_question_for_skill(skill, difficulty, question_id)
                questions.append(question)
                question_id += 1
        
        # Fill remaining slots with general questions if needed
        while len(questions) < num_questions and self.resume_skills:
            skill = self.resume_skills[len(questions) % len(self.resume_skills)]
            difficulty = QuestionDifficulty.INTERMEDIATE
            question = self._generate_question_for_skill(skill, difficulty, question_id)
            questions.append(question)
            question_id += 1
        
        self.generated_questions = questions
        return questions
    
    def _determine_question_difficulty(self, skill: ResumeSkill) -> QuestionDifficulty:
        """Determine question difficulty based on skill level"""
        if skill.experience_level == "expert":
            return QuestionDifficulty.ADVANCED
        elif skill.experience_level == "advanced":
            return QuestionDifficulty.INTERMEDIATE
        elif skill.years_of_experience >= 5:
            return QuestionDifficulty.INTERMEDIATE
        else:
            return QuestionDifficulty.BASIC
    
    def _generate_question_for_skill(self, skill: ResumeSkill, difficulty: QuestionDifficulty, question_id: int) -> GeneratedQuestion:
        """Generate a specific question for a skill"""
        # Get template
        templates = self.question_templates.get(skill.category, {})
        difficulty_templates = templates.get(difficulty.value, ["Tell me about your experience with {skill}."])
        
        # Select template
        template = difficulty_templates[question_id % len(difficulty_templates)]
        
        # Generate question text
        question_text = template.format(skill=skill.name)
        
        # Determine category
        category_map = {
            "technical": QuestionCategory.TECHNICAL_SKILLS,
            "soft_skills": QuestionCategory.SOFT_SKILLS,
            "experience": QuestionCategory.EXPERIENCE,
            "projects": QuestionCategory.PROJECTS,
            "education": QuestionCategory.EDUCATION,
            "certifications": QuestionCategory.CERTIFICATIONS
        }
        
        category = category_map.get(skill.category, QuestionCategory.TECHNICAL_SKILLS)
        
        # Generate expected keywords
        expected_keywords = skill.keywords.copy()
        if skill.name not in expected_keywords:
            expected_keywords.append(skill.name)
        
        # Generate scoring criteria
        scoring_criteria = {
            "keyword_match": 0.4,
            "detail_level": 0.3,
            "relevance": 0.2,
            "communication": 0.1
        }
        
        # Generate follow-up suggestions
        follow_ups = self._generate_follow_ups(skill, difficulty)
        
        return GeneratedQuestion(
            id=f"q_{question_id}",
            text=question_text,
            category=category,
            difficulty=difficulty,
            target_skills=[skill.name],
            expected_keywords=expected_keywords,
            scoring_criteria=scoring_criteria,
            follow_up_suggestions=follow_ups,
            max_response_time=120
        )
    
    def _generate_follow_ups(self, skill: ResumeSkill, difficulty: QuestionDifficulty) -> List[str]:
        """Generate follow-up suggestions based on skill and difficulty"""
        follow_ups = []
        
        if skill.category == "technical":
            follow_ups = [
                f"Can you provide a specific example of how you used {skill.name}?",
                f"What challenges did you face while working with {skill.name}?",
                f"How would you explain {skill.name} to a non-technical person?"
            ]
        elif skill.category == "experience":
            follow_ups = [
                "What was your biggest accomplishment in this role?",
                "How did you collaborate with your team?",
                "What did you learn from this experience?"
            ]
        elif skill.category == "projects":
            follow_ups = [
                "What was the business impact of this project?",
                "How did you handle project challenges?",
                "What would you do differently now?"
            ]
        else:
            follow_ups = [
                "Can you give me a specific example?",
                "How did you measure success?",
                "What feedback did you receive?"
            ]
        
        return follow_ups[:2]  # Return top 2 follow-ups
    
    def get_next_question(self) -> Optional[GeneratedQuestion]:
        """Get the next question to ask"""
        if self.current_question_index < len(self.generated_questions):
            question = self.generated_questions[self.current_question_index]
            self.current_question_index += 1
            return question
        return None
    
    def synthesize_question_audio(self, question_text: str) -> bytes:
        """Synthesize audio for the question"""
        try:
            # Use voice TTS to synthesize
            audio_data = synthesize_interviewer_speech(question_text)
            return audio_data
        except Exception as e:
            st.error(f"Error synthesizing speech: {e}")
            return b""
    
    def capture_user_response(self) -> Tuple[str, float]:
        """Capture user response via speech-to-text"""
        try:
            # Simulate speech capture
            with st.spinner("Listening..."):
                time.sleep(2)  # Simulate recording time
                
                # Use speech-to-text
                transcribed_text, confidence = transcribe_openai_whisper_optional(b"")
                
                if not transcribed_text:
                    transcribed_text, confidence = transcribe_with_google(b"")
                
                # If still no result, use demo text
                if not transcribed_text:
                    demo_responses = [
                        "I have extensive experience with this technology and have used it in multiple projects.",
                        "I worked on several projects where I implemented solutions using these skills.",
                        "I have good experience in this area and have successfully delivered results."
                    ]
                    import random
                    transcribed_text = random.choice(demo_responses)
                    confidence = 0.85
                
                response_time = 30.0  # Simulated response time
                
                return transcribed_text, confidence
                
        except Exception as e:
            st.error(f"Error capturing response: {e}")
            return "", 0.0
    
    def analyze_answer(self, question: GeneratedQuestion, user_response: str, response_time: float) -> AnswerAnalysis:
        """Analyze user's answer and calculate score"""
        # Calculate relevance score
        relevance_score = self._calculate_relevance_score(question, user_response)
        
        # Calculate completeness score
        completeness_score = self._calculate_completeness_score(user_response, question.max_response_time)
        
        # Calculate technical accuracy score
        technical_score = self._calculate_technical_accuracy_score(question, user_response)
        
        # Calculate communication score
        communication_score = self._calculate_communication_score(user_response)
        
        # Calculate overall score
        overall_score = (
            relevance_score * self.scoring_weights["relevance"] +
            completeness_score * self.scoring_weights["completeness"] +
            technical_score * self.scoring_weights["technical_accuracy"] +
            communication_score * self.scoring_weights["communication"]
        )
        
        # Identify matched and missing keywords
        matched_keywords, missing_keywords = self._analyze_keyword_match(question, user_response)
        
        # Generate strengths and improvements
        strengths, improvements = self._generate_feedback_points(
            relevance_score, completeness_score, technical_score, communication_score
        )
        
        # Generate detailed feedback
        detailed_feedback = self._generate_detailed_feedback(
            question, user_response, overall_score, strengths, improvements
        )
        
        analysis = AnswerAnalysis(
            question_id=question.id,
            user_response=user_response,
            response_time=response_time,
            relevance_score=relevance_score,
            completeness_score=completeness_score,
            technical_accuracy_score=technical_score,
            communication_score=communication_score,
            overall_score=overall_score,
            matched_keywords=matched_keywords,
            missing_keywords=missing_keywords,
            strengths=strengths,
            improvements=improvements,
            detailed_feedback=detailed_feedback
        )
        
        self.answer_analyses.append(analysis)
        return analysis
    
    def _calculate_relevance_score(self, question: GeneratedQuestion, user_response: str) -> float:
        """Calculate relevance score based on keyword matching"""
        response_lower = user_response.lower()
        expected_keywords = [kw.lower() for kw in question.expected_keywords]
        
        matched_count = sum(1 for keyword in expected_keywords if keyword in response_lower)
        total_keywords = len(expected_keywords)
        
        if total_keywords == 0:
            return 75.0  # Default score if no keywords
        
        relevance = (matched_count / total_keywords) * 100
        
        # Bonus for multiple matches
        if matched_count >= 2:
            relevance += 10
        
        return min(100.0, relevance)
    
    def _calculate_completeness_score(self, user_response: str, max_time: float) -> float:
        """Calculate completeness score based on response length and detail"""
        word_count = len(user_response.split())
        
        # Expected minimum words for a complete answer
        min_words = 20
        ideal_words = 50
        
        if word_count < min_words:
            return (word_count / min_words) * 60
        elif word_count <= ideal_words:
            return 60 + ((word_count - min_words) / (ideal_words - min_words)) * 30
        else:
            return 90 + min(10, (word_count - ideal_words) / 20)
    
    def _calculate_technical_accuracy_score(self, question: GeneratedQuestion, user_response: str) -> float:
        """Calculate technical accuracy score"""
        # Check for technical indicators
        technical_indicators = [
            "implemented", "developed", "designed", "architected", "built",
            "created", "deployed", "optimized", "configured", "integrated"
        ]
        
        response_lower = user_response.lower()
        technical_count = sum(1 for indicator in technical_indicators if indicator in response_lower)
        
        # Base score
        base_score = 60.0
        
        # Add technical indicators bonus
        technical_bonus = min(30, technical_count * 8)
        
        # Check for specific examples
        example_indicators = ["for example", "specifically", "such as", "in particular"]
        example_bonus = min(10, sum(1 for indicator in example_indicators if indicator in response_lower) * 3)
        
        return min(100.0, base_score + technical_bonus + example_bonus)
    
    def _calculate_communication_score(self, user_response: str) -> float:
        """Calculate communication score"""
        # Check for clear structure
        sentences = [s.strip() for s in re.split(r'[.!?]+', user_response) if s.strip()]
        
        if not sentences:
            return 30.0
        
        # Average sentence length
        words = user_response.split()
        avg_sentence_length = len(words) / len(sentences)
        
        # Ideal range: 10-20 words per sentence
        if 10 <= avg_sentence_length <= 20:
            structure_score = 100.0
        else:
            structure_score = max(50.0, 100.0 - abs(avg_sentence_length - 15) * 3)
        
        # Check for professional language
        professional_words = [
            "collaborated", "managed", "led", "coordinated", "developed",
            "implemented", "achieved", "delivered", "optimized", "improved"
        ]
        
        response_lower = user_response.lower()
        professional_count = sum(1 for word in professional_words if word in response_lower)
        professional_score = min(50.0, professional_count * 10)
        
        return (structure_score + professional_score) / 2
    
    def _analyze_keyword_match(self, question: GeneratedQuestion, user_response: str) -> Tuple[List[str], List[str]]:
        """Analyze which keywords were matched and which were missed"""
        response_lower = user_response.lower()
        expected_keywords = [kw.lower() for kw in question.expected_keywords]
        
        matched_keywords = [kw for kw in expected_keywords if kw in response_lower]
        missing_keywords = [kw for kw in expected_keywords if kw not in response_lower]
        
        return matched_keywords, missing_keywords
    
    def _generate_feedback_points(self, relevance: float, completeness: float, technical: float, communication: float) -> Tuple[List[str], List[str]]:
        """Generate strengths and improvement points"""
        strengths = []
        improvements = []
        
        # Strengths
        if relevance >= 80:
            strengths.append("Excellent relevance to the question")
        if completeness >= 80:
            strengths.append("Comprehensive and detailed response")
        if technical >= 80:
            strengths.append("Strong technical accuracy")
        if communication >= 80:
            strengths.append("Clear and professional communication")
        
        # Improvements
        if relevance < 60:
            improvements.append("Focus more on the specific question asked")
        if completeness < 60:
            improvements.append("Provide more detail and specific examples")
        if technical < 60:
            improvements.append("Include more technical details and terminology")
        if communication < 60:
            improvements.append("Work on structuring your response more clearly")
        
        return strengths, improvements
    
    def _generate_detailed_feedback(self, question: GeneratedQuestion, user_response: str, overall_score: float, strengths: List[str], improvements: List[str]) -> str:
        """Generate detailed feedback for the user"""
        feedback_parts = []
        
        # Overall assessment
        if overall_score >= 85:
            feedback_parts.append("Excellent response! You demonstrated strong understanding and communication skills.")
        elif overall_score >= 70:
            feedback_parts.append("Good response with room for improvement in specific areas.")
        elif overall_score >= 55:
            feedback_parts.append("Fair response. Focus on the improvement areas mentioned.")
        else:
            feedback_parts.append("The response needs significant improvement. Consider the feedback points carefully.")
        
        # Add strengths
        if strengths:
            feedback_parts.append("Strengths: " + ", ".join(strengths))
        
        # Add improvements
        if improvements:
            feedback_parts.append("Areas for improvement: " + ", ".join(improvements))
        
        # Add specific suggestions based on question category
        if question.category == QuestionCategory.TECHNICAL_SKILLS:
            feedback_parts.append("For technical questions, try to include specific examples of implementation and discuss challenges faced.")
        elif question.category == QuestionCategory.EXPERIENCE:
            feedback_parts.append("For experience questions, focus on quantifiable achievements and specific outcomes.")
        elif question.category == QuestionCategory.PROJECTS:
            feedback_parts.append("For project questions, emphasize your role, the approach taken, and the business impact.")
        
        return " ".join(feedback_parts)
    
    def get_interview_summary(self) -> Dict[str, Any]:
        """Get comprehensive interview summary"""
        if not self.answer_analyses:
            return {"message": "No interview data available"}
        
        # Calculate overall scores
        avg_relevance = sum(a.relevance_score for a in self.answer_analyses) / len(self.answer_analyses)
        avg_completeness = sum(a.completeness_score for a in self.answer_analyses) / len(self.answer_analyses)
        avg_technical = sum(a.technical_accuracy_score for a in self.answer_analyses) / len(self.answer_analyses)
        avg_communication = sum(a.communication_score for a in self.answer_analyses) / len(self.answer_analyses)
        avg_overall = sum(a.overall_score for a in self.answer_analyses) / len(self.answer_analyses)
        
        # Performance distribution
        performance_levels = {"Excellent": 0, "Good": 0, "Fair": 0, "Poor": 0}
        for analysis in self.answer_analyses:
            if analysis.overall_score >= 85:
                performance_levels["Excellent"] += 1
            elif analysis.overall_score >= 70:
                performance_levels["Good"] += 1
            elif analysis.overall_score >= 55:
                performance_levels["Fair"] += 1
            else:
                performance_levels["Poor"] += 1
        
        # Category performance
        category_performance = {}
        for analysis in self.answer_analyses:
            question = next((q for q in self.generated_questions if q.id == analysis.question_id), None)
            if question:
                category = question.category.value
                if category not in category_performance:
                    category_performance[category] = []
                category_performance[category].append(analysis.overall_score)
        
        category_avg = {cat: sum(scores) / len(scores) for cat, scores in category_performance.items()}
        
        # Common strengths and improvements
        all_strengths = []
        all_improvements = []
        for analysis in self.answer_analyses:
            all_strengths.extend(analysis.strengths)
            all_improvements.extend(analysis.improvements)
        
        # Count frequency
        from collections import Counter
        common_strengths = Counter(all_strengths).most_common(3)
        common_improvements = Counter(all_improvements).most_common(3)
        
        return {
            "interview_overview": {
                "total_questions": len(self.generated_questions),
                "questions_answered": len(self.answer_analyses),
                "resume_skills_analyzed": len(self.resume_skills)
            },
            "performance_summary": {
                "average_relevance": avg_relevance,
                "average_completeness": avg_completeness,
                "average_technical": avg_technical,
                "average_communication": avg_communication,
                "average_overall": avg_overall,
                "final_grade": self._calculate_grade(avg_overall)
            },
            "performance_distribution": performance_levels,
            "category_performance": category_avg,
            "common_strengths": [{"strength": strength, "count": count} for strength, count in common_strengths],
            "common_improvements": [{"improvement": improvement, "count": count} for improvement, count in common_improvements],
            "detailed_responses": [
                {
                    "question_id": analysis.question_id,
                    "question": next((q.text for q in self.generated_questions if q.id == analysis.question_id), ""),
                    "user_response": analysis.user_response,
                    "overall_score": analysis.overall_score,
                    "feedback": analysis.detailed_feedback
                }
                for analysis in self.answer_analyses
            ]
        }
    
    def _calculate_grade(self, score: float) -> str:
        """Calculate letter grade"""
        if score >= 90:
            return "A+"
        elif score >= 85:
            return "A"
        elif score >= 80:
            return "A-"
        elif score >= 75:
            return "B+"
        elif score >= 70:
            return "B"
        elif score >= 65:
            return "B-"
        elif score >= 60:
            return "C+"
        elif score >= 55:
            return "C"
        elif score >= 50:
            return "C-"
        else:
            return "D"
    
    def reset_interview(self):
        """Reset interview state"""
        self.generated_questions.clear()
        self.answer_analyses.clear()
        self.current_question_index = 0
        self.interview_active = False

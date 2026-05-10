"""
Enhanced Skill Extraction and ATS Scoring System
"""
import re
import spacy
import nltk
from typing import Dict, List, Tuple, Set, Any
from collections import Counter
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Download required NLTK data (NLTK 3.9+ uses punkt_tab for tokenizers)
def _ensure_nltk_resource(name: str, find_path: str) -> None:
    try:
        nltk.data.find(find_path)
    except LookupError:
        nltk.download(name, quiet=True)


_ensure_nltk_resource("punkt_tab", "tokenizers/punkt_tab/english/")
_ensure_nltk_resource("punkt", "tokenizers/punkt")
_ensure_nltk_resource("stopwords", "corpora/stopwords")

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize

class EnhancedSkillExtractor:
    """Advanced skill extraction with multiple techniques"""
    
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            self.nlp = spacy.blank("en")
        
        # Enhanced skill categories
        self.skill_categories = {
            'technical': {
                'programming_languages': [
                    'python', 'java', 'javascript', 'c++', 'c#', 'ruby', 'php', 'swift',
                    'kotlin', 'go', 'rust', 'typescript', 'scala', 'perl', 'r', 'matlab'
                ],
                'web_technologies': [
                    'html', 'css', 'react', 'angular', 'vue', 'nodejs', 'express', 'django',
                    'flask', 'spring', 'laravel', 'rails', 'asp.net', 'bootstrap', 'jquery'
                ],
                'databases': [
                    'mysql', 'postgresql', 'mongodb', 'sqlite', 'redis', 'oracle', 'sql server',
                    'cassandra', 'elasticsearch', 'firebase', 'dynamodb'
                ],
                'cloud_platforms': [
                    'aws', 'azure', 'google cloud', 'gcp', 'heroku', 'digitalocean', 'vercel',
                    'netlify', 'cloudflare', 'alibaba cloud'
                ],
                'devops_tools': [
                    'docker', 'kubernetes', 'jenkins', 'gitlab', 'github', 'terraform', 'ansible',
                    'circleci', 'travis ci', 'bamboo', 'puppet', 'chef'
                ],
                'data_science': [
                    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'jupyter',
                    'tableau', 'power bi', 'excel', 'spss', 'sas', 'matplotlib', 'seaborn'
                ],
                'mobile_development': [
                    'react native', 'flutter', 'swift', 'kotlin', 'android studio', 'xcode',
                    'cordova', 'ionic', 'unity'
                ]
            },
            'soft_skills': {
                'communication': [
                    'communication', 'public speaking', 'presentation', 'writing', 'listening',
                    'negotiation', 'interpersonal', 'storytelling', 'documentation'
                ],
                'leadership': [
                    'leadership', 'management', 'team building', 'mentoring', 'delegation',
                    'strategic planning', 'decision making', 'problem solving', 'critical thinking'
                ],
                'collaboration': [
                    'teamwork', 'collaboration', 'agile', 'scrum', 'kanban', 'cross-functional',
                    'partnership', 'networking', 'relationship building'
                ],
                'adaptability': [
                    'adaptability', 'flexibility', 'learning', 'curiosity', 'innovation',
                    'creativity', 'time management', 'organization', 'multitasking'
                ]
            },
            'tools_software': {
                'productivity': [
                    'microsoft office', 'office 365', 'google workspace', 'slack', 'trello',
                    'asana', 'notion', 'jira', 'confluence', 'zoom', 'teams'
                ],
                'design': [
                    'photoshop', 'illustrator', 'figma', 'sketch', 'adobe xd', 'canva',
                    'invision', 'zeplin', 'framer', 'webflow'
                ],
                'development_tools': [
                    'vs code', 'intellij', 'eclipse', 'visual studio', 'xcode', 'android studio',
                    'postman', 'git', 'github desktop', 'gitkraken', 'source tree'
                ]
            }
        }
        
        # Create comprehensive skill list
        self.all_skills = []
        for category in self.skill_categories.values():
            for subcategory in category.values():
                self.all_skills.extend(subcategory)
        
        # Initialize TF-IDF vectorizer
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
    
    def extract_skills_advanced(self, text: str) -> Dict[str, Any]:
        """Extract skills using multiple advanced techniques"""
        text_lower = text.lower()
        doc = self.nlp(text)
        
        extracted_skills = {
            'technical_skills': set(),
            'soft_skills': set(),
            'tools_software': set(),
            'skill_confidence': {},
            'skill_context': {},
            'total_skills_found': 0
        }
        
        # 1. Pattern-based extraction
        pattern_skills = self._extract_patterns(text_lower)
        
        # 2. NLP-based extraction
        nlp_skills = self._extract_nlp_entities(doc)
        
        # 3. Context-based extraction
        context_skills = self._extract_contextual(text_lower)
        
        # 4. Combine and categorize skills
        all_found_skills = pattern_skills.union(nlp_skills).union(context_skills)
        
        for skill in all_found_skills:
            category, confidence = self._categorize_skill(skill, text_lower)
            if category and confidence > 0.5:
                extracted_skills[category].add(skill)
                extracted_skills['skill_confidence'][skill] = confidence
                extracted_skills['skill_context'][skill] = self._get_skill_context(skill, text_lower)
        
        # Convert sets to lists and sort by confidence
        for category in ['technical_skills', 'soft_skills', 'tools_software']:
            skills = list(extracted_skills[category])
            skills.sort(key=lambda x: extracted_skills['skill_confidence'].get(x, 0), reverse=True)
            extracted_skills[category] = skills
        
        extracted_skills['total_skills_found'] = len(all_found_skills)
        
        return extracted_skills
    
    def _extract_patterns(self, text: str) -> Set[str]:
        """Extract skills using regex patterns"""
        found_skills = set()
        
        # Create skill patterns
        for category in self.skill_categories.values():
            for subcategory, skills in category.items():
                for skill in skills:
                    # Create various patterns for the skill
                    patterns = [
                        rf'\b{re.escape(skill)}\b',
                        rf'\b{re.escape(skill.replace(" ", "[-_\\s]"))}\b',
                        rf'\b{re.escape(skill.replace(" ", ""))}\b'
                    ]
                    
                    for pattern in patterns:
                        if re.search(pattern, text, re.IGNORECASE):
                            found_skills.add(skill.lower())
                            break
        
        return found_skills
    
    def _extract_nlp_entities(self, doc) -> Set[str]:
        """Extract skills using NLP entity recognition"""
        found_skills = set()
        
        # Extract noun phrases and check against skills
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            if chunk_text in self.all_skills:
                found_skills.add(chunk_text)
        
        # Extract named entities
        for ent in doc.ents:
            ent_text = ent.text.lower()
            if ent_text in self.all_skills:
                found_skills.add(ent_text)
        
        return found_skills
    
    def _extract_contextual(self, text: str) -> Set[str]:
        """Extract skills based on context clues"""
        found_skills = set()
        
        # Context indicators for skills
        context_patterns = [
            r'(?:experience with|skilled in|proficient in|knowledge of|familiar with|expert in)\s+([^.]+)',
            r'(?:using|utilizing|leveraging|implemented|developed|designed)\s+([^.]+)',
            r'(?:technologies|tools|skills|languages|frameworks|platforms):\s*([^.]+)',
            r'(?:stack|tech stack|technology stack):\s*([^.]+)'
        ]
        
        for pattern in context_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract potential skills from context
                words = re.findall(r'\b\w+(?:[-_]\w+)*\b', match.lower())
                for word in words:
                    if word in self.all_skills:
                        found_skills.add(word)
        
        return found_skills
    
    def _categorize_skill(self, skill: str, text: str) -> Tuple[str, float]:
        """Categorize skill and return confidence score"""
        skill_lower = skill.lower()
        
        # Check each category
        for category_name, category_data in self.skill_categories.items():
            for subcategory, skills in category_data.items():
                if skill_lower in [s.lower() for s in skills]:
                    # Calculate confidence based on context
                    confidence = self._calculate_confidence(skill_lower, text, category_name)
                    return category_name, confidence
        
        return "", 0.0
    
    def _calculate_confidence(self, skill: str, text: str, category: str) -> float:
        """Calculate confidence score for skill extraction"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on multiple mentions
        mentions = text.count(skill)
        confidence += min(mentions * 0.1, 0.3)
        
        # Boost confidence based on context
        context_boosters = {
            'technical_skills': ['experience', 'developed', 'implemented', 'used', 'skilled'],
            'soft_skills': ['demonstrated', 'showed', 'excellent', 'strong', 'proven'],
            'tools_software': ['using', 'utilizing', 'proficient', 'expert', 'knowledge']
        }
        
        for booster in context_boosters.get(category, []):
            if booster in text.lower():
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _get_skill_context(self, skill: str, text: str) -> str:
        """Extract context around skill mention"""
        sentences = sent_tokenize(text)
        for sentence in sentences:
            if skill.lower() in sentence.lower():
                return sentence.strip()
        return ""
    
    def get_skill_gaps(self, extracted_skills: Dict[str, Any], job_requirements: Dict[str, List[str]]) -> Dict[str, Any]:
        """Analyze skill gaps between extracted skills and job requirements"""
        all_extracted = set()
        for category_skills in extracted_skills.values():
            if isinstance(category_skills, list):
                all_extracted.update([s.lower() for s in category_skills])
        
        all_required = set()
        for category_skills in job_requirements.values():
            all_required.update([s.lower() for s in category_skills])
        
        matched_skills = all_extracted.intersection(all_required)
        missing_skills = all_required - all_extracted
        additional_skills = all_extracted - all_required
        
        return {
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'additional_skills': list(additional_skills),
            'match_percentage': len(matched_skills) / len(all_required) * 100 if all_required else 0,
            'total_required': len(all_required),
            'total_matched': len(matched_skills),
            'total_missing': len(missing_skills)
        }

class EnhancedATSScorer:
    """Advanced ATS scoring system"""
    
    def __init__(self):
        self.skill_extractor = EnhancedSkillExtractor()
        
        # Job role requirements database
        self.job_requirements = {
            'Software Engineer': {
                'technical': ['python', 'java', 'javascript', 'git', 'sql', 'algorithms', 'data structures'],
                'soft': ['problem solving', 'teamwork', 'communication', 'critical thinking'],
                'tools': ['vs code', 'git', 'jira', 'docker']
            },
            'Web Developer': {
                'technical': ['html', 'css', 'javascript', 'react', 'nodejs', 'api', 'responsive design'],
                'soft': ['creativity', 'attention to detail', 'communication', 'adaptability'],
                'tools': ['vs code', 'chrome devtools', 'figma', 'git']
            },
            'Data Analyst': {
                'technical': ['python', 'sql', 'excel', 'tableau', 'statistics', 'data visualization'],
                'soft': ['analytical thinking', 'attention to detail', 'communication', 'problem solving'],
                'tools': ['excel', 'tableau', 'python', 'sql', 'jupyter']
            },
            'Product Manager': {
                'technical': ['product management', 'agile', 'scrum', 'data analysis', 'user research'],
                'soft': ['leadership', 'communication', 'strategic thinking', 'stakeholder management'],
                'tools': ['jira', 'confluence', 'figma', 'google analytics']
            },
            'DevOps Engineer': {
                'technical': ['docker', 'kubernetes', 'aws', 'ci/cd', 'linux', 'networking'],
                'soft': ['problem solving', 'automation', 'collaboration', 'continuous learning'],
                'tools': ['docker', 'kubernetes', 'jenkins', 'aws', 'terraform']
            }
        }
    
    def calculate_ats_score(self, resume_text: str, target_role: str) -> Dict[str, Any]:
        """Calculate comprehensive ATS score"""
        # Extract skills from resume
        extracted_skills = self.skill_extractor.extract_skills_advanced(resume_text)
        
        # Get job requirements
        job_reqs = self.job_requirements.get(target_role, {})
        
        # Analyze skill gaps
        skill_gaps = self.skill_extractor.get_skill_gaps(extracted_skills, job_reqs)
        
        # Calculate various score components
        keyword_score = self._calculate_keyword_score(resume_text, job_reqs)
        skills_score = skill_gaps['match_percentage']
        structure_score = self._calculate_structure_score(resume_text)
        experience_score = self._calculate_experience_score(resume_text)
        education_score = self._calculate_education_score(resume_text)
        
        # Calculate overall ATS score
        weights = {
            'keyword_score': 0.3,
            'skills_score': 0.3,
            'structure_score': 0.2,
            'experience_score': 0.15,
            'education_score': 0.05
        }
        
        overall_score = (
            keyword_score * weights['keyword_score'] +
            skills_score * weights['skills_score'] +
            structure_score * weights['structure_score'] +
            experience_score * weights['experience_score'] +
            education_score * weights['education_score']
        )
        
        return {
            'overall_score': round(overall_score, 1),
            'component_scores': {
                'keyword_score': round(keyword_score, 1),
                'skills_score': round(skills_score, 1),
                'structure_score': round(structure_score, 1),
                'experience_score': round(experience_score, 1),
                'education_score': round(education_score, 1)
            },
            'extracted_skills': extracted_skills,
            'skill_gaps': skill_gaps,
            'recommendations': self._generate_recommendations(skill_gaps, extracted_skills),
            'grade': self._get_grade(overall_score)
        }
    
    def _calculate_keyword_score(self, text: str, job_reqs: Dict[str, List[str]]) -> float:
        """Calculate keyword matching score"""
        text_lower = text.lower()
        all_keywords = []
        for category_skills in job_reqs.values():
            all_keywords.extend([k.lower() for k in category_skills])
        
        found_keywords = sum(1 for keyword in all_keywords if keyword in text_lower)
        return (found_keywords / len(all_keywords)) * 100 if all_keywords else 0
    
    def _calculate_structure_score(self, text: str) -> float:
        """Calculate resume structure score"""
        score = 0
        text_lower = text.lower()
        
        # Check for essential sections
        sections = {
            'experience': ['experience', 'work experience', 'employment', 'professional experience'],
            'education': ['education', 'academic', 'qualification', 'degree'],
            'skills': ['skills', 'technical skills', 'competencies', 'expertise'],
            'contact': ['email', 'phone', 'address', 'linkedin', 'github'],
            'summary': ['summary', 'objective', 'profile', 'about']
        }
        
        for section, indicators in sections.items():
            if any(indicator in text_lower for indicator in indicators):
                score += 20
        
        return min(score, 100)
    
    def _calculate_experience_score(self, text: str) -> float:
        """Calculate experience relevance score"""
        text_lower = text.lower()
        
        # Experience indicators
        experience_indicators = [
            'years of experience', 'year of experience', '+ years', 'worked at',
            'employed at', 'position', 'role', 'responsibilities', 'achievements'
        ]
        
        score = 0
        for indicator in experience_indicators:
            if indicator in text_lower:
                score += 20
        
        return min(score, 100)
    
    def _calculate_education_score(self, text: str) -> float:
        """Calculate education relevance score"""
        text_lower = text.lower()
        
        education_indicators = [
            'bachelor', 'master', 'phd', 'degree', 'university', 'college',
            'graduated', 'gpa', 'certification', 'diploma'
        ]
        
        score = 0
        for indicator in education_indicators:
            if indicator in text_lower:
                score += 20
        
        return min(score, 100)
    
    def _generate_recommendations(self, skill_gaps: Dict[str, Any], extracted_skills: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        # Skill gap recommendations
        if skill_gaps['missing_skills']:
            recommendations.append(
                f"Add these key skills: {', '.join(skill_gaps['missing_skills'][:5])}"
            )
        
        # Skills quantity recommendations
        total_skills = extracted_skills['total_skills_found']
        if total_skills < 10:
            recommendations.append("Consider adding more relevant skills to strengthen your profile")
        elif total_skills > 50:
            recommendations.append("Consider focusing on the most relevant skills to avoid dilution")
        
        # Technical skills balance
        tech_skills = len(extracted_skills.get('technical_skills', []))
        soft_skills = len(extracted_skills.get('soft_skills', []))
        
        if tech_skills < soft_skills:
            recommendations.append("Add more technical skills to better match job requirements")
        elif soft_skills < tech_skills / 3:
            recommendations.append("Add more soft skills to show well-rounded capabilities")
        
        # ATS optimization tips
        recommendations.extend([
            "Use standard section headings (Experience, Education, Skills)",
            "Include keywords from the job description naturally",
            "Quantify achievements with numbers and metrics",
            "Keep formatting simple and ATS-friendly"
        ])
        
        return recommendations
    
    def _get_grade(self, score: float) -> str:
        """Get grade based on score"""
        if score >= 90:
            return "A+ (Excellent)"
        elif score >= 80:
            return "A (Very Good)"
        elif score >= 70:
            return "B (Good)"
        elif score >= 60:
            return "C (Average)"
        elif score >= 50:
            return "D (Below Average)"
        else:
            return "F (Needs Improvement)"
    
    def compare_multiple_roles(self, resume_text: str, roles: List[str]) -> Dict[str, Any]:
        """Compare resume against multiple job roles"""
        results = {}
        
        for role in roles:
            if role in self.job_requirements:
                results[role] = self.calculate_ats_score(resume_text, role)
        
        # Find best fit
        best_role = max(results.keys(), key=lambda x: results[x]['overall_score'])
        
        return {
            'role_comparisons': results,
            'best_fit_role': best_role,
            'best_fit_score': results[best_role]['overall_score'],
            'recommendations': self._generate_role_recommendations(results)
        }
    
    def _generate_role_recommendations(self, results: Dict[str, Dict[str, Any]]) -> List[str]:
        """Generate role-specific recommendations"""
        recommendations = []
        
        # Find top 3 roles
        sorted_roles = sorted(results.keys(), key=lambda x: results[x]['overall_score'], reverse=True)[:3]
        
        recommendations.append(f"Top matching roles: {', '.join(sorted_roles)}")
        
        # Role-specific advice
        best_role = sorted_roles[0]
        best_score = results[best_role]['overall_score']
        
        if best_score >= 80:
            recommendations.append(f"Strong match for {best_role}! Focus on highlighting relevant experience")
        elif best_score >= 60:
            recommendations.append(f"Good potential for {best_role}. Consider adding missing key skills")
        else:
            recommendations.append(f"Consider additional experience or training for {best_role}")
        
        return recommendations

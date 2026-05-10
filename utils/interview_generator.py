"""
AI-Powered Interview Question Generator
"""
import random
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class InterviewQuestionGenerator:
    """Generate personalized interview questions based on resume skills and experience"""
    
    def __init__(self):
        # Question templates and databases
        self.technical_questions = {
            'programming_languages': {
                'python': [
                    "What are Python's key features and advantages?",
                    "Explain Python's GIL (Global Interpreter Lock) and its implications.",
                    "How does Python handle memory management?",
                    "What are Python decorators and how do you use them?",
                    "Explain the difference between lists and tuples in Python.",
                    "How do you handle exceptions in Python?",
                    "What are Python's built-in data structures?",
                    "Explain list comprehensions and generator expressions."
                ],
                'java': [
                    "What is the difference between JDK, JRE, and JVM?",
                    "Explain Java's garbage collection mechanism.",
                    "What are Java's access modifiers?",
                    "Explain the concept of polymorphism in Java.",
                    "What is the difference between abstract classes and interfaces?",
                    "How does Java handle multithreading?",
                    "What are Java collections and their types?",
                    "Explain the Spring framework and its benefits."
                ],
                'javascript': [
                    "What is the difference between let, const, and var?",
                    "Explain closures in JavaScript with examples.",
                    "What is hoisting in JavaScript?",
                    "How does JavaScript handle asynchronous operations?",
                    "Explain the difference between == and === in JavaScript.",
                    "What are JavaScript promises and async/await?",
                    "How does prototypal inheritance work in JavaScript?",
                    "What is the event loop in JavaScript?"
                ],
                'sql': [
                    "What is the difference between INNER JOIN and OUTER JOIN?",
                    "Explain database normalization and its forms.",
                    "What are database indexes and how do they work?",
                    "How do you optimize SQL queries?",
                    "What is the difference between WHERE and HAVING clauses?",
                    "Explain transactions and ACID properties.",
                    "What are database stored procedures?",
                    "How do you handle NULL values in SQL?"
                ]
            },
            'web_technologies': {
                'react': [
                    "What is the virtual DOM and how does React use it?",
                    "Explain React component lifecycle methods.",
                    "What are React hooks and how do they work?",
                    "How do you manage state in React applications?",
                    "What is the difference between props and state?",
                    "Explain React's context API.",
                    "How does React handle forms?",
                    "What are React's performance optimization techniques?"
                ],
                'html': [
                    "What is the difference between HTML4 and HTML5?",
                    "Explain semantic HTML and its benefits.",
                    "What are HTML5 semantic elements?",
                    "How do you optimize HTML for performance?",
                    "What is the difference between block and inline elements?",
                    "Explain HTML forms and validation.",
                    "What are HTML data attributes?",
                    "How do you ensure HTML accessibility?"
                ],
                'css': [
                    "What is the CSS box model?",
                    "Explain CSS specificity and how it works.",
                    "What are CSS Grid and Flexbox?",
                    "How do you optimize CSS for performance?",
                    "What are CSS preprocessors and their benefits?",
                    "Explain responsive design principles.",
                    "What are CSS animations and transitions?",
                    "How do you handle CSS cross-browser compatibility?"
                ]
            },
            'databases': {
                'mysql': [
                    "What are MySQL storage engines?",
                    "How do you optimize MySQL database performance?",
                    "What are MySQL transactions?",
                    "Explain MySQL indexing strategies.",
                    "How do you backup and restore MySQL databases?",
                    "What are MySQL triggers and stored procedures?",
                    "How do you handle MySQL security?",
                    "What are MySQL replication types?"
                ],
                'mongodb': [
                    "What is NoSQL and when would you use it?",
                    "Explain MongoDB's document structure.",
                    "What are MongoDB indexes?",
                    "How does MongoDB handle relationships?",
                    "What is the aggregation pipeline in MongoDB?",
                    "How do you optimize MongoDB queries?",
                    "What are MongoDB replication and sharding?",
                    "How do you secure MongoDB databases?"
                ]
            },
            'cloud_platforms': {
                'aws': [
                    "What is AWS and its key services?",
                    "Explain EC2 instances and their types.",
                    "What is S3 and how do you use it?",
                    "How does AWS handle security and compliance?",
                    "What are AWS Lambda and serverless computing?",
                    "Explain AWS VPC and networking.",
                    "How do you monitor AWS resources?",
                    "What are AWS best practices for cost optimization?"
                ],
                'azure': [
                    "What is Microsoft Azure and its core services?",
                    "Explain Azure Virtual Machines.",
                    "What is Azure Blob Storage?",
                    "How does Azure handle identity and access management?",
                    "What are Azure Functions and serverless computing?",
                    "Explain Azure networking concepts.",
                    "How do you monitor Azure resources?",
                    "What are Azure's compliance and security features?"
                ]
            }
        }
        
        self.behavioral_questions = {
            'teamwork': [
                "Describe a situation where you had to work with a difficult team member. How did you handle it?",
                "Tell me about a time you had to collaborate with others to achieve a goal.",
                "How do you handle conflicts within a team?",
                "Describe your ideal team environment.",
                "How do you contribute to team meetings and discussions?",
                "Tell me about a time you had to lead a team project.",
                "How do you handle disagreements with your colleagues?",
                "Describe a situation where you had to mentor a team member."
            ],
            'problem_solving': [
                "Describe a complex problem you solved recently.",
                "Tell me about a time you had to think outside the box.",
                "How do you approach unfamiliar challenges?",
                "Describe a situation where you had to make a quick decision.",
                "Tell me about a time you failed and what you learned.",
                "How do you handle pressure and tight deadlines?",
                "Describe a situation where you had to analyze data to make a decision.",
                "Tell me about a time you improved a process."
            ],
            'leadership': [
                "Describe your leadership style.",
                "Tell me about a time you had to motivate others.",
                "How do you handle underperforming team members?",
                "Describe a situation where you had to take initiative.",
                "How do you delegate tasks effectively?",
                "Tell me about a time you had to make an unpopular decision.",
                "How do you develop your team members' skills?",
                "Describe a situation where you had to manage change."
            ],
            'communication': [
                "How do you explain technical concepts to non-technical people?",
                "Describe a situation where you had to present complex information.",
                "How do you handle difficult conversations?",
                "Tell me about a time you had to persuade someone.",
                "How do you ensure effective communication in remote teams?",
                "Describe a situation where miscommunication caused problems.",
                "How do you adapt your communication style?",
                "Tell me about a time you had to give constructive feedback."
            ],
            'adaptability': [
                "Describe a situation where you had to adapt to change quickly.",
                "How do you stay updated with new technologies?",
                "Tell me about a time you had to learn something new quickly.",
                "How do you handle ambiguity and uncertainty?",
                "Describe a situation where you had to pivot your approach.",
                "How do you manage competing priorities?",
                "Tell me about a time you had to work with new technologies.",
                "How do you handle unexpected challenges?"
            ]
        }
        
        self.situational_questions = {
            'project_management': [
                "You're working on a project with a tight deadline. A team member is falling behind. What do you do?",
                "How would you handle a project that's going over budget?",
                "Describe how you would prioritize features in a new product.",
                "How do you ensure quality while meeting deadlines?",
                "What would you do if a stakeholder changes requirements mid-project?",
                "How do you handle resource allocation in projects?",
                "Describe your approach to risk management in projects.",
                "How do you measure project success?"
            ],
            'technical_challenges': [
                "How would you debug a complex issue in production?",
                "Describe your approach to system design.",
                "How would you handle a system outage?",
                "What would you do if you discovered a security vulnerability?",
                "How do you approach performance optimization?",
                "Describe how you would scale a system.",
                "How do you handle technical debt?",
                "What would you do if you disagreed with a technical decision?"
            ],
            'client_interactions': [
                "How would you handle a client who is unhappy with the work?",
                "Describe how you would gather requirements from a client.",
                "How do you manage client expectations?",
                "What would you do if a client requests something outside the scope?",
                "How do you present technical solutions to clients?",
                "Describe how you would handle a difficult client conversation.",
                "How do you build trust with clients?",
                "What would you do if a client doesn't know what they want?"
            ]
        }
    
    def generate_interview_questions(
        self, 
        skills: Dict[str, Any], 
        experience_level: str = "mid",
        question_count: int = 10,
        question_types: List[str] = None
    ) -> Dict[str, Any]:
        """Generate personalized interview questions based on skills and experience"""
        
        if question_types is None:
            question_types = ['technical', 'behavioral', 'situational']
        
        generated_questions = {
            'technical_questions': [],
            'behavioral_questions': [],
            'situational_questions': [],
            'total_questions': 0,
            'generation_time': datetime.now().isoformat(),
            'experience_level': experience_level,
            'skill_based_questions': []
        }
        
        # Generate technical questions based on skills
        technical_questions = self._generate_technical_questions(skills, experience_level)
        generated_questions['technical_questions'] = technical_questions[:question_count // 3]
        
        # Generate behavioral questions
        behavioral_questions = self._generate_behavioral_questions(skills, experience_level)
        generated_questions['behavioral_questions'] = behavioral_questions[:question_count // 3]
        
        # Generate situational questions
        situational_questions = self._generate_situational_questions(skills, experience_level)
        generated_questions['situational_questions'] = situational_questions[:question_count // 3]
        
        # Generate skill-specific questions
        skill_questions = self._generate_skill_specific_questions(skills)
        generated_questions['skill_based_questions'] = skill_questions[:question_count // 3]
        
        # Calculate total
        generated_questions['total_questions'] = (
            len(generated_questions['technical_questions']) +
            len(generated_questions['behavioral_questions']) +
            len(generated_questions['situational_questions']) +
            len(generated_questions['skill_based_questions'])
        )
        
        return generated_questions
    
    def _generate_technical_questions(self, skills: Dict[str, Any], experience_level: str) -> List[Dict[str, str]]:
        """Generate technical questions based on extracted skills"""
        questions = []
        
        # Get technical skills
        tech_skills = skills.get('technical_skills', [])
        
        for skill in tech_skills[:10]:  # Limit to top 10 skills
            skill_lower = skill.lower()
            
            # Find matching questions in our database
            for category, skill_questions in self.technical_questions.items():
                for skill_name, question_list in skill_questions.items():
                    if skill_name in skill_lower or skill_lower in skill_name:
                        for question in random.sample(question_list, min(3, len(question_list))):
                            questions.append({
                                'question': question,
                                'category': category,
                                'skill': skill,
                                'difficulty': self._get_difficulty_level(experience_level),
                                'type': 'technical'
                            })
                        break
        
        return questions
    
    def _generate_behavioral_questions(self, skills: Dict[str, Any], experience_level: str) -> List[Dict[str, str]]:
        """Generate behavioral questions"""
        questions = []
        
        # Select relevant behavioral categories based on skills
        behavioral_categories = ['teamwork', 'problem_solving', 'communication']
        
        if len(skills.get('technical_skills', [])) > 10:
            behavioral_categories.append('leadership')
        
        for category in behavioral_categories:
            if category in self.behavioral_questions:
                category_questions = self.behavioral_questions[category]
                selected_questions = random.sample(
                    category_questions, 
                    min(3, len(category_questions))
                )
                
                for question in selected_questions:
                    questions.append({
                        'question': question,
                        'category': category,
                        'skill': 'behavioral',
                        'difficulty': self._get_difficulty_level(experience_level),
                        'type': 'behavioral'
                    })
        
        return questions
    
    def _generate_situational_questions(self, skills: Dict[str, Any], experience_level: str) -> List[Dict[str, str]]:
        """Generate situational questions"""
        questions = []
        
        # Select relevant situational categories
        situational_categories = ['technical_challenges', 'project_management']
        
        if len(skills.get('technical_skills', [])) > 5:
            situational_categories.append('client_interactions')
        
        for category in situational_categories:
            if category in self.situational_questions:
                category_questions = self.situational_questions[category]
                selected_questions = random.sample(
                    category_questions, 
                    min(2, len(category_questions))
                )
                
                for question in selected_questions:
                    questions.append({
                        'question': question,
                        'category': category,
                        'skill': 'situational',
                        'difficulty': self._get_difficulty_level(experience_level),
                        'type': 'situational'
                    })
        
        return questions
    
    def _generate_skill_specific_questions(self, skills: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate questions specific to the candidate's skill set"""
        questions = []
        
        # Combine all skills
        all_skills = []
        all_skills.extend(skills.get('technical_skills', []))
        all_skills.extend(skills.get('soft_skills', []))
        all_skills.extend(skills.get('tools_software', []))
        
        # Generate custom questions for top skills
        for skill in all_skills[:5]:
            custom_questions = [
                f"Can you describe a project where you used {skill} extensively?",
                f"What challenges did you face while working with {skill}?",
                f"How do you stay updated with {skill} best practices?",
                f"What's your experience level with {skill} and how have you improved?",
                f"Can you compare {skill} with similar technologies you've used?"
            ]
            
            for question in random.sample(custom_questions, min(2, len(custom_questions))):
                questions.append({
                    'question': question,
                    'category': 'skill_specific',
                    'skill': skill,
                    'difficulty': 'medium',
                    'type': 'skill_specific'
                })
        
        return questions
    
    def _get_difficulty_level(self, experience_level: str) -> str:
        """Get question difficulty based on experience level"""
        difficulty_map = {
            'entry': ['easy', 'medium'],
            'mid': ['medium', 'hard'],
            'senior': ['hard', 'expert'],
            'lead': ['expert', 'advanced']
        }
        
        difficulties = difficulty_map.get(experience_level, ['medium'])
        return random.choice(difficulties)
    
    def generate_mock_interview(
        self, 
        skills: Dict[str, Any], 
        role: str = "Software Engineer",
        duration_minutes: int = 30
    ) -> Dict[str, Any]:
        """Generate a complete mock interview structure"""
        
        # Calculate question distribution based on duration
        total_questions = max(5, duration_minutes // 3)
        
        question_distribution = {
            'introduction': 1,
            'technical': total_questions // 3,
            'behavioral': total_questions // 3,
            'situational': total_questions // 4,
            'closing': 1
        }
        
        # Generate questions
        all_questions = self.generate_interview_questions(
            skills, 
            experience_level="mid",
            question_count=total_questions
        )
        
        # Structure the interview
        interview_structure = {
            'role': role,
            'duration_minutes': duration_minutes,
            'total_questions': total_questions,
            'sections': [
                {
                    'section': 'Introduction',
                    'duration_minutes': 2,
                    'questions': [
                        {
                            'question': "Tell me about yourself and your experience.",
                            'type': 'introduction',
                            'tips': "Focus on relevant experience and key achievements."
                        }
                    ]
                }
            ],
            'tips': self._generate_interview_tips(role),
            'evaluation_criteria': self._generate_evaluation_criteria(role)
        }
        
        # Add technical section
        if all_questions['technical_questions']:
            interview_structure['sections'].append({
                'section': 'Technical Assessment',
                'duration_minutes': duration_minutes // 3,
                'questions': all_questions['technical_questions'][:question_distribution['technical']]
            })
        
        # Add behavioral section
        if all_questions['behavioral_questions']:
            interview_structure['sections'].append({
                'section': 'Behavioral Questions',
                'duration_minutes': duration_minutes // 3,
                'questions': all_questions['behavioral_questions'][:question_distribution['behavioral']]
            })
        
        # Add situational section
        if all_questions['situational_questions']:
            interview_structure['sections'].append({
                'section': 'Situational Questions',
                'duration_minutes': duration_minutes // 4,
                'questions': all_questions['situational_questions'][:question_distribution['situational']]
            })
        
        # Add closing section
        interview_structure['sections'].append({
            'section': 'Closing',
            'duration_minutes': 3,
            'questions': [
                {
                    'question': "Do you have any questions for us?",
                    'type': 'closing',
                    'tips': "Prepare thoughtful questions about the role, team, and company."
                }
            ]
        })
        
        return interview_structure
    
    def _generate_interview_tips(self, role: str) -> List[str]:
        """Generate interview tips for the specific role"""
        general_tips = [
            "Research the company and role beforehand",
            "Prepare specific examples using the STAR method",
            "Practice common interview questions",
            "Dress professionally and be punctual",
            "Bring copies of your resume",
            "Prepare questions to ask the interviewer"
        ]
        
        role_specific_tips = {
            'Software Engineer': [
                "Be ready to solve coding problems",
                "Review data structures and algorithms",
                "Prepare to discuss your projects in detail",
                "Be ready for system design questions"
            ],
            'Web Developer': [
                "Prepare to discuss your portfolio",
                "Review HTML, CSS, and JavaScript concepts",
                "Be ready to discuss responsive design",
                "Prepare to talk about frameworks you've used"
            ],
            'Data Analyst': [
                "Prepare to discuss data analysis projects",
            "Review statistical concepts",
            "Be ready to discuss data visualization",
            "Prepare to talk about tools and software"
            ]
        }
        
        tips = general_tips + role_specific_tips.get(role, [])
        return tips[:10]  # Return top 10 tips
    
    def _generate_evaluation_criteria(self, role: str) -> Dict[str, List[str]]:
        """Generate evaluation criteria for the role"""
        criteria = {
            'Software Engineer': {
                'technical': [
                    "Problem-solving ability",
                    "Code quality and structure",
                    "Algorithm knowledge",
                    "System design understanding",
                    "Testing and debugging skills"
                ],
                'behavioral': [
                    "Communication skills",
                    "Team collaboration",
                    "Problem-solving approach",
                    "Learning attitude",
                    "Time management"
                ]
            },
            'Web Developer': {
                'technical': [
                    "HTML/CSS proficiency",
                    "JavaScript knowledge",
                    "Framework expertise",
                    "Responsive design skills",
                    "Browser compatibility knowledge"
                ],
                'behavioral': [
                    "Attention to detail",
                    "Creativity",
                    "User experience focus",
                    "Collaboration skills",
                    "Adaptability"
                ]
            },
            'Data Analyst': {
                'technical': [
                    "Data analysis skills",
                    "Statistical knowledge",
                    "Tool proficiency",
                    "Data visualization",
                    "SQL expertise"
                ],
                'behavioral': [
                    "Analytical thinking",
                    "Attention to detail",
                    "Communication skills",
                    "Business acumen",
                    "Problem-solving approach"
                ]
            }
        }
        
        return criteria.get(role, {
            'technical': ["Technical knowledge", "Problem-solving skills"],
            'behavioral': ["Communication", "Teamwork", "Adaptability"]
        })
    
    def generate_followup_questions(self, initial_answer: str, question_type: str) -> List[str]:
        """Generate follow-up questions based on initial answers"""
        followup_templates = {
            'technical': [
                "Can you elaborate on the technical challenges you faced?",
                "What alternative approaches did you consider?",
                "How would you improve your solution?",
                "What did you learn from this experience?"
            ],
            'behavioral': [
                "What was the specific outcome of this situation?",
                "How did this experience change your approach?",
                "What would you do differently now?",
                "How did you measure the success of your actions?"
            ],
            'situational': [
                "What factors would you consider in this situation?",
                "How would you prioritize your actions?",
                "What resources would you need?",
                "How would you measure success?"
            ]
        }
        
        return followup_templates.get(question_type, ["Can you provide more details?"])

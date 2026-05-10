"""
Skill Learning Roadmap Generator
"""
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import json

class SkillLearningRoadmapGenerator:
    """Generate personalized skill learning roadmaps"""
    
    def __init__(self):
        # Skill database with learning paths
        self.skill_database = {
            'programming_languages': {
                'python': {
                    'difficulty': 'beginner',
                    'time_to_learn': '2-3 months',
                    'prerequisites': [],
                    'learning_path': [
                        'Basic syntax and data types',
                        'Control flow and functions',
                        'Object-oriented programming',
                        'Data structures (lists, dictionaries, sets)',
                        'File handling and exceptions',
                        'Modules and packages',
                        'Basic algorithms and problem solving'
                    ],
                    'resources': {
                        'courses': [
                            'Python for Everybody (Coursera)',
                            'Complete Python Bootcamp (Udemy)',
                            'Python Official Tutorial'
                        ],
                        'projects': [
                            'Build a calculator',
                            'Create a to-do list app',
                            'Build a simple web scraper',
                            'Develop a text-based game'
                        ],
                        'practice_platforms': [
                            'LeetCode (Python)',
                            'HackerRank',
                            'Codewars',
                            'Exercism'
                        ]
                    },
                    'career_impact': 'High - Versatile language used in web development, data science, AI, and automation'
                },
                'javascript': {
                    'difficulty': 'beginner',
                    'time_to_learn': '2-3 months',
                    'prerequisites': ['HTML', 'CSS'],
                    'learning_path': [
                        'Basic syntax and variables',
                        'Functions and scope',
                        'DOM manipulation',
                        'Events and event handling',
                        'Arrays and objects',
                        'Async programming (callbacks, promises, async/await)',
                        'ES6+ features',
                        'Basic frameworks (React/Vue)'
                    ],
                    'resources': {
                        'courses': [
                            'JavaScript.info',
                            'The Modern JavaScript Tutorial',
                            'Eloquent JavaScript (book)'
                        ],
                        'projects': [
                            'Build a todo app',
                            'Create a weather app',
                            'Build a simple game',
                            'Develop a portfolio website'
                        ],
                        'practice_platforms': [
                            'Codewars',
                            'LeetCode (JavaScript)',
                            'FreeCodeCamp',
                            'Frontend Mentor'
                        ]
                    },
                    'career_impact': 'High - Essential for web development and increasingly used in backend development'
                },
                'java': {
                    'difficulty': 'intermediate',
                    'time_to_learn': '4-6 months',
                    'prerequisites': ['Basic programming concepts'],
                    'learning_path': [
                        'Java syntax and basic concepts',
                        'Object-oriented programming in Java',
                        'Collections framework',
                        'Exception handling',
                        'File I/O',
                        'Multithreading',
                        'Basic frameworks (Spring)',
                        'Unit testing with JUnit'
                    ],
                    'resources': {
                        'courses': [
                            'Java Programming Basics (Coursera)',
                            'Spring Boot Tutorial',
                            'Oracle Java Documentation'
                        ],
                        'projects': [
                            'Build a banking application',
                            'Create a library management system',
                            'Develop a REST API',
                            'Build a simple Android app'
                        ],
                        'practice_platforms': [
                            'LeetCode (Java)',
                            'HackerRank',
                            'Codewars'
                        ]
                    },
                    'career_impact': 'High - Widely used in enterprise applications, Android development, and large-scale systems'
                }
            },
            'web_technologies': {
                'react': {
                    'difficulty': 'intermediate',
                    'time_to_learn': '2-3 months',
                    'prerequisites': ['JavaScript', 'HTML', 'CSS'],
                    'learning_path': [
                        'React basics and JSX',
                        'Components and props',
                        'State and lifecycle',
                        'Hooks (useState, useEffect)',
                        'Handling events',
                        'Conditional rendering',
                        'Lists and keys',
                        'Forms and controlled components',
                        'React Router',
                        'State management (Context/Redux)'
                    ],
                    'resources': {
                        'courses': [
                            'React Official Documentation',
                            'React Tutorial (W3Schools)',
                            'Modern React with Redux (Udemy)'
                        ],
                        'projects': [
                            'Build a todo app with React',
                            'Create a weather dashboard',
                            'Build a social media clone',
                            'Develop an e-commerce frontend'
                        ],
                        'practice_platforms': [
                            'Frontend Mentor',
                            'Codewars (React challenges)',
                            'React challenges on GitHub'
                        ]
                    },
                    'career_impact': 'Very High - Most popular frontend framework with high demand'
                },
                'nodejs': {
                    'difficulty': 'intermediate',
                    'time_to_learn': '2-3 months',
                    'prerequisites': ['JavaScript', 'Basic web concepts'],
                    'learning_path': [
                        'Node.js basics and runtime',
                        'Modules and require()',
                        'File system operations',
                        'HTTP module and servers',
                        'Express.js framework',
                        'Middleware and routing',
                        'Database integration',
                        'Authentication and security',
                        'REST API development',
                        'Testing with Jest/Mocha'
                    ],
                    'resources': {
                        'courses': [
                            'Node.js Official Documentation',
                            'Express.js Tutorial',
                            'Node.js Best Practices'
                        ],
                        'projects': [
                            'Build a REST API',
                            'Create a chat application',
                            'Build a blog backend',
                            'Develop a file sharing service'
                        ],
                        'practice_platforms': [
                            'Node.js challenges on GitHub',
                            'Backend development practice',
                            'API development exercises'
                        ]
                    },
                    'career_impact': 'High - Enables full-stack JavaScript development'
                }
            },
            'databases': {
                'sql': {
                    'difficulty': 'beginner',
                    'time_to_learn': '1-2 months',
                    'prerequisites': [],
                    'learning_path': [
                        'Basic SQL syntax and SELECT',
                        'Filtering with WHERE',
                        'Sorting with ORDER BY',
                        'Joins (INNER, OUTER, LEFT, RIGHT)',
                        'Grouping and aggregation',
                        'Subqueries',
                        'INSERT, UPDATE, DELETE',
                        'Database design basics',
                        'Indexes and performance',
                        'Advanced queries'
                    ],
                    'resources': {
                        'courses': [
                            'SQLBolt',
                            'Mode Analytics SQL Tutorial',
                            'SQL for Data Analysis (Coursera)'
                        ],
                        'projects': [
                            'Design a library database',
                            'Create an e-commerce database',
                            'Build a student management system',
                            'Design a social media database'
                        ],
                        'practice_platforms': [
                            'LeetCode (Database)',
                            'HackerRank (SQL)',
                            'SQLZOO',
                            'Codewars (SQL)'
                        ]
                    },
                    'career_impact': 'Very High - Essential for almost all software development roles'
                },
                'mongodb': {
                    'difficulty': 'beginner',
                    'time_to_learn': '1-2 months',
                    'prerequisites': ['Basic programming concepts'],
                    'learning_path': [
                        'NoSQL concepts and MongoDB basics',
                        'Document structure and BSON',
                        'CRUD operations',
                        'Querying and filtering',
                        'Aggregation framework',
                        'Indexing and performance',
                        'Schema design',
                        'MongoDB Atlas (cloud)',
                        'Integration with applications',
                        'Security best practices'
                    ],
                    'resources': {
                        'courses': [
                            'MongoDB University',
                            'MongoDB Official Documentation',
                            'NoSQL Database Tutorial'
                        ],
                        'projects': [
                            'Build a blog with MongoDB',
                            'Create an inventory management system',
                            'Design a user analytics database',
                            'Build a real-time chat backend'
                        ],
                        'practice_platforms': [
                            'MongoDB Atlas free tier',
                            'MongoDB exercises',
                            'NoSQL challenges'
                        ]
                    },
                    'career_impact': 'High - Popular NoSQL database for modern applications'
                }
            },
            'cloud_platforms': {
                'aws': {
                    'difficulty': 'intermediate',
                    'time_to_learn': '3-4 months',
                    'prerequisites': ['Basic networking', 'Linux fundamentals'],
                    'learning_path': [
                        'AWS basics and global infrastructure',
                        'IAM and security',
                        'EC2 instances and VPC',
                        'S3 storage',
                        'RDS databases',
                        'Lambda and serverless',
                        'API Gateway',
                        'CloudFormation/IaC',
                        'Monitoring and logging',
                        'AWS certification preparation'
                    ],
                    'resources': {
                        'courses': [
                            'AWS Cloud Practitioner',
                            'AWS Solutions Architect',
                            'AWS Official Documentation',
                            'aCloudGuru tutorials'
                        ],
                        'projects': [
                            'Deploy a web application on AWS',
                            'Set up a serverless architecture',
                            'Build a data pipeline',
                            'Create a disaster recovery setup'
                        ],
                        'practice_platforms': [
                            'AWS Free Tier',
                            'AWS Educate',
                            'CloudGuru labs',
                            'Qwiklabs'
                        ]
                    },
                    'career_impact': 'Very High - Leading cloud platform with high demand for certified professionals'
                }
            }
        }
        
        # Career paths and required skills
        self.career_paths = {
            'Software Engineer': {
                'core_skills': ['python', 'java', 'javascript', 'sql', 'git'],
                'advanced_skills': ['aws', 'docker', 'kubernetes', 'react', 'nodejs'],
                'soft_skills': ['problem solving', 'teamwork', 'communication'],
                'learning_timeline': '6-12 months to entry level, 2-3 years to proficient'
            },
            'Web Developer': {
                'core_skills': ['html', 'css', 'javascript', 'react', 'nodejs'],
                'advanced_skills': ['typescript', 'nextjs', 'graphql', 'aws', 'docker'],
                'soft_skills': ['creativity', 'attention to detail', 'adaptability'],
                'learning_timeline': '3-6 months to entry level, 1-2 years to proficient'
            },
            'Data Analyst': {
                'core_skills': ['sql', 'python', 'excel', 'tableau'],
                'advanced_skills': ['statistics', 'machine learning', 'aws', 'mongodb'],
                'soft_skills': ['analytical thinking', 'attention to detail', 'communication'],
                'learning_timeline': '4-8 months to entry level, 2 years to proficient'
            },
            'DevOps Engineer': {
                'core_skills': ['linux', 'aws', 'docker', 'git'],
                'advanced_skills': ['kubernetes', 'terraform', 'jenkins', 'python'],
                'soft_skills': ['automation', 'collaboration', 'problem solving'],
                'learning_timeline': '6-9 months to entry level, 2-3 years to proficient'
            }
        }
    
    def generate_roadmap(
        self, 
        current_skills: Dict[str, List[str]], 
        target_role: str,
        time_commitment: str = "part-time",  # "part-time", "full-time", "casual"
        learning_style: str = "balanced"  # "visual", "hands-on", "theoretical", "balanced"
    ) -> Dict[str, Any]:
        """Generate personalized learning roadmap"""
        
        # Get career path requirements
        career_requirements = self.career_paths.get(target_role, {})
        required_skills = career_requirements.get('core_skills', []) + career_requirements.get('advanced_skills', [])
        
        # Analyze current skills vs requirements
        skill_gap_analysis = self._analyze_skill_gap(current_skills, required_skills)
        
        # Prioritize skills to learn
        prioritized_skills = self._prioritize_skills(skill_gap_analysis, career_requirements)
        
        # Generate learning timeline
        timeline = self._generate_timeline(prioritized_skills, time_commitment)
        
        # Create learning phases
        learning_phases = self._create_learning_phases(prioritized_skills, timeline, learning_style)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(skill_gap_analysis, target_role, learning_style)
        
        return {
            'target_role': target_role,
            'current_skills_summary': self._summarize_current_skills(current_skills),
            'skill_gap_analysis': skill_gap_analysis,
            'prioritized_skills': prioritized_skills,
            'learning_timeline': timeline,
            'learning_phases': learning_phases,
            'recommendations': recommendations,
            'career_insights': self._get_career_insights(target_role),
            'estimated_completion': self._estimate_completion_time(timeline, time_commitment),
            'success_metrics': self._define_success_metrics(target_role, prioritized_skills)
        }
    
    def _analyze_skill_gap(self, current_skills: Dict[str, List[str]], required_skills: List[str]) -> Dict[str, Any]:
        """Analyze gap between current and required skills"""
        current_flat = []
        for category, skills in current_skills.items():
            if isinstance(skills, list):
                current_flat.extend([s.lower() for s in skills])
        
        required_flat = [s.lower() for s in required_skills]
        
        matched_skills = set(current_flat).intersection(set(required_flat))
        missing_skills = set(required_flat) - set(current_flat)
        additional_skills = set(current_flat) - set(required_flat)
        
        return {
            'matched_skills': list(matched_skills),
            'missing_skills': list(missing_skills),
            'additional_skills': list(additional_skills),
            'match_percentage': len(matched_skills) / len(required_flat) * 100 if required_flat else 0,
            'total_required': len(required_flat),
            'total_matched': len(matched_skills),
            'total_missing': len(missing_skills)
        }
    
    def _prioritize_skills(self, gap_analysis: Dict[str, Any], career_requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Prioritize skills based on importance and dependencies"""
        prioritized = []
        missing_skills = gap_analysis['missing_skills']
        
        # Core skills first
        core_skills = career_requirements.get('core_skills', [])
        advanced_skills = career_requirements.get('advanced_skills', [])
        
        # Add core skills (higher priority)
        for skill in missing_skills:
            if skill in core_skills:
                skill_info = self._get_skill_info(skill)
                prioritized.append({
                    'skill': skill,
                    'priority': 'high',
                    'category': 'core',
                    'difficulty': skill_info.get('difficulty', 'intermediate'),
                    'time_to_learn': skill_info.get('time_to_learn', '2-3 months'),
                    'prerequisites': skill_info.get('prerequisites', []),
                    'career_impact': skill_info.get('career_impact', 'Medium')
                })
        
        # Add advanced skills
        for skill in missing_skills:
            if skill in advanced_skills:
                skill_info = self._get_skill_info(skill)
                prioritized.append({
                    'skill': skill,
                    'priority': 'medium',
                    'category': 'advanced',
                    'difficulty': skill_info.get('difficulty', 'intermediate'),
                    'time_to_learn': skill_info.get('time_to_learn', '3-4 months'),
                    'prerequisites': skill_info.get('prerequisites', []),
                    'career_impact': skill_info.get('career_impact', 'Medium')
                })
        
        # Sort by difficulty and dependencies
        prioritized.sort(key=lambda x: (
            {'high': 1, 'medium': 2, 'low': 3}[x['priority']],
            {'beginner': 1, 'intermediate': 2, 'advanced': 3}[x['difficulty']],
            len(x['prerequisites'])
        ))
        
        return prioritized
    
    def _get_skill_info(self, skill: str) -> Dict[str, Any]:
        """Get detailed information about a skill"""
        for category, skills in self.skill_database.items():
            if skill in skills:
                return skills[skill]
        return {}
    
    def _generate_timeline(self, prioritized_skills: List[Dict[str, Any]], time_commitment: str) -> Dict[str, Any]:
        """Generate learning timeline based on time commitment"""
        time_multipliers = {
            'casual': 2.0,      # Casual learning takes 2x longer
            'part-time': 1.5,   # Part-time takes 1.5x longer
            'full-time': 1.0    # Full-time is baseline
        }
        
        multiplier = time_multipliers.get(time_commitment, 1.5)
        
        total_weeks = 0
        skill_timelines = []
        
        for skill in prioritized_skills:
            # Convert time_to_learn to weeks (approximately)
            time_str = skill['time_to_learn']
            if 'month' in time_str:
                months = int(time_str.split('-')[0]) if '-' in time_str else int(time_str.split()[0])
                weeks = months * 4 * multiplier
            else:
                weeks = 8 * multiplier  # Default to 2 weeks
            
            skill_timeline = {
                'skill': skill['skill'],
                'start_week': total_weeks + 1,
                'end_week': total_weeks + weeks,
                'duration_weeks': weeks,
                'estimated_hours_per_week': self._get_hours_per_week(time_commitment)
            }
            
            skill_timelines.append(skill_timeline)
            total_weeks += weeks
        
        return {
            'total_weeks': total_weeks,
            'total_months': round(total_weeks / 4, 1),
            'skill_timelines': skill_timelines,
            'time_commitment': time_commitment,
            'estimated_total_hours': total_weeks * self._get_hours_per_week(time_commitment)
        }
    
    def _get_hours_per_week(self, time_commitment: str) -> int:
        """Get estimated hours per week based on commitment level"""
        hours_map = {
            'casual': 5,      # 5 hours/week
            'part-time': 15,  # 15 hours/week
            'full-time': 40   # 40 hours/week
        }
        return hours_map.get(time_commitment, 15)
    
    def _create_learning_phases(self, prioritized_skills: List[Dict[str, Any]], timeline: Dict[str, Any], learning_style: str) -> List[Dict[str, Any]]:
        """Create structured learning phases"""
        phases = []
        total_weeks = timeline['total_weeks']
        
        # Create phases based on timeline
        phase_duration = max(4, total_weeks // 4)  # Each phase is at least 4 weeks
        
        for i in range(0, len(prioritized_skills), 2):  # 2 skills per phase
            phase_skills = prioritized_skills[i:i+2]
            
            if phase_skills:
                phase_number = len(phases) + 1
                start_week = i * phase_duration + 1
                end_week = min(start_week + phase_duration - 1, total_weeks)
                
                phase = {
                    'phase_number': phase_number,
                    'title': f"Phase {phase_number}: Foundation Building" if phase_number == 1 else f"Phase {phase_number}: Skill Development",
                    'start_week': start_week,
                    'end_week': end_week,
                    'duration_weeks': end_week - start_week + 1,
                    'skills': phase_skills,
                    'learning_objectives': self._generate_learning_objectives(phase_skills),
                    'projects': self._suggest_projects_for_phase(phase_skills),
                    'resources': self._get_resources_for_phase(phase_skills, learning_style),
                    'milestones': self._define_milestones(phase_skills)
                }
                
                phases.append(phase)
        
        return phases
    
    def _generate_learning_objectives(self, skills: List[Dict[str, Any]]) -> List[str]:
        """Generate learning objectives for a phase"""
        objectives = []
        for skill in skills:
            skill_name = skill['skill']
            skill_info = self._get_skill_info(skill_name)
            learning_path = skill_info.get('learning_path', [])
            
            if learning_path:
                # Take first 2-3 items from learning path as objectives
                for item in learning_path[:2]:
                    objectives.append(f"Master {skill_name}: {item}")
            else:
                objectives.append(f"Learn fundamentals of {skill_name}")
        
        return objectives
    
    def _suggest_projects_for_phase(self, skills: List[Dict[str, Any]]) -> List[str]:
        """Suggest projects for the learning phase"""
        projects = []
        for skill in skills:
            skill_name = skill['skill']
            skill_info = self._get_skill_info(skill_name)
            skill_projects = skill_info.get('resources', {}).get('projects', [])
            
            if skill_projects:
                projects.extend(skill_projects[:2])  # Take 2 projects per skill
        
        return projects[:4]  # Return max 4 projects per phase
    
    def _get_resources_for_phase(self, skills: List[Dict[str, Any]], learning_style: str) -> Dict[str, List[str]]:
        """Get learning resources based on learning style"""
        resources = {
            'courses': [],
            'projects': [],
            'practice_platforms': []
        }
        
        for skill in skills:
            skill_name = skill['skill']
            skill_info = self._get_skill_info(skill_name)
            skill_resources = skill_info.get('resources', {})
            
            # Filter resources based on learning style
            if learning_style == 'hands-on':
                resources['projects'].extend(skill_resources.get('projects', []))
                resources['practice_platforms'].extend(skill_resources.get('practice_platforms', []))
            elif learning_style == 'theoretical':
                resources['courses'].extend(skill_resources.get('courses', []))
            else:  # balanced
                for resource_type, resource_list in skill_resources.items():
                    resources[resource_type].extend(resource_list[:2])  # Take 2 of each type
        
        # Remove duplicates and limit
        for resource_type in resources:
            resources[resource_type] = list(set(resources[resource_type]))[:5]
        
        return resources
    
    def _define_milestones(self, skills: List[Dict[str, Any]]) -> List[str]:
        """Define milestones for the learning phase"""
        milestones = []
        for skill in skills:
            skill_name = skill['skill']
            milestones.append(f"Complete basic {skill_name} tutorial")
            milestones.append(f"Build first project with {skill_name}")
            milestones.append(f"Pass {skill_name} assessment quiz")
        
        return milestones[:4]  # Return max 4 milestones
    
    def _generate_recommendations(self, gap_analysis: Dict[str, Any], target_role: str, learning_style: str) -> List[str]:
        """Generate personalized recommendations"""
        recommendations = []
        
        # Based on skill gap
        if gap_analysis['match_percentage'] < 30:
            recommendations.append("Focus on building fundamental skills first before advanced topics")
        elif gap_analysis['match_percentage'] < 60:
            recommendations.append("You have some relevant skills - focus on filling the core gaps")
        else:
            recommendations.append("Build on your existing skills with advanced topics")
        
        # Based on learning style
        if learning_style == 'hands-on':
            recommendations.append("Focus on practical projects and real-world applications")
        elif learning_style == 'theoretical':
            recommendations.append("Start with comprehensive courses and documentation")
        else:
            recommendations.append("Balance theory with practical projects for best results")
        
        # Career-specific recommendations
        career_insights = self._get_career_insights(target_role)
        recommendations.extend(career_insights.get('recommendations', []))
        
        return recommendations[:6]  # Return top 6 recommendations
    
    def _get_career_insights(self, target_role: str) -> Dict[str, Any]:
        """Get career-specific insights"""
        career_data = self.career_paths.get(target_role, {})
        
        return {
            'job_market_demand': 'High' if target_role in ['Software Engineer', 'Data Analyst'] else 'Medium',
            'average_salary_range': self._get_salary_range(target_role),
            'growth_potential': 'High' if target_role in ['Software Engineer', 'DevOps Engineer'] else 'Medium',
            'industry_trends': self._get_industry_trends(target_role),
            'certifications': self._get_relevant_certifications(target_role),
            'recommendations': self._get_career_recommendations(target_role)
        }
    
    def _get_salary_range(self, role: str) -> str:
        """Get estimated salary range"""
        salary_ranges = {
            'Software Engineer': '$70,000 - $150,000',
            'Web Developer': '$60,000 - $120,000',
            'Data Analyst': '$65,000 - $130,000',
            'DevOps Engineer': '$80,000 - $160,000'
        }
        return salary_ranges.get(role, '$60,000 - $120,000')
    
    def _get_industry_trends(self, role: str) -> List[str]:
        """Get current industry trends for the role"""
        trends = {
            'Software Engineer': ['AI/ML integration', 'Cloud-native development', 'Microservices architecture'],
            'Web Developer': ['Progressive Web Apps', 'JAMstack architecture', 'WebAssembly'],
            'Data Analyst': ['Big data analytics', 'Machine learning', 'Real-time data processing'],
            'DevOps Engineer': ['GitOps', 'Serverless computing', 'Infrastructure as Code']
        }
        return trends.get(role, ['Continuous learning required'])
    
    def _get_relevant_certifications(self, role: str) -> List[str]:
        """Get relevant certifications for the role"""
        certifications = {
            'Software Engineer': ['AWS Certified Developer', 'Google Cloud Professional', 'Microsoft Azure Developer'],
            'Web Developer': ['AWS Certified Cloud Practitioner', 'Google Mobile Web Specialist', 'Meta React Certification'],
            'Data Analyst': ['Google Data Analytics Certificate', 'IBM Data Science Certificate', 'AWS Certified Data Analytics'],
            'DevOps Engineer': ['AWS Certified DevOps Engineer', 'Kubernetes Administrator', 'Terraform Certification']
        }
        return certifications.get(role, [])
    
    def _get_career_recommendations(self, role: str) -> List[str]:
        """Get career-specific recommendations"""
        recommendations = {
            'Software Engineer': ['Build a strong portfolio of projects', 'Contribute to open source', 'Practice algorithmic problem solving'],
            'Web Developer': ['Create impressive portfolio projects', 'Stay updated with frontend trends', 'Learn both frontend and backend'],
            'Data Analyst': ['Develop strong SQL skills', 'Learn data visualization tools', 'Build analytical projects'],
            'DevOps Engineer': ['Gain hands-on cloud experience', 'Learn infrastructure automation', 'Understand security best practices']
        }
        return recommendations.get(role, [])
    
    def _estimate_completion_time(self, timeline: Dict[str, Any], time_commitment: str) -> str:
        """Estimate completion time based on timeline and commitment"""
        total_months = timeline['total_months']
        
        if time_commitment == 'full-time':
            return f"Approximately {total_months} months"
        elif time_commitment == 'part-time':
            return f"Approximately {total_months * 1.5:.1f} months"
        else:
            return f"Approximately {total_months * 2:.1f} months"
    
    def _define_success_metrics(self, target_role: str, prioritized_skills: List[Dict[str, Any]]) -> List[str]:
        """Define success metrics for the learning journey"""
        metrics = [
            "Complete all learning objectives for each phase",
            "Build portfolio projects demonstrating each skill",
            "Pass technical assessments for core skills"
        ]
        
        # Add role-specific metrics
        if target_role == 'Software Engineer':
            metrics.extend([
                "Solve 50+ coding problems",
                "Contribute to an open-source project",
                "Build a full-stack application"
            ])
        elif target_role == 'Web Developer':
            metrics.extend([
                "Build 3+ responsive websites",
                "Create a portfolio website",
                "Master at least one frontend framework"
            ])
        elif target_role == 'Data Analyst':
            metrics.extend([
                "Complete 5+ data analysis projects",
                "Master SQL and at least one BI tool",
                "Create a data visualization portfolio"
            ])
        
        return metrics[:6]  # Return top 6 metrics
    
    def _summarize_current_skills(self, current_skills: Dict[str, List[str]]) -> Dict[str, Any]:
        """Summarize current skills"""
        summary = {
            'total_skills': 0,
            'categories': {}
        }
        
        for category, skills in current_skills.items():
            if isinstance(skills, list):
                skill_count = len(skills)
                summary['total_skills'] += skill_count
                summary['categories'][category] = skill_count
        
        return summary
    
    def export_roadmap(self, roadmap_data: Dict[str, Any]) -> str:
        """Export roadmap as formatted text"""
        formatted = f"""
# Learning Roadmap for {roadmap_data['target_role']}

## Current Skills Summary
- Total Skills: {roadmap_data['current_skills_summary']['total_skills']}
- Match with Requirements: {roadmap_data['skill_gap_analysis']['match_percentage']:.1f}%

## Learning Timeline
- Estimated Duration: {roadmap_data['estimated_completion']}
- Total Hours: {roadmap_data['learning_timeline']['estimated_total_hours']}

## Learning Phases
"""
        
        for phase in roadmap_data['learning_phases']:
            formatted += f"""
### {phase['title']}
- Duration: {phase['duration_weeks']} weeks
- Skills: {', '.join([s['skill'] for s in phase['skills']])}
- Key Projects: {', '.join(phase['projects'][:2])}
"""
        
        formatted += f"""
## Recommendations
{chr(10).join(f"• {rec}" for rec in roadmap_data['recommendations'])}

## Success Metrics
{chr(10).join(f"• {metric}" for metric in roadmap_data['success_metrics'])}
"""
        
        return formatted

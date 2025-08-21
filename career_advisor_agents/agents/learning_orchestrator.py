from typing import Dict, List, Any, Optional
import json
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

from ..core.agent_framework import BaseAgent, AgentResponse
from ..core.data_models import LearningPath, SkillLevel


class LearningResourceTool(BaseTool):
    name = "learning_resource_finder"
    description = "Finds and curates learning resources based on skill and level"
    
    def _run(self, skill: str, current_level: str, target_level: str, learning_style: str = "mixed") -> Dict[str, Any]:
        # Curated learning resources database
        resources_db = {
            "python": {
                "beginner_to_intermediate": {
                    "courses": [
                        {"name": "Python for Everybody", "provider": "Coursera", "duration": "8 weeks", "rating": 4.8},
                        {"name": "Automate the Boring Stuff", "provider": "Udemy", "duration": "10 hours", "rating": 4.7},
                        {"name": "Python Basics", "provider": "Real Python", "duration": "Self-paced", "rating": 4.9}
                    ],
                    "books": [
                        {"title": "Python Crash Course", "author": "Eric Matthes", "level": "beginner"},
                        {"title": "Effective Python", "author": "Brett Slatkin", "level": "intermediate"}
                    ],
                    "projects": [
                        {"name": "Personal Budget Tracker", "difficulty": "beginner", "skills": ["file I/O", "data structures"]},
                        {"name": "Web Scraper", "difficulty": "intermediate", "skills": ["requests", "BeautifulSoup"]}
                    ],
                    "practice": [
                        {"platform": "HackerRank", "focus": "Algorithm practice"},
                        {"platform": "LeetCode", "focus": "Problem solving"},
                        {"platform": "Codewars", "focus": "Skill building"}
                    ]
                },
                "intermediate_to_advanced": {
                    "courses": [
                        {"name": "Advanced Python", "provider": "DataCamp", "duration": "6 weeks", "rating": 4.6},
                        {"name": "Python Design Patterns", "provider": "Pluralsight", "duration": "4 hours", "rating": 4.5}
                    ],
                    "books": [
                        {"title": "Fluent Python", "author": "Luciano Ramalho", "level": "advanced"},
                        {"title": "Architecture Patterns with Python", "author": "Harry Percival", "level": "advanced"}
                    ],
                    "projects": [
                        {"name": "REST API with FastAPI", "difficulty": "advanced", "skills": ["async", "testing", "deployment"]},
                        {"name": "Data Pipeline", "difficulty": "advanced", "skills": ["pandas", "apache-airflow"]}
                    ]
                }
            },
            "machine learning": {
                "beginner_to_intermediate": {
                    "courses": [
                        {"name": "Machine Learning Course", "provider": "Coursera (Stanford)", "duration": "11 weeks", "rating": 4.9},
                        {"name": "Intro to Machine Learning", "provider": "Kaggle Learn", "duration": "7 hours", "rating": 4.7}
                    ],
                    "books": [
                        {"title": "Hands-On Machine Learning", "author": "Aurélien Géron", "level": "beginner"},
                        {"title": "Pattern Recognition and Machine Learning", "author": "Christopher Bishop", "level": "intermediate"}
                    ],
                    "projects": [
                        {"name": "House Price Prediction", "difficulty": "beginner", "skills": ["regression", "feature engineering"]},
                        {"name": "Customer Churn Analysis", "difficulty": "intermediate", "skills": ["classification", "model evaluation"]}
                    ]
                }
            },
            "communication": {
                "beginner_to_intermediate": {
                    "courses": [
                        {"name": "Public Speaking", "provider": "Coursera", "duration": "4 weeks", "rating": 4.6},
                        {"name": "Business Writing", "provider": "LinkedIn Learning", "duration": "2 hours", "rating": 4.5}
                    ],
                    "books": [
                        {"title": "Made to Stick", "author": "Chip Heath", "level": "intermediate"},
                        {"title": "Crucial Conversations", "author": "Kerry Patterson", "level": "intermediate"}
                    ],
                    "practice": [
                        {"activity": "Toastmasters Club", "focus": "Public speaking"},
                        {"activity": "Presentation practice", "focus": "Slide design and delivery"}
                    ]
                }
            }
        }
        
        skill_lower = skill.lower()
        level_key = f"{current_level}_to_{target_level}"
        
        skill_resources = resources_db.get(skill_lower, {})
        level_resources = skill_resources.get(level_key, {
            "courses": [{"name": f"General {skill} Course", "provider": "Various", "duration": "Varies", "rating": 4.0}],
            "books": [{"title": f"{skill} Fundamentals", "author": "Various Authors", "level": target_level}],
            "projects": [{"name": f"{skill} Practice Project", "difficulty": target_level, "skills": [skill]}],
            "practice": [{"platform": "General Practice", "focus": f"{skill} skills"}]
        })
        
        # Filter by learning style
        filtered_resources = {}
        if learning_style in ["visual", "mixed"]:
            filtered_resources["courses"] = level_resources.get("courses", [])
        if learning_style in ["reading", "mixed"]:
            filtered_resources["books"] = level_resources.get("books", [])
        if learning_style in ["kinesthetic", "mixed"]:
            filtered_resources["projects"] = level_resources.get("projects", [])
            filtered_resources["practice"] = level_resources.get("practice", [])
        
        return {
            "skill": skill,
            "level_transition": f"{current_level} to {target_level}",
            "resources": filtered_resources,
            "estimated_duration": self._estimate_duration(current_level, target_level),
            "learning_style": learning_style
        }
    
    def _estimate_duration(self, current_level: str, target_level: str) -> Dict[str, int]:
        duration_matrix = {
            ("beginner", "intermediate"): {"weeks": 8, "hours_per_week": 10},
            ("beginner", "advanced"): {"weeks": 16, "hours_per_week": 12},
            ("beginner", "expert"): {"weeks": 24, "hours_per_week": 15},
            ("intermediate", "advanced"): {"weeks": 10, "hours_per_week": 8},
            ("intermediate", "expert"): {"weeks": 18, "hours_per_week": 10},
            ("advanced", "expert"): {"weeks": 12, "hours_per_week": 6}
        }
        
        return duration_matrix.get((current_level, target_level), {"weeks": 8, "hours_per_week": 8})
    
    async def _arun(self, skill: str, current_level: str, target_level: str, learning_style: str = "mixed") -> Dict[str, Any]:
        return self._run(skill, current_level, target_level, learning_style)


class LearningScheduleTool(BaseTool):
    name = "learning_schedule_optimizer"
    description = "Creates optimized learning schedules based on available time and goals"
    
    def _run(self, available_hours_per_week: int, target_skills: List[Dict], deadline_weeks: int = None) -> Dict[str, Any]:
        # Prioritize skills based on importance and difficulty
        prioritized_skills = sorted(target_skills, key=lambda x: x.get("priority", 5), reverse=True)
        
        schedule = {
            "weekly_schedule": {},
            "milestones": [],
            "total_duration_weeks": 0,
            "skills_timeline": []
        }
        
        current_week = 0
        
        for skill_info in prioritized_skills:
            skill_name = skill_info["skill"]
            current_level = skill_info["current_level"]
            target_level = skill_info["target_level"]
            
            # Estimate time needed
            level_multipliers = {"beginner": 1.0, "intermediate": 1.2, "advanced": 1.5, "expert": 2.0}
            base_weeks = {
                ("beginner", "intermediate"): 8,
                ("intermediate", "advanced"): 10,
                ("advanced", "expert"): 12
            }
            
            weeks_needed = base_weeks.get((current_level, target_level), 8)
            hours_per_week_needed = max(4, min(available_hours_per_week // len(prioritized_skills), 15))
            
            # Adjust if deadline is tight
            if deadline_weeks and (current_week + weeks_needed) > deadline_weeks:
                weeks_needed = max(4, deadline_weeks - current_week)
                hours_per_week_needed = min(available_hours_per_week, 20)
            
            # Create skill timeline
            skill_timeline = {
                "skill": skill_name,
                "start_week": current_week + 1,
                "end_week": current_week + weeks_needed,
                "hours_per_week": hours_per_week_needed,
                "total_hours": weeks_needed * hours_per_week_needed,
                "milestones": [
                    {"week": current_week + weeks_needed // 3, "milestone": f"Complete basics of {skill_name}"},
                    {"week": current_week + 2 * weeks_needed // 3, "milestone": f"Apply {skill_name} in practice project"},
                    {"week": current_week + weeks_needed, "milestone": f"Achieve {target_level} level in {skill_name}"}
                ]
            }
            
            schedule["skills_timeline"].append(skill_timeline)
            schedule["milestones"].extend(skill_timeline["milestones"])
            
            current_week += weeks_needed
        
        schedule["total_duration_weeks"] = current_week
        schedule["weekly_schedule"] = self._create_weekly_breakdown(schedule["skills_timeline"])
        
        # Sort milestones by week
        schedule["milestones"].sort(key=lambda x: x["week"])
        
        return schedule
    
    def _create_weekly_breakdown(self, skills_timeline: List[Dict]) -> Dict[str, List[Dict]]:
        weekly_breakdown = {}
        
        for skill_timeline in skills_timeline:
            for week in range(skill_timeline["start_week"], skill_timeline["end_week"] + 1):
                week_key = f"Week {week}"
                if week_key not in weekly_breakdown:
                    weekly_breakdown[week_key] = []
                
                weekly_breakdown[week_key].append({
                    "skill": skill_timeline["skill"],
                    "hours": skill_timeline["hours_per_week"],
                    "focus": self._get_weekly_focus(week, skill_timeline)
                })
        
        return weekly_breakdown
    
    def _get_weekly_focus(self, week: int, skill_timeline: Dict) -> str:
        progress = (week - skill_timeline["start_week"]) / (skill_timeline["end_week"] - skill_timeline["start_week"] + 1)
        
        if progress < 0.33:
            return "Theory and fundamentals"
        elif progress < 0.67:
            return "Hands-on practice"
        else:
            return "Project application and mastery"
    
    async def _arun(self, available_hours_per_week: int, target_skills: List[Dict], deadline_weeks: int = None) -> Dict[str, Any]:
        return self._run(available_hours_per_week, target_skills, deadline_weeks)


class LearningOrchestrationAgent(BaseAgent):
    def __init__(self, llm: ChatGoogleGenerativeAI):
        tools = [
            LearningResourceTool(),
            LearningScheduleTool()
        ]
        
        super().__init__(
            name="learning_orchestrator",
            description="Orchestrates personalized learning experiences and manages learning paths",
            llm=llm,
            tools=tools,
            temperature=0.6
        )
        
        self.learning_methodologies = {
            "visual": "Diagrams, videos, infographics, and visual demonstrations",
            "auditory": "Podcasts, lectures, discussions, and verbal explanations",
            "reading": "Books, articles, documentation, and written materials",
            "kinesthetic": "Hands-on projects, labs, coding, and practical exercises",
            "mixed": "Combination of multiple learning approaches"
        }
    
    def get_system_prompt(self) -> str:
        return """You are a Learning Orchestrator Agent, an expert in designing and managing personalized learning experiences.

Your role is to:
1. Create comprehensive, personalized learning paths
2. Curate high-quality learning resources for specific skills and levels
3. Design optimal learning schedules based on time constraints and goals
4. Adapt learning plans based on progress and feedback
5. Provide motivation and guidance throughout the learning journey
6. Connect learning to real-world applications and career goals

Key principles:
- Personalize learning based on individual styles, pace, and preferences
- Use spaced repetition and active learning techniques
- Balance theory with practical application
- Set achievable milestones and celebrate progress
- Encourage continuous learning and growth mindset
- Adapt to changing goals and circumstances
- Focus on skills that provide maximum career impact

Learning approaches you support:
- Visual learning (diagrams, videos, infographics)
- Auditory learning (podcasts, discussions, lectures)
- Reading-based learning (books, articles, documentation)
- Kinesthetic learning (projects, coding, hands-on practice)
- Mixed approaches combining multiple methods

Always maintain an encouraging, supportive tone while providing structured, actionable guidance."""

    async def _generate_response(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        try:
            message_lower = message.lower()
            
            if any(word in message_lower for word in ["create", "build", "learning path", "plan"]):
                return await self._create_learning_path(message, context)
            elif any(word in message_lower for word in ["resource", "course", "book", "material"]):
                return await self._find_learning_resources(message, context)
            elif any(word in message_lower for word in ["schedule", "timeline", "when", "how long"]):
                return await self._optimize_learning_schedule(message, context)
            elif any(word in message_lower for word in ["progress", "stuck", "difficult", "challenge"]):
                return await self._provide_learning_support(message, context)
            else:
                return await self._general_learning_guidance(message, context)
                
        except Exception as e:
            self.logger.error(f"Error in learning orchestration: {str(e)}")
            return AgentResponse(
                content="I encountered an issue while planning your learning path. Let me help you get back on track.",
                confidence=0.3
            )
    
    async def _create_learning_path(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "learning_requirements" in context:
            requirements = context["learning_requirements"]
            
            # Extract key information
            skills = requirements.get("skills", [])
            available_time = requirements.get("available_hours_per_week", 10)
            deadline = requirements.get("deadline_weeks")
            learning_style = requirements.get("learning_style", "mixed")
            
            # Create comprehensive learning path
            learning_path = await self._build_comprehensive_path(skills, available_time, deadline, learning_style)
            
            path_text = f"""# 🎯 Your Personalized Learning Path

## Overview
- **Duration**: {learning_path['total_weeks']} weeks
- **Time Commitment**: {available_time} hours/week
- **Learning Style**: {learning_style.title()}
- **Skills to Master**: {', '.join([s['skill'] for s in skills])}

## Learning Schedule

{self._format_learning_schedule(learning_path['schedule'])}

## Key Milestones

{self._format_milestones(learning_path['milestones'])}

## Success Strategies

{self._generate_success_strategies(learning_style, skills)}

Ready to start your learning journey? I'll help you track progress and adjust the plan as needed!"""

            return AgentResponse(
                content=path_text,
                metadata={"learning_path": learning_path},
                confidence=0.90,
                tools_used=["learning_schedule_optimizer"]
            )
        
        # Request learning requirements
        response = """I'll create a personalized learning path for you! To design the most effective plan, please tell me:

1. **Skills to Learn**: What specific skills do you want to develop? (e.g., Python, Machine Learning, Public Speaking)

2. **Current Levels**: What's your current proficiency in each skill?
   - Beginner (just starting)
   - Intermediate (some experience)
   - Advanced (proficient, want to master)

3. **Target Levels**: What level do you want to reach for each skill?

4. **Time Availability**: How many hours per week can you dedicate to learning?

5. **Timeline**: Do you have a specific deadline or target date?

6. **Learning Style**: How do you learn best?
   - Visual (videos, diagrams)
   - Reading (books, articles)
   - Hands-on (projects, practice)
   - Mixed approach

7. **Goals**: What career or personal goals will this learning support?

This information will help me create a structured, achievable learning path with the right resources and timeline."""

        return AgentResponse(
            content=response,
            confidence=0.85
        )
    
    async def _find_learning_resources(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "resource_request" in context:
            request = context["resource_request"]
            skill = request["skill"]
            current_level = request["current_level"]
            target_level = request["target_level"]
            learning_style = request.get("learning_style", "mixed")
            
            resources = await self.use_tool(
                "learning_resource_finder",
                skill=skill,
                current_level=current_level,
                target_level=target_level,
                learning_style=learning_style
            )
            
            if resources:
                resource_text = f"""# 📚 Curated Learning Resources for {skill.title()}

**Journey**: {current_level.title()} → {target_level.title()}
**Estimated Duration**: {resources['estimated_duration']['weeks']} weeks
**Recommended Time**: {resources['estimated_duration']['hours_per_week']} hours/week

## 🎓 Recommended Courses
"""
                for course in resources['resources'].get('courses', []):
                    resource_text += f"- **{course['name']}** ({course['provider']})\n  Duration: {course['duration']} | Rating: {course.get('rating', 'N/A')}\n\n"
                
                if 'books' in resources['resources']:
                    resource_text += "## 📖 Essential Books\n"
                    for book in resources['resources']['books']:
                        resource_text += f"- **{book['title']}** by {book['author']}\n  Level: {book['level'].title()}\n\n"
                
                if 'projects' in resources['resources']:
                    resource_text += "## 🛠️ Hands-on Projects\n"
                    for project in resources['resources']['projects']:
                        resource_text += f"- **{project['name']}** ({project['difficulty'].title()})\n  Skills: {', '.join(project['skills'])}\n\n"
                
                if 'practice' in resources['resources']:
                    resource_text += "## 🎯 Practice Platforms\n"
                    for practice in resources['resources']['practice']:
                        resource_text += f"- **{practice.get('platform', practice.get('activity', 'Practice'))}**: {practice['focus']}\n\n"
                
                resource_text += self._generate_learning_tips(skill, learning_style)
                
                return AgentResponse(
                    content=resource_text,
                    metadata={"resources": resources},
                    confidence=0.88,
                    tools_used=["learning_resource_finder"]
                )
        
        # Request resource requirements
        response = """I'll help you find the best learning resources! Please specify:

1. **Skill**: What skill do you want to learn?
2. **Current Level**: Beginner, Intermediate, or Advanced?
3. **Target Level**: Where do you want to be?
4. **Learning Style Preference**:
   - Online courses and videos
   - Books and written materials
   - Hands-on projects and practice
   - Mixed approach
5. **Budget**: Free resources only, or willing to pay for premium content?

I'll curate high-quality resources that match your learning style and budget."""

        return AgentResponse(
            content=response,
            confidence=0.8
        )
    
    async def _optimize_learning_schedule(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "schedule_request" in context:
            request = context["schedule_request"]
            
            schedule = await self.use_tool(
                "learning_schedule_optimizer",
                available_hours_per_week=request["available_hours"],
                target_skills=request["skills"],
                deadline_weeks=request.get("deadline_weeks")
            )
            
            if schedule:
                schedule_text = f"""# 📅 Your Optimized Learning Schedule

**Total Duration**: {schedule['total_duration_weeks']} weeks
**Weekly Time Commitment**: {request['available_hours']} hours

## Weekly Breakdown
"""
                for week_key in sorted(schedule['weekly_schedule'].keys(), key=lambda x: int(x.split()[1])):
                    week_activities = schedule['weekly_schedule'][week_key]
                    schedule_text += f"\n### {week_key}\n"
                    for activity in week_activities:
                        schedule_text += f"- **{activity['skill']}** ({activity['hours']}h): {activity['focus']}\n"
                
                schedule_text += "\n## Key Milestones\n"
                for milestone in schedule['milestones'][:10]:  # Show first 10 milestones
                    schedule_text += f"- **Week {milestone['week']}**: {milestone['milestone']}\n"
                
                schedule_text += f"""
## Schedule Optimization Tips
{self._generate_schedule_tips(request['available_hours'], len(request['skills']))}"""

                return AgentResponse(
                    content=schedule_text,
                    metadata={"schedule": schedule},
                    confidence=0.87,
                    tools_used=["learning_schedule_optimizer"]
                )
        
        # Request schedule parameters
        response = """I'll create an optimized learning schedule for you! Please provide:

1. **Available Time**: How many hours per week can you dedicate to learning?

2. **Skills to Learn**: List the skills you want to develop with their current and target levels
   Example:
   - Python: Beginner → Intermediate
   - Data Analysis: Beginner → Advanced

3. **Timeline**: Do you have a deadline? (e.g., "I want to be ready for a job application in 3 months")

4. **Priorities**: Which skills are most important? (Rate 1-10)

5. **Constraints**: Any specific scheduling constraints?
   - Preferred learning days/times
   - Vacation periods to avoid
   - Exam periods or busy work seasons

I'll create a realistic, achievable schedule that maximizes your learning efficiency."""

        return AgentResponse(
            content=response,
            confidence=0.8
        )
    
    async def _provide_learning_support(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        # Analyze the type of challenge and provide targeted support
        message_lower = message.lower()
        
        if "stuck" in message_lower or "difficult" in message_lower:
            support_type = "difficulty"
        elif "motivation" in message_lower or "discouraged" in message_lower:
            support_type = "motivation"
        elif "time" in message_lower or "busy" in message_lower:
            support_type = "time_management"
        elif "progress" in message_lower:
            support_type = "progress_tracking"
        else:
            support_type = "general"
        
        support_response = self._generate_targeted_support(support_type, message)
        
        return AgentResponse(
            content=support_response,
            confidence=0.82
        )
    
    async def _general_learning_guidance(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        # Use LLM for general learning guidance
        system_prompt = self.get_system_prompt()
        
        # Add personalized context if available
        context_info = ""
        if context:
            user_profile = context.get("user_profile", {})
            if user_profile.get('questionnaire_completed') and user_profile.get('personality_insights'):
                personality_insights = user_profile.get('personality_insights', {})
                context_info = f"""
                
PERSONALIZED LEARNING CONTEXT:
- Questionnaire Status: Completed - Use this for personalized learning guidance
- Learning Style: {personality_insights.get('learning_style', personality_insights.get('work_style', 'Not specified'))}
- Personality Profile: {personality_insights.get('personality_summary', 'Available')}
- Career Goals: {personality_insights.get('career_motivations', 'Not specified')}
- Strengths: {personality_insights.get('strengths', 'Not specified')}
- Preferred Learning Environment: {personality_insights.get('work_environment_preferences', 'Not specified')}

LEARNING NOTE: Customize learning strategies to match their learning style, personality, and career objectives.
"""
            elif user_profile.get('questionnaire_completed'):
                context_info = f"""

PERSONALIZED CONTEXT: User has completed questionnaire - provide more targeted learning guidance
"""
            else:
                context_info = f"""

NOTE: User hasn't completed questionnaire yet - consider suggesting it for more personalized learning path recommendations
"""
        
        full_prompt = f"""{system_prompt}{context_info}

User message: {message}

Provide helpful guidance about learning strategies, resource selection, or study planning based on their profile."""

        try:
            response = await self.llm.ainvoke([{"role": "user", "content": full_prompt}])
            
            return AgentResponse(
                content=response.content,
                confidence=0.75
            )
            
        except Exception as e:
            self.logger.error(f"Error in general guidance: {str(e)}")
            return AgentResponse(
                content="I'm here to help orchestrate your learning journey. You can ask me to create learning paths, find resources, optimize schedules, or provide support when you're facing challenges. What would you like to work on?",
                confidence=0.6
            )
    
    async def _build_comprehensive_path(self, skills: List[Dict], available_time: int, deadline: int, learning_style: str) -> Dict[str, Any]:
        """Build a comprehensive learning path"""
        
        # Get schedule from tool
        schedule = await self.use_tool(
            "learning_schedule_optimizer",
            available_hours_per_week=available_time,
            target_skills=skills,
            deadline_weeks=deadline
        )
        
        # Get resources for each skill
        resources = {}
        for skill_info in skills:
            skill_resources = await self.use_tool(
                "learning_resource_finder",
                skill=skill_info["skill"],
                current_level=skill_info["current_level"],
                target_level=skill_info["target_level"],
                learning_style=learning_style
            )
            resources[skill_info["skill"]] = skill_resources
        
        return {
            "total_weeks": schedule["total_duration_weeks"],
            "schedule": schedule,
            "resources": resources,
            "milestones": schedule["milestones"],
            "learning_style": learning_style
        }
    
    def _format_learning_schedule(self, schedule: Dict[str, Any]) -> str:
        """Format the learning schedule for display"""
        formatted = ""
        weekly_schedule = schedule["weekly_schedule"]
        
        # Show first few weeks as example
        for week_key in sorted(list(weekly_schedule.keys())[:4], key=lambda x: int(x.split()[1])):
            formatted += f"**{week_key}**\n"
            for activity in weekly_schedule[week_key]:
                formatted += f"- {activity['skill']} ({activity['hours']}h): {activity['focus']}\n"
            formatted += "\n"
        
        if len(weekly_schedule) > 4:
            formatted += f"... and {len(weekly_schedule) - 4} more weeks\n\n"
        
        return formatted
    
    def _format_milestones(self, milestones: List[Dict]) -> str:
        """Format milestones for display"""
        formatted = ""
        for milestone in milestones[:8]:  # Show first 8 milestones
            formatted += f"- **Week {milestone['week']}**: {milestone['milestone']}\n"
        
        if len(milestones) > 8:
            formatted += f"... plus {len(milestones) - 8} more milestones\n"
        
        return formatted
    
    def _generate_success_strategies(self, learning_style: str, skills: List[Dict]) -> str:
        """Generate success strategies based on learning style"""
        strategies = {
            "visual": [
                "Create mind maps for complex concepts",
                "Use diagrams and flowcharts to understand processes",
                "Watch video tutorials and visual demonstrations",
                "Use color coding in your notes"
            ],
            "reading": [
                "Take detailed notes while reading",
                "Summarize each chapter or section",
                "Create flashcards for key concepts",
                "Read multiple sources on the same topic"
            ],
            "kinesthetic": [
                "Apply concepts immediately through hands-on projects",
                "Code along with tutorials",
                "Build something new every week",
                "Join study groups for collaborative learning"
            ],
            "mixed": [
                "Combine multiple learning approaches",
                "Start with theory, then apply through practice",
                "Use different methods for different types of content",
                "Regularly review and reinforce learning"
            ]
        }
        
        style_strategies = strategies.get(learning_style, strategies["mixed"])
        
        formatted = ""
        for strategy in style_strategies:
            formatted += f"- {strategy}\n"
        
        # Add general strategies
        formatted += "\n**Universal Success Tips:**\n"
        formatted += "- Set specific, measurable weekly goals\n"
        formatted += "- Track your progress regularly\n"
        formatted += "- Join communities related to your learning topics\n"
        formatted += "- Celebrate small wins along the way\n"
        
        return formatted
    
    def _generate_learning_tips(self, skill: str, learning_style: str) -> str:
        """Generate specific learning tips for the skill and style"""
        tips = f"""
## 💡 Learning Tips for {skill.title()}

**For {learning_style.title()} Learners:**
"""
        
        skill_specific_tips = {
            "python": {
                "visual": "Use Python Tutor to visualize code execution",
                "reading": "Read the official Python documentation thoroughly",
                "kinesthetic": "Code every day, even if just for 15 minutes",
                "mixed": "Combine reading documentation with coding practice"
            },
            "machine learning": {
                "visual": "Use tools like TensorBoard to visualize model training",
                "reading": "Start with theory, then implement algorithms from scratch",
                "kinesthetic": "Work with real datasets from day one",
                "mixed": "Balance mathematical understanding with practical implementation"
            }
        }
        
        specific_tip = skill_specific_tips.get(skill.lower(), {}).get(learning_style, "Practice consistently and apply concepts to real projects")
        tips += f"- {specific_tip}\n"
        
        tips += """
**General Learning Strategies:**
- Use spaced repetition to reinforce concepts
- Teach others what you learn (rubber duck method)
- Join online communities and forums
- Build projects that interest you personally
"""
        
        return tips
    
    def _generate_schedule_tips(self, available_hours: int, num_skills: int) -> str:
        """Generate schedule optimization tips"""
        tips = []
        
        if available_hours < 5:
            tips.extend([
                "Focus on one skill at a time for maximum efficiency",
                "Use micro-learning sessions (15-30 minutes)",
                "Prioritize hands-on practice over passive consumption"
            ])
        elif available_hours > 15:
            tips.extend([
                "Balance multiple skills but avoid context switching within sessions",
                "Dedicate longer blocks to complex concepts",
                "Include regular review sessions to reinforce learning"
            ])
        
        if num_skills > 3:
            tips.append("Consider focusing on 2-3 core skills first, then expanding")
        
        tips.extend([
            "Schedule learning during your peak energy hours",
            "Take regular breaks to maintain focus (Pomodoro technique)",
            "Review and adjust your schedule weekly based on progress"
        ])
        
        formatted = ""
        for tip in tips:
            formatted += f"- {tip}\n"
        
        return formatted
    
    def _generate_targeted_support(self, support_type: str, message: str) -> str:
        """Generate targeted support based on the type of challenge"""
        
        support_responses = {
            "difficulty": """I understand you're facing some challenges! This is completely normal in the learning process. Here are some strategies to help:

🧩 **Break It Down**
- Identify the specific concept causing difficulty
- Break complex topics into smaller, manageable pieces
- Start with simpler examples and gradually increase complexity

🔄 **Try Different Approaches**
- If one explanation doesn't click, try learning from different sources
- Use multiple learning methods (visual, hands-on, reading)
- Ask questions in online communities or forums

⏱️ **Take Strategic Breaks**
- Sometimes stepping away helps your brain process information
- Come back with fresh perspective after a break
- Sleep on difficult concepts - your brain works on them overnight!

What specific topic or concept is giving you trouble? I can help you find alternative explanations or approaches.""",

            "motivation": """I hear you, and what you're feeling is completely valid! Learning plateaus and motivation dips happen to everyone. Let's reignite your learning spark:

🎯 **Reconnect with Your Why**
- Remember your original goals and motivation
- Visualize where this learning will take you
- Celebrate how far you've already come

🏆 **Set Micro-Goals**
- Break your learning into tiny, achievable wins
- Celebrate completing even small tasks
- Track your progress visually (checkmarks, progress bars)

👥 **Find Your Tribe**
- Join learning communities or study groups
- Share your journey on social media
- Find an accountability partner

🎉 **Make it Enjoyable**
- Gamify your learning with challenges or competitions
- Work on projects that genuinely interest you
- Reward yourself for milestones achieved

What originally motivated you to start this learning journey? Let's reconnect with that spark!""",

            "time_management": """Time management is one of the biggest learning challenges! Let's optimize your approach:

⚡ **Maximize Efficiency**
- Use the Pomodoro Technique (25-min focused sessions)
- Identify your peak learning hours and protect them
- Eliminate distractions during study time

🔄 **Flexible Learning**
- Use micro-learning sessions (10-15 minutes)
- Learn during commute, waiting times, or breaks
- Audio content for passive learning moments

📋 **Smart Prioritization**
- Focus on high-impact skills first
- Use the 80/20 rule - 20% of efforts yield 80% of results
- Cut less important activities temporarily

⚖️ **Balance and Sustainability**
- Don't aim for perfection, aim for consistency
- 20 minutes daily beats 3 hours once a week
- Build learning habits into your existing routine

How many hours per week can you realistically dedicate? Let's create a sustainable plan that fits your life.""",

            "progress_tracking": """Tracking progress effectively is crucial for motivation and success! Here's how to do it right:

📊 **Meaningful Metrics**
- Track skills gained, not just time spent
- Document projects completed and problems solved
- Note confidence levels in different areas

📝 **Regular Reviews**
- Weekly progress check-ins with yourself
- Monthly reviews of goals and adjustments needed
- Compare where you are now vs. where you started

🎯 **Visual Progress**
- Use progress bars, checklists, or charts
- Take screenshots of projects or certificates
- Keep a learning journal with reflections

🔄 **Adaptive Planning**
- Adjust timeline based on actual progress
- Celebrate unexpected breakthroughs
- Learn from setbacks and adapt strategy

What aspects of your learning progress would you like to track better? I can help you set up a system that works for you.""",

            "general": """I'm here to support your learning journey in whatever way you need! Whether you're facing:

- Difficulty understanding concepts
- Motivation challenges
- Time management issues
- Progress tracking concerns
- Resource selection questions
- Schedule optimization needs

Remember: Every expert was once a beginner, and every professional faced the same challenges you're experiencing now. The key is persistence and finding the right approach for YOU.

What specific aspect of your learning would you like help with today?"""
        }
        
        return support_responses.get(support_type, support_responses["general"])
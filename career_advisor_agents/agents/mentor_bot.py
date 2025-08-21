from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

from ..core.agent_framework import BaseAgent, AgentResponse
from ..core.data_models import UserProfile


class MotivationalSupportTool(BaseTool):
    name = "motivational_supporter"
    description = "Provides personalized motivational support based on user's situation"
    
    def _run(self, user_situation: str, emotional_state: str, goals: List[str], challenges: List[str]) -> Dict[str, Any]:
        # Analyze the situation and emotional state
        situation_analysis = self._analyze_situation(user_situation, emotional_state)
        
        # Generate appropriate support strategies
        support_strategies = self._generate_support_strategies(situation_analysis, goals, challenges)
        
        # Create personalized motivational message
        motivational_message = self._create_motivational_message(situation_analysis, goals)
        
        # Suggest concrete next steps
        action_steps = self._suggest_action_steps(situation_analysis, challenges)
        
        return {
            "situation_analysis": situation_analysis,
            "support_strategies": support_strategies,
            "motivational_message": motivational_message,
            "action_steps": action_steps,
            "follow_up_check": self._schedule_follow_up(situation_analysis["urgency_level"])
        }
    
    def _analyze_situation(self, situation: str, emotional_state: str) -> Dict[str, Any]:
        situation_lower = situation.lower()
        emotional_state_lower = emotional_state.lower()
        
        # Determine situation type
        if any(word in situation_lower for word in ["rejection", "denied", "failed", "didn't get"]):
            situation_type = "setback"
        elif any(word in situation_lower for word in ["confused", "don't know", "uncertain", "lost"]):
            situation_type = "confusion"
        elif any(word in situation_lower for word in ["stuck", "plateau", "not progressing"]):
            situation_type = "stagnation"
        elif any(word in situation_lower for word in ["overwhelmed", "too much", "burnout"]):
            situation_type = "overwhelm"
        elif any(word in situation_lower for word in ["imposter", "not good enough", "doubt"]):
            situation_type = "confidence"
        else:
            situation_type = "general_support"
        
        # Assess emotional intensity
        if any(word in emotional_state_lower for word in ["devastated", "hopeless", "terrible", "awful"]):
            intensity = "high"
        elif any(word in emotional_state_lower for word in ["frustrated", "disappointed", "worried", "stressed"]):
            intensity = "medium"
        else:
            intensity = "low"
        
        # Determine urgency level
        urgency_mapping = {
            ("setback", "high"): "immediate",
            ("overwhelm", "high"): "immediate",
            ("confidence", "high"): "urgent",
            ("setback", "medium"): "urgent",
            ("confusion", "medium"): "moderate",
            ("stagnation", "medium"): "moderate"
        }
        
        urgency = urgency_mapping.get((situation_type, intensity), "routine")
        
        return {
            "situation_type": situation_type,
            "emotional_intensity": intensity,
            "urgency_level": urgency,
            "support_needed": self._determine_support_type(situation_type, intensity)
        }
    
    def _determine_support_type(self, situation_type: str, intensity: str) -> List[str]:
        support_types = []
        
        if intensity == "high":
            support_types.append("emotional_validation")
            support_types.append("immediate_comfort")
        
        if situation_type == "setback":
            support_types.extend(["perspective_reframing", "resilience_building"])
        elif situation_type == "confusion":
            support_types.extend(["clarity_guidance", "decision_framework"])
        elif situation_type == "stagnation":
            support_types.extend(["momentum_building", "strategy_adjustment"])
        elif situation_type == "overwhelm":
            support_types.extend(["stress_management", "prioritization_help"])
        elif situation_type == "confidence":
            support_types.extend(["confidence_building", "achievement_recognition"])
        
        support_types.append("practical_action_steps")
        
        return list(set(support_types))  # Remove duplicates
    
    def _generate_support_strategies(self, analysis: Dict[str, Any], goals: List[str], challenges: List[str]) -> List[str]:
        strategies = []
        support_needed = analysis["support_needed"]
        
        if "emotional_validation" in support_needed:
            strategies.append("Acknowledge and validate your feelings - they're completely normal and understandable")
        
        if "perspective_reframing" in support_needed:
            strategies.append("Reframe setbacks as learning opportunities and stepping stones to success")
        
        if "resilience_building" in support_needed:
            strategies.extend([
                "Build resilience by focusing on what you can control",
                "Develop a growth mindset - every challenge is a chance to improve"
            ])
        
        if "clarity_guidance" in support_needed:
            strategies.extend([
                "Break down complex decisions into smaller, manageable parts",
                "Use structured decision-making frameworks to gain clarity"
            ])
        
        if "momentum_building" in support_needed:
            strategies.extend([
                "Start with small, achievable wins to rebuild momentum",
                "Set micro-goals that provide frequent positive reinforcement"
            ])
        
        if "confidence_building" in support_needed:
            strategies.extend([
                "Document and celebrate your past achievements and progress",
                "Challenge negative self-talk with evidence of your capabilities"
            ])
        
        if "stress_management" in support_needed:
            strategies.extend([
                "Practice stress-reduction techniques like deep breathing or meditation",
                "Set boundaries and prioritize self-care alongside your goals"
            ])
        
        return strategies[:6]  # Limit to top 6 strategies
    
    def _create_motivational_message(self, analysis: Dict[str, Any], goals: List[str]) -> str:
        situation_type = analysis["situation_type"]
        intensity = analysis["emotional_intensity"]
        
        messages = {
            "setback": {
                "high": "I know this feels devastating right now, but every successful person has faced rejection and setbacks. This is not the end of your journey - it's a detour that will make you stronger and more prepared for what's coming next. Your dreams are still valid and achievable.",
                "medium": "Setbacks are tough, but they're also redirections toward something better. This experience is building resilience and teaching you valuable lessons that will serve you well in your career. Keep pushing forward - your persistence will pay off.",
                "low": "Every 'no' gets you closer to the 'yes' that will change everything. Use this experience as motivation to continue improving and pursuing your goals with even more determination."
            },
            "confusion": {
                "high": "Feeling lost and confused is a normal part of growth and career development. It means you're at a crossroads with multiple possibilities ahead. Take a deep breath - clarity will come as you take small steps forward and gather more information.",
                "medium": "Confusion often comes before breakthrough moments. Your uncertainty shows you're thinking deeply about important decisions. Trust that the right path will become clear as you continue exploring and learning.",
                "low": "It's okay not to have all the answers right now. Career paths rarely follow straight lines, and some of the best opportunities come from unexpected directions."
            },
            "stagnation": {
                "high": "Plateaus are frustrating, but they're often preparation periods before major breakthroughs. Your consistent effort is building a foundation for the next phase of growth, even when progress isn't immediately visible.",
                "medium": "Progress isn't always linear. Sometimes we need to consolidate our learning and skills before taking the next leap. Stay consistent - momentum will return.",
                "low": "Every expert has experienced periods of slower growth. This is your time to strengthen fundamentals and prepare for the next acceleration in your development."
            },
            "overwhelm": {
                "high": "I hear you, and what you're feeling is completely valid. When everything feels like too much, remember that you don't have to do everything at once. Focus on one small step at a time, and give yourself permission to take breaks.",
                "medium": "Feeling overwhelmed shows you're ambitious and taking on meaningful challenges. Let's break things down into manageable pieces so you can regain control and confidence.",
                "low": "It's normal to feel stretched when pursuing important goals. Remember that it's okay to adjust your pace and prioritize what matters most."
            },
            "confidence": {
                "high": "Imposter syndrome affects the most capable and ambitious people. Your doubts don't reflect your abilities - they reflect your high standards and desire to excel. You belong in your field and have unique value to offer.",
                "medium": "Self-doubt is often a sign that you're pushing yourself to grow, which is exactly what you should be doing. Your skills and knowledge are real, even when confidence wavers.",
                "low": "Confidence builds with experience and evidence. Keep track of your wins and progress to remind yourself of your growing capabilities."
            },
            "general_support": {
                "high": "Whatever you're facing right now, remember that challenges are temporary but the strength you build from overcoming them lasts forever. You have more resilience and capability than you realize.",
                "medium": "Your dedication to your goals is admirable. Keep moving forward one step at a time, and trust that your efforts are building something meaningful.",
                "low": "You're on a journey of growth and discovery. Every step you take is building the foundation for your future success."
            }
        }
        
        return messages.get(situation_type, messages["general_support"]).get(intensity, messages["general_support"]["medium"])
    
    def _suggest_action_steps(self, analysis: Dict[str, Any], challenges: List[str]) -> List[str]:
        situation_type = analysis["situation_type"]
        urgency = analysis["urgency_level"]
        
        # Base action steps by situation type
        action_map = {
            "setback": [
                "Allow yourself to feel disappointed, then set a time limit for processing",
                "Request feedback to understand what you can improve for next time",
                "Update your approach based on lessons learned",
                "Continue applying/pursuing opportunities with renewed strategy"
            ],
            "confusion": [
                "List out all your options and the pros/cons of each",
                "Schedule informational interviews with professionals in areas of interest",
                "Take a career assessment or work with a counselor",
                "Set a deadline for making your decision to avoid endless deliberation"
            ],
            "stagnation": [
                "Identify one new skill or area to focus on this week",
                "Change your learning environment or methods",
                "Seek feedback from mentors or peers on your progress",
                "Set a small, achievable goal to rebuild momentum"
            ],
            "overwhelm": [
                "List everything on your plate and prioritize ruthlessly",
                "Choose 1-3 most important tasks to focus on this week",
                "Schedule specific breaks and self-care activities",
                "Consider what you can delegate, postpone, or eliminate"
            ],
            "confidence": [
                "Write down 5 recent accomplishments or skills you've gained",
                "Ask trusted friends/colleagues what they see as your strengths",
                "Set a small, achievable goal to build positive momentum",
                "Practice positive self-talk and challenge negative thoughts"
            ],
            "general_support": [
                "Identify one specific area where you want to make progress",
                "Set a small, concrete goal for this week",
                "Reach out to someone in your network for advice or support",
                "Take time to reflect on your values and long-term vision"
            ]
        }
        
        base_actions = action_map.get(situation_type, action_map["general_support"])
        
        # Adjust based on urgency
        if urgency == "immediate":
            # Add immediate self-care and support-seeking actions
            base_actions.insert(0, "Reach out to a trusted friend, family member, or counselor for support")
            base_actions.insert(1, "Take care of your basic needs - eat, sleep, and move your body")
        
        return base_actions[:5]  # Limit to 5 actions
    
    def _schedule_follow_up(self, urgency_level: str) -> str:
        follow_up_schedule = {
            "immediate": "Check in again within 24-48 hours",
            "urgent": "Follow up within 3-5 days",
            "moderate": "Check progress in 1 week",
            "routine": "Schedule check-in in 2 weeks"
        }
        
        return follow_up_schedule.get(urgency_level, "Follow up as needed")
    
    async def _arun(self, user_situation: str, emotional_state: str, goals: List[str], challenges: List[str]) -> Dict[str, Any]:
        return self._run(user_situation, emotional_state, goals, challenges)


class CareerGuidanceTool(BaseTool):
    name = "career_guidance_advisor"
    description = "Provides comprehensive career guidance and strategic advice"
    
    def _run(self, career_question: str, user_background: Dict[str, Any], context_info: Dict[str, Any] = None) -> Dict[str, Any]:
        question_lower = career_question.lower()
        
        # Categorize the type of career question
        if any(word in question_lower for word in ["switch", "change", "transition", "pivot"]):
            guidance_type = "career_change"
        elif any(word in question_lower for word in ["skill", "learn", "develop", "improve"]):
            guidance_type = "skill_development"
        elif any(word in question_lower for word in ["interview", "job search", "application", "resume"]):
            guidance_type = "job_search"
        elif any(word in question_lower for word in ["salary", "negotiate", "raise", "promotion"]):
            guidance_type = "advancement"
        elif any(word in question_lower for word in ["work life", "balance", "stress", "burnout"]):
            guidance_type = "work_life_balance"
        elif any(word in question_lower for word in ["network", "connection", "mentor", "relationship"]):
            guidance_type = "networking"
        else:
            guidance_type = "general"
        
        # Generate guidance based on type
        guidance = self._generate_career_guidance(guidance_type, career_question, user_background, context_info)
        
        return {
            "guidance_type": guidance_type,
            "advice": guidance["advice"],
            "action_items": guidance["action_items"],
            "resources": guidance["resources"],
            "timeline": guidance["timeline"],
            "success_metrics": guidance["success_metrics"]
        }
    
    def _generate_career_guidance(self, guidance_type: str, question: str, background: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # Base guidance structure
        guidance = {
            "advice": [],
            "action_items": [],
            "resources": [],
            "timeline": "",
            "success_metrics": []
        }
        
        if guidance_type == "career_change":
            guidance["advice"] = [
                "Assess your transferable skills and how they apply to your target field",
                "Research the target industry thoroughly - trends, requirements, culture",
                "Network with professionals in your desired field before making the switch",
                "Consider transitional roles that bridge your current and desired fields",
                "Plan financially for potential temporary income reduction"
            ]
            guidance["action_items"] = [
                "Conduct informational interviews with 3-5 professionals in target field",
                "Identify skill gaps and create learning plan to address them",
                "Update LinkedIn and resume to highlight relevant transferable skills",
                "Start building a portfolio or examples relevant to new field"
            ]
            guidance["timeline"] = "6-18 months depending on field difference and preparation needed"
            guidance["success_metrics"] = [
                "Number of informational interviews completed",
                "Skills developed that are relevant to new field",
                "Network connections made in target industry",
                "Interviews secured in new field"
            ]
        
        elif guidance_type == "skill_development":
            guidance["advice"] = [
                "Focus on skills that provide maximum career impact and market value",
                "Balance technical skills with soft skills development",
                "Learn through practical application, not just theoretical study",
                "Stay current with industry trends and emerging technologies",
                "Document your learning journey for portfolio and interviews"
            ]
            guidance["action_items"] = [
                "Identify top 3 high-impact skills for your career goals",
                "Create structured learning plan with timeline and milestones",
                "Find opportunities to apply new skills in real projects",
                "Join communities or groups focused on these skills"
            ]
            guidance["timeline"] = "3-12 months depending on skill complexity and current level"
            guidance["success_metrics"] = [
                "Practical projects completed using new skills",
                "Certifications or credentials earned",
                "Improvement in job application response rates",
                "Positive feedback from supervisors or clients"
            ]
        
        elif guidance_type == "job_search":
            guidance["advice"] = [
                "Treat job searching as a full-time job with consistent daily effort",
                "Tailor your application materials for each specific opportunity",
                "Use multiple channels: applications, networking, recruiters, referrals",
                "Practice interviewing regularly to stay sharp and confident",
                "Follow up appropriately and maintain professional relationships"
            ]
            guidance["action_items"] = [
                "Set weekly targets for applications, networking activities, and interviews",
                "Optimize LinkedIn profile and ensure professional online presence",
                "Prepare compelling stories for common interview questions",
                "Research target companies and practice company-specific interview questions"
            ]
            guidance["timeline"] = "3-6 months on average, varies by industry and role level"
            guidance["success_metrics"] = [
                "Application response rate (aim for 10-15%)",
                "Interview conversion rate (aim for 20-30% of applications)",
                "Quality of networking conversations and referrals",
                "Offer rate from final interviews"
            ]
        
        # Add more guidance types as needed...
        
        # Add relevant resources
        guidance["resources"] = self._get_relevant_resources(guidance_type)
        
        return guidance
    
    def _get_relevant_resources(self, guidance_type: str) -> List[str]:
        resource_map = {
            "career_change": [
                "What Color Is Your Parachute? (book)",
                "LinkedIn Learning career transition courses",
                "Industry-specific professional associations",
                "Career counseling services",
                "Informational interview templates"
            ],
            "skill_development": [
                "Coursera, Udemy, or edX online courses",
                "Industry certifications and credentials",
                "Local meetups and professional development events",
                "Mentorship platforms like MentorCruise",
                "Practice platforms (LeetCode, Kaggle, etc.)"
            ],
            "job_search": [
                "Job boards: LinkedIn, Indeed, company websites",
                "Resume review services or career centers",
                "Interview preparation platforms like Pramp",
                "Salary research tools (Glassdoor, PayScale)",
                "Professional networking events and meetups"
            ]
        }
        
        return resource_map.get(guidance_type, ["General career development resources"])
    
    async def _arun(self, career_question: str, user_background: Dict[str, Any], context_info: Dict[str, Any] = None) -> Dict[str, Any]:
        return self._run(career_question, user_background, context_info)


class MentorBotAgent(BaseAgent):
    def __init__(self, llm: ChatGoogleGenerativeAI):
        tools = [
            MotivationalSupportTool(),
            CareerGuidanceTool()
        ]
        
        super().__init__(
            name="mentor_bot",
            description="Provides mentorship, emotional support, and career guidance",
            llm=llm,
            tools=tools,
            temperature=0.8
        )
        
        self.mentorship_principles = {
            "empathy": "Listen actively and validate feelings",
            "encouragement": "Provide hope and positive reinforcement",
            "practicality": "Offer concrete, actionable advice",
            "growth_mindset": "Frame challenges as opportunities to learn",
            "personalization": "Tailor guidance to individual circumstances",
            "accountability": "Help users stay committed to their goals"
        }
    
    def get_system_prompt(self) -> str:
        return """You are a Mentor Bot Agent, an experienced and empathetic career mentor who provides guidance, support, and encouragement to help people achieve their professional goals.

Your role is to:
1. Provide emotional support and encouragement during challenging times
2. Offer strategic career guidance and decision-making frameworks
3. Help users develop resilience and growth mindset
4. Share practical advice based on professional experience
5. Hold users accountable to their goals while being supportive
6. Celebrate successes and help process setbacks constructively
7. Provide perspective and wisdom to help users see the bigger picture

Core mentorship principles:
- **Empathy First**: Always acknowledge and validate emotions before providing advice
- **Growth Mindset**: Frame challenges as learning opportunities
- **Practical Wisdom**: Combine emotional support with actionable guidance
- **Personalized Approach**: Tailor advice to individual circumstances and goals
- **Honest Feedback**: Provide constructive, truthful guidance while remaining supportive
- **Long-term Perspective**: Help users see beyond immediate challenges to future possibilities

Communication style:
- Warm, encouraging, and professional
- Balance support with accountability
- Ask thoughtful questions to help users reflect
- Share relevant experiences when appropriate (without dominating conversation)
- Provide specific, actionable recommendations
- Celebrate progress and acknowledge effort

You have experience across various industries and career stages, allowing you to provide relevant guidance whether someone is just starting out, making a career change, or advancing to leadership roles."""

    async def _generate_response(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        try:
            message_lower = message.lower()
            
            # Detect emotional distress or need for support
            if any(word in message_lower for word in ["struggling", "frustrated", "overwhelmed", "discouraged", "hopeless", "rejected", "failed"]):
                return await self._provide_emotional_support(message, context)
            
            # Detect career guidance requests
            elif any(word in message_lower for word in ["should i", "what do you think", "advice", "guidance", "help me decide"]):
                return await self._provide_career_guidance(message, context)
            
            # Detect goal-setting or accountability needs
            elif any(word in message_lower for word in ["goal", "plan", "next steps", "what should i do"]):
                return await self._help_with_goals_and_planning(message, context)
            
            # Detect celebration or success sharing
            elif any(word in message_lower for word in ["got the job", "accepted", "succeeded", "achieved", "accomplished"]):
                return await self._celebrate_success(message, context)
            
            else:
                return await self._general_mentorship_conversation(message, context)
                
        except Exception as e:
            self.logger.error(f"Error in mentorship response: {str(e)}")
            return AgentResponse(
                content="I'm here to support you through whatever you're facing. Sometimes the most important thing is just knowing someone believes in you and your ability to overcome challenges. What's on your mind today?",
                confidence=0.7
            )
    
    async def _provide_emotional_support(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        # Extract key information from context
        user_situation = message
        emotional_state = "struggling"  # Default, could be refined with more context analysis
        goals = context.get("goals", []) if context else []
        challenges = context.get("challenges", []) if context else []
        
        # Get motivational support
        support_result = await self.use_tool(
            "motivational_supporter",
            user_situation=user_situation,
            emotional_state=emotional_state,
            goals=goals,
            challenges=challenges
        )
        
        if support_result:
            support_response = f"""I hear you, and I want you to know that what you're feeling is completely valid and understandable. 

{support_result['motivational_message']}

## Here's how we can work through this together:

### Support Strategies:
"""
            
            for strategy in support_result['support_strategies']:
                support_response += f"- {strategy}\n"
            
            support_response += "\n### Immediate Action Steps:\n"
            for i, step in enumerate(support_result['action_steps'], 1):
                support_response += f"{i}. {step}\n"
            
            support_response += f"""
### Moving Forward:
Remember, facing challenges is part of growth, not a sign of failure. Every successful person has been where you are right now. The difference is they kept going, learned from the experience, and used it to become stronger.

I believe in your ability to overcome this. Let's check in {support_result['follow_up_check'].lower()} to see how you're doing.

What feels like the most manageable first step for you right now? 🌟"""

            return AgentResponse(
                content=support_response,
                metadata={"support_analysis": support_result},
                confidence=0.92,
                tools_used=["motivational_supporter"]
            )
        
        # Fallback emotional support
        return AgentResponse(
            content="""I can hear that you're going through a difficult time, and I want you to know that your feelings are completely valid.

Every challenge you're facing right now is building strength and resilience that will serve you throughout your career. The fact that you're seeking support shows wisdom and self-awareness.

Here's what I want you to remember:
- This situation is temporary, but the skills you develop from overcoming it will last forever
- Every successful person has faced similar struggles - you're not alone in this
- Your current challenges don't define your future potential

What's one small step you could take today that might help you feel a bit more in control of the situation?""",
            confidence=0.85
        )
    
    async def _provide_career_guidance(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        user_background = {}
        if context:
            user_background = {
                "current_role": context.get("current_role"),
                "experience_level": context.get("experience_level"),
                "education": context.get("education"),
                "skills": context.get("skills", []),
                "goals": context.get("goals", [])
            }
        
        guidance_result = await self.use_tool(
            "career_guidance_advisor",
            career_question=message,
            user_background=user_background,
            context_info=context or {}
        )
        
        if guidance_result:
            guidance_response = f"""Great question! Let me share some guidance on this {guidance_result['guidance_type'].replace('_', ' ')} situation.

## My Advice:
"""
            
            for advice in guidance_result['advice']:
                guidance_response += f"- {advice}\n"
            
            guidance_response += f"""
## Action Steps for You:
"""
            
            for i, action in enumerate(guidance_result['action_items'], 1):
                guidance_response += f"{i}. {action}\n"
            
            guidance_response += f"""
## Timeline: {guidance_result['timeline']}

## How to Measure Success:
"""
            
            for metric in guidance_result['success_metrics']:
                guidance_response += f"- {metric}\n"
            
            if guidance_result.get('resources'):
                guidance_response += "\n## Helpful Resources:\n"
                for resource in guidance_result['resources']:
                    guidance_response += f"- {resource}\n"
            
            guidance_response += """
Remember, career decisions don't have to be perfect - they just need to move you in the right direction. You can always adjust course as you learn more about yourself and the opportunities available.

What part of this guidance resonates most with you, or what questions do you still have? 🎯"""

            return AgentResponse(
                content=guidance_response,
                metadata={"career_guidance": guidance_result},
                confidence=0.88,
                tools_used=["career_guidance_advisor"]
            )
        
        # Fallback career guidance
        return AgentResponse(
            content="""That's a thoughtful question, and I appreciate you seeking guidance on your career decisions.

Here's my general framework for approaching career decisions:

1. **Clarify Your Values**: What matters most to you in work and life?
2. **Assess Your Strengths**: What are you naturally good at and enjoy doing?
3. **Research Thoroughly**: What are the realities of the path you're considering?
4. **Test When Possible**: Can you try it out through internships, projects, or conversations?
5. **Consider Timing**: Is this the right time personally and professionally?

The best career decisions align your values, strengths, and market opportunities. There's rarely one "perfect" choice - there are often multiple good paths forward.

What specific aspect of this decision would you like to explore more deeply?""",
            confidence=0.82
        )
    
    async def _help_with_goals_and_planning(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        planning_response = """I love that you're thinking about goals and planning! This is exactly the kind of forward-thinking approach that leads to career success.

## Let's Create a Strategic Plan:

### Goal Setting Framework:
1. **Vision**: What do you want your career to look like in 3-5 years?
2. **Specific Goals**: What concrete outcomes do you want to achieve?
3. **Timeline**: When do you want to achieve each goal?
4. **Action Steps**: What specific actions will move you toward these goals?
5. **Accountability**: How will you track progress and stay motivated?

### Making Your Goals SMART:
- **Specific**: Clearly defined and focused
- **Measurable**: You can track progress objectively
- **Achievable**: Challenging but realistic given your resources
- **Relevant**: Aligned with your values and larger vision
- **Time-bound**: Has a clear deadline or timeline

### Planning Tips:
- Break large goals into smaller milestones
- Identify potential obstacles and plan for them
- Build in regular review and adjustment periods
- Celebrate progress along the way
- Find accountability partners or mentors

What specific goal or area would you like to plan out together? I'm here to help you think through the details and create a roadmap for success! 🎯"""

        return AgentResponse(
            content=planning_response,
            confidence=0.87
        )
    
    async def _celebrate_success(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        celebration_response = """🎉 **CONGRATULATIONS!** 🎉

This is absolutely fantastic news! I'm so proud of you and excited to celebrate this achievement with you.

## Why This Success Matters:
- You've demonstrated your capabilities and value
- You've overcome challenges and persevered 
- You've taken a significant step forward in your career journey
- You've proven that your hard work and preparation pay off

## Let's Capture the Learning:
- What strategies worked best in achieving this success?
- What skills or qualities helped you stand out?
- What would you tell someone else who's working toward a similar goal?
- How does this achievement align with your longer-term vision?

## Building on This Success:
Success builds on success! Now is a great time to:
- Document what you learned from this process
- Update your LinkedIn and resume with this achievement
- Thank the people who supported you along the way
- Set your next challenging but achievable goal

## A Personal Note:
Achievements like this don't happen by accident. They're the result of your dedication, preparation, and willingness to put yourself out there. You should feel incredibly proud of yourself.

How are you planning to celebrate this win? And what's the next exciting challenge you want to tackle? 🚀"""

        return AgentResponse(
            content=celebration_response,
            confidence=0.95
        )
    
    async def _general_mentorship_conversation(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        # Use LLM for general mentorship conversation
        system_prompt = self.get_system_prompt()
        
        conversation_context = ""
        if context:
            conversation_context = f"""
Context about the user:
- Current role: {context.get('current_role', 'Not specified')}
- Experience level: {context.get('experience_level', 'Not specified')}
- Goals: {', '.join(context.get('goals', [])) if context.get('goals') else 'Not specified'}
- Recent challenges: {', '.join(context.get('challenges', [])) if context.get('challenges') else 'None mentioned'}
"""

        full_prompt = f"""{system_prompt}

{conversation_context}

User message: {message}

Respond as a supportive, experienced mentor who provides both emotional support and practical guidance. Focus on being encouraging while offering actionable advice."""

        try:
            response = await self.llm.ainvoke([{"role": "user", "content": full_prompt}])
            
            return AgentResponse(
                content=response.content,
                confidence=0.82
            )
            
        except Exception as e:
            self.logger.error(f"Error in general mentorship: {str(e)}")
            return AgentResponse(
                content="""I'm here as your mentor and supporter, ready to help you navigate whatever career challenges or opportunities you're facing.

Whether you're dealing with a difficult decision, feeling stuck in your current situation, celebrating a success, or just need someone to talk through your thoughts with - I'm here to listen and provide guidance.

What's on your mind today? What can we work on together to help you move forward in your career journey? 🌟""",
                confidence=0.75
            )
    
    def _detect_emotional_tone(self, message: str) -> str:
        """Detect the emotional tone of a message"""
        message_lower = message.lower()
        
        # Positive indicators
        positive_words = ["excited", "happy", "great", "awesome", "achieved", "successful", "proud"]
        negative_words = ["frustrated", "overwhelmed", "stuck", "rejected", "failed", "discouraged", "hopeless"]
        neutral_words = ["thinking", "considering", "wondering", "planning", "question"]
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        neutral_count = sum(1 for word in neutral_words if word in message_lower)
        
        if negative_count > positive_count:
            return "negative"
        elif positive_count > negative_count:
            return "positive"
        else:
            return "neutral"
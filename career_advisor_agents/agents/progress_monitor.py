from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

from ..core.agent_framework import BaseAgent, AgentResponse
from ..core.data_models import ProgressUpdate, UserGoal


class ProgressAnalysisTool(BaseTool):
    name = "progress_analyzer"
    description = "Analyzes learning progress and identifies trends"
    
    def _run(self, progress_data: List[Dict[str, Any]], goals: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not progress_data:
            return {
                "overall_progress": 0.0,
                "trend": "no_data",
                "insights": ["No progress data available yet"],
                "recommendations": ["Start tracking your learning activities"]
            }
        
        # Calculate overall progress metrics
        total_progress = sum(entry.get("progress_percentage", 0) for entry in progress_data)
        avg_progress = total_progress / len(progress_data)
        
        # Analyze progress trend
        if len(progress_data) >= 2:
            recent_progress = progress_data[-3:]  # Last 3 entries
            older_progress = progress_data[-6:-3] if len(progress_data) >= 6 else progress_data[:-3]
            
            if older_progress:
                recent_avg = sum(entry.get("progress_percentage", 0) for entry in recent_progress) / len(recent_progress)
                older_avg = sum(entry.get("progress_percentage", 0) for entry in older_progress) / len(older_progress)
                
                if recent_avg > older_avg + 5:
                    trend = "accelerating"
                elif recent_avg < older_avg - 5:
                    trend = "slowing"
                else:
                    trend = "steady"
            else:
                trend = "steady"
        else:
            trend = "insufficient_data"
        
        # Generate insights
        insights = []
        recommendations = []
        
        # Progress level insights
        if avg_progress >= 80:
            insights.append("Excellent progress! You're on track to exceed your goals")
            recommendations.append("Consider setting more ambitious targets")
        elif avg_progress >= 60:
            insights.append("Good progress! You're making solid advancement")
            recommendations.append("Maintain current pace and stay consistent")
        elif avg_progress >= 40:
            insights.append("Moderate progress. There's room for improvement")
            recommendations.append("Consider increasing study time or changing approach")
        else:
            insights.append("Progress is slower than ideal. Time to reassess strategy")
            recommendations.append("Review your learning methods and time allocation")
        
        # Trend insights
        if trend == "accelerating":
            insights.append("Your learning velocity is increasing - great momentum!")
            recommendations.append("Capitalize on this momentum by tackling challenging topics")
        elif trend == "slowing":
            insights.append("Progress has slowed recently. This might indicate fatigue or increased difficulty")
            recommendations.append("Consider taking a strategic break or simplifying current topics")
        
        # Activity pattern analysis
        activities_completed = sum(len(entry.get("milestones_completed", [])) for entry in progress_data)
        challenges_identified = sum(len(entry.get("challenges", [])) for entry in progress_data)
        
        if challenges_identified > activities_completed:
            insights.append("You're encountering more challenges than completing activities")
            recommendations.append("Focus on overcoming current challenges before taking on new ones")
        
        # Goal alignment analysis
        goal_progress = {}
        for goal in goals:
            goal_name = goal.get("title", "")
            related_progress = [p for p in progress_data if p.get("goal_name") == goal_name]
            if related_progress:
                goal_avg = sum(p.get("progress_percentage", 0) for p in related_progress) / len(related_progress)
                goal_progress[goal_name] = goal_avg
        
        return {
            "overall_progress": avg_progress,
            "trend": trend,
            "activities_completed": activities_completed,
            "challenges_identified": challenges_identified,
            "goal_progress": goal_progress,
            "insights": insights,
            "recommendations": recommendations,
            "last_update": max(entry.get("date_recorded", datetime.now()) for entry in progress_data) if progress_data else None
        }
    
    async def _arun(self, progress_data: List[Dict[str, Any]], goals: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._run(progress_data, goals)


class MotivationAssessmentTool(BaseTool):
    name = "motivation_assessor"
    description = "Assesses motivation levels and suggests interventions"
    
    def _run(self, recent_activities: List[str], challenges: List[str], achievements: List[str]) -> Dict[str, Any]:
        # Calculate motivation indicators
        activity_score = len(recent_activities) * 2  # Activities are positive
        challenge_score = len(challenges) * -1      # Challenges are negative
        achievement_score = len(achievements) * 3   # Achievements are very positive
        
        raw_score = activity_score + challenge_score + achievement_score
        
        # Normalize to 0-100 scale
        motivation_level = max(0, min(100, 50 + raw_score * 5))
        
        # Determine motivation category
        if motivation_level >= 75:
            category = "high"
            description = "High motivation and engagement"
        elif motivation_level >= 50:
            category = "moderate"
            description = "Moderate motivation with room for improvement"
        elif motivation_level >= 25:
            category = "low"
            description = "Low motivation - intervention needed"
        else:
            category = "very_low"
            description = "Very low motivation - significant support required"
        
        # Generate motivational interventions
        interventions = self._generate_interventions(category, challenges, achievements)
        
        return {
            "motivation_level": motivation_level,
            "category": category,
            "description": description,
            "factors": {
                "recent_activities": len(recent_activities),
                "challenges_faced": len(challenges),
                "achievements_earned": len(achievements)
            },
            "interventions": interventions
        }
    
    def _generate_interventions(self, category: str, challenges: List[str], achievements: List[str]) -> List[str]:
        interventions = []
        
        if category == "high":
            interventions = [
                "Maintain momentum by setting stretch goals",
                "Share your success story to inspire others",
                "Consider mentoring someone else in their learning journey"
            ]
        elif category == "moderate":
            interventions = [
                "Set smaller, more achievable milestones",
                "Find a learning buddy or accountability partner",
                "Celebrate recent wins and progress made"
            ]
        elif category == "low":
            interventions = [
                "Take a strategic break to avoid burnout",
                "Revisit your original motivation and goals",
                "Switch to easier, more engaging learning materials",
                "Seek support from mentors or learning communities"
            ]
        else:  # very_low
            interventions = [
                "Consider pausing current learning to reassess goals",
                "Speak with a mentor or counselor about your challenges",
                "Focus on basic self-care and stress management",
                "Restart with much simpler, more manageable tasks"
            ]
        
        # Add challenge-specific interventions
        if challenges:
            if any("time" in challenge.lower() for challenge in challenges):
                interventions.append("Explore micro-learning techniques for better time management")
            if any("difficult" in challenge.lower() or "hard" in challenge.lower() for challenge in challenges):
                interventions.append("Break down difficult concepts into smaller, manageable pieces")
        
        return interventions
    
    async def _arun(self, recent_activities: List[str], challenges: List[str], achievements: List[str]) -> Dict[str, Any]:
        return self._run(recent_activities, challenges, achievements)


class ProgressMonitorAgent(BaseAgent):
    def __init__(self, llm: ChatGoogleGenerativeAI):
        tools = [
            ProgressAnalysisTool(),
            MotivationAssessmentTool()
        ]
        
        super().__init__(
            name="progress_monitor",
            description="Monitors learning progress, tracks goals, and maintains motivation",
            llm=llm,
            tools=tools,
            temperature=0.4
        )
        
        self.progress_metrics = {
            "completion_rate": "Percentage of planned activities completed",
            "consistency": "Regular engagement with learning activities",
            "quality": "Depth of understanding and skill application",
            "momentum": "Rate of progress acceleration or deceleration"
        }
    
    def get_system_prompt(self) -> str:
        return """You are a Progress Monitor Agent, an expert in tracking learning progress, maintaining motivation, and optimizing learning outcomes.

Your role is to:
1. Analyze learning progress data to identify trends and patterns
2. Track goal completion and milestone achievement
3. Assess motivation levels and provide targeted interventions
4. Generate actionable insights from progress data
5. Provide encouragement and celebrate achievements
6. Identify obstacles and recommend solutions
7. Help learners stay accountable to their commitments

Key principles:
- Focus on progress, not perfection
- Celebrate small wins and milestones
- Identify patterns in learning behavior
- Provide constructive, actionable feedback
- Maintain a supportive and encouraging tone
- Help learners develop self-monitoring skills
- Adapt recommendations based on individual progress patterns

Progress dimensions you monitor:
- Quantitative metrics (completion rates, time spent, milestones achieved)
- Qualitative indicators (understanding depth, skill application, confidence)
- Consistency patterns (regular engagement, study habits)
- Motivation levels (enthusiasm, persistence, goal alignment)
- Challenge identification (obstacles, difficulties, blockers)

Always maintain a balance between honest assessment and motivational support."""

    async def _generate_response(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        try:
            message_lower = message.lower()
            
            if any(word in message_lower for word in ["progress", "how am i doing", "track"]):
                return await self._analyze_progress(message, context)
            elif any(word in message_lower for word in ["goal", "milestone", "target"]):
                return await self._review_goals(message, context)
            elif any(word in message_lower for word in ["stuck", "struggling", "difficult", "motivation"]):
                return await self._provide_motivation_support(message, context)
            elif any(word in message_lower for word in ["celebrate", "achievement", "completed"]):
                return await self._celebrate_achievements(message, context)
            else:
                return await self._general_progress_guidance(message, context)
                
        except Exception as e:
            self.logger.error(f"Error in progress monitoring: {str(e)}")
            return AgentResponse(
                content="I encountered an issue while analyzing your progress. Let me help you get back on track with your learning journey.",
                confidence=0.3
            )
    
    async def _analyze_progress(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "progress_data" in context:
            progress_data = context["progress_data"]
            goals = context.get("goals", [])
            
            analysis = await self.use_tool(
                "progress_analyzer",
                progress_data=progress_data,
                goals=goals
            )
            
            if analysis:
                trend_emoji = {
                    "accelerating": "🚀",
                    "steady": "📈",
                    "slowing": "⚠️",
                    "no_data": "📊"
                }
                
                progress_text = f"""# 📊 Your Learning Progress Report

## Overall Progress: {analysis['overall_progress']:.1f}%

**Trend**: {trend_emoji.get(analysis['trend'], '📈')} {analysis['trend'].replace('_', ' ').title()}

### 🎯 Key Metrics
- Activities Completed: {analysis['activities_completed']}
- Challenges Identified: {analysis['challenges_identified']}
- Last Update: {analysis.get('last_update', 'No recent updates')}

### 💡 Insights
"""
                for insight in analysis['insights']:
                    progress_text += f"- {insight}\n"
                
                progress_text += "\n### 🎯 Goal Progress\n"
                if analysis.get('goal_progress'):
                    for goal, progress in analysis['goal_progress'].items():
                        progress_text += f"- **{goal}**: {progress:.1f}%\n"
                else:
                    progress_text += "- No specific goal progress data available\n"
                
                progress_text += "\n### 📋 Recommendations\n"
                for recommendation in analysis['recommendations']:
                    progress_text += f"- {recommendation}\n"
                
                progress_text += f"\n{self._generate_motivational_message(analysis)}"
                
                return AgentResponse(
                    content=progress_text,
                    metadata={"progress_analysis": analysis},
                    confidence=0.88,
                    tools_used=["progress_analyzer"]
                )
        
        # Request progress data
        response = """I'd love to analyze your learning progress! To provide meaningful insights, please share:

1. **Recent Activities**: What have you been working on lately?
   - Courses completed or in progress
   - Projects finished or milestones reached
   - Skills practiced or developed

2. **Current Challenges**: What obstacles are you facing?
   - Specific topics you're struggling with
   - Time management issues
   - Motivation or focus problems

3. **Achievements**: What wins have you had recently?
   - Concepts that finally "clicked"
   - Projects you're proud of
   - Skills you've noticeably improved

4. **Goals**: What are you working towards?
   - Short-term learning objectives
   - Long-term career goals
   - Skill development targets

With this information, I can provide detailed insights about your progress trajectory and personalized recommendations for improvement."""

        return AgentResponse(
            content=response,
            confidence=0.8
        )
    
    async def _review_goals(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "goals" in context:
            goals = context["goals"]
            current_date = datetime.now()
            
            goal_review = """# 🎯 Goal Review and Assessment

## Current Goals Status
"""
            
            for goal in goals:
                goal_name = goal.get("title", "Unnamed Goal")
                progress = goal.get("progress_percentage", 0)
                target_date = goal.get("target_date")
                status = goal.get("status", "active")
                
                status_emoji = {
                    "active": "🔄",
                    "completed": "✅",
                    "paused": "⏸️",
                    "cancelled": "❌"
                }
                
                goal_review += f"""
### {status_emoji.get(status, '🔄')} {goal_name}
- **Progress**: {progress}%
- **Status**: {status.title()}
- **Target Date**: {target_date or 'Not set'}
"""
                
                # Add timeline analysis
                if target_date and status == "active":
                    try:
                        target_dt = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                        days_remaining = (target_dt - current_date).days
                        
                        if days_remaining < 0:
                            goal_review += f"- **Timeline**: ⚠️ Overdue by {abs(days_remaining)} days\n"
                        elif days_remaining < 30:
                            goal_review += f"- **Timeline**: 🚨 {days_remaining} days remaining\n"
                        else:
                            goal_review += f"- **Timeline**: ✅ {days_remaining} days remaining\n"
                    except:
                        goal_review += "- **Timeline**: Date format unclear\n"
                
                # Progress recommendations
                if progress < 25 and status == "active":
                    goal_review += "- **Recommendation**: Focus on getting started with small, achievable tasks\n"
                elif progress < 50 and status == "active":
                    goal_review += "- **Recommendation**: Good start! Maintain momentum with consistent effort\n"
                elif progress < 75 and status == "active":
                    goal_review += "- **Recommendation**: Strong progress! Push through to completion\n"
                elif progress >= 75 and status == "active":
                    goal_review += "- **Recommendation**: Almost there! Focus on finishing strong\n"
            
            goal_review += self._generate_goal_strategy_recommendations(goals)
            
            return AgentResponse(
                content=goal_review,
                metadata={"goal_analysis": goals},
                confidence=0.85
            )
        
        # Request goal information
        response = """Let's review your goals together! Please share:

1. **Current Goals**: What are you working towards?
   - Goal name and description
   - Current progress (as a percentage)
   - Target completion date
   - Current status (active, paused, completed)

2. **Priority Level**: Which goals are most important? (1-10 scale)

3. **Recent Progress**: What have you accomplished toward each goal recently?

4. **Obstacles**: What's preventing you from making faster progress?

5. **Timeline Concerns**: Are any deadlines approaching that worry you?

I'll help you assess where you stand, celebrate progress made, and create strategies to accelerate toward completion."""

        return AgentResponse(
            content=response,
            confidence=0.8
        )
    
    async def _provide_motivation_support(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and any(key in context for key in ["recent_activities", "challenges", "achievements"]):
            recent_activities = context.get("recent_activities", [])
            challenges = context.get("challenges", [])
            achievements = context.get("achievements", [])
            
            motivation_assessment = await self.use_tool(
                "motivation_assessor",
                recent_activities=recent_activities,
                challenges=challenges,
                achievements=achievements
            )
            
            if motivation_assessment:
                support_text = f"""# 🌟 Motivation Assessment & Support

## Current Motivation Level: {motivation_assessment['motivation_level']}/100

**Status**: {motivation_assessment['description']}

### 📈 Contributing Factors
- Recent Activities: {motivation_assessment['factors']['recent_activities']}
- Challenges Faced: {motivation_assessment['factors']['challenges_faced']}
- Achievements Earned: {motivation_assessment['factors']['achievements_earned']}

### 💪 Personalized Support Strategies
"""
                
                for intervention in motivation_assessment['interventions']:
                    support_text += f"- {intervention}\n"
                
                support_text += f"""
### 🎯 Immediate Action Steps
{self._generate_immediate_motivation_actions(motivation_assessment)}

Remember: Every expert was once a beginner who refused to give up. You've got this! 🚀"""

                return AgentResponse(
                    content=support_text,
                    metadata={"motivation_assessment": motivation_assessment},
                    confidence=0.87,
                    tools_used=["motivation_assessor"]
                )
        
        # Provide general motivational support
        message_lower = message.lower()
        
        if "stuck" in message_lower:
            support_type = "stuck"
        elif "motivation" in message_lower or "discouraged" in message_lower:
            support_type = "motivation"
        elif "difficult" in message_lower or "hard" in message_lower:
            support_type = "difficulty"
        else:
            support_type = "general"
        
        support_response = self._generate_contextual_support(support_type, message)
        
        return AgentResponse(
            content=support_response,
            confidence=0.82
        )
    
    async def _celebrate_achievements(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        achievements = context.get("achievements", []) if context else []
        
        celebration_text = """# 🎉 Celebrating Your Achievements!

"""
        
        if achievements:
            celebration_text += "## Recent Wins:\n"
            for achievement in achievements:
                celebration_text += f"🏆 {achievement}\n"
            
            celebration_text += f"""
## Why This Matters:
{self._generate_achievement_significance(achievements)}

## Building on Success:
{self._generate_momentum_builders(achievements)}
"""
        else:
            celebration_text += """I'd love to celebrate your achievements with you! 

What have you accomplished recently that you're proud of?
- Skills you've learned or improved
- Projects you've completed
- Challenges you've overcome
- Goals you've reached
- Milestones you've achieved

Every step forward deserves recognition! 🌟"""
        
        return AgentResponse(
            content=celebration_text,
            confidence=0.9
        )
    
    async def _general_progress_guidance(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        # Use LLM for general progress guidance
        system_prompt = self.get_system_prompt()
        
        full_prompt = f"""{system_prompt}

User message: {message}

Provide supportive guidance about progress monitoring, goal tracking, or maintaining motivation in learning."""

        try:
            response = await self.llm.ainvoke([{"role": "user", "content": full_prompt}])
            
            return AgentResponse(
                content=response.content,
                confidence=0.75
            )
            
        except Exception as e:
            self.logger.error(f"Error in general guidance: {str(e)}")
            return AgentResponse(
                content="I'm here to help you monitor your progress and stay motivated in your learning journey. You can ask me to analyze your progress, review your goals, provide motivation support, or celebrate your achievements. What would you like to focus on today?",
                confidence=0.6
            )
    
    def _generate_motivational_message(self, analysis: Dict[str, Any]) -> str:
        """Generate a motivational message based on progress analysis"""
        overall_progress = analysis['overall_progress']
        trend = analysis['trend']
        
        if overall_progress >= 80:
            if trend == "accelerating":
                return "🚀 **Outstanding!** You're not just succeeding, you're accelerating! Your dedication is paying off in a big way."
            else:
                return "🏆 **Excellent work!** You're maintaining high performance. Keep this momentum going!"
        elif overall_progress >= 60:
            if trend == "accelerating":
                return "📈 **Great progress!** You're picking up speed and building excellent momentum. You're on track for success!"
            else:
                return "👍 **Good job!** Solid, steady progress. Consistency like yours always pays off in the end."
        elif overall_progress >= 40:
            if trend == "slowing":
                return "💪 **Don't give up!** Progress might feel slow right now, but that's often when the most important learning happens. Push through!"
            else:
                return "🎯 **Keep going!** You're building a foundation. Every step forward counts, even when it doesn't feel like it."
        else:
            return "🌱 **Every journey starts with small steps!** You're learning and growing. Focus on progress, not perfection, and celebrate each small win."
    
    def _generate_goal_strategy_recommendations(self, goals: List[Dict[str, Any]]) -> str:
        """Generate strategic recommendations for goal achievement"""
        active_goals = [g for g in goals if g.get("status", "active") == "active"]
        
        if not active_goals:
            return "\n## 🎯 Goal Strategy\n- Consider setting new learning goals to maintain momentum\n- Review completed goals for lessons learned\n"
        
        recommendations = "\n## 🎯 Goal Strategy Recommendations\n"
        
        # Too many active goals
        if len(active_goals) > 3:
            recommendations += "- **Focus Suggestion**: Consider prioritizing 2-3 core goals for better focus and results\n"
        
        # Progress distribution analysis
        high_progress_goals = [g for g in active_goals if g.get("progress_percentage", 0) >= 75]
        low_progress_goals = [g for g in active_goals if g.get("progress_percentage", 0) < 25]
        
        if high_progress_goals:
            recommendations += f"- **Push to Finish**: You have {len(high_progress_goals)} goal(s) close to completion - prioritize finishing these!\n"
        
        if low_progress_goals:
            recommendations += f"- **Get Started**: {len(low_progress_goals)} goal(s) need more attention - break them into smaller, actionable steps\n"
        
        # Timeline pressure analysis
        urgent_goals = []
        for goal in active_goals:
            target_date = goal.get("target_date")
            if target_date:
                try:
                    target_dt = datetime.fromisoformat(target_date.replace('Z', '+00:00'))
                    days_remaining = (target_dt - datetime.now()).days
                    if days_remaining < 30:
                        urgent_goals.append(goal)
                except:
                    pass
        
        if urgent_goals:
            recommendations += f"- **Time Pressure**: {len(urgent_goals)} goal(s) have deadlines within 30 days - create focused action plans\n"
        
        recommendations += "- **Regular Reviews**: Schedule weekly goal check-ins to maintain momentum and adjust as needed\n"
        
        return recommendations
    
    def _generate_immediate_motivation_actions(self, assessment: Dict[str, Any]) -> str:
        """Generate immediate actionable steps based on motivation assessment"""
        category = assessment['category']
        
        actions = {
            "high": [
                "Set a stretch goal to maintain challenge level",
                "Help someone else with their learning journey",
                "Document your success strategies for future reference"
            ],
            "moderate": [
                "Choose one small task to complete today",
                "Reach out to a learning buddy or mentor",
                "Review your recent achievements to boost confidence"
            ],
            "low": [
                "Take a 15-minute break from learning",
                "Do one very simple, easy task to rebuild momentum",
                "Remind yourself why you started this learning journey"
            ],
            "very_low": [
                "Take a full day break if possible",
                "Talk to someone supportive about your challenges",
                "Consider adjusting your goals to be more manageable"
            ]
        }
        
        category_actions = actions.get(category, actions["moderate"])
        
        formatted = ""
        for i, action in enumerate(category_actions, 1):
            formatted += f"{i}. {action}\n"
        
        return formatted
    
    def _generate_contextual_support(self, support_type: str, message: str) -> str:
        """Generate contextual support based on the type of challenge"""
        
        support_messages = {
            "stuck": """# 🧗 Getting Unstuck: Your Action Plan

Feeling stuck is a normal part of learning! Here's how to move forward:

## 🔍 Diagnose the Block
- **Knowledge Gap**: Missing foundational concepts?
- **Complexity Overload**: Trying to learn too much at once?
- **Application Difficulty**: Understanding theory but struggling with practice?
- **Motivation Dip**: Know what to do but can't get started?

## 🛠️ Unstuck Strategies
1. **Step Back**: Take a 10-minute break and return with fresh eyes
2. **Break It Down**: Divide the challenge into smaller, manageable pieces
3. **Change Perspective**: Try learning the same concept from a different source
4. **Ask for Help**: Reach out to communities, mentors, or study partners
5. **Practice Easier Examples**: Build confidence with simpler versions first

## 🎯 Quick Win Actions
- Identify the smallest possible next step
- Set a 15-minute timer and work on just that
- Celebrate completing even small tasks

Remember: Being stuck means you're at the edge of your current knowledge - that's where growth happens! 🌱""",

            "motivation": """# 🔥 Motivation Reboot: Reconnect with Your Why

It's completely normal for motivation to fluctuate. Let's reignite your learning spark:

## 🎯 Reconnect with Purpose
- Why did you start this learning journey?
- What will achieving your goals mean for your life?
- Who will benefit from your new skills?

## 🏆 Celebrate Progress Made
- List 3 things you've learned recently (no matter how small)
- Compare your current knowledge to where you started
- Acknowledge the effort you've already invested

## ⚡ Motivation Boosters
1. **Micro-Commitments**: Promise just 10 minutes today
2. **Buddy System**: Find an accountability partner
3. **Reward System**: Plan small rewards for milestones
4. **Progress Visualization**: Create a visual progress tracker
5. **Success Stories**: Read about others who've achieved similar goals

## 🚀 Momentum Starters
- Choose the most interesting or easiest topic
- Set an impossibly small goal (5 minutes of reading)
- Change your learning environment
- Try a different format (video instead of text)

Your future self will thank you for not giving up! 💪""",

            "difficulty": """# 💡 Tackling Difficult Content: Strategic Approach

Challenging material means you're growing! Here's how to master difficult concepts:

## 🧩 Difficulty Breakdown Strategies
1. **Concept Mapping**: Draw connections between ideas
2. **Analogy Building**: Compare new concepts to familiar ones
3. **Multiple Sources**: Learn from different perspectives
4. **Teach-Back Method**: Explain concepts in your own words

## 📚 Learning Reinforcement
- **Spaced Repetition**: Review concepts at increasing intervals
- **Active Practice**: Apply concepts immediately after learning
- **Question Generation**: Create your own questions about the material
- **Real-World Connections**: Find practical applications

## 🔄 When to Pivot
- Try a different learning format (visual, audio, hands-on)
- Seek prerequisite knowledge you might be missing
- Take strategic breaks to let your brain process
- Consider getting help from a tutor or mentor

## 🎯 Progress Mindset
- Focus on understanding, not speed
- Embrace the struggle as part of learning
- Celebrate small breakthroughs
- Remember: confusion is the beginning of understanding

Difficult doesn't mean impossible - it means valuable! 🏆""",

            "general": """# 🌟 Your Learning Journey Support

I'm here to help you stay on track and motivated! Here are some ways I can support you:

## 📊 Progress Tracking
- Analyze your learning trends and patterns
- Celebrate milestones and achievements
- Identify areas for improvement

## 🎯 Goal Management
- Review and adjust your learning goals
- Create actionable plans for goal achievement
- Track deadline and milestone progress

## 💪 Motivation Support
- Provide encouragement during challenging times
- Help you reconnect with your learning purpose
- Suggest strategies to overcome obstacles

## 🧠 Learning Optimization
- Recommend study techniques and strategies
- Help you overcome learning plateaus
- Suggest ways to make learning more effective

What specific aspect of your learning journey would you like support with today? I'm here to help you succeed! 🚀"""
        }
        
        return support_messages.get(support_type, support_messages["general"])
    
    def _generate_achievement_significance(self, achievements: List[str]) -> str:
        """Explain why achievements matter"""
        if not achievements:
            return "Every small step forward builds the foundation for bigger successes."
        
        significance = """Your achievements represent more than just completed tasks - they show:

🧠 **Skill Development**: Each accomplishment has expanded your capabilities
💪 **Persistence**: You've demonstrated the ability to follow through on commitments
🎯 **Goal Alignment**: You're making concrete progress toward your objectives
🔄 **Learning Process**: You've proven you can learn, apply, and succeed

These wins create momentum that makes future challenges easier to overcome."""
        
        return significance
    
    def _generate_momentum_builders(self, achievements: List[str]) -> str:
        """Suggest ways to build on current achievements"""
        builders = """Here's how to build on your current success:

1. **Document Your Learning**: Write down key insights or methods that led to success
2. **Teach Others**: Share your knowledge with someone else to reinforce learning
3. **Set the Next Challenge**: Use this momentum to tackle the next level of difficulty
4. **Reflect on Growth**: Compare your current abilities to where you started
5. **Plan Celebration**: Take time to properly acknowledge your progress

Success builds on success - you're creating a positive learning cycle! 🔄"""
        
        return builders
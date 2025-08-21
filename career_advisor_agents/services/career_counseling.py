from typing import Dict, List, Any, Optional, Tuple
import asyncio
import json
from datetime import datetime
from langchain.schema import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import BaseTool

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.data_models import (
    UserProfile, ConversationMessage, CareerRecommendation,
    UserGoal, ProgressUpdate
)


class SentimentAnalysisTool(BaseTool):
    name: str = "sentiment_analysis"
    description: str = "Analyzes sentiment and emotional state of user messages"
    
    def _run(self, message: str) -> Dict[str, Any]:
        # Simplified sentiment analysis
        # In production, use proper NLP libraries like TextBlob, VADER, or cloud APIs
        
        positive_words = ["excited", "happy", "motivated", "confident", "optimistic", "great", "good", "love", "enjoy"]
        negative_words = ["worried", "anxious", "confused", "frustrated", "stressed", "difficult", "hate", "dislike", "fear"]
        uncertainty_words = ["unsure", "confused", "maybe", "perhaps", "don't know", "uncertain", "doubt"]
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        uncertainty_count = sum(1 for word in uncertainty_words if word in message_lower)
        
        total_words = len(message.split())
        
        # Calculate sentiment scores
        sentiment_score = (positive_count - negative_count) / max(total_words * 0.1, 1)
        confidence_score = max(0, 1 - (uncertainty_count / max(total_words * 0.1, 1)))
        
        # Determine primary emotion
        if positive_count > negative_count and positive_count > uncertainty_count:
            primary_emotion = "positive"
        elif negative_count > positive_count and negative_count > uncertainty_count:
            primary_emotion = "negative"
        elif uncertainty_count > 0:
            primary_emotion = "uncertain"
        else:
            primary_emotion = "neutral"
        
        return {
            "sentiment_score": max(-1, min(1, sentiment_score)),
            "confidence_level": max(0, min(1, confidence_score)),
            "primary_emotion": primary_emotion,
            "emotional_indicators": {
                "positive_signals": positive_count,
                "negative_signals": negative_count,
                "uncertainty_signals": uncertainty_count
            }
        }
    
    async def _arun(self, message: str) -> Dict[str, Any]:
        return self._run(message)


class ConversationContextTool(BaseTool):
    name: str = "conversation_context"
    description: str = "Analyzes conversation context and determines appropriate response strategy"
    
    def _run(self, conversation_history: List[Dict[str, str]], current_message: str) -> Dict[str, Any]:
        # Analyze conversation patterns and context
        if not conversation_history:
            return {
                "conversation_stage": "initial",
                "user_needs": ["introduction", "goal_setting"],
                "suggested_approach": "welcoming_and_exploratory"
            }
        
        recent_topics = []
        question_count = 0
        user_concerns = []
        
        for msg in conversation_history[-5:]:  # Look at last 5 messages
            content = msg.get("content", "").lower()
            
            # Track topics
            if any(word in content for word in ["career", "job", "work"]):
                recent_topics.append("career_exploration")
            if any(word in content for word in ["skill", "learn", "course"]):
                recent_topics.append("skill_development")
            if any(word in content for word in ["interview", "application", "resume"]):
                recent_topics.append("job_search")
            
            # Track questions
            if "?" in content:
                question_count += 1
            
            # Identify concerns
            if any(word in content for word in ["worried", "concern", "problem", "difficult"]):
                user_concerns.append(content)
        
        # Determine conversation stage
        if len(conversation_history) < 3:
            stage = "early_exploration"
        elif question_count > 2:
            stage = "information_gathering"
        elif recent_topics:
            stage = "focused_discussion"
        else:
            stage = "ongoing_support"
        
        return {
            "conversation_stage": stage,
            "recent_topics": list(set(recent_topics)),
            "user_engagement_level": min(len(conversation_history) * 0.2, 1.0),
            "concerns_identified": len(user_concerns) > 0,
            "suggested_approach": self._get_approach_strategy(stage, recent_topics, user_concerns)
        }
    
    def _get_approach_strategy(self, stage: str, topics: List[str], concerns: List[str]) -> str:
        if concerns:
            return "supportive_and_reassuring"
        elif stage == "early_exploration":
            return "exploratory_and_engaging"
        elif "skill_development" in topics:
            return "practical_and_actionable"
        elif "job_search" in topics:
            return "strategic_and_tactical"
        else:
            return "collaborative_and_reflective"
    
    async def _arun(self, conversation_history: List[Dict[str, str]], current_message: str) -> Dict[str, Any]:
        return self._run(conversation_history, current_message)


class CareerCounselingService:
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.sentiment_tool = SentimentAnalysisTool()
        self.context_tool = ConversationContextTool()
        
        # Knowledge base of career advice
        self.knowledge_base = {
            "career_change": {
                "key_considerations": [
                    "Assess transferable skills",
                    "Research target industry requirements",
                    "Consider financial implications",
                    "Build relevant network connections",
                    "Plan gradual transition if possible"
                ],
                "common_challenges": [
                    "Age discrimination concerns",
                    "Salary reduction anxiety",
                    "Skill gap identification",
                    "Network building from scratch"
                ]
            },
            "skill_development": {
                "learning_strategies": [
                    "Online courses and certifications",
                    "Hands-on projects and portfolios",
                    "Mentorship and coaching",
                    "Industry conferences and workshops",
                    "Cross-functional team collaboration"
                ],
                "trending_skills": {
                    "technical": ["AI/ML", "Cloud Computing", "Cybersecurity", "Data Analysis"],
                    "soft": ["Emotional Intelligence", "Remote Collaboration", "Adaptability", "Critical Thinking"]
                }
            },
            "job_search": {
                "modern_strategies": [
                    "LinkedIn optimization",
                    "Personal branding",
                    "Network leveraging",
                    "Portfolio development",
                    "Interview storytelling"
                ],
                "application_best_practices": [
                    "Customize resume for each application",
                    "Write compelling cover letters",
                    "Prepare STAR method examples",
                    "Research company culture thoroughly"
                ]
            }
        }
        
        # Response templates for different emotional states
        self.response_templates = {
            "supportive": {
                "opening": "I understand this can feel overwhelming, and that's completely normal. ",
                "encouragement": "Remember that career transitions take time, and you're taking positive steps by seeking guidance. ",
                "action": "Let's break this down into manageable steps that will help you move forward confidently."
            },
            "exploratory": {
                "opening": "That's a great question that shows you're thinking strategically about your future. ",
                "encouragement": "Exploring different options is exactly what you should be doing at this stage. ",
                "action": "Let me help you think through the various possibilities and what each might mean for you."
            },
            "practical": {
                "opening": "I appreciate you being specific about what you need. ",
                "encouragement": "Taking action to develop your skills shows great initiative. ",
                "action": "Here are some concrete steps you can take to move forward effectively."
            }
        }
    
    async def process_counseling_request(
        self, 
        user_id: str, 
        message: str, 
        user_profile: Optional[UserProfile] = None,
        conversation_history: Optional[List[ConversationMessage]] = None
    ) -> Dict[str, Any]:
        """
        Main method to process career counseling requests with AI
        """
        try:
            # Simplified sentiment analysis
            sentiment_analysis = self._simple_sentiment_analysis(message)
            
            # Convert conversation history to simple format
            history_dict = []
            if conversation_history:
                history_dict = [
                    {"role": "user", "content": msg.user_message}
                    for msg in conversation_history[-5:] if msg.user_message  # Last 5 user messages
                ]
            
            # Generate AI-powered response directly
            response = await self._generate_ai_counseling_response(
                message, user_profile, sentiment_analysis, history_dict
            )
            
            # Simple follow-up actions based on message content
            follow_up_actions = self._simple_follow_up_actions(message)
            
            return {
                "response": response,
                "sentiment_analysis": sentiment_analysis,
                "follow_up_actions": follow_up_actions,
                "conversation_metadata": {
                    "response_type": "ai_generated",
                    "user_id": user_id,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            print(f"Counseling error: {str(e)}")  # Debug logging
            # Still try to generate an AI response as fallback
            try:
                response = await self._generate_simple_ai_response(message)
                return {
                    "response": response,
                    "sentiment_analysis": {"primary_emotion": "neutral", "confidence_level": 0.5},
                    "follow_up_actions": ["general_career_exploration"],
                    "conversation_metadata": {"fallback_used": True}
                }
            except Exception as fallback_error:
                return {
                    "response": "I want to help you with your career concerns. Could you tell me a bit more about what's on your mind so I can provide the most relevant guidance?",
                    "error": f"Primary: {str(e)}, Fallback: {str(fallback_error)}",
                    "sentiment_analysis": {"primary_emotion": "neutral"},
                    "follow_up_actions": ["general_career_exploration"]
                }
    
    async def _generate_counseling_response(
        self,
        message: str,
        user_profile: Optional[UserProfile],
        sentiment: Dict[str, Any],
        context: Dict[str, Any],
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate empathetic, contextually appropriate counseling response"""
        
        # Select appropriate response template
        approach = context.get("suggested_approach", "collaborative_and_reflective")
        template_key = self._map_approach_to_template(approach)
        template = self.response_templates.get(template_key, self.response_templates["exploratory"])
        
        # Build context for LLM
        system_prompt = self._build_counseling_system_prompt(sentiment, context, user_profile)
        
        # Include relevant knowledge base information
        relevant_knowledge = self._get_relevant_knowledge(message, context)
        
        conversation_context = ""
        if conversation_history:
            recent_context = conversation_history[-3:]  # Last 3 exchanges
            conversation_context = "\n".join([
                f"{'User' if msg['role'] == 'user' else 'Counselor'}: {msg['content']}"
                for msg in recent_context
            ])
        
        user_info = ""
        if user_profile:
            user_info = f"""
User Background:
- Career Stage: {user_profile.career_stage or 'Not specified'}
- Education: {user_profile.education_level or 'Not specified'}
- Goals: {', '.join(user_profile.career_goals) if user_profile.career_goals else 'Not specified'}
"""
        
        full_prompt = f"""{system_prompt}

{user_info}

Recent conversation context:
{conversation_context}

Relevant guidance from knowledge base:
{relevant_knowledge}

Current user message: {message}

Emotional context: {sentiment.get('primary_emotion', 'neutral')} (confidence: {sentiment.get('confidence_level', 0):.2f})
Conversation stage: {context.get('conversation_stage', 'ongoing')}

Please provide a thoughtful, empathetic response that:
1. Acknowledges the user's emotional state appropriately
2. Provides practical, actionable guidance
3. Maintains a supportive and professional tone
4. Builds on previous conversation context
5. Encourages continued engagement and growth

Response template to consider: {template}"""

        try:
            response = await self.llm.ainvoke([{"role": "user", "content": full_prompt}])
            return response.content
            
        except Exception as e:
            # Fallback response
            emotion = sentiment.get('primary_emotion', 'neutral')
            if emotion == 'negative':
                return f"{template['opening']} {template['encouragement']} What specific aspect would you like to focus on first?"
            elif emotion == 'uncertain':
                return f"{template['opening']} It's natural to feel uncertain about career decisions. What's the main question or concern on your mind right now?"
            else:
                return f"{template['opening']} {template['action']} What would be most helpful for you to explore next?"
    
    def _build_counseling_system_prompt(
        self,
        sentiment: Dict[str, Any],
        context: Dict[str, Any],
        user_profile: Optional[UserProfile]
    ) -> str:
        base_prompt = """You are an expert career counselor with deep expertise in vocational psychology, career development theory, and emotional intelligence. Your role is to provide supportive, practical, and insightful career guidance.

Key principles for your responses:
1. Show empathy and emotional intelligence
2. Provide concrete, actionable advice
3. Draw from established career development theories
4. Maintain appropriate professional boundaries
5. Encourage self-reflection and growth
6. Be realistic while remaining optimistic
7. Adapt your communication style to the user's emotional state

"""
        
        emotion = sentiment.get('primary_emotion', 'neutral')
        if emotion == 'negative':
            base_prompt += """
The user appears to be experiencing some stress or negative emotions. Prioritize:
- Validation and normalization of their feelings
- Breaking down overwhelming situations into manageable steps
- Providing reassurance while being honest about challenges
- Offering immediate, small actions they can take
"""
        elif emotion == 'uncertain':
            base_prompt += """
The user seems uncertain or confused. Focus on:
- Helping clarify their thoughts and priorities
- Asking thoughtful questions to guide self-discovery
- Providing frameworks for decision-making
- Offering multiple perspectives or options
"""
        elif emotion == 'positive':
            base_prompt += """
The user appears motivated and positive. Leverage this by:
- Building on their enthusiasm with specific action plans
- Challenging them appropriately to grow
- Helping them maintain momentum
- Connecting their energy to concrete goals
"""
        
        conversation_stage = context.get('conversation_stage', 'ongoing')
        if conversation_stage == 'early_exploration':
            base_prompt += """
This is early in the conversation. Focus on:
- Building rapport and trust
- Understanding their background and goals
- Asking open-ended questions
- Setting a foundation for deeper exploration
"""
        
        return base_prompt
    
    def _map_approach_to_template(self, approach: str) -> str:
        mapping = {
            "supportive_and_reassuring": "supportive",
            "exploratory_and_engaging": "exploratory",
            "practical_and_actionable": "practical",
            "strategic_and_tactical": "practical",
            "collaborative_and_reflective": "exploratory"
        }
        return mapping.get(approach, "exploratory")
    
    def _get_relevant_knowledge(self, message: str, context: Dict[str, Any]) -> str:
        """Extract relevant knowledge base information based on message content"""
        message_lower = message.lower()
        relevant_info = []
        
        # Check for career change topics
        if any(phrase in message_lower for phrase in ["career change", "switch careers", "new field", "transition"]):
            career_change_info = self.knowledge_base["career_change"]
            relevant_info.append(f"Career Change Considerations: {', '.join(career_change_info['key_considerations'][:3])}")
        
        # Check for skill development topics
        if any(phrase in message_lower for phrase in ["skill", "learn", "course", "training", "development"]):
            skill_info = self.knowledge_base["skill_development"]
            relevant_info.append(f"Skill Development Strategies: {', '.join(skill_info['learning_strategies'][:3])}")
        
        # Check for job search topics
        if any(phrase in message_lower for phrase in ["job search", "interview", "resume", "application", "hiring"]):
            job_search_info = self.knowledge_base["job_search"]
            relevant_info.append(f"Job Search Best Practices: {', '.join(job_search_info['modern_strategies'][:3])}")
        
        return "\n".join(relevant_info) if relevant_info else "General career development guidance available."
    
    def _suggest_follow_up_actions(
        self,
        sentiment: Dict[str, Any],
        context: Dict[str, Any],
        user_profile: Optional[UserProfile]
    ) -> List[str]:
        """Suggest appropriate follow-up actions based on conversation analysis"""
        actions = []
        
        emotion = sentiment.get('primary_emotion', 'neutral')
        stage = context.get('conversation_stage', 'ongoing')
        topics = context.get('recent_topics', [])
        
        # Emotional state-based actions
        if emotion == 'negative':
            actions.extend([
                "emotional_support_check_in",
                "break_down_overwhelming_tasks",
                "schedule_follow_up_conversation"
            ])
        elif emotion == 'uncertain':
            actions.extend([
                "clarifying_questions",
                "decision_framework_guidance",
                "exploration_exercises"
            ])
        elif emotion == 'positive':
            actions.extend([
                "action_plan_creation",
                "goal_setting_session",
                "momentum_building_tasks"
            ])
        
        # Topic-based actions
        if "career_exploration" in topics:
            actions.append("personality_and_interest_assessment")
        if "skill_development" in topics:
            actions.append("learning_path_creation")
        if "job_search" in topics:
            actions.append("application_strategy_development")
        
        # Stage-based actions
        if stage == "early_exploration":
            actions.append("comprehensive_intake_session")
        elif stage == "focused_discussion":
            actions.append("deep_dive_analysis")
        
        # Profile-based actions
        if user_profile and not user_profile.career_goals:
            actions.append("goal_setting_workshop")
        
        return list(set(actions))  # Remove duplicates
    
    def _calculate_support_level(self, sentiment: Dict[str, Any]) -> float:
        """Calculate how much emotional support is needed (0-1 scale)"""
        emotion = sentiment.get('primary_emotion', 'neutral')
        confidence = sentiment.get('confidence_level', 0.5)
        
        if emotion == 'negative':
            return max(0.7, 1 - confidence)
        elif emotion == 'uncertain':
            return max(0.5, 1 - confidence)
        elif emotion == 'positive':
            return min(0.3, 1 - confidence)
        else:
            return 0.5
    
    def _calculate_information_density(self, context: Dict[str, Any]) -> float:
        """Calculate how much information to provide (0-1 scale)"""
        stage = context.get('conversation_stage', 'ongoing')
        engagement = context.get('user_engagement_level', 0.5)
        
        if stage == 'early_exploration':
            return min(0.6, engagement + 0.2)
        elif stage == 'information_gathering':
            return min(0.8, engagement + 0.3)
        elif stage == 'focused_discussion':
            return min(1.0, engagement + 0.4)
        else:
            return engagement
    
    def _calculate_personalization_level(self, user_profile: Optional[UserProfile]) -> float:
        """Calculate how personalized the response should be (0-1 scale)"""
        if not user_profile:
            return 0.2
        
        personalization_score = 0.2  # Base level
        
        if user_profile.personality:
            personalization_score += 0.2
        if user_profile.interests:
            personalization_score += 0.2
        if user_profile.career_goals:
            personalization_score += 0.2
        if user_profile.skills:
            personalization_score += 0.2
        
        return min(1.0, personalization_score)
    
    def _simple_sentiment_analysis(self, message: str) -> Dict[str, Any]:
        """Simplified sentiment analysis without external tools"""
        positive_words = ["excited", "happy", "motivated", "confident", "optimistic", "great", "good", "love", "enjoy"]
        negative_words = ["worried", "anxious", "confused", "frustrated", "stressed", "difficult", "hate", "dislike", "fear"]
        uncertainty_words = ["unsure", "confused", "maybe", "perhaps", "don't know", "uncertain", "doubt"]
        
        message_lower = message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        uncertainty_count = sum(1 for word in uncertainty_words if word in message_lower)
        
        total_words = len(message.split())
        
        # Calculate sentiment scores
        sentiment_score = (positive_count - negative_count) / max(total_words * 0.1, 1)
        confidence_score = max(0, 1 - (uncertainty_count / max(total_words * 0.1, 1)))
        
        # Determine primary emotion
        if positive_count > negative_count and positive_count > uncertainty_count:
            primary_emotion = "positive"
        elif negative_count > positive_count and negative_count > uncertainty_count:
            primary_emotion = "negative"
        elif uncertainty_count > 0:
            primary_emotion = "uncertain"
        else:
            primary_emotion = "neutral"
        
        return {
            "sentiment_score": max(-1, min(1, sentiment_score)),
            "confidence_level": max(0, min(1, confidence_score)),
            "primary_emotion": primary_emotion,
            "emotional_indicators": {
                "positive_signals": positive_count,
                "negative_signals": negative_count,
                "uncertainty_signals": uncertainty_count
            }
        }
    
    async def _generate_ai_counseling_response(
        self, 
        message: str, 
        user_profile: Optional[UserProfile], 
        sentiment_analysis: Dict[str, Any], 
        history_dict: List[Dict[str, str]]
    ) -> str:
        """Generate AI-powered counseling response using Google Gemini"""
        
        # Build user context
        user_context = ""
        if user_profile:
            user_context = f"""
User Background:
- Career Stage: {user_profile.career_stage or 'Not specified'}
- Education: {user_profile.education_level or 'Not specified'}
- Age: {user_profile.age or 'Not specified'}
- Location: {user_profile.location or 'Not specified'}
"""
        
        # Build conversation history
        conversation_context = ""
        if history_dict:
            recent_history = history_dict[-3:]  # Last 3 messages
            conversation_context = "\n".join([
                f"User: {msg['content']}" for msg in recent_history
            ])
        
        # Build system prompt for career counseling
        system_prompt = f"""You are an expert career counselor with deep expertise in vocational psychology and career development. 

Your role is to provide empathetic, practical, and insightful career guidance. Always:
1. Show empathy and understanding
2. Provide concrete, actionable advice
3. Ask thoughtful follow-up questions when appropriate
4. Maintain a supportive and professional tone
5. Be realistic while remaining encouraging

{user_context}

Recent conversation:
{conversation_context}

Current user emotional state: {sentiment_analysis.get('primary_emotion', 'neutral')}

User's current message: {message}

Please provide a thoughtful, empathetic response that acknowledges their situation and offers practical guidance. Keep your response conversational and supportive (2-4 sentences)."""

        try:
            # Call Google Gemini LLM
            response = await self.llm.ainvoke([{"role": "user", "content": system_prompt}])
            ai_content = response.content if hasattr(response, 'content') else str(response)
            return ai_content.strip()
            
        except Exception as e:
            print(f"AI response error: {str(e)}")
            # Fallback response based on sentiment
            emotion = sentiment_analysis.get('primary_emotion', 'neutral')
            if emotion == 'negative':
                return "I understand this situation can feel challenging. Career concerns are completely normal, and taking the time to think through your options shows great self-awareness. What specific aspect would you like to focus on first?"
            elif emotion == 'uncertain':
                return "It's natural to feel uncertain about career decisions - they're some of the most important choices we make. Let's explore your thoughts together. What's the main question on your mind right now?"
            elif emotion == 'positive':
                return "I love your enthusiasm! It's wonderful to see someone excited about their career journey. Let's channel that energy into creating a concrete plan. What's the first step you'd like to take?"
            else:
                return "Thank you for sharing that with me. Career development is an ongoing journey, and I'm here to support you. What would be most helpful for you to explore today?"
    
    def _simple_follow_up_actions(self, message: str) -> List[str]:
        """Generate simple follow-up actions based on message content"""
        message_lower = message.lower()
        actions = []
        
        # Career change related
        if any(phrase in message_lower for phrase in ["career change", "switch careers", "new field", "transition"]):
            actions.extend(["career_exploration", "transferable_skills_assessment", "industry_research"])
        
        # Skill development related
        if any(phrase in message_lower for phrase in ["skill", "learn", "course", "training", "development"]):
            actions.extend(["skills_assessment", "learning_plan_creation", "certification_guidance"])
        
        # Job search related
        if any(phrase in message_lower for phrase in ["job search", "interview", "resume", "application", "hiring"]):
            actions.extend(["resume_review", "interview_preparation", "job_search_strategy"])
        
        # Goal setting related
        if any(phrase in message_lower for phrase in ["goal", "plan", "future", "direction"]):
            actions.extend(["goal_setting", "action_plan_creation", "milestone_planning"])
        
        # Emotional support related
        if any(phrase in message_lower for phrase in ["worried", "anxious", "stressed", "confused", "frustrated"]):
            actions.extend(["emotional_support", "stress_management", "confidence_building"])
        
        # Default actions if nothing specific detected
        if not actions:
            actions = ["general_career_exploration", "self_assessment", "goal_clarification"]
        
        return actions[:3]  # Return max 3 actions
    
    async def _generate_simple_ai_response(self, message: str) -> str:
        """Generate a simple AI response for fallback scenarios"""
        
        simple_prompt = f"""You are a helpful career counselor. A user has asked: "{message}"

Please provide a brief, supportive response that:
1. Acknowledges their question or concern
2. Offers encouragement
3. Suggests a helpful next step

Keep your response friendly and concise (1-2 sentences)."""

        try:
            response = await self.llm.ainvoke([{"role": "user", "content": simple_prompt}])
            ai_content = response.content if hasattr(response, 'content') else str(response)
            return ai_content.strip()
            
        except Exception as e:
            print(f"Simple AI response error: {str(e)}")
            return "I want to help you with your career concerns. Could you tell me a bit more about what's on your mind so I can provide the most relevant guidance?"
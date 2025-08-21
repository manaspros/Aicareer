from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime
from langchain.tools import BaseTool
from langchain.schema import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.agent_framework import BaseAgent, AgentResponse
from core.data_models import (
    UserProfile, PersonalityAssessment, InterestAssessment, 
    CareerRecommendation, SkillLevel, PersonalityType, RIASECType
)


class PersonalityAssessmentTool(BaseTool):
    name: str = "personality_assessment"
    description: str = "Analyzes user responses to generate Big Five personality scores"
    
    def _run(self, responses: List[str]) -> Dict[str, float]:
        # Simplified personality scoring based on response analysis
        # In production, this would use validated psychological instruments
        personality_keywords = {
            "openness": ["creative", "curious", "imaginative", "artistic", "innovative"],
            "conscientiousness": ["organized", "reliable", "disciplined", "punctual", "responsible"],
            "extraversion": ["outgoing", "social", "energetic", "talkative", "assertive"],
            "agreeableness": ["cooperative", "trusting", "helpful", "empathetic", "kind"],
            "neuroticism": ["anxious", "stressed", "worried", "emotional", "sensitive"]
        }
        
        scores = {trait: 50.0 for trait in personality_keywords}  # Start with neutral scores
        
        for response in responses:
            response_lower = response.lower()
            for trait, keywords in personality_keywords.items():
                keyword_count = sum(1 for keyword in keywords if keyword in response_lower)
                if keyword_count > 0:
                    scores[trait] += min(keyword_count * 10, 30)
        
        # Normalize scores to 0-100 range
        for trait in scores:
            scores[trait] = min(max(scores[trait], 0), 100)
        
        return scores
    
    async def _arun(self, responses: List[str]) -> Dict[str, float]:
        return self._run(responses)


class InterestAssessmentTool(BaseTool):
    name: str = "interest_assessment"
    description: str = "Analyzes user interests using Holland Code (RIASEC) framework"
    
    def _run(self, interests: List[str], preferences: List[str]) -> Dict[str, float]:
        riasec_keywords = {
            "realistic": ["hands-on", "mechanical", "outdoor", "tools", "building", "repair"],
            "investigative": ["research", "analyze", "science", "problem-solving", "data", "experiment"],
            "artistic": ["creative", "design", "music", "art", "writing", "performance"],
            "social": ["helping", "teaching", "counseling", "community", "people", "service"],
            "enterprising": ["leadership", "business", "sales", "persuading", "managing", "influencing"],
            "conventional": ["organizing", "details", "procedures", "office", "data-entry", "clerical"]
        }
        
        scores = {trait: 30.0 for trait in riasec_keywords}  # Start with low baseline
        
        all_responses = interests + preferences
        for response in all_responses:
            response_lower = response.lower()
            for trait, keywords in riasec_keywords.items():
                keyword_count = sum(1 for keyword in keywords if keyword in response_lower)
                if keyword_count > 0:
                    scores[trait] += min(keyword_count * 15, 40)
        
        # Normalize scores to 0-100 range
        for trait in scores:
            scores[trait] = min(max(scores[trait], 0), 100)
        
        return scores
    
    async def _arun(self, interests: List[str], preferences: List[str]) -> Dict[str, float]:
        return self._run(interests, preferences)


class CareerMatchingTool(BaseTool):
    name: str = "career_matching"
    description: str = "Matches user profile to potential career paths"
    
    def _run(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Simplified career matching logic
        # In production, this would use comprehensive career databases
        
        career_database = [
            {
                "title": "Software Engineer",
                "industry": "Technology",
                "personality_fit": {"openness": 70, "conscientiousness": 80},
                "interest_fit": {"investigative": 85, "realistic": 60},
                "required_skills": ["Programming", "Problem Solving", "Mathematics"],
                "salary_range": {"min": 70000, "max": 150000},
                "growth_outlook": "Excellent - 22% growth expected"
            },
            {
                "title": "Marketing Manager",
                "industry": "Business",
                "personality_fit": {"extraversion": 75, "openness": 65},
                "interest_fit": {"enterprising": 80, "artistic": 60},
                "required_skills": ["Communication", "Analytics", "Strategy"],
                "salary_range": {"min": 60000, "max": 120000},
                "growth_outlook": "Good - 10% growth expected"
            },
            {
                "title": "Data Scientist",
                "industry": "Technology/Analytics",
                "personality_fit": {"openness": 80, "conscientiousness": 75},
                "interest_fit": {"investigative": 90, "conventional": 50},
                "required_skills": ["Statistics", "Python", "Machine Learning"],
                "salary_range": {"min": 80000, "max": 160000},
                "growth_outlook": "Excellent - 31% growth expected"
            },
            {
                "title": "Teacher",
                "industry": "Education",
                "personality_fit": {"agreeableness": 80, "extraversion": 60},
                "interest_fit": {"social": 85, "artistic": 50},
                "required_skills": ["Communication", "Patience", "Subject Knowledge"],
                "salary_range": {"min": 40000, "max": 80000},
                "growth_outlook": "Average - 5% growth expected"
            },
            {
                "title": "Graphic Designer",
                "industry": "Creative/Marketing",
                "personality_fit": {"openness": 85, "artistic": 80},
                "interest_fit": {"artistic": 90, "realistic": 40},
                "required_skills": ["Design Software", "Creativity", "Visual Communication"],
                "salary_range": {"min": 35000, "max": 75000},
                "growth_outlook": "Average - 3% growth expected"
            }
        ]
        
        personality = user_profile.get("personality", {})
        interests = user_profile.get("interests", {})
        
        scored_careers = []
        for career in career_database:
            match_score = 0.0
            
            # Calculate personality match
            personality_score = 0.0
            if personality:
                for trait, target_score in career["personality_fit"].items():
                    if trait in personality:
                        diff = abs(personality[trait] - target_score)
                        personality_score += max(0, 100 - diff)
                personality_score = personality_score / len(career["personality_fit"]) if career["personality_fit"] else 0
            
            # Calculate interest match
            interest_score = 0.0
            if interests:
                for trait, target_score in career["interest_fit"].items():
                    if trait in interests:
                        diff = abs(interests[trait] - target_score)
                        interest_score += max(0, 100 - diff)
                interest_score = interest_score / len(career["interest_fit"]) if career["interest_fit"] else 0
            
            # Combined match score (weighted average)
            match_score = (personality_score * 0.4 + interest_score * 0.6)
            
            career_copy = career.copy()
            career_copy["match_score"] = match_score
            career_copy["personality_alignment"] = personality_score
            career_copy["interest_alignment"] = interest_score
            
            scored_careers.append(career_copy)
        
        # Sort by match score and return top matches
        scored_careers.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_careers[:5]
    
    async def _arun(self, user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        return self._run(user_profile)


class CareerAnalystAgent(BaseAgent):
    def __init__(self, llm: ChatGoogleGenerativeAI):
        tools = [
            PersonalityAssessmentTool(),
            InterestAssessmentTool(),
            CareerMatchingTool()
        ]
        
        super().__init__(
            name="career_analyst",
            description="Analyzes personality, interests, and provides career recommendations",
            llm=llm,
            tools=tools,
            temperature=0.7
        )
        
        self.assessment_questions = {
            "personality": [
                "How do you typically approach new challenges or problems?",
                "Describe your ideal work environment and team dynamics.",
                "What motivates you most in your work or studies?",
                "How do you handle stress and pressure?",
                "What are your greatest strengths and how do you use them?"
            ],
            "interests": [
                "What activities or subjects genuinely excite you?",
                "What kind of problems do you enjoy solving?",
                "What industries or fields fascinate you most?",
                "What would you do if money wasn't a consideration?",
                "What kind of impact do you want to make in the world?"
            ]
        }
    
    def get_system_prompt(self) -> str:
        return """You are a Career Analyst Agent, an expert in career counseling and vocational guidance. 

Your role is to:
1. Conduct personality assessments using the Big Five model
2. Analyze career interests using the Holland Code (RIASEC) framework
3. Provide personalized career recommendations with detailed reasoning
4. Explain the connection between personality traits, interests, and career fit
5. Suggest actionable next steps for career development

Key guidelines:
- Ask thoughtful, open-ended questions to understand the user deeply
- Use evidence-based psychological frameworks for assessments
- Provide specific, actionable career recommendations
- Explain your reasoning clearly and help users understand themselves better
- Be encouraging while being realistic about career paths
- Consider the user's background, education, and constraints
- Suggest multiple pathways and alternatives

Always maintain a supportive, professional tone while being thorough in your analysis."""

    async def _generate_response(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        try:
            # Always use AI-powered response first, enhanced with tools if needed
            ai_response = await self._ai_powered_response(message, context)
            
            # If user specifically requests formal assessment, provide structured tools
            message_lower = message.lower()
            if any(word in message_lower for word in ["formal assessment", "structured test", "complete evaluation"]):
                # Enhance AI response with structured assessment tools
                if "personality" in message_lower:
                    structured_response = await self._conduct_personality_assessment(message, context)
                    ai_response.metadata.update(structured_response.metadata)
                    ai_response.tools_used.extend(structured_response.tools_used)
                elif "interest" in message_lower:
                    structured_response = await self._analyze_interests(message, context)
                    ai_response.metadata.update(structured_response.metadata)
                    ai_response.tools_used.extend(structured_response.tools_used)
            
            return ai_response
                
        except Exception as e:
            self.logger.error(f"Error in career analysis: {str(e)}")
            return AgentResponse(
                content="I encountered an issue while analyzing your career profile. Let me try a different approach.",
                confidence=0.3
            )
    
    async def _ai_powered_response(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Main AI-powered response using Google Gemini LLM"""
        try:
            # Build comprehensive context for AI
            system_prompt = self.get_system_prompt()
            
            # Add user context if available
            user_context = ""
            if context:
                user_profile = context.get("user_profile", {})
                if user_profile:
                    user_context = f"""
User Profile Context:
- Name: {user_profile.get('name', 'Not provided')}
- Age: {user_profile.get('age', 'Not provided')}
- Education: {user_profile.get('education_level', 'Not provided')}
- Career Stage: {user_profile.get('career_stage', 'Not provided')}
- Location: {user_profile.get('location', 'Not provided')}
"""
                    
                    # Add personalized questionnaire insights if available
                    if user_profile.get('questionnaire_completed') and user_profile.get('personality_insights'):
                        personality_insights = user_profile.get('personality_insights', {})
                        user_context += f"""

PERSONALIZED INSIGHTS FROM QUESTIONNAIRE:
- Questionnaire Status: Completed
- Personality Insights: {personality_insights.get('personality_summary', 'Available but not detailed')}
- Interest Profile: {personality_insights.get('interest_summary', 'Available but not detailed')}
- Career Motivations: {personality_insights.get('career_motivations', 'Not specified')}
- Work Style Preferences: {personality_insights.get('work_style', 'Not specified')}
- Values and Priorities: {personality_insights.get('values', 'Not specified')}
- Skills and Strengths: {personality_insights.get('strengths', 'Not specified')}

IMPORTANT: Use these personalized insights as the PRIMARY foundation for your recommendations. This data is based on the user's detailed responses and should significantly influence your guidance.
"""
                    else:
                        user_context += f"""

QUESTIONNAIRE STATUS: {'Completed' if user_profile.get('questionnaire_completed') else 'Not completed'}
NOTE: {'Personalized insights available but limited' if user_profile.get('questionnaire_completed') else 'User has not completed the personalized questionnaire yet - recommend they complete it for more accurate career guidance.'}
"""
            
            # Add conversation history
            conversation_context = ""
            if self.memory.chat_memory.messages:
                recent_messages = self.memory.chat_memory.messages[-4:]
                conversation_context = "\n".join([
                    f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}"
                    for msg in recent_messages
                ])
            
            # Build the full prompt for AI
            full_prompt = f"""{system_prompt}

{user_context}

Previous conversation:
{conversation_context}

Current user message: {message}

Please provide a comprehensive, personalized response based on your career expertise and the user's context. If they're asking about career recommendations, personality insights, or professional development, draw upon career development theories, industry knowledge, and best practices. Be specific, actionable, and supportive."""

            # Call Google Gemini AI
            self.logger.info(f"Calling Google Gemini for career guidance...")
            llm_response = await self.llm.ainvoke([{"role": "user", "content": full_prompt}])
            
            # Extract and process the AI response
            ai_content = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            
            # Calculate confidence based on response quality
            confidence = self._calculate_response_confidence(ai_content, message)
            
            # Extract any structured insights from the response
            metadata = self._extract_response_metadata(ai_content, context)
            
            self.logger.info(f"Generated AI response with {len(ai_content)} characters, confidence: {confidence}")
            
            return AgentResponse(
                content=ai_content,
                metadata=metadata,
                confidence=confidence,
                tools_used=["google_gemini_ai"]
            )
            
        except Exception as e:
            self.logger.error(f"Error in AI-powered response: {str(e)}")
            # Fallback to general guidance if AI fails
            return await self._general_career_guidance(message, context)
    
    def _calculate_response_confidence(self, response: str, original_message: str) -> float:
        """Calculate confidence score based on response quality indicators"""
        confidence = 0.5  # Base confidence
        
        # Check response length (longer, more detailed responses generally better)
        if len(response) > 200:
            confidence += 0.2
        if len(response) > 500:
            confidence += 0.1
            
        # Check for specific career advice indicators
        career_indicators = ["recommend", "suggest", "consider", "skills", "career", "path", "opportunity"]
        for indicator in career_indicators:
            if indicator.lower() in response.lower():
                confidence += 0.05
                
        # Check for actionable advice
        action_indicators = ["start by", "next step", "you should", "try", "practice", "learn"]
        for indicator in action_indicators:
            if indicator.lower() in response.lower():
                confidence += 0.05
        
        return min(confidence, 1.0)  # Cap at 1.0
    
    def _extract_response_metadata(self, response: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Extract structured metadata from AI response"""
        metadata = {
            "response_type": "ai_generated",
            "response_length": len(response),
            "timestamp": datetime.now().isoformat()
        }
        
        # Try to identify response themes
        themes = []
        if any(word in response.lower() for word in ["personality", "traits", "character"]):
            themes.append("personality")
        if any(word in response.lower() for word in ["skills", "abilities", "competencies"]):
            themes.append("skills")
        if any(word in response.lower() for word in ["career", "job", "profession", "occupation"]):
            themes.append("career_guidance")
        if any(word in response.lower() for word in ["learn", "study", "education", "training"]):
            themes.append("learning")
            
        metadata["themes"] = themes
        return metadata

    async def _conduct_personality_assessment(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        # Check if user has provided assessment responses
        if context and "assessment_responses" in context:
            responses = context["assessment_responses"]
            personality_scores = await self.use_tool("personality_assessment", responses=responses)
            
            if personality_scores:
                personality = PersonalityAssessment(**personality_scores)
                
                analysis = f"""Based on your responses, here's your personality profile:

**Big Five Personality Assessment Results:**
- **Openness to Experience**: {personality.openness:.1f}/100 - {"High" if personality.openness > 70 else "Moderate" if personality.openness > 40 else "Low"}
- **Conscientiousness**: {personality.conscientiousness:.1f}/100 - {"High" if personality.conscientiousness > 70 else "Moderate" if personality.conscientiousness > 40 else "Low"}
- **Extraversion**: {personality.extraversion:.1f}/100 - {"High" if personality.extraversion > 70 else "Moderate" if personality.extraversion > 40 else "Low"}
- **Agreeableness**: {personality.agreeableness:.1f}/100 - {"High" if personality.agreeableness > 70 else "Moderate" if personality.agreeableness > 40 else "Low"}
- **Neuroticism**: {personality.neuroticism:.1f}/100 - {"High" if personality.neuroticism > 70 else "Moderate" if personality.neuroticism > 40 else "Low"}

**What this means for your career:**
{self._interpret_personality_results(personality)}

Would you like me to also assess your interests to provide comprehensive career recommendations?"""

                return AgentResponse(
                    content=analysis,
                    metadata={"personality_assessment": personality.dict()},
                    confidence=0.85,
                    tools_used=["personality_assessment"]
                )
        
        # Start personality assessment
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(self.assessment_questions["personality"])])
        
        response = f"""I'll help you understand your personality profile for career planning. Let's start with a Big Five personality assessment.

Please answer these questions thoughtfully and honestly:

{questions_text}

Take your time to reflect on each question. Your responses will help me understand your work style, preferences, and natural tendencies."""

        return AgentResponse(
            content=response,
            metadata={"assessment_stage": "personality_questions"},
            confidence=0.9
        )
    
    async def _analyze_interests(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "interests" in context and "preferences" in context:
            interests = context["interests"]
            preferences = context["preferences"]
            
            interest_scores = await self.use_tool("interest_assessment", 
                                                interests=interests, 
                                                preferences=preferences)
            
            if interest_scores:
                interests_obj = InterestAssessment(**interest_scores)
                top_interests = interests_obj.top_interests
                
                analysis = f"""Based on your interests, here's your Holland Code (RIASEC) profile:

**Interest Assessment Results:**
- **Realistic**: {interest_scores['realistic']:.1f}/100 - Hands-on, practical activities
- **Investigative**: {interest_scores['investigative']:.1f}/100 - Research, analysis, problem-solving
- **Artistic**: {interest_scores['artistic']:.1f}/100 - Creative, expressive activities
- **Social**: {interest_scores['social']:.1f}/100 - Helping, teaching, working with people
- **Enterprising**: {interest_scores['enterprising']:.1f}/100 - Leading, persuading, business activities
- **Conventional**: {interest_scores['conventional']:.1f}/100 - Organizing, detailed, structured work

**Your top 3 interest areas are: {', '.join(top_interests[:3]).title()}**

{self._interpret_interest_results(interests_obj)}

Would you like me to combine this with a personality assessment for comprehensive career recommendations?"""

                return AgentResponse(
                    content=analysis,
                    metadata={"interest_assessment": interest_scores},
                    confidence=0.85,
                    tools_used=["interest_assessment"]
                )
        
        # Request interest information
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(self.assessment_questions["interests"])])
        
        response = f"""Let me understand your interests and preferences to help with career guidance.

Please share your thoughts on these questions:

{questions_text}

Your answers will help me understand what motivates and energizes you professionally."""

        return AgentResponse(
            content=response,
            metadata={"assessment_stage": "interest_questions"},
            confidence=0.9
        )
    
    async def _provide_career_recommendations(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if not context or "user_profile" not in context:
            return AgentResponse(
                content="To provide personalized career recommendations, I need to first understand your personality and interests. Would you like to complete our assessment process?",
                confidence=0.7
            )
        
        user_profile = context["user_profile"]
        career_matches = await self.use_tool("career_matching", user_profile=user_profile)
        
        if career_matches:
            recommendations_text = "Based on your personality and interests, here are my top career recommendations:\n\n"
            
            for i, career in enumerate(career_matches[:3], 1):
                recommendations_text += f"""**{i}. {career['title']}** (Match: {career['match_score']:.1f}%)
- **Industry**: {career['industry']}
- **Why it fits**: Personality alignment {career['personality_alignment']:.1f}%, Interest alignment {career['interest_alignment']:.1f}%
- **Key skills needed**: {', '.join(career['required_skills'])}
- **Salary range**: ${career['salary_range']['min']:,} - ${career['salary_range']['max']:,}
- **Outlook**: {career['growth_outlook']}

"""
            
            recommendations_text += self._generate_action_plan(career_matches[:3])
            
            return AgentResponse(
                content=recommendations_text,
                metadata={"career_recommendations": career_matches},
                confidence=0.88,
                tools_used=["career_matching"]
            )
        
        return AgentResponse(
            content="I'm having trouble generating specific recommendations right now. Could you tell me more about your background and what types of work interest you?",
            confidence=0.4
        )
    
    async def _general_career_guidance(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        # Use LLM for general career guidance
        system_prompt = self.get_system_prompt()
        
        conversation_context = ""
        if self.memory.chat_memory.messages:
            recent_messages = self.memory.chat_memory.messages[-4:]
            conversation_context = "\n".join([
                f"{'User' if hasattr(msg, 'content') and not hasattr(msg, 'response_metadata') else 'Assistant'}: {msg.content}"
                for msg in recent_messages
            ])
        
        full_prompt = f"""{system_prompt}

Previous conversation:
{conversation_context}

User's current message: {message}

Provide helpful, specific career guidance based on your expertise."""

        try:
            response = await self.llm.ainvoke([{"role": "user", "content": full_prompt}])
            
            return AgentResponse(
                content=response.content,
                confidence=0.75
            )
            
        except Exception as e:
            self.logger.error(f"Error in general guidance: {str(e)}")
            return AgentResponse(
                content="I'm here to help with career guidance. You can ask me about career assessments, exploring different professions, or getting personalized recommendations. What would you like to know?",
                confidence=0.6
            )
    
    def _interpret_personality_results(self, personality: PersonalityAssessment) -> str:
        interpretations = []
        
        if personality.openness > 70:
            interpretations.append("• Your high openness suggests you'd thrive in creative, innovative, or research-oriented roles")
        elif personality.openness < 40:
            interpretations.append("• Your preference for structure suggests you'd excel in established, well-defined career paths")
        
        if personality.conscientiousness > 70:
            interpretations.append("• Your strong conscientiousness makes you well-suited for roles requiring attention to detail and reliability")
        
        if personality.extraversion > 70:
            interpretations.append("• Your extraversion indicates you'd flourish in people-facing roles like sales, management, or counseling")
        elif personality.extraversion < 40:
            interpretations.append("• Your introversion suggests you'd excel in focused, independent work environments")
        
        if personality.agreeableness > 70:
            interpretations.append("• Your high agreeableness suggests you'd thrive in collaborative, service-oriented careers")
        
        return "\n".join(interpretations) if interpretations else "Your balanced personality profile gives you flexibility across many career paths."
    
    def _interpret_interest_results(self, interests: InterestAssessment) -> str:
        top_interest = interests.top_interests[0]
        
        interpretations = {
            "realistic": "You're drawn to hands-on, practical work. Consider careers in engineering, trades, agriculture, or technical fields.",
            "investigative": "You enjoy research and analysis. Science, technology, healthcare, and research roles would be great fits.",
            "artistic": "You value creativity and self-expression. Explore careers in design, media, entertainment, or creative industries.",
            "social": "You're motivated by helping others. Education, counseling, social work, or healthcare could be fulfilling.",
            "enterprising": "You're energized by leadership and business. Consider management, sales, entrepreneurship, or business roles.",
            "conventional": "You appreciate organization and structure. Finance, administration, operations, or data management roles suit you."
        }
        
        return interpretations.get(top_interest, "Your interests suggest multiple career paths could be fulfilling.")
    
    def _generate_action_plan(self, career_matches: List[Dict[str, Any]]) -> str:
        if not career_matches:
            return ""
        
        top_career = career_matches[0]
        skills_needed = top_career.get('required_skills', [])
        
        action_plan = f"""
**Recommended Next Steps:**
1. **Skill Development**: Focus on building these key skills: {', '.join(skills_needed[:3])}
2. **Networking**: Connect with professionals in {top_career['industry']} through LinkedIn or industry events
3. **Experience**: Look for internships, volunteer opportunities, or projects in {top_career['title']} roles
4. **Learning**: Consider relevant courses or certifications in your areas of interest
5. **Exploration**: Research day-in-the-life content for {top_career['title']} to validate your interest

Would you like me to elaborate on any of these recommendations or help you create a detailed development plan?"""

        return action_plan
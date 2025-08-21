from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.data_models import UserProfile


class QuestionnaireQuestion(BaseModel):
    id: str
    question: str
    question_type: str  # "multiple_choice", "text", "scale", "ranking"
    options: Optional[List[str]] = None
    scale_min: Optional[int] = None
    scale_max: Optional[int] = None
    category: str  # "personality", "interests", "values", "goals", "background"
    importance: int  # 1-5, how important this question is


class QuestionnaireResponse(BaseModel):
    question_id: str
    response: Any  # Can be string, number, or list
    timestamp: datetime = datetime.now()


class OnboardingQuestionnaireService:
    """AI-powered personalized onboarding questionnaire generator"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
    
    async def generate_personalized_questionnaire(
        self, 
        user_profile: UserProfile
    ) -> List[QuestionnaireQuestion]:
        """Generate a personalized questionnaire based on user profile"""
        
        # Create AI prompt for generating questions
        prompt = f"""You are a career counseling expert designing a personalized questionnaire for a student/professional. 

User Profile:
- Name: {user_profile.name}
- Age: {user_profile.age or 'Not specified'}
- Education: {user_profile.education_level or 'Not specified'}
- Career Stage: {user_profile.career_stage or 'Not specified'}
- Location: {user_profile.location or 'Not specified'}

Generate 15-20 thoughtful questions that will help understand:

1. **Personality & Work Style** (4-5 questions)
   - Communication preferences
   - Problem-solving approach
   - Leadership style
   - Team vs individual work

2. **Interests & Passions** (4-5 questions)
   - Subject areas that excite them
   - Activities they enjoy
   - Types of problems they like solving
   - Industries that interest them

3. **Values & Motivations** (3-4 questions)
   - What drives them professionally
   - Work-life balance priorities
   - Impact they want to make
   - Success metrics

4. **Goals & Aspirations** (3-4 questions)
   - Short-term career goals (1-2 years)
   - Long-term vision (5-10 years)
   - Skills they want to develop
   - Dream job characteristics

5. **Background & Experience** (2-3 questions)
   - Relevant experiences or projects
   - Challenges they've overcome
   - Learning preferences
   - Current skills/strengths

Make questions:
- Age-appropriate and relevant to their career stage
- Open-ended where possible to get detailed insights
- Specific enough to be actionable
- Engaging and thought-provoking

Return ONLY a valid JSON array of questions with this exact format:
[
  {{
    "id": "q1",
    "question": "Question text here",
    "question_type": "text",
    "category": "personality",
    "importance": 4
  }},
  ...
]

Question types: "text", "multiple_choice", "scale", "ranking"
Categories: "personality", "interests", "values", "goals", "background"
Importance: 1-5 (5 = most important)"""

        try:
            # Call Google Gemini AI
            response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
            ai_response = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            questions_data = self._extract_json_from_response(ai_response)
            
            # Convert to QuestionnaireQuestion objects
            questions = []
            for i, q_data in enumerate(questions_data):
                question = QuestionnaireQuestion(
                    id=q_data.get('id', f'q{i+1}'),
                    question=q_data['question'],
                    question_type=q_data.get('question_type', 'text'),
                    options=q_data.get('options'),
                    scale_min=q_data.get('scale_min'),
                    scale_max=q_data.get('scale_max'),
                    category=q_data.get('category', 'general'),
                    importance=q_data.get('importance', 3)
                )
                questions.append(question)
            
            return questions[:20]  # Limit to 20 questions max
            
        except Exception as e:
            print(f"Error generating questionnaire: {str(e)}")
            # Return fallback questions
            return self._get_fallback_questions()
    
    def _extract_json_from_response(self, response: str) -> List[Dict[str, Any]]:
        """Extract JSON array from AI response"""
        try:
            # Find JSON array in the response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON array found in response")
                
        except Exception as e:
            print(f"Error parsing JSON: {str(e)}")
            return self._get_fallback_questions_data()
    
    def _get_fallback_questions(self) -> List[QuestionnaireQuestion]:
        """Fallback questions if AI generation fails"""
        fallback_data = self._get_fallback_questions_data()
        
        questions = []
        for q_data in fallback_data:
            question = QuestionnaireQuestion(**q_data)
            questions.append(question)
        
        return questions
    
    def _get_fallback_questions_data(self) -> List[Dict[str, Any]]:
        """Default fallback questions"""
        return [
            {
                "id": "q1",
                "question": "What activities or subjects have you always been naturally drawn to, even outside of work or school?",
                "question_type": "text",
                "category": "interests",
                "importance": 5
            },
            {
                "id": "q2", 
                "question": "Describe a time when you felt most engaged and energized while working on something. What were you doing?",
                "question_type": "text",
                "category": "personality",
                "importance": 5
            },
            {
                "id": "q3",
                "question": "What does success look like to you in 5 years? Be as specific as possible.",
                "question_type": "text",
                "category": "goals",
                "importance": 5
            },
            {
                "id": "q4",
                "question": "When working on a project, do you prefer to: work independently, collaborate closely with others, or lead a team?",
                "question_type": "multiple_choice",
                "options": ["Work independently", "Collaborate closely with others", "Lead a team", "It depends on the situation"],
                "category": "personality",
                "importance": 4
            },
            {
                "id": "q5",
                "question": "What kind of impact do you want your career to have on the world or your community?",
                "question_type": "text",
                "category": "values",
                "importance": 4
            },
            {
                "id": "q6",
                "question": "Which of these work environments appeals to you most?",
                "question_type": "multiple_choice",
                "options": ["Fast-paced startup", "Established corporation", "Non-profit organization", "Government agency", "Freelance/consulting", "Academia/research"],
                "category": "values",
                "importance": 4
            },
            {
                "id": "q7",
                "question": "What skills or knowledge areas are you most excited to develop in the next 2 years?",
                "question_type": "text",
                "category": "goals",
                "importance": 4
            },
            {
                "id": "q8",
                "question": "How important is work-life balance to you on a scale of 1-10?",
                "question_type": "scale",
                "scale_min": 1,
                "scale_max": 10,
                "category": "values",
                "importance": 3
            },
            {
                "id": "q9",
                "question": "Tell me about a challenge or problem you've solved that you're proud of. What was your approach?",
                "question_type": "text",
                "category": "background",
                "importance": 4
            },
            {
                "id": "q10",
                "question": "Which industries or fields spark your curiosity, even if you don't know much about them yet?",
                "question_type": "text",
                "category": "interests",
                "importance": 4
            }
        ]
    
    async def analyze_questionnaire_responses(
        self, 
        questions: List[QuestionnaireQuestion],
        responses: List[QuestionnaireResponse],
        user_profile: UserProfile
    ) -> Dict[str, Any]:
        """Analyze questionnaire responses using AI to extract insights"""
        
        # Combine questions and responses for analysis
        qa_pairs = []
        for response in responses:
            question = next((q for q in questions if q.id == response.question_id), None)
            if question:
                qa_pairs.append({
                    "question": question.question,
                    "category": question.category,
                    "importance": question.importance,
                    "response": response.response
                })
        
        # Create analysis prompt
        prompt = f"""As a career counselor and psychologist, analyze these questionnaire responses from {user_profile.name} to extract deep insights for career guidance.

User Profile:
- Age: {user_profile.age or 'Not specified'}
- Education: {user_profile.education_level or 'Not specified'}
- Career Stage: {user_profile.career_stage or 'Not specified'}

Questionnaire Responses:
{json.dumps(qa_pairs, indent=2)}

Provide a comprehensive analysis in JSON format with these sections:

{{
  "personality_insights": {{
    "work_style": "summary of their work preferences",
    "communication_style": "how they communicate and collaborate",
    "problem_solving_approach": "their approach to challenges",
    "leadership_potential": "leadership traits and potential",
    "key_strengths": ["strength1", "strength2", "strength3"]
  }},
  "interest_insights": {{
    "primary_interests": ["interest1", "interest2", "interest3"],
    "preferred_activities": ["activity1", "activity2"],
    "industry_alignment": ["industry1", "industry2", "industry3"],
    "learning_preferences": "how they like to learn and grow"
  }},
  "values_motivation": {{
    "core_values": ["value1", "value2", "value3"],
    "motivation_drivers": ["driver1", "driver2"],
    "work_life_balance": "their balance preferences",
    "impact_goals": "what impact they want to make"
  }},
  "career_direction": {{
    "short_term_goals": ["goal1", "goal2"],
    "long_term_vision": "their 5-10 year career vision",
    "skill_development_priorities": ["skill1", "skill2", "skill3"],
    "potential_career_paths": ["path1", "path2", "path3"]
  }},
  "recommendations": {{
    "immediate_actions": ["action1", "action2", "action3"],
    "skill_building": ["skill1", "skill2"],
    "networking_suggestions": ["suggestion1", "suggestion2"],
    "exploration_activities": ["activity1", "activity2"]
  }}
}}

Be specific, actionable, and personalized. Focus on insights that will help with career planning and decision-making."""

        try:
            # Call Google Gemini AI
            response = await self.llm.ainvoke([{"role": "user", "content": prompt}])
            ai_response = response.content if hasattr(response, 'content') else str(response)
            
            # Extract JSON from response
            analysis = self._extract_json_from_analysis(ai_response)
            
            return analysis
            
        except Exception as e:
            print(f"Error analyzing responses: {str(e)}")
            # Return basic analysis
            return {
                "personality_insights": {
                    "work_style": "Analysis in progress",
                    "key_strengths": ["Problem solving", "Communication", "Adaptability"]
                },
                "interest_insights": {
                    "primary_interests": ["Technology", "Problem solving", "Learning"],
                    "industry_alignment": ["Technology", "Consulting", "Education"]
                },
                "career_direction": {
                    "potential_career_paths": ["Software Development", "Data Analysis", "Project Management"]
                },
                "recommendations": {
                    "immediate_actions": ["Complete skills assessment", "Network with professionals", "Research career paths"]
                }
            }
    
    def _extract_json_from_analysis(self, response: str) -> Dict[str, Any]:
        """Extract JSON analysis from AI response"""
        try:
            # Find JSON object in the response
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = response[start_idx:end_idx]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON object found in response")
                
        except Exception as e:
            print(f"Error parsing analysis JSON: {str(e)}")
            return {}
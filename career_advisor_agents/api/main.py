import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables from .env file
# Try loading from current directory and parent directory
load_dotenv()  # Try current directory first
load_dotenv(project_root / ".env")  # Try project root directory

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, List, Optional, Any
import logging
import asyncio
from datetime import datetime
import uuid

from core.llm_config import create_default_llm_config, AgentLLMFactory
from core.agent_framework import AgentOrchestrator, AgentMetrics
from agents.career_analyst import CareerAnalystAgent
from services.database import get_database, get_user_repository, DatabaseManager, UserRepository
from services.career_counseling import CareerCounselingService
from services.predictive_analytics import PredictiveAnalyticsService
from services.onboarding_questionnaire import OnboardingQuestionnaireService, QuestionnaireResponse
from core.data_models import (
    UserProfile, CareerAnalysisRequest, CareerAnalysisResponse,
    ConversationMessage, ProgressUpdate
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
agent_orchestrator: Optional[AgentOrchestrator] = None
agent_metrics: Optional[AgentMetrics] = None
counseling_service: Optional[CareerCounselingService] = None
analytics_service: Optional[PredictiveAnalyticsService] = None
questionnaire_service: Optional[OnboardingQuestionnaireService] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events for the FastAPI app"""
    # Startup
    logger.info("Starting Career Advisor Agent System...")
    
    try:
        # Initialize database
        db_manager = await get_database()
        logger.info("Database initialized")
        
        # Initialize LLM configuration
        llm_config = create_default_llm_config()
        llm_factory = AgentLLMFactory(llm_config)
        
        # Initialize global services
        global agent_orchestrator, agent_metrics, counseling_service, analytics_service, questionnaire_service
        
        agent_orchestrator = AgentOrchestrator()
        agent_metrics = AgentMetrics()
        
        # Create and register agents
        career_analyst_llm = llm_factory.get_llm_for_agent("career_analyst")
        career_analyst = CareerAnalystAgent(career_analyst_llm)
        agent_orchestrator.register_agent(career_analyst)
        
        # Initialize services
        counseling_llm = llm_factory.get_llm_for_agent("mentor_bot")
        counseling_service = CareerCounselingService(counseling_llm)
        analytics_llm = llm_factory.get_llm_for_agent("analytics_agent")
        analytics_service = PredictiveAnalyticsService(analytics_llm)
        questionnaire_llm = llm_factory.get_llm_for_agent("questionnaire_agent")
        questionnaire_service = OnboardingQuestionnaireService(questionnaire_llm)
        
        logger.info("All services initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {str(e)}")
        raise
    
    # Shutdown
    logger.info("Shutting down Career Advisor Agent System...")
    if db_manager:
        await db_manager.close()


app = FastAPI(
    title="AI Career & Skill Development Advisor",
    description="Multi-agent system for career planning and skill development using LangChain and Google Gemini",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": "connected" if agent_orchestrator else "disconnected",
            "agents": len(agent_orchestrator.list_agents()) if agent_orchestrator else 0,
            "llm": "available"
        }
    }

# User Management Endpoints
@app.post("/api/users/register")
async def register_user(
    user_data: Dict[str, Any],
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Register a new user"""
    try:
        # Generate user ID if not provided
        user_id = user_data.get("user_id", str(uuid.uuid4()))
        
        # Handle enum conversions for registration
        from core.data_models import EducationLevel, CareerStage
        
        education_level = None
        if user_data.get("education_level"):
            try:
                education_level = EducationLevel(user_data["education_level"])
            except ValueError:
                logger.warning(f"Invalid education_level: {user_data.get('education_level')}")
        
        career_stage = None
        if user_data.get("career_stage"):
            try:
                career_stage = CareerStage(user_data["career_stage"])
            except ValueError:
                logger.warning(f"Invalid career_stage: {user_data.get('career_stage')}")
        
        user_profile = UserProfile(
            user_id=user_id,
            name=user_data["name"],
            email=user_data["email"],
            age=user_data.get("age"),
            location=user_data.get("location"),
            education_level=education_level,
            career_stage=career_stage
        )
        
        await user_repo.create_user(user_profile)
        
        return {
            "user_id": user_id,
            "message": "User registered successfully",
            "status": "success"
        }
        
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        logger.error(f"User data received: {user_data}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.get("/api/users/{user_id}/profile")
async def get_user_profile(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get user profile"""
    try:
        user_profile = await user_repo.get_user(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        return user_profile.dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/users/{user_id}/profile")
async def update_user_profile(
    user_id: str,
    profile_data: Dict[str, Any],
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update user profile"""
    try:
        # Get existing profile
        existing_profile = await user_repo.get_user(user_id)
        if not existing_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update with new data, handling enum conversions
        from core.data_models import EducationLevel, CareerStage
        
        for key, value in profile_data.items():
            if hasattr(existing_profile, key) and value is not None:
                # Handle enum conversions
                if key == "education_level" and isinstance(value, str):
                    try:
                        value = EducationLevel(value)
                    except ValueError:
                        logger.warning(f"Invalid education_level value: {value}")
                        continue
                elif key == "career_stage" and isinstance(value, str):
                    try:
                        value = CareerStage(value)
                    except ValueError:
                        logger.warning(f"Invalid career_stage value: {value}")
                        continue
                
                setattr(existing_profile, key, value)
        
        success = await user_repo.update_user(existing_profile)
        
        if success:
            return {"message": "Profile updated successfully", "status": "success"}
        else:
            raise HTTPException(status_code=500, detail="Failed to update profile")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Onboarding Questionnaire Endpoints
@app.get("/api/questionnaire/generate/{user_id}")
async def generate_questionnaire(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Generate personalized questionnaire for user"""
    try:
        if not questionnaire_service:
            raise HTTPException(status_code=503, detail="Questionnaire service not initialized")
        
        # Get user profile
        user_profile = await user_repo.get_user(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if already completed
        if getattr(user_profile, 'questionnaire_completed', False):
            return {
                "message": "Questionnaire already completed",
                "completed": True,
                "questions": []
            }
        
        # Generate personalized questions
        questions = await questionnaire_service.generate_personalized_questionnaire(user_profile)
        
        return {
            "user_id": user_id,
            "questions": [q.dict() for q in questions],
            "total_questions": len(questions),
            "estimated_time": len(questions) * 2  # 2 minutes per question
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating questionnaire: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/questionnaire/submit/{user_id}")
async def submit_questionnaire(
    user_id: str,
    submission_data: Dict[str, Any],
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Submit completed questionnaire responses"""
    try:
        if not questionnaire_service:
            raise HTTPException(status_code=503, detail="Questionnaire service not initialized")
        
        # Get user profile
        user_profile = await user_repo.get_user(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Parse responses
        questions_data = submission_data.get("questions", [])
        responses_data = submission_data.get("responses", [])
        
        questions = [questionnaire_service._get_fallback_questions()[0].__class__(**q) for q in questions_data]
        responses = [QuestionnaireResponse(**r) for r in responses_data]
        
        # Analyze responses
        analysis = await questionnaire_service.analyze_questionnaire_responses(
            questions, responses, user_profile
        )
        
        # Save to database with proper JSON serialization
        questionnaire_data = {
            "responses": [r.dict() for r in responses],
            "analysis": analysis,
            "completed_at": datetime.now().isoformat()
        }
        
        # Ensure all data is JSON serializable
        import json
        questionnaire_data = json.loads(json.dumps(questionnaire_data, default=str))
        
        await user_repo.save_questionnaire_results(user_id, questionnaire_data)
        
        return {
            "message": "Questionnaire submitted successfully",
            "analysis": analysis,
            "next_steps": [
                "Explore personalized career recommendations",
                "Schedule a career counseling session",
                "Take skills assessments based on your profile"
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting questionnaire: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/questionnaire/status/{user_id}")
async def get_questionnaire_status(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Check questionnaire completion status"""
    try:
        user_profile = await user_repo.get_user(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        completed = getattr(user_profile, 'questionnaire_completed', False)
        responses = getattr(user_profile, 'questionnaire_responses', None)
        
        return {
            "user_id": user_id,
            "completed": completed,
            "has_responses": responses is not None,
            "completion_date": responses.get("completed_at") if responses else None,
            "analysis_available": bool(responses and responses.get("analysis"))
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting questionnaire status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Agent Interaction Endpoints
@app.post("/api/agents/career-analysis")
async def career_analysis(
    request: CareerAnalysisRequest,
    background_tasks: BackgroundTasks,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Perform career analysis using career analyst agent"""
    try:
        if not agent_orchestrator:
            raise HTTPException(status_code=503, detail="Agent system not initialized")
        
        start_time = datetime.now()
        
        # Get user profile
        user_profile = await user_repo.get_user(request.user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Prepare context for agent
        context = {
            "user_profile": user_profile.dict(),
            "analysis_type": request.analysis_type,
            "parameters": request.parameters
        }
        
        # Route to career analyst agent
        response = await agent_orchestrator.route_message(
            message=f"Perform {request.analysis_type} analysis",
            agent_name="career_analyst",
            context=context
        )
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Record metrics
        if agent_metrics:
            agent_metrics.record_interaction("career_analyst", processing_time / 1000, response.confidence)
        
        # Save conversation in background
        background_tasks.add_task(
            save_conversation_background,
            user_repo,
            request.user_id,
            "career_analyst",
            f"Analysis request: {request.analysis_type}",
            response.content,
            context,
            response.metadata,
            response.confidence,
            processing_time
        )
        
        return CareerAnalysisResponse(
            request_id=str(uuid.uuid4()),
            user_id=request.user_id,
            analysis_type=request.analysis_type,
            results=response.metadata,
            confidence=response.confidence * 100,
            processing_time_ms=processing_time
        ).dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in career analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/counseling/chat")
async def counseling_chat(
    message_data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Chat with career counseling service"""
    try:
        user_id = message_data["user_id"]
        message = message_data["message"]
        
        if not counseling_service:
            raise HTTPException(status_code=503, detail="Counseling service not initialized")
        
        # Get user profile and conversation history
        user_profile = await user_repo.get_user(user_id)
        conversation_history = await user_repo.get_conversation_history(user_id, limit=10)
        
        # Process counseling request
        result = await counseling_service.process_counseling_request(
            user_id=user_id,
            message=message,
            user_profile=user_profile,
            conversation_history=conversation_history
        )
        
        # Save conversation in background
        background_tasks.add_task(
            save_conversation_background,
            user_repo,
            user_id,
            "mentor_bot",
            message,
            result["response"],
            {"sentiment": result["sentiment_analysis"]},
            result.get("conversation_metadata", {}),
            result["sentiment_analysis"].get("confidence_level", 0.5),
            None
        )
        
        return {
            "response": result["response"],
            "sentiment_analysis": result["sentiment_analysis"],
            "follow_up_actions": result["follow_up_actions"],
            "conversation_metadata": result.get("conversation_metadata", {})
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in counseling chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/agents/recommendations/{user_id}")
async def get_career_recommendations(
    user_id: str,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get career recommendations for user"""
    try:
        if not agent_orchestrator:
            raise HTTPException(status_code=503, detail="Agent system not initialized")
        
        # Get user profile
        user_profile = await user_repo.get_user(user_id)
        if not user_profile:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if user has completed questionnaire for personalized recommendations
        questionnaire_completed = user_profile.questionnaire_completed if hasattr(user_profile, 'questionnaire_completed') else False
        
        if not questionnaire_completed:
            # Recommend completing questionnaire first
            return {
                "recommendations": [
                    "Complete your personalized career questionnaire to unlock detailed, AI-powered career recommendations",
                    "The questionnaire analyzes your personality, interests, values, and work preferences",
                    "This enables us to provide highly targeted career guidance based on your unique profile"
                ],
                "confidence": 0.9,
                "explanation": "To provide you with the most accurate and personalized career recommendations, I recommend completing our comprehensive career questionnaire first. This will help me understand your personality, interests, values, and work preferences to give you highly targeted career guidance.",
                "requires_questionnaire": True,
                "questionnaire_status": "not_completed"
            }
        
        # Get personalized recommendations from career analyst
        message = "Based on my completed questionnaire data, provide detailed career recommendations that are specifically tailored to my personality insights, interests, values, and career goals."
        
        context = {"user_profile": user_profile.dict()}
        response = await agent_orchestrator.route_message(
            message=message,
            agent_name="career_analyst",
            context=context
        )
        
        return {
            "recommendations": response.metadata.get("career_recommendations", []),
            "confidence": response.confidence,
            "explanation": response.content,
            "personalized": True,
            "questionnaire_status": "completed"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Analytics Endpoints
@app.get("/api/analytics/career-trends")
async def get_career_trends(
    industry: Optional[str] = None,
    role: Optional[str] = None,
    time_horizon: Optional[str] = "medium"
):
    """Get career trend analysis"""
    try:
        if not analytics_service:
            raise HTTPException(status_code=503, detail="Analytics service not initialized")
        
        if industry and role:
            # Get specific industry/role analysis
            result = await analytics_service.generate_career_outlook(
                role=role,
                industry=industry,
                skills=[],  # Could be extended to include skills
                location="national"
            )
            return result
        else:
            # Return general trends
            return {
                "message": "Please specify both industry and role for detailed analysis",
                "available_industries": ["technology", "healthcare", "finance", "education", "manufacturing"],
                "sample_roles": ["software engineer", "data scientist", "marketing manager", "teacher", "nurse"]
            }
            
    except Exception as e:
        logger.error(f"Error getting career trends: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/skill-demand")
async def get_skill_demand_analysis(skills: str):
    """Get skill demand trend analysis"""
    try:
        if not analytics_service:
            raise HTTPException(status_code=503, detail="Analytics service not initialized")
        
        skill_list = [skill.strip() for skill in skills.split(",")]
        
        predictions = await analytics_service.trend_analyzer.analyze_skill_demand_trends(skill_list)
        
        return {
            "skills_analyzed": skill_list,
            "predictions": [
                {
                    "skill": pred.supporting_data["skill"],
                    "prediction": pred.prediction,
                    "confidence": pred.confidence,
                    "time_horizon": pred.time_horizon,
                    "recommendations": pred.recommendations,
                    "implications": pred.implications
                }
                for pred in predictions
            ],
            "analysis_date": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing skill demand: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analytics/market-predictions")
async def get_market_predictions(
    industry: str,
    analysis_type: str = "disruption"
):
    """Get market predictions and disruption analysis"""
    try:
        if not analytics_service:
            raise HTTPException(status_code=503, detail="Analytics service not initialized")
        
        if analysis_type == "disruption":
            result = await analytics_service.predict_industry_disruption(industry)
            return result
        else:
            return {"error": "Only 'disruption' analysis type is currently supported"}
            
    except Exception as e:
        logger.error(f"Error getting market predictions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# System Information Endpoints
@app.get("/api/system/agents")
async def list_agents():
    """List all available agents"""
    if not agent_orchestrator:
        raise HTTPException(status_code=503, detail="Agent system not initialized")
    
    agents = agent_orchestrator.list_agents()
    return {
        "agents": agents,
        "total_count": len(agents)
    }


@app.get("/api/system/metrics")
async def get_system_metrics():
    """Get system performance metrics"""
    if not agent_metrics:
        return {"message": "Metrics not available"}
    
    return {
        "agent_metrics": agent_metrics.get_all_metrics(),
        "system_status": "operational",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/conversations/{user_id}")
async def get_conversation_history(
    user_id: str,
    limit: int = 20,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Get conversation history for user"""
    try:
        conversations = await user_repo.get_conversation_history(user_id, limit)
        
        return {
            "user_id": user_id,
            "conversations": [conv.dict() for conv in conversations],
            "total_count": len(conversations)
        }
        
    except Exception as e:
        logger.error(f"Error getting conversation history: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Background Tasks
async def save_conversation_background(
    user_repo: UserRepository,
    user_id: str,
    agent_name: str,
    user_message: str,
    agent_response: str,
    context: Dict[str, Any],
    metadata: Dict[str, Any],
    confidence: float,
    processing_time_ms: Optional[int]
):
    """Save conversation to database in background"""
    try:
        import json
        
        # Clean up context and metadata to be JSON serializable
        def make_json_serializable(obj):
            if isinstance(obj, dict):
                return {k: make_json_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [make_json_serializable(item) for item in obj]
            elif isinstance(obj, datetime):
                return obj.isoformat()
            elif hasattr(obj, '__dict__'):
                return str(obj)  # Convert objects to string representation
            else:
                return obj
        
        clean_context = make_json_serializable(context)
        clean_metadata = make_json_serializable(metadata)
        
        conversation = ConversationMessage(
            message_id=str(uuid.uuid4()),
            user_id=user_id,
            agent_name=agent_name,
            user_message=user_message,
            agent_response=agent_response,
            context=clean_context,
            metadata=clean_metadata,
            confidence=confidence,
            processing_time_ms=processing_time_ms,
            timestamp=datetime.now()
        )
        
        await user_repo.save_conversation(conversation)
        
    except Exception as e:
        logger.error(f"Error saving conversation: {str(e)}")


def main():
    """Main entry point for running the application"""
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)

if __name__ == "__main__":
    main()
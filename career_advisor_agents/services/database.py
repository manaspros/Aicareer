import os
import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, JSON, Boolean,
    ForeignKey, Table, create_engine, text
)
from sqlalchemy.orm import relationship
from contextlib import asynccontextmanager
import sqlite3
import logging

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.data_models import (
    UserProfile, PersonalityAssessment, InterestAssessment,
    CareerRecommendation, SkillAssessmentResult, ProgressUpdate,
    ConversationMessage, UserGoal
)

# Database Models
Base = declarative_base()

# Association tables for many-to-many relationships
user_skills_table = Table(
    'user_skills',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.user_id'), primary_key=True),
    Column('skill_name', String, primary_key=True)
)

user_interests_table = Table(
    'user_interests', 
    Base.metadata,
    Column('user_id', String, ForeignKey('users.user_id'), primary_key=True),
    Column('interest_name', String, primary_key=True)
)


class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    age = Column(Integer)
    location = Column(String)
    education_level = Column(String)
    career_stage = Column(String)
    
    # Onboarding and personalization
    questionnaire_completed = Column(Boolean, default=False)
    questionnaire_responses = Column(JSON)
    personality_insights = Column(JSON)
    interest_insights = Column(JSON)
    
    # JSON fields for flexible data
    career_goals = Column(JSON)
    values = Column(JSON)
    preferred_work_environment = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    personality_assessments = relationship("PersonalityAssessmentDB", back_populates="user")
    interest_assessments = relationship("InterestAssessmentDB", back_populates="user")
    skill_assessments = relationship("SkillAssessmentDB", back_populates="user")
    career_recommendations = relationship("CareerRecommendationDB", back_populates="user")
    conversations = relationship("ConversationDB", back_populates="user")
    progress_updates = relationship("ProgressUpdateDB", back_populates="user")
    goals = relationship("UserGoalDB", back_populates="user")


class PersonalityAssessmentDB(Base):
    __tablename__ = 'personality_assessments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    openness = Column(Float, nullable=False)
    conscientiousness = Column(Float, nullable=False)
    extraversion = Column(Float, nullable=False)
    agreeableness = Column(Float, nullable=False)
    neuroticism = Column(Float, nullable=False)
    
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="personality_assessments")


class InterestAssessmentDB(Base):
    __tablename__ = 'interest_assessments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    realistic = Column(Float, nullable=False)
    investigative = Column(Float, nullable=False)
    artistic = Column(Float, nullable=False)
    social = Column(Float, nullable=False)
    enterprising = Column(Float, nullable=False)
    conventional = Column(Float, nullable=False)
    
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="interest_assessments")


class Skill(Base):
    __tablename__ = 'skills'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    category = Column(String, nullable=False)
    description = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SkillAssessmentDB(Base):
    __tablename__ = 'skill_assessments'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    skill_name = Column(String, nullable=False)
    
    assessed_level = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=False)
    
    strengths = Column(JSON)
    improvement_areas = Column(JSON)
    recommendations = Column(JSON)
    
    assessment_method = Column(String)
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="skill_assessments")


class CareerRecommendationDB(Base):
    __tablename__ = 'career_recommendations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text)
    industry = Column(String, nullable=False)
    match_score = Column(Float, nullable=False)
    
    required_skills = Column(JSON)
    preferred_skills = Column(JSON)
    education_requirements = Column(JSON)
    
    salary_range = Column(JSON)
    growth_outlook = Column(String)
    work_environment = Column(JSON)
    
    reasoning = Column(Text)
    recommended_actions = Column(JSON)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="career_recommendations")


class ConversationDB(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    message_id = Column(String, unique=True, nullable=False)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    agent_name = Column(String, nullable=False)
    
    user_message = Column(Text, nullable=False)
    agent_response = Column(Text, nullable=False)
    
    context = Column(JSON)
    conversation_metadata = Column(JSON)
    
    confidence = Column(Float, default=0.0)
    processing_time_ms = Column(Integer)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="conversations")


class ProgressUpdateDB(Base):
    __tablename__ = 'progress_updates'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    skill_name = Column(String)
    goal_name = Column(String)
    
    progress_percentage = Column(Float, nullable=False)
    milestones_completed = Column(JSON)
    current_activities = Column(JSON)
    
    achievements = Column(JSON)
    challenges = Column(JSON)
    next_steps = Column(JSON)
    
    notes = Column(Text)
    date_recorded = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="progress_updates")


class UserGoalDB(Base):
    __tablename__ = 'user_goals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.user_id'), nullable=False)
    
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String, nullable=False)
    
    target_date = Column(DateTime)
    priority = Column(Integer, default=5)
    
    milestones = Column(JSON)
    success_metrics = Column(JSON)
    
    status = Column(String, default='active')
    progress_percentage = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="goals")


class IndustryTrendDB(Base):
    __tablename__ = 'industry_trends'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    industry = Column(String, nullable=False)
    trend_name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    
    impact_level = Column(String, nullable=False)
    time_horizon = Column(String, nullable=False)
    
    affected_roles = Column(JSON)
    emerging_skills = Column(JSON)
    declining_skills = Column(JSON)
    
    source = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class DatabaseManager:
    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or os.getenv("DATABASE_URL", "sqlite:///./career_advisor.db")
        self.engine = None
        self.async_session_factory = None
        self.logger = logging.getLogger(__name__)
        
    async def initialize(self):
        """Initialize database connection and create tables"""
        try:
            # Create async engine
            if self.database_url.startswith("sqlite"):
                # For SQLite, use aiosqlite
                sqlite_url = self.database_url.replace("sqlite://", "sqlite+aiosqlite://")
                self.engine = create_async_engine(sqlite_url, echo=False)
            else:
                # For PostgreSQL and other databases
                self.engine = create_async_engine(self.database_url, echo=False)
            
            # Create session factory
            self.async_session_factory = sessionmaker(
                bind=self.engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )
            
            # Create all tables
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            self.logger.info("Database initialized successfully")
            
            # Populate initial data
            await self._populate_initial_data()
            
        except Exception as e:
            self.logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    async def _populate_initial_data(self):
        """Populate database with initial reference data"""
        async with self.get_session() as session:
            try:
                # Check if skills already exist
                result = await session.execute(text("SELECT COUNT(*) FROM skills"))
                count = result.scalar()
                
                if count == 0:
                    # Add common skills
                    skills_data = [
                        {"name": "Python", "category": "Technical"},
                        {"name": "Machine Learning", "category": "Technical"},
                        {"name": "Data Analysis", "category": "Technical"},
                        {"name": "Communication", "category": "Soft"},
                        {"name": "Leadership", "category": "Soft"},
                        {"name": "Project Management", "category": "Business"},
                        {"name": "JavaScript", "category": "Technical"},
                        {"name": "SQL", "category": "Technical"},
                        {"name": "Problem Solving", "category": "Soft"},
                        {"name": "Digital Marketing", "category": "Business"}
                    ]
                    
                    for skill_data in skills_data:
                        skill = Skill(**skill_data)
                        session.add(skill)
                    
                    await session.commit()
                    self.logger.info("Initial skills data populated")
                    
            except Exception as e:
                self.logger.error(f"Error populating initial data: {str(e)}")
                await session.rollback()
    
    @asynccontextmanager
    async def get_session(self):
        """Get async database session with automatic cleanup"""
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()
    
    async def close(self):
        """Close database connection"""
        if self.engine:
            await self.engine.dispose()
            self.logger.info("Database connection closed")


class UserRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        
    async def create_user(self, user_profile: UserProfile) -> str:
        """Create a new user in the database"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Creating user with profile: {user_profile}")
        logger.info(f"Education level type: {type(user_profile.education_level)}")
        logger.info(f"Career stage type: {type(user_profile.career_stage)}")
        
        async with self.db_manager.get_session() as session:
            try:
                # Handle enum to string conversion safely
                education_level_str = None
                if user_profile.education_level:
                    if hasattr(user_profile.education_level, 'value'):
                        education_level_str = user_profile.education_level.value
                    else:
                        education_level_str = str(user_profile.education_level)
                
                career_stage_str = None
                if user_profile.career_stage:
                    if hasattr(user_profile.career_stage, 'value'):
                        career_stage_str = user_profile.career_stage.value
                    else:
                        career_stage_str = str(user_profile.career_stage)
                
                db_user = User(
                    user_id=user_profile.user_id,
                    name=user_profile.name,
                    email=user_profile.email,
                    age=user_profile.age,
                    location=user_profile.location,
                    education_level=education_level_str,
                    career_stage=career_stage_str,
                    career_goals=user_profile.career_goals,
                    values=user_profile.values,
                    preferred_work_environment=user_profile.preferred_work_environment
                )
                
                session.add(db_user)
                await session.commit()
                
                return user_profile.user_id
                
            except Exception as e:
                await session.rollback()
                raise e
    
    async def get_user(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        async with self.db_manager.get_session() as session:
            try:
                result = await session.get(User, user_id)
                if result:
                    return self._db_user_to_profile(result)
                return None
            except Exception as e:
                raise e
    
    async def update_user(self, user_profile: UserProfile) -> bool:
        """Update existing user profile"""
        async with self.db_manager.get_session() as session:
            try:
                db_user = await session.get(User, user_profile.user_id)
                if not db_user:
                    return False
                
                # Update fields
                db_user.name = user_profile.name
                db_user.email = user_profile.email
                db_user.age = user_profile.age
                db_user.location = user_profile.location
                
                # Handle enum to string conversion safely
                if user_profile.education_level:
                    if hasattr(user_profile.education_level, 'value'):
                        db_user.education_level = user_profile.education_level.value
                    else:
                        db_user.education_level = str(user_profile.education_level)
                else:
                    db_user.education_level = None
                    
                if user_profile.career_stage:
                    if hasattr(user_profile.career_stage, 'value'):
                        db_user.career_stage = user_profile.career_stage.value
                    else:
                        db_user.career_stage = str(user_profile.career_stage)
                else:
                    db_user.career_stage = None
                db_user.career_goals = user_profile.career_goals
                db_user.values = user_profile.values
                db_user.preferred_work_environment = user_profile.preferred_work_environment
                db_user.updated_at = datetime.utcnow()
                
                await session.commit()
                return True
                
            except Exception as e:
                await session.rollback()
                raise e
    
    async def save_personality_assessment(self, user_id: str, assessment: PersonalityAssessment):
        """Save personality assessment results"""
        async with self.db_manager.get_session() as session:
            try:
                db_assessment = PersonalityAssessmentDB(
                    user_id=user_id,
                    openness=assessment.openness,
                    conscientiousness=assessment.conscientiousness,
                    extraversion=assessment.extraversion,
                    agreeableness=assessment.agreeableness,
                    neuroticism=assessment.neuroticism,
                    assessment_date=assessment.assessment_date
                )
                
                session.add(db_assessment)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise e
    
    async def save_interest_assessment(self, user_id: str, assessment: InterestAssessment):
        """Save interest assessment results"""
        async with self.db_manager.get_session() as session:
            try:
                db_assessment = InterestAssessmentDB(
                    user_id=user_id,
                    realistic=assessment.realistic,
                    investigative=assessment.investigative,
                    artistic=assessment.artistic,
                    social=assessment.social,
                    enterprising=assessment.enterprising,
                    conventional=assessment.conventional,
                    assessment_date=assessment.assessment_date
                )
                
                session.add(db_assessment)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise e
    
    async def save_career_recommendations(self, user_id: str, recommendations: List[CareerRecommendation]):
        """Save career recommendations"""
        async with self.db_manager.get_session() as session:
            try:
                for rec in recommendations:
                    db_rec = CareerRecommendationDB(
                        user_id=user_id,
                        title=rec.title,
                        description=rec.description,
                        industry=rec.industry,
                        match_score=rec.match_score,
                        required_skills=rec.required_skills,
                        preferred_skills=rec.preferred_skills,
                        education_requirements=rec.education_requirements,
                        salary_range=rec.salary_range,
                        growth_outlook=rec.growth_outlook,
                        work_environment=rec.work_environment,
                        reasoning=rec.reasoning,
                        recommended_actions=rec.recommended_actions
                    )
                    
                    session.add(db_rec)
                
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise e
    
    async def save_conversation(self, message: ConversationMessage):
        """Save conversation message"""
        async with self.db_manager.get_session() as session:
            try:
                db_message = ConversationDB(
                    message_id=message.message_id,
                    user_id=message.user_id,
                    agent_name=message.agent_name,
                    user_message=message.user_message,
                    agent_response=message.agent_response,
                    context=message.context,
                    conversation_metadata=message.metadata,
                    confidence=message.confidence,
                    processing_time_ms=message.processing_time_ms,
                    timestamp=message.timestamp
                )
                
                session.add(db_message)
                await session.commit()
                
            except Exception as e:
                await session.rollback()
                raise e
    
    async def get_conversation_history(self, user_id: str, limit: int = 50) -> List[ConversationMessage]:
        """Get conversation history for user"""
        async with self.db_manager.get_session() as session:
            try:
                from sqlalchemy import select
                query = select(ConversationDB).where(
                    ConversationDB.user_id == user_id
                ).order_by(ConversationDB.timestamp.desc()).limit(limit)
                
                result = await session.execute(query)
                conversations = result.scalars().all()
                
                return [self._db_conversation_to_message(conv) for conv in conversations]
                
            except Exception as e:
                raise e
    
    def _db_user_to_profile(self, db_user: User) -> UserProfile:
        """Convert database user to UserProfile"""
        from core.data_models import EducationLevel, CareerStage
        
        return UserProfile(
            user_id=db_user.user_id,
            name=db_user.name,
            email=db_user.email,
            age=db_user.age,
            location=db_user.location,
            education_level=EducationLevel(db_user.education_level) if db_user.education_level else None,
            career_stage=CareerStage(db_user.career_stage) if db_user.career_stage else None,
            career_goals=db_user.career_goals or [],
            values=db_user.values or [],
            preferred_work_environment=db_user.preferred_work_environment or [],
            created_at=db_user.created_at,
            updated_at=db_user.updated_at
        )
    
    def _db_conversation_to_message(self, db_conv: ConversationDB) -> ConversationMessage:
        """Convert database conversation to ConversationMessage"""
        return ConversationMessage(
            message_id=db_conv.message_id,
            user_id=db_conv.user_id,
            agent_name=db_conv.agent_name,
            user_message=db_conv.user_message,
            agent_response=db_conv.agent_response,
            context=db_conv.context or {},
            metadata=db_conv.conversation_metadata or {},
            confidence=db_conv.confidence,
            processing_time_ms=db_conv.processing_time_ms,
            timestamp=db_conv.timestamp
        )
    
    async def save_questionnaire_results(self, user_id: str, results: Dict[str, Any]):
        """Save questionnaire results and mark as completed"""
        async with self.db_manager.get_session() as session:
            try:
                db_user = await session.get(User, user_id)
                if not db_user:
                    raise ValueError(f"User {user_id} not found")
                
                # Update user with questionnaire results
                db_user.questionnaire_completed = True
                db_user.questionnaire_responses = results
                
                # Extract and save insights
                analysis = results.get("analysis", {})
                db_user.personality_insights = analysis.get("personality_insights")
                db_user.interest_insights = analysis.get("interest_insights")
                db_user.updated_at = datetime.utcnow()
                
                await session.commit()
                return True
                
            except Exception as e:
                await session.rollback()
                raise e


# Global database manager instance
db_manager = DatabaseManager()

async def get_database() -> DatabaseManager:
    """Dependency to get database manager"""
    if not db_manager.engine:
        await db_manager.initialize()
    return db_manager

async def get_user_repository() -> UserRepository:
    """Dependency to get user repository"""
    db = await get_database()
    return UserRepository(db)
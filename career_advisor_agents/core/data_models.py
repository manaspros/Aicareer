from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional, Union
from datetime import datetime, date
from enum import Enum


class PersonalityType(str, Enum):
    OPENNESS = "openness"
    CONSCIENTIOUSNESS = "conscientiousness"
    EXTRAVERSION = "extraversion"
    AGREEABLENESS = "agreeableness"
    NEUROTICISM = "neuroticism"


class RIASECType(str, Enum):
    REALISTIC = "realistic"
    INVESTIGATIVE = "investigative"
    ARTISTIC = "artistic"
    SOCIAL = "social"
    ENTERPRISING = "enterprising"
    CONVENTIONAL = "conventional"


class SkillLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class CareerStage(str, Enum):
    STUDENT = "student"
    ENTRY_LEVEL = "entry_level"
    MID_CAREER = "mid_career"
    SENIOR_LEVEL = "senior_level"
    EXECUTIVE = "executive"


class EducationLevel(str, Enum):
    HIGH_SCHOOL = "high_school"
    ASSOCIATES = "associates"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    PHD = "phd"
    PROFESSIONAL = "professional"


class PersonalityAssessment(BaseModel):
    openness: float = Field(..., ge=0, le=100, description="Openness to experience score")
    conscientiousness: float = Field(..., ge=0, le=100, description="Conscientiousness score")
    extraversion: float = Field(..., ge=0, le=100, description="Extraversion score")
    agreeableness: float = Field(..., ge=0, le=100, description="Agreeableness score")
    neuroticism: float = Field(..., ge=0, le=100, description="Neuroticism score")
    assessment_date: datetime = Field(default_factory=datetime.now)


class InterestAssessment(BaseModel):
    realistic: float = Field(..., ge=0, le=100, description="Realistic interest score")
    investigative: float = Field(..., ge=0, le=100, description="Investigative interest score")
    artistic: float = Field(..., ge=0, le=100, description="Artistic interest score")
    social: float = Field(..., ge=0, le=100, description="Social interest score")
    enterprising: float = Field(..., ge=0, le=100, description="Enterprising interest score")
    conventional: float = Field(..., ge=0, le=100, description="Conventional interest score")
    assessment_date: datetime = Field(default_factory=datetime.now)
    
    @property
    def top_interests(self) -> List[str]:
        scores = {
            "realistic": self.realistic,
            "investigative": self.investigative,
            "artistic": self.artistic,
            "social": self.social,
            "enterprising": self.enterprising,
            "conventional": self.conventional
        }
        return sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:3]


class Skill(BaseModel):
    name: str
    category: str
    level: SkillLevel
    years_experience: Optional[float] = 0.0
    certifications: List[str] = []
    last_updated: datetime = Field(default_factory=datetime.now)


class UserProfile(BaseModel):
    user_id: str
    name: str
    email: str
    age: Optional[int] = None
    location: Optional[str] = None
    education_level: Optional[EducationLevel] = None
    career_stage: Optional[CareerStage] = None
    
    personality: Optional[PersonalityAssessment] = None
    interests: Optional[InterestAssessment] = None
    skills: List[Skill] = []
    
    # Questionnaire and personalization fields
    questionnaire_completed: bool = False
    questionnaire_responses: Optional[Dict[str, Any]] = None
    personality_insights: Optional[Dict[str, Any]] = None
    interest_insights: Optional[Dict[str, Any]] = None
    
    career_goals: List[str] = []
    values: List[str] = []
    preferred_work_environment: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        use_enum_values = True


class CareerRecommendation(BaseModel):
    title: str
    description: str
    industry: str
    match_score: float = Field(..., ge=0, le=100)
    
    required_skills: List[str] = []
    preferred_skills: List[str] = []
    education_requirements: List[str] = []
    
    salary_range: Optional[Dict[str, Union[int, str]]] = None
    growth_outlook: Optional[str] = None
    work_environment: List[str] = []
    
    reasoning: str
    recommended_actions: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.now)


class LearningPath(BaseModel):
    skill_name: str
    current_level: SkillLevel
    target_level: SkillLevel
    estimated_duration_weeks: int
    
    courses: List[Dict[str, Any]] = []
    milestones: List[Dict[str, Any]] = []
    resources: List[Dict[str, Any]] = []
    
    prerequisites: List[str] = []
    next_skills: List[str] = []
    
    created_at: datetime = Field(default_factory=datetime.now)


class SkillAssessmentResult(BaseModel):
    user_id: str
    skill_name: str
    assessed_level: SkillLevel
    confidence_score: float = Field(..., ge=0, le=100)
    
    strengths: List[str] = []
    improvement_areas: List[str] = []
    recommendations: List[str] = []
    
    assessment_method: str
    assessment_date: datetime = Field(default_factory=datetime.now)


class ProgressUpdate(BaseModel):
    user_id: str
    skill_name: Optional[str] = None
    goal_name: Optional[str] = None
    
    progress_percentage: float = Field(..., ge=0, le=100)
    milestones_completed: List[str] = []
    current_activities: List[str] = []
    
    achievements: List[str] = []
    challenges: List[str] = []
    next_steps: List[str] = []
    
    notes: Optional[str] = None
    date_recorded: datetime = Field(default_factory=datetime.now)


class OpportunityMatch(BaseModel):
    title: str
    company: str
    location: str
    type: str  # internship, job, volunteer
    
    description: str
    requirements: List[str] = []
    preferred_qualifications: List[str] = []
    
    match_score: float = Field(..., ge=0, le=100)
    skill_alignment: Dict[str, float] = {}
    
    application_deadline: Optional[date] = None
    application_url: Optional[str] = None
    
    salary_range: Optional[Dict[str, Union[int, str]]] = None
    benefits: List[str] = []
    
    matching_reasons: List[str] = []
    growth_potential: Optional[str] = None
    
    created_at: datetime = Field(default_factory=datetime.now)


class ConversationMessage(BaseModel):
    message_id: str
    user_id: str
    agent_name: str
    
    user_message: str
    agent_response: str
    
    context: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    
    confidence: float = Field(default=0.0, ge=0, le=1)
    processing_time_ms: Optional[int] = None
    
    timestamp: datetime = Field(default_factory=datetime.now)


class UserGoal(BaseModel):
    user_id: str
    title: str
    description: str
    category: str  # career, skill, education, etc.
    
    target_date: Optional[date] = None
    priority: int = Field(default=5, ge=1, le=10)
    
    milestones: List[Dict[str, Any]] = []
    success_metrics: List[str] = []
    
    status: str = Field(default="active")  # active, completed, paused, cancelled
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class IndustryTrend(BaseModel):
    industry: str
    trend_name: str
    description: str
    
    impact_level: str  # high, medium, low
    time_horizon: str  # short, medium, long term
    
    affected_roles: List[str] = []
    emerging_skills: List[str] = []
    declining_skills: List[str] = []
    
    source: str
    confidence: float = Field(..., ge=0, le=100)
    
    created_at: datetime = Field(default_factory=datetime.now)


class CareerAnalysisRequest(BaseModel):
    user_id: str
    analysis_type: str
    parameters: Dict[str, Any] = {}
    
    
class CareerAnalysisResponse(BaseModel):
    request_id: str
    user_id: str
    analysis_type: str
    
    results: Dict[str, Any]
    recommendations: List[CareerRecommendation] = []
    
    confidence: float = Field(..., ge=0, le=100)
    processing_time_ms: int
    
    created_at: datetime = Field(default_factory=datetime.now)
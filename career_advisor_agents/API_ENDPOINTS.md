# AI Career Advisor - API Endpoints Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required. All endpoints are open for testing.

---

## 🏥 System Health & Information

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-20T10:30:00",
  "services": {
    "database": "connected",
    "agents": 6,
    "llm": "available"
  }
}
```

### List Available Agents
```http
GET /api/system/agents
```

**Response:**
```json
{
  "agents": [
    "career_analyst",
    "skills_assessor", 
    "learning_orchestrator",
    "progress_monitor",
    "opportunity_scout",
    "mentor_bot"
  ],
  "total_count": 6
}
```

### System Performance Metrics
```http
GET /api/system/metrics
```

**Response:**
```json
{
  "agent_metrics": {
    "career_analyst": {
      "total_interactions": 15,
      "avg_response_time": 1.2,
      "avg_confidence": 0.85
    }
  },
  "system_status": "operational",
  "timestamp": "2024-01-20T10:30:00"
}
```

---

## 👤 User Management

### Register New User
```http
POST /api/users/register
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "age": 25,
  "location": "New York, NY",
  "education_level": "bachelors",
  "career_stage": "student"
}
```

**Response:**
```json
{
  "user_id": "uuid-generated-id",
  "message": "User registered successfully",
  "status": "success"
}
```

### Get User Profile
```http
GET /api/users/{user_id}/profile
```

**Response:**
```json
{
  "user_id": "user-uuid",
  "name": "John Doe",
  "email": "john@example.com",
  "age": 25,
  "location": "New York, NY",
  "education_level": "bachelors",
  "career_stage": "student",
  "career_goals": [],
  "values": [],
  "preferred_work_environment": [],
  "created_at": "2024-01-20T10:00:00",
  "updated_at": "2024-01-20T10:00:00"
}
```

### Update User Profile
```http
PUT /api/users/{user_id}/profile
```

**Request Body:**
```json
{
  "career_goals": ["become a data scientist", "work in tech"],
  "values": ["work-life balance", "innovation", "growth"],
  "preferred_work_environment": ["remote", "collaborative", "fast-paced"]
}
```

### Create User Goal
```http
POST /api/users/{user_id}/goals
```

**Request Body:**
```json
{
  "title": "Learn Python Programming",
  "description": "Master Python for data science applications",
  "category": "skill_development",
  "target_date": "2024-06-30",
  "priority": 8,
  "milestones": [
    {"milestone": "Complete Python basics", "target_date": "2024-02-28"},
    {"milestone": "Build first project", "target_date": "2024-04-30"}
  ],
  "success_metrics": ["Complete 3 projects", "Pass certification exam"]
}
```

### Get User Goals
```http
GET /api/users/{user_id}/goals?status=active
```

**Response:**
```json
{
  "user_id": "user-uuid",
  "goals": [
    {
      "goal_id": "goal-uuid",
      "title": "Learn Python Programming",
      "description": "Master Python for data science applications",
      "category": "skill_development",
      "status": "active",
      "progress_percentage": 35.0,
      "target_date": "2024-06-30",
      "created_at": "2024-01-15"
    }
  ],
  "total_count": 1
}
```

---

## 🤖 AI Agent Interactions

### Career Analysis
```http
POST /api/agents/career-analysis
```

**Request Body:**
```json
{
  "user_id": "user-uuid",
  "analysis_type": "personality_assessment",
  "parameters": {
    "assessment_responses": [
      "I enjoy working on creative projects",
      "I like to organize and plan things carefully",
      "I prefer working in teams rather than alone",
      "I handle stress by breaking problems into smaller parts",
      "My greatest strength is analytical thinking"
    ]
  }
}
```

**Response:**
```json
{
  "request_id": "analysis-uuid",
  "user_id": "user-uuid",
  "analysis_type": "personality_assessment",
  "results": {
    "personality_assessment": {
      "openness": 78.5,
      "conscientiousness": 85.2,
      "extraversion": 65.0,
      "agreeableness": 72.1,
      "neuroticism": 42.3
    }
  },
  "confidence": 88.5,
  "processing_time_ms": 2500,
  "created_at": "2024-01-20T10:30:00"
}
```

### Career Counseling Chat
```http
POST /api/agents/counseling/chat
```

**Request Body:**
```json
{
  "user_id": "user-uuid",
  "message": "I'm feeling overwhelmed about choosing a career path. I'm interested in both technology and healthcare but don't know which direction to pursue."
}
```

**Response:**
```json
{
  "response": "I understand this can feel overwhelming, and that's completely normal. The intersection of technology and healthcare is actually one of the most exciting and growing areas...",
  "sentiment_analysis": {
    "sentiment_score": -0.3,
    "confidence_level": 0.8,
    "primary_emotion": "uncertain",
    "emotional_indicators": {
      "positive_signals": 1,
      "negative_signals": 2,
      "uncertainty_signals": 3
    }
  },
  "follow_up_actions": [
    "emotional_support_check_in",
    "clarifying_questions",
    "exploration_exercises"
  ],
  "conversation_metadata": {
    "emotional_support_level": 0.7,
    "information_density": 0.6,
    "personalization_level": 0.8
  }
}
```

### Get Career Recommendations
```http
GET /api/agents/recommendations/{user_id}
```

**Response:**
```json
{
  "recommendations": [
    {
      "title": "Data Scientist",
      "industry": "Technology",
      "match_score": 92.5,
      "description": "Analyze complex data to extract insights...",
      "required_skills": ["Python", "Statistics", "Machine Learning"],
      "salary_range": {"min": 80000, "max": 150000},
      "growth_outlook": "Excellent - 31% growth expected",
      "reasoning": "Strong match with analytical thinking and interest in technology"
    }
  ],
  "confidence": 0.88,
  "explanation": "Based on your personality assessment and stated interests..."
}
```

### Skills Assessment
```http
POST /api/agents/skills-assessment
```

**Request Body:**
```json
{
  "user_id": "user-uuid",
  "skills": ["Python", "Communication", "Problem Solving"]
}
```

**Response:**
```json
{
  "user_id": "user-uuid",
  "assessment_results": [
    {
      "user_id": "user-uuid",
      "skill_name": "Python",
      "assessed_level": "intermediate",
      "confidence_score": 75.0,
      "strengths": ["Quick learner", "Problem solver"],
      "improvement_areas": ["Advanced techniques", "Best practices"],
      "recommendations": [
        "Practice Python through hands-on projects",
        "Take advanced Python course"
      ],
      "assessment_method": "interactive_questionnaire"
    }
  ],
  "assessment_date": "2024-01-20T10:30:00",
  "next_steps": [
    "Review assessment results",
    "Create learning plan for improvement areas"
  ]
}
```

### Create Learning Path
```http
POST /api/agents/learning-path
```

**Request Body:**
```json
{
  "user_id": "user-uuid",
  "target_skill": "Machine Learning",
  "current_level": "beginner",
  "target_level": "intermediate"
}
```

**Response:**
```json
{
  "user_id": "user-uuid",
  "learning_path": {
    "skill_name": "Machine Learning",
    "current_level": "beginner",
    "target_level": "intermediate",
    "estimated_duration_weeks": 12,
    "learning_modules": [
      {
        "module_id": 1,
        "title": "Machine Learning Fundamentals",
        "duration_weeks": 3,
        "resources": [
          {"type": "course", "name": "Introduction to Machine Learning"},
          {"type": "book", "name": "ML for Beginners"}
        ]
      }
    ],
    "milestones": [
      {"week": 3, "milestone": "Complete ML basics"},
      {"week": 12, "milestone": "Build ML portfolio project"}
    ]
  },
  "path_id": "path-uuid",
  "created_date": "2024-01-20T10:30:00",
  "status": "active"
}
```

### Find Opportunities
```http
GET /api/agents/opportunities/{user_id}?opportunity_type=internship&location=remote
```

**Response:**
```json
{
  "user_id": "user-uuid",
  "opportunities": [
    {
      "opportunity_id": "opp-uuid",
      "title": "Data Science Intern",
      "company": "TechCorp",
      "location": "Remote",
      "type": "internship",
      "description": "Work with our data science team on real-world projects",
      "requirements": ["Python", "Statistics", "Machine Learning basics"],
      "match_score": 85.0,
      "application_deadline": "2024-03-15",
      "application_url": "https://example.com/apply",
      "matching_reasons": [
        "Strong match with Python skills",
        "Aligns with data science career goal"
      ]
    }
  ],
  "total_matches": 1,
  "search_criteria": {
    "type": "internship",
    "location": "remote"
  }
}
```

---

## 📊 Analytics & Insights

### Career Trends Analysis
```http
GET /api/analytics/career-trends?industry=technology&role=software%20engineer
```

**Response:**
```json
{
  "role": "software engineer",
  "industry": "technology",
  "location": "national",
  "analysis_date": "2024-01-20T10:30:00",
  "detailed_analyses": {
    "job_growth": {
      "prediction": "Strong growth expected in technology - software engineer roles",
      "confidence": 0.85,
      "supporting_data": {
        "growth_rate": 15.2,
        "industry": "technology"
      }
    },
    "salary_trends": {
      "prediction": "Strong upward salary trend for software engineer in technology",
      "confidence": 0.80,
      "supporting_data": {
        "current_salary": 110500,
        "projected_salary": 141456,
        "growth_rate": 6.8
      }
    },
    "automation_impact": {
      "prediction": "Very Low automation risk for software engineer in technology",
      "confidence": 0.75,
      "supporting_data": {
        "automation_risk": 0.204
      }
    }
  },
  "overall_outlook": {
    "overall_rating": "Very Positive",
    "summary": "Excellent career prospects with strong growth potential",
    "confidence": 0.8
  },
  "recommendations": [
    "Excellent earning potential in this field",
    "Maintain momentum by setting stretch goals"
  ]
}
```

### Skill Demand Analysis
```http
GET /api/analytics/skill-demand?skills=Python,Machine%20Learning,JavaScript
```

**Response:**
```json
{
  "skills_analyzed": ["Python", "Machine Learning", "JavaScript"],
  "predictions": [
    {
      "skill": "Machine Learning",
      "prediction": "Very high demand growth for Machine Learning",
      "confidence": 0.85,
      "time_horizon": "short",
      "recommendations": [
        "Prioritize developing this skill immediately",
        "Seek certification or formal training"
      ],
      "implications": [
        "High growth potential with relatively low competition",
        "Excellent opportunity for career advancement"
      ]
    },
    {
      "skill": "Python",
      "prediction": "Very high demand growth for Python",
      "confidence": 0.85,
      "time_horizon": "short",
      "recommendations": [
        "Prioritize developing this skill immediately",
        "Build portfolio projects demonstrating this skill"
      ],
      "implications": [
        "High growth potential with relatively low competition",
        "Potential for salary premium"
      ]
    }
  ],
  "analysis_date": "2024-01-20T10:30:00"
}
```

### Market Predictions
```http
GET /api/analytics/market-predictions?industry=technology&analysis_type=disruption
```

**Response:**
```json
{
  "industry": "technology",
  "disruption_risk_level": "Very High",
  "disruption_score": 0.8,
  "description": "Industry facing imminent significant disruption",
  "timeline": "2-5 years",
  "key_disruptors": ["AI/ML", "Quantum Computing", "Automation"],
  "detailed_factors": {
    "ai_impact": 0.8,
    "regulatory_risk": 0.4,
    "market_volatility": 0.6,
    "innovation_pace": 0.9
  },
  "implications": [
    "Rapid skill evolution required to stay relevant",
    "New job categories will emerge while others disappear"
  ],
  "preparation_strategies": [
    "Develop skills in emerging technologies immediately",
    "Build a diverse skill set to increase adaptability"
  ]
}
```

### Industry Insights
```http
GET /api/analytics/industry-insights/{industry}
```

**Example: GET /api/analytics/industry-insights/technology**

**Response:**
```json
{
  "industry": "technology",
  "overview": {
    "market_size": "$500B globally",
    "growth_rate": "8.2% annually",
    "employment": "2.3M professionals",
    "average_salary": "$75,000 - $150,000"
  },
  "trending_skills": [
    {"skill": "Artificial Intelligence", "demand_growth": 45.2},
    {"skill": "Cloud Computing", "demand_growth": 35.8}
  ],
  "top_companies": [
    {"name": "Google", "employees": "150k+", "rating": 4.5},
    {"name": "Microsoft", "employees": "200k+", "rating": 4.4}
  ],
  "career_paths": [
    {
      "path": "Software Engineer → Senior Engineer → Tech Lead → Engineering Manager",
      "typical_duration": "8-12 years",
      "salary_progression": "$80k → $120k → $160k → $200k+"
    }
  ],
  "future_outlook": {
    "automation_impact": "Low to Medium",
    "growth_projection": "Strong growth expected through 2030",
    "key_challenges": ["Skills shortage", "Rapid technology change"],
    "opportunities": ["AI/ML integration", "Remote work normalization"]
  }
}
```

---

## 📈 Progress Tracking

### Get User Progress
```http
GET /api/progress/{user_id}
```

**Response:**
```json
{
  "user_id": "user-uuid",
  "overall_progress": {
    "career_goals_completion": 25.0,
    "skills_development_progress": 40.0,
    "learning_activities_completed": 12,
    "total_activities_planned": 30,
    "streak_days": 7,
    "last_activity_date": "2024-01-20"
  },
  "active_goals": [
    {
      "goal_id": "goal-uuid",
      "title": "Learn Python Programming",
      "progress_percentage": 35.0,
      "days_remaining": 160,
      "status": "on_track"
    }
  ],
  "recent_achievements": [
    "Completed Python Basics Course",
    "Built first data analysis project"
  ],
  "upcoming_milestones": [
    "Complete intermediate Python course",
    "Start machine learning fundamentals"
  ]
}
```

### Update Progress
```http
POST /api/progress/{user_id}/update
```

**Request Body:**
```json
{
  "skill_name": "Python",
  "progress_percentage": 45.0,
  "milestones_completed": ["Completed Python basics", "Built first project"],
  "current_activities": ["Working on data analysis project"],
  "achievements": ["Solved 50 coding challenges"],
  "challenges": ["Understanding advanced concepts"],
  "next_steps": ["Start web development with Flask"],
  "notes": "Making good progress, enjoying the practical projects"
}
```

**Response:**
```json
{
  "message": "Progress updated successfully",
  "update_id": "update-uuid",
  "status": "success",
  "timestamp": "2024-01-20T10:30:00"
}
```

---

## 💬 Conversation History

### Get Conversation History
```http
GET /api/conversations/{user_id}?limit=20
```

**Response:**
```json
{
  "user_id": "user-uuid",
  "conversations": [
    {
      "message_id": "msg-uuid",
      "user_id": "user-uuid",
      "agent_name": "mentor_bot",
      "user_message": "I'm feeling overwhelmed about my career choices",
      "agent_response": "I understand that feeling overwhelmed is completely normal...",
      "context": {"sentiment": "negative"},
      "metadata": {"emotional_support_level": 0.8},
      "confidence": 0.85,
      "processing_time_ms": 1500,
      "timestamp": "2024-01-20T10:30:00"
    }
  ],
  "total_count": 1
}
```

---

## 📝 Testing with Postman

### Collection Setup
1. Create a new Postman collection called "AI Career Advisor"
2. Add environment variables:
   - `baseUrl`: `http://localhost:8000`
   - `userId`: (will be set after user registration)

### Test Flow
1. **Health Check** → GET `/health`
2. **Register User** → POST `/api/users/register`
3. **Career Counseling** → POST `/api/agents/counseling/chat`
4. **Career Analysis** → POST `/api/agents/career-analysis`
5. **Get Recommendations** → GET `/api/agents/recommendations/{userId}`
6. **Skills Assessment** → POST `/api/agents/skills-assessment`
7. **Analytics** → GET `/api/analytics/career-trends`

### Error Responses
All endpoints return standard HTTP status codes:
- `200`: Success
- `400`: Bad Request (invalid input)
- `404`: Not Found (user/resource not found)
- `422`: Validation Error (Pydantic validation failed)
- `500`: Internal Server Error

**Error Response Format:**
```json
{
  "detail": "Error message description",
  "error": "Technical error details",
  "status_code": 500
}
```

---

## 🔐 Notes

- No authentication required for testing
- All user data is stored in local SQLite database
- Requires Google Gemini API key in `.env` file
- Server must be running on `http://localhost:8000`
- All timestamps are in ISO 8601 format
- UUIDs are automatically generated for IDs
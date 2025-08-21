# AI Career & Skill Development Advisor Agent System

A comprehensive multi-agent AI system built with LangChain and Google Gemini 2.5 Flash that helps students and professionals plan their careers, develop skills, and find opportunities.

## 🌟 Features

### Core Agents
- **Career Analyst Agent**: Personality assessment (Big Five), interest analysis (Holland Code/RIASEC), and career recommendations
- **Skills Assessor Agent**: Comprehensive skill evaluation, gap analysis, and development planning
- **Learning Orchestrator Agent**: Personalized learning paths, resource curation, and schedule optimization
- **Progress Monitor Agent**: Learning progress tracking, goal management, and motivation support
- **Opportunity Scout Agent**: Job/internship matching, application tracking, and networking guidance
- **Mentor Bot Agent**: Emotional support, career guidance, and motivational coaching

### Key Capabilities
- **Natural Language Career Counseling**: Conversational AI with sentiment analysis and emotional intelligence
- **Predictive Analytics**: Industry trends, job market analysis, and skill demand forecasting
- **Personalized Recommendations**: AI-driven career paths based on individual profiles and market data
- **Comprehensive Database**: Career information, skills taxonomy, and industry trends
- **RESTful API**: Full-featured API with FastAPI for integration with frontend applications

## 🏗️ Architecture

```
career_advisor_agents/
├── agents/                 # Specialized AI agents
│   ├── career_analyst.py      # Personality & career analysis
│   ├── skills_assessor.py     # Skill evaluation & gap analysis
│   ├── learning_orchestrator.py # Learning path creation
│   ├── progress_monitor.py     # Progress tracking & motivation
│   ├── opportunity_scout.py    # Job matching & applications
│   └── mentor_bot.py          # Emotional support & guidance
├── core/                   # Core framework
│   ├── agent_framework.py     # Base agent classes
│   ├── llm_config.py          # Gemini 2.5 Flash configuration
│   └── data_models.py         # Pydantic data models
├── services/              # Business logic services
│   ├── career_counseling.py   # NLP counseling service
│   ├── predictive_analytics.py # Market analysis & predictions
│   └── database.py            # Database management
├── api/                   # FastAPI application
│   ├── main.py               # API server & endpoints
│   └── routes.py             # Additional route definitions
├── data/                  # Static data files
│   ├── career_data.json      # Career paths & requirements
│   ├── skills_taxonomy.json  # Skills classification & relationships
│   └── industry_trends.json  # Market trends & predictions
└── tests/                 # Test suites
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Google Gemini API key
- Optional: PostgreSQL for production

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd career_advisor_agents
```

2. **Create virtual environment**
```bash
python -m venv career_advisor_env
source career_advisor_env/bin/activate  # Linux/Mac
# or
career_advisor_env\Scripts\activate  # Windows
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. **Run the application**
```bash
cd career_advisor_agents
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📋 API Endpoints

### User Management
- `POST /api/users/register` - Register new user
- `GET /api/users/{user_id}/profile` - Get user profile
- `PUT /api/users/{user_id}/profile` - Update user profile
- `POST /api/users/{user_id}/goals` - Create user goals
- `GET /api/users/{user_id}/goals` - Get user goals

### Agent Interactions
- `POST /api/agents/career-analysis` - Career analysis request
- `POST /api/agents/counseling/chat` - Career counseling chat
- `GET /api/agents/recommendations/{user_id}` - Get career recommendations
- `POST /api/agents/skills-assessment` - Conduct skills assessment
- `POST /api/agents/learning-path` - Create learning path
- `GET /api/agents/opportunities/{user_id}` - Find matching opportunities

### Analytics & Insights
- `GET /api/analytics/career-trends` - Career trend analysis
- `GET /api/analytics/skill-demand` - Skill demand analysis
- `GET /api/analytics/market-predictions` - Market predictions
- `GET /api/analytics/industry-insights/{industry}` - Industry insights

### Progress Tracking
- `GET /api/progress/{user_id}` - Get user progress
- `POST /api/progress/{user_id}/update` - Update progress

### System Information
- `GET /health` - Health check
- `GET /api/system/agents` - List available agents
- `GET /api/system/metrics` - System performance metrics

## 🔧 Configuration

### Environment Variables

Key environment variables (see `.env.example` for complete list):

```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key
DATABASE_URL=sqlite:///./career_advisor.db

# Optional but recommended
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langchain_api_key
SECRET_KEY=your_secret_key

# External APIs (optional)
BLS_API_KEY=your_bls_api_key
LINKEDIN_CLIENT_ID=your_linkedin_id
```

### Database Setup

**Development (SQLite)**
```bash
# Uses SQLite by default - no setup required
DATABASE_URL=sqlite:///./career_advisor.db
```

**Production (PostgreSQL)**
```bash
# Install PostgreSQL and create database
createdb career_advisor_db

# Update environment
DATABASE_URL=postgresql+asyncpg://username:password@localhost/career_advisor_db
```

## 🧪 Testing

Run the test suite:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ --cov=career_advisor_agents --cov-report=html
```

## 📊 Usage Examples

### Career Analysis Example
```python
import requests

# Register user
user_data = {
    "name": "John Doe",
    "email": "john@example.com",
    "education_level": "bachelors",
    "career_stage": "student"
}
response = requests.post("http://localhost:8000/api/users/register", json=user_data)
user_id = response.json()["user_id"]

# Request career analysis
analysis_request = {
    "user_id": user_id,
    "analysis_type": "personality_assessment",
    "parameters": {
        "assessment_responses": [
            "I enjoy working on creative projects",
            "I like to organize and plan things carefully",
            "I prefer working in teams rather than alone"
        ]
    }
}
response = requests.post("http://localhost:8000/api/agents/career-analysis", json=analysis_request)
```

### Career Counseling Chat
```python
counseling_request = {
    "user_id": user_id,
    "message": "I'm feeling overwhelmed about choosing a career path. I'm interested in both technology and healthcare but don't know which direction to pursue."
}
response = requests.post("http://localhost:8000/api/agents/counseling/chat", json=counseling_request)
```

## 🔮 Advanced Features

### Predictive Analytics
- **Job Market Trends**: Analysis of growth industries and emerging roles
- **Skill Demand Forecasting**: Predictions of future skill requirements
- **Salary Trend Analysis**: Compensation projections by role and industry
- **Automation Impact Assessment**: Risk analysis for job displacement

### Personalization
- **Adaptive Learning**: AI learns from user interactions to improve recommendations
- **Context Awareness**: Considers user's background, goals, and constraints
- **Multi-Modal Assessment**: Combines personality, interests, skills, and values
- **Dynamic Goal Adjustment**: Updates recommendations as user progresses

### Integration Capabilities
- **External APIs**: BLS, LinkedIn, Glassdoor (when available)
- **Learning Platforms**: Integration-ready for Coursera, Udemy, etc.
- **ATS Systems**: Structured data for Applicant Tracking Systems
- **Career Centers**: Institutional deployment support

## 🚀 Deployment

### Development
```bash
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production
```bash
# Using Gunicorn
gunicorn api.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Using Docker (create Dockerfile)
docker build -t career-advisor .
docker run -p 8000:8000 career-advisor
```

### Cloud Deployment
The system is designed for easy deployment on:
- **Google Cloud Run** (recommended for Gemini integration)
- **AWS Lambda** with API Gateway
- **Azure Container Instances**
- **Heroku** or similar PaaS platforms

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain** team for the excellent agent framework
- **Google** for Gemini 2.5 Flash API access
- **FastAPI** team for the modern web framework
- **OpenAI** for inspiration and research in AI agents
- Career development research from various academic institutions

## 🆘 Support

- **Documentation**: Check the `/docs` endpoint when running
- **Issues**: Report bugs via GitHub Issues
- **Discussions**: Join the community discussions
- **Email**: Contact the development team

## 🗺️ Roadmap

- [ ] **Mobile App Integration**: React Native/Flutter SDK
- [ ] **Advanced NLP**: Custom domain-specific language models
- [ ] **Real-time Collaboration**: Multi-user career planning sessions
- [ ] **AR/VR Integration**: Immersive career exploration experiences
- [ ] **Blockchain Credentials**: Verifiable skill and achievement records
- [ ] **Global Localization**: Multi-language and regional job market support

---

Built with ❤️ using LangChain, Google Gemini 2.5 Flash, and FastAPI
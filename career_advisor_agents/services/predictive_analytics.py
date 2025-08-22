from typing import Dict, List, Any, Optional, Tuple
import asyncio
import json
import aiohttp
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from langchain_google_genai import ChatGoogleGenerativeAI

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.data_models import IndustryTrend, CareerRecommendation


class TrendType(str, Enum):
    JOB_GROWTH = "job_growth"
    SKILL_DEMAND = "skill_demand"
    SALARY_TRENDS = "salary_trends"
    INDUSTRY_DISRUPTION = "industry_disruption"
    REMOTE_WORK = "remote_work"
    AUTOMATION_IMPACT = "automation_impact"


@dataclass
class PredictionResult:
    trend_type: TrendType
    prediction: str
    confidence: float
    time_horizon: str  # "short", "medium", "long"
    supporting_data: Dict[str, Any]
    implications: List[str]
    recommendations: List[str]


class DataSourceManager:
    """Manages connections to external data sources"""
    
    def __init__(self):
        self.bls_base_url = "https://api.bls.gov/publicAPI/v2/timeseries/data/"
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get_bls_employment_data(self, series_id: str, years: List[int]) -> Dict[str, Any]:
        """Fetch employment data from Bureau of Labor Statistics API"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            payload = {
                "seriesid": [series_id],
                "startyear": str(min(years)),
                "endyear": str(max(years))
            }
            
            async with self.session.post(self.bls_base_url, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {"status": "error", "message": f"HTTP {response.status}"}
                    
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def get_simulated_industry_data(self, industry: str) -> Dict[str, Any]:
        """Simulate industry data (replace with real APIs in production)"""
        # This simulates data that would come from sources like:
        # - LinkedIn Economic Graph
        # - Indeed Job Trends
        # - Glassdoor salary data
        # - Industry reports
        
        simulated_data = {
            "technology": {
                "job_growth_rate": 15.2,
                "average_salary_change": 8.5,
                "top_skills_demand": ["Python", "Machine Learning", "Cloud Computing", "DevOps"],
                "automation_risk": "low",
                "remote_work_adoption": 0.75,
                "market_volatility": "medium"
            },
            "healthcare": {
                "job_growth_rate": 12.1,
                "average_salary_change": 5.2,
                "top_skills_demand": ["Telemedicine", "Data Analysis", "Patient Care", "Compliance"],
                "automation_risk": "low",
                "remote_work_adoption": 0.35,
                "market_volatility": "low"
            },
            "finance": {
                "job_growth_rate": 6.8,
                "average_salary_change": 4.1,
                "top_skills_demand": ["FinTech", "Risk Analysis", "Compliance", "Digital Banking"],
                "automation_risk": "medium",
                "remote_work_adoption": 0.65,
                "market_volatility": "high"
            },
            "education": {
                "job_growth_rate": 3.2,
                "average_salary_change": 2.8,
                "top_skills_demand": ["Online Teaching", "Educational Technology", "Curriculum Design"],
                "automation_risk": "low",
                "remote_work_adoption": 0.45,
                "market_volatility": "low"
            },
            "manufacturing": {
                "job_growth_rate": 1.1,
                "average_salary_change": 3.2,
                "top_skills_demand": ["Automation", "Quality Control", "Lean Manufacturing", "IoT"],
                "automation_risk": "high",
                "remote_work_adoption": 0.15,
                "market_volatility": "medium"
            }
        }
        
        return simulated_data.get(industry.lower(), {
            "job_growth_rate": 5.0,
            "average_salary_change": 3.0,
            "top_skills_demand": ["Communication", "Problem Solving", "Adaptability"],
            "automation_risk": "medium",
            "remote_work_adoption": 0.40,
            "market_volatility": "medium"
        })


class TrendAnalyzer:
    """Analyzes trends and makes predictions about career markets using AI"""
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.data_source = DataSourceManager()
        
    async def analyze_job_growth_trends(self, industry: str, role: str) -> PredictionResult:
        """Analyze job growth trends for specific industry/role"""
        
        async with self.data_source as ds:
            industry_data = await ds.get_simulated_industry_data(industry)
        
        growth_rate = industry_data.get("job_growth_rate", 5.0)
        
        # Determine trend classification
        if growth_rate > 10:
            trend_description = "Strong growth expected"
            confidence = 0.85
        elif growth_rate > 5:
            trend_description = "Moderate growth expected"
            confidence = 0.75
        elif growth_rate > 0:
            trend_description = "Slow growth expected"
            confidence = 0.70
        else:
            trend_description = "Decline or stagnation expected"
            confidence = 0.65
        
        implications = []
        recommendations = []
        
        if growth_rate > 8:
            implications.extend([
                "High demand for qualified professionals",
                "Competitive salaries and benefits",
                "Multiple career advancement opportunities"
            ])
            recommendations.extend([
                "Consider entering this field soon to capitalize on growth",
                "Develop specialized skills to stand out in competitive market",
                "Build professional network in this expanding industry"
            ])
        elif growth_rate < 2:
            implications.extend([
                "Limited new job opportunities",
                "Potential salary stagnation",
                "Increased competition for existing positions"
            ])
            recommendations.extend([
                "Consider developing transferable skills for related fields",
                "Focus on becoming indispensable in current role",
                "Explore adjacent industries with better growth prospects"
            ])
        
        return PredictionResult(
            trend_type=TrendType.JOB_GROWTH,
            prediction=f"{trend_description} in {industry} - {role} roles",
            confidence=confidence,
            time_horizon="medium",
            supporting_data={
                "growth_rate": growth_rate,
                "industry": industry,
                "data_source": "simulated_industry_analysis"
            },
            implications=implications,
            recommendations=recommendations
        )
    
    async def analyze_skill_demand_trends(self, skills: List[str]) -> List[PredictionResult]:
        """Analyze demand trends for specific skills using AI (parallel processing)"""
        async def analyze_single_skill(skill: str) -> PredictionResult:
            try:
                # Create AI prompt for skill analysis
                prompt = f"""As a career market analyst with access to current job market data and industry trends, analyze the demand outlook for the skill "{skill}".

Please provide:
1. Current market demand level (high/moderate/low)
2. Growth trajectory over next 2-3 years
3. Market saturation level
4. Industry applications where this skill is most valuable
5. Specific recommendations for someone learning this skill
6. Career opportunities and salary potential

Consider factors like:
- Industry automation trends
- Remote work impact
- Emerging technologies
- Economic factors
- Student and career-transition perspectives

Provide a realistic, data-informed analysis focused on helping students and career changers make informed decisions."""

                # Call Google Gemini AI
                # Use timeout for AI analysis (60 seconds)
                import asyncio
                from langchain.schema import HumanMessage
                response = await asyncio.wait_for(
                    self.llm.ainvoke([HumanMessage(content=prompt)]),
                    timeout=60.0
                )
                ai_analysis = response.content if hasattr(response, 'content') else str(response)
                
                # Extract key insights from AI response
                confidence = self._calculate_analysis_confidence(ai_analysis, skill)
                prediction_text = self._extract_main_prediction(ai_analysis, skill)
                implications = self._extract_implications(ai_analysis)
                recommendations = self._extract_recommendations(ai_analysis)
                time_horizon = self._determine_time_horizon(ai_analysis)
                
                return PredictionResult(
                    trend_type=TrendType.SKILL_DEMAND,
                    prediction=prediction_text,
                    confidence=confidence,
                    time_horizon=time_horizon,
                    supporting_data={
                        "skill": skill,
                        "ai_analysis": ai_analysis,
                        "analysis_date": datetime.now().isoformat()
                    },
                    implications=implications,
                    recommendations=recommendations
                )
                
            except Exception as e:
                # Log the detailed error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Skills analysis failed for '{skill}': {str(e)}")
                logger.error(f"Error type: {type(e).__name__}")
                
                # Enhanced fallback with realistic skill-specific data
                skill_insights = self._get_skill_fallback_data(skill)
                
                return PredictionResult(
                    trend_type=TrendType.SKILL_DEMAND,
                    prediction=skill_insights["prediction"],
                    confidence=skill_insights["confidence"],
                    time_horizon=skill_insights["time_horizon"],
                    supporting_data={"skill": skill, "error": str(e), "fallback": True},
                    implications=skill_insights["implications"],
                    recommendations=skill_insights["recommendations"]
                )
        
        # Process skills in parallel for better performance
        import asyncio
        predictions = await asyncio.gather(
            *[analyze_single_skill(skill) for skill in skills],
            return_exceptions=True
        )
        
        # Handle any exceptions and ensure we have PredictionResult objects
        result_predictions = []
        for i, prediction in enumerate(predictions):
            if isinstance(prediction, Exception):
                # Create enhanced fallback result for exceptions
                skill = skills[i] if i < len(skills) else "unknown"
                skill_insights = self._get_skill_fallback_data(skill)
                result_predictions.append(PredictionResult(
                    trend_type=TrendType.SKILL_DEMAND,
                    prediction=skill_insights["prediction"],
                    confidence=skill_insights["confidence"],
                    time_horizon=skill_insights["time_horizon"],
                    supporting_data={"skill": skill, "error": str(prediction), "fallback": True},
                    implications=skill_insights["implications"],
                    recommendations=skill_insights["recommendations"]
                ))
            else:
                result_predictions.append(prediction)
        
        return result_predictions
    
    def _get_skill_fallback_data(self, skill: str) -> Dict[str, Any]:
        """Provide realistic fallback data for specific skills"""
        skill_lower = skill.lower()
        
        # Enhanced skill-specific insights
        skill_data = {
            "python": {
                "prediction": "High demand with strong growth trajectory",
                "confidence": 0.85,
                "time_horizon": "short",
                "implications": [
                    "Excellent job market opportunities in data science and web development",
                    "Growing demand in AI/ML, automation, and enterprise applications",
                    "Strong salary growth potential across multiple industries"
                ],
                "recommendations": [
                    "Focus on data science libraries (pandas, numpy, scikit-learn)",
                    "Learn web frameworks like Django or FastAPI",
                    "Develop skills in cloud platforms (AWS, Azure, GCP)",
                    "Build a portfolio of data analysis and automation projects"
                ]
            },
            "javascript": {
                "prediction": "Consistently high demand across web and mobile development",
                "confidence": 0.82,
                "time_horizon": "short",
                "implications": [
                    "Essential for frontend and increasingly backend development",
                    "Strong demand in e-commerce, fintech, and SaaS companies",
                    "Evolving ecosystem with new frameworks and tools"
                ],
                "recommendations": [
                    "Master modern frameworks like React, Vue, or Angular",
                    "Learn Node.js for full-stack development",
                    "Understand TypeScript for enterprise applications",
                    "Stay updated with modern JavaScript features (ES6+)"
                ]
            },
            "react": {
                "prediction": "Very high demand for frontend development roles",
                "confidence": 0.88,
                "time_horizon": "short",
                "implications": [
                    "Dominant frontend framework with extensive job opportunities",
                    "High salaries in tech companies and startups",
                    "Strong ecosystem with excellent tooling and community support"
                ],
                "recommendations": [
                    "Learn React hooks and modern patterns",
                    "Understand state management (Redux, Context API)",
                    "Practice with Next.js for full-stack React applications",
                    "Build responsive, accessible user interfaces"
                ]
            },
            "java": {
                "prediction": "Stable high demand in enterprise environments",
                "confidence": 0.80,
                "time_horizon": "medium",
                "implications": [
                    "Strong demand in large enterprises and financial institutions",
                    "Excellent career stability and growth opportunities",
                    "Evolving with cloud-native and microservices architectures"
                ],
                "recommendations": [
                    "Learn Spring Boot for modern Java development",
                    "Understand microservices and cloud deployment",
                    "Focus on enterprise integration patterns",
                    "Develop skills in containerization (Docker, Kubernetes)"
                ]
            }
        }
        
        # Return specific data or generic fallback
        if skill_lower in skill_data:
            return skill_data[skill_lower]
        else:
            # Generic fallback for unlisted skills
            return {
                "prediction": f"Moderate to high demand anticipated for {skill} skills",
                "confidence": 0.65,
                "time_horizon": "medium",
                "implications": [
                    f"{skill} shows potential for career growth",
                    "Market demand varies by industry and location",
                    "Continuous learning recommended to stay competitive"
                ],
                "recommendations": [
                    f"Research current {skill} job postings in your area",
                    "Build practical projects to demonstrate proficiency",
                    "Connect with professionals using {skill} in industry",
                    "Consider complementary skills to enhance marketability"
                ]
            }
    
    def _calculate_analysis_confidence(self, analysis: str, skill: str) -> float:
        """Calculate confidence based on analysis detail and specificity"""
        confidence = 0.6  # Base confidence
        
        # Check for specific indicators of thorough analysis
        if len(analysis) > 300:
            confidence += 0.1
        if any(word in analysis.lower() for word in ["data", "research", "studies", "report"]):
            confidence += 0.1
        if any(word in analysis.lower() for word in ["growth", "demand", "trend", "market"]):
            confidence += 0.1
        if skill.lower() in analysis.lower():
            confidence += 0.1
            
        return min(confidence, 0.95)
    
    def _extract_main_prediction(self, analysis: str, skill: str) -> str:
        """Extract the main prediction from AI analysis"""
        # Look for key phrases that indicate the main prediction
        analysis_lower = analysis.lower()
        
        if any(phrase in analysis_lower for phrase in ["high demand", "strong growth", "increasing"]):
            return f"Strong market demand for {skill} with positive growth outlook"
        elif any(phrase in analysis_lower for phrase in ["moderate", "stable", "steady"]):
            return f"Stable market demand for {skill} with consistent opportunities"
        elif any(phrase in analysis_lower for phrase in ["declining", "decreasing", "low demand"]):
            return f"Declining market demand for {skill} - consider skill evolution"
        else:
            return f"Market demand analysis for {skill} - see detailed insights"
    
    def _extract_implications(self, analysis: str) -> List[str]:
        """Extract key implications from AI analysis"""
        implications = []
        
        # Look for common implication patterns
        if "automation" in analysis.lower():
            implications.append("Consider automation impact on skill relevance")
        if "remote work" in analysis.lower():
            implications.append("Remote work trends may affect demand patterns")
        if "emerging" in analysis.lower():
            implications.append("Emerging technology creating new opportunities")
        if "competition" in analysis.lower():
            implications.append("Market competition may affect job availability")
            
        # Default implications if none found
        if not implications:
            implications = ["Market conditions are evolving - stay informed"]
            
        return implications[:3]  # Limit to top 3
    
    def _extract_recommendations(self, analysis: str) -> List[str]:
        """Extract actionable recommendations from AI analysis"""
        recommendations = []
        
        # Look for recommendation patterns
        if any(word in analysis.lower() for word in ["certification", "course", "training"]):
            recommendations.append("Pursue formal training or certification")
        if any(word in analysis.lower() for word in ["portfolio", "project", "practice"]):
            recommendations.append("Build practical projects to demonstrate skills")
        if any(word in analysis.lower() for word in ["network", "community", "connect"]):
            recommendations.append("Connect with professionals in this field")
        if any(word in analysis.lower() for word in ["specialize", "niche", "focus"]):
            recommendations.append("Consider specializing in high-demand areas")
            
        # Default recommendations if none found
        if not recommendations:
            recommendations = ["Research current industry requirements", "Consider market trends when developing this skill"]
            
        return recommendations[:3]  # Limit to top 3
    
    def _determine_time_horizon(self, analysis: str) -> str:
        """Determine time horizon based on analysis content"""
        if any(phrase in analysis.lower() for phrase in ["rapid", "quickly", "immediate", "short-term"]):
            return "short"
        elif any(phrase in analysis.lower() for phrase in ["long-term", "decade", "future", "eventual"]):
            return "long"
        else:
            return "medium"
    
    async def analyze_automation_impact(self, role: str, industry: str) -> PredictionResult:
        """Analyze potential impact of automation on specific roles"""
        
        # Automation risk assessment (based on Oxford study methodology)
        automation_risks = {
            # High risk roles
            "data entry clerk": 0.99,
            "cashier": 0.97,
            "telemarketer": 0.99,
            "assembly line worker": 0.95,
            "bookkeeping clerk": 0.98,
            
            # Medium risk roles  
            "financial analyst": 0.43,
            "marketing specialist": 0.61,
            "customer service representative": 0.55,
            "accountant": 0.94,
            "paralegal": 0.94,
            
            # Low risk roles
            "software engineer": 0.17,
            "teacher": 0.04,
            "doctor": 0.00,
            "therapist": 0.00,
            "artist": 0.04,
            "manager": 0.16,
            "scientist": 0.11
        }
        
        role_lower = role.lower()
        automation_risk = automation_risks.get(role_lower, 0.50)  # Default to medium risk
        
        async with self.data_source as ds:
            industry_data = await ds.get_simulated_industry_data(industry)
        
        industry_automation_factor = {
            "manufacturing": 1.2,
            "finance": 1.1,
            "retail": 1.15,
            "technology": 0.8,
            "healthcare": 0.7,
            "education": 0.6
        }.get(industry.lower(), 1.0)
        
        adjusted_risk = min(0.99, automation_risk * industry_automation_factor)
        
        if adjusted_risk > 0.8:
            risk_level = "Very High"
            time_horizon = "short"
            confidence = 0.85
        elif adjusted_risk > 0.6:
            risk_level = "High"
            time_horizon = "medium"
            confidence = 0.80
        elif adjusted_risk > 0.4:
            risk_level = "Medium"
            time_horizon = "long"
            confidence = 0.75
        elif adjusted_risk > 0.2:
            risk_level = "Low"
            time_horizon = "long"
            confidence = 0.70
        else:
            risk_level = "Very Low"
            time_horizon = "long"
            confidence = 0.75
        
        implications = []
        recommendations = []
        
        if adjusted_risk > 0.7:
            implications.extend([
                "High probability of job displacement by automation",
                "Need for significant reskilling or career transition",
                "Timeline for change may be accelerated"
            ])
            recommendations.extend([
                "Begin transition to automation-resistant skills immediately",
                "Focus on human-centric capabilities (creativity, empathy, complex reasoning)",
                "Consider roles that involve managing or working alongside automated systems",
                "Develop skills in emerging technologies to stay relevant"
            ])
        elif adjusted_risk > 0.4:
            implications.extend([
                "Partial automation likely, changing job requirements",
                "Need to adapt and learn new technologies",
                "Opportunity to specialize in human-AI collaboration"
            ])
            recommendations.extend([
                "Stay updated with automation trends in your field",
                "Develop skills that complement automated systems",
                "Focus on strategic and creative aspects of your role",
                "Consider training in relevant technologies"
            ])
        else:
            implications.extend([
                "Low risk of displacement, but technology will augment work",
                "Opportunities to leverage automation for increased productivity",
                "Focus on uniquely human skills remains important"
            ])
            recommendations.extend([
                "Stay curious about how technology can enhance your work",
                "Develop comfort with new tools and systems",
                "Focus on leadership and interpersonal skills",
                "Consider becoming a bridge between technical and human aspects"
            ])
        
        return PredictionResult(
            trend_type=TrendType.AUTOMATION_IMPACT,
            prediction=f"{risk_level} automation risk for {role} in {industry}",
            confidence=confidence,
            time_horizon=time_horizon,
            supporting_data={
                "automation_risk": adjusted_risk,
                "base_risk": automation_risk,
                "industry_factor": industry_automation_factor,
                "role": role,
                "industry": industry
            },
            implications=implications,
            recommendations=recommendations
        )
    
    async def analyze_salary_trends(self, role: str, industry: str, location: str = "national") -> PredictionResult:
        """Analyze salary trends and projections"""
        
        # Simulate salary trend data (in production, use Glassdoor API, PayScale, etc.)
        base_salaries = {
            "software engineer": {"base": 85000, "growth_rate": 6.8, "volatility": 0.15},
            "data scientist": {"base": 95000, "growth_rate": 8.2, "volatility": 0.20},
            "marketing manager": {"base": 70000, "growth_rate": 4.1, "volatility": 0.12},
            "teacher": {"base": 45000, "growth_rate": 2.3, "volatility": 0.08},
            "financial analyst": {"base": 65000, "growth_rate": 3.7, "volatility": 0.18},
            "nurse": {"base": 55000, "growth_rate": 5.1, "volatility": 0.10}
        }
        
        role_data = base_salaries.get(role.lower(), {"base": 50000, "growth_rate": 3.5, "volatility": 0.12})
        
        # Industry multipliers
        industry_multipliers = {
            "technology": 1.3,
            "finance": 1.25,
            "healthcare": 1.1,
            "education": 0.8,
            "manufacturing": 1.05,
            "retail": 0.9
        }
        
        industry_mult = industry_multipliers.get(industry.lower(), 1.0)
        adjusted_base = role_data["base"] * industry_mult
        growth_rate = role_data["growth_rate"]
        
        # 5-year projection
        projected_salary = adjusted_base * ((1 + growth_rate/100) ** 5)
        total_growth = ((projected_salary - adjusted_base) / adjusted_base) * 100
        
        if growth_rate > 7:
            trend_desc = "Strong upward salary trend"
            confidence = 0.80
        elif growth_rate > 4:
            trend_desc = "Moderate salary growth"
            confidence = 0.75
        elif growth_rate > 2:
            trend_desc = "Slow salary growth"
            confidence = 0.70
        else:
            trend_desc = "Salary stagnation risk"
            confidence = 0.65
        
        implications = [
            f"Current average salary: ${adjusted_base:,.0f}",
            f"5-year projection: ${projected_salary:,.0f} ({total_growth:.1f}% total growth)",
            f"Annual growth rate: {growth_rate:.1f}%"
        ]
        
        recommendations = []
        if growth_rate > 6:
            recommendations.extend([
                "Excellent earning potential in this field",
                "Consider negotiating salary based on strong market trends",
                "Invest in skills to maximize earning potential"
            ])
        elif growth_rate < 3:
            recommendations.extend([
                "Consider supplementing income or changing specialization",
                "Look for roles with better compensation growth",
                "Focus on non-monetary benefits and job satisfaction"
            ])
        
        return PredictionResult(
            trend_type=TrendType.SALARY_TRENDS,
            prediction=f"{trend_desc} for {role} in {industry}",
            confidence=confidence,
            time_horizon="medium",
            supporting_data={
                "current_salary": adjusted_base,
                "projected_salary": projected_salary,
                "growth_rate": growth_rate,
                "total_growth": total_growth,
                "role": role,
                "industry": industry
            },
            implications=implications,
            recommendations=recommendations
        )


class PredictiveAnalyticsService:
    """Main service for career predictive analytics using AI"""
    
    def __init__(self, llm: Optional[ChatGoogleGenerativeAI] = None):
        from core.llm_config import create_default_llm_config, AgentLLMFactory
        if llm is None:
            llm_config = create_default_llm_config()
            llm_factory = AgentLLMFactory(llm_config)
            self.llm = llm_factory.get_llm_for_agent("analytics_agent")
        else:
            self.llm = llm
        self.trend_analyzer = TrendAnalyzer(self.llm)
        
    async def generate_career_outlook(
        self,
        role: str,
        industry: str,
        skills: List[str],
        location: str = "national"
    ) -> Dict[str, Any]:
        """Generate comprehensive career outlook analysis"""
        
        try:
            # Run multiple analyses concurrently
            analyses = await asyncio.gather(
                self.trend_analyzer.analyze_job_growth_trends(industry, role),
                self.trend_analyzer.analyze_salary_trends(role, industry, location),
                self.trend_analyzer.analyze_automation_impact(role, industry),
                self.trend_analyzer.analyze_skill_demand_trends(skills),
                return_exceptions=True
            )
            
            job_growth, salary_trends, automation_impact, skill_trends = analyses
            
            # Handle any errors
            results = {}
            if isinstance(job_growth, PredictionResult):
                results["job_growth"] = job_growth
            if isinstance(salary_trends, PredictionResult):
                results["salary_trends"] = salary_trends
            if isinstance(automation_impact, PredictionResult):
                results["automation_impact"] = automation_impact
            if isinstance(skill_trends, list):
                results["skill_trends"] = skill_trends
            
            # Generate overall career outlook
            overall_outlook = self._synthesize_career_outlook(results)
            
            return {
                "role": role,
                "industry": industry,
                "location": location,
                "analysis_date": datetime.now().isoformat(),
                "detailed_analyses": results,
                "overall_outlook": overall_outlook,
                "recommendations": self._generate_strategic_recommendations(results)
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "role": role,
                "industry": industry,
                "analysis_date": datetime.now().isoformat(),
                "message": "Unable to complete full analysis, partial results may be available"
            }
    
    async def predict_industry_disruption(self, industry: str) -> Dict[str, Any]:
        """Predict potential industry disruptions and their impact"""
        
        # Use AI to analyze industry disruption instead of hardcoded data
        try:
            prompt = f"""As an industry analyst, analyze disruption risks for the "{industry}" industry. Consider:

1. AI & automation impact potential (0-1 scale)
2. Regulatory change risks (0-1 scale) 
3. Market volatility factors (0-1 scale)
4. Innovation pace and competitive pressure (0-1 scale)
5. Key emerging disruptors
6. Timeline for major changes

Provide realistic assessment focused on career planning for students and professionals. Include specific technologies, trends, and market forces."""

            # Use timeout for AI analysis (30 seconds)
            import asyncio
            response = await asyncio.wait_for(
                self.llm.ainvoke([{"role": "user", "content": prompt}]),
                timeout=30.0
            )
            ai_analysis = response.content if hasattr(response, 'content') else str(response)
            
            # Parse AI response to extract structured data
            disruption_data = self._parse_ai_disruption_analysis(ai_analysis, industry)
            
        except Exception as e:
            # Fallback to basic analysis if AI fails
            disruption_data = {
                "ai_impact": 0.5,
                "regulatory_risk": 0.5, 
                "market_volatility": 0.5,
                "innovation_pace": 0.5,
                "key_disruptors": ["Digital transformation", "Changing market demands"],
                "timeline": "3-5 years",
                "ai_analysis": f"Analysis temporarily unavailable: {str(e)}"
            }
        
        industry_data = disruption_data
        
        # Calculate overall disruption risk
        disruption_score = (
            industry_data["ai_impact"] * 0.3 +
            industry_data["regulatory_risk"] * 0.2 +
            industry_data["market_volatility"] * 0.2 +
            industry_data["innovation_pace"] * 0.3
        )
        
        if disruption_score > 0.75:
            risk_level = "Very High"
            description = "Industry facing imminent significant disruption"
        elif disruption_score > 0.6:
            risk_level = "High"
            description = "Major changes expected in the near future"
        elif disruption_score > 0.4:
            risk_level = "Medium"
            description = "Gradual transformation likely"
        else:
            risk_level = "Low"
            description = "Relatively stable with incremental changes"
        
        return {
            "industry": industry,
            "disruption_risk_level": risk_level,
            "disruption_score": disruption_score,
            "description": description,
            "timeline": industry_data["timeline"],
            "key_disruptors": industry_data["key_disruptors"],
            "detailed_factors": {
                "ai_impact": industry_data["ai_impact"],
                "regulatory_risk": industry_data["regulatory_risk"],
                "market_volatility": industry_data["market_volatility"],
                "innovation_pace": industry_data["innovation_pace"]
            },
            "implications": self._generate_disruption_implications(risk_level, industry_data),
            "preparation_strategies": self._generate_disruption_strategies(risk_level, industry_data)
        }
    
    def _synthesize_career_outlook(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize multiple analyses into overall career outlook"""
        
        positive_indicators = 0
        negative_indicators = 0
        total_confidence = 0
        confidence_count = 0
        
        # Analyze job growth
        if "job_growth" in results:
            jg = results["job_growth"]
            if "strong" in jg.prediction.lower() or "high" in jg.prediction.lower():
                positive_indicators += 2
            elif "moderate" in jg.prediction.lower():
                positive_indicators += 1
            elif "decline" in jg.prediction.lower():
                negative_indicators += 2
            total_confidence += jg.confidence
            confidence_count += 1
        
        # Analyze salary trends
        if "salary_trends" in results:
            st = results["salary_trends"]
            if "strong" in st.prediction.lower():
                positive_indicators += 2
            elif "moderate" in st.prediction.lower():
                positive_indicators += 1
            elif "stagnation" in st.prediction.lower():
                negative_indicators += 1
            total_confidence += st.confidence
            confidence_count += 1
        
        # Analyze automation impact
        if "automation_impact" in results:
            ai = results["automation_impact"]
            if "very high" in ai.prediction.lower() or "high" in ai.prediction.lower():
                negative_indicators += 2
            elif "medium" in ai.prediction.lower():
                negative_indicators += 1
            else:
                positive_indicators += 1
            total_confidence += ai.confidence
            confidence_count += 1
        
        # Determine overall outlook
        net_score = positive_indicators - negative_indicators
        avg_confidence = total_confidence / max(confidence_count, 1)
        
        if net_score >= 3:
            outlook = "Very Positive"
            summary = "Excellent career prospects with strong growth potential"
        elif net_score >= 1:
            outlook = "Positive"
            summary = "Good career prospects with solid opportunities"
        elif net_score >= -1:
            outlook = "Neutral"
            summary = "Mixed indicators, careful planning recommended"
        elif net_score >= -3:
            outlook = "Challenging"
            summary = "Some challenges ahead, adaptation strategies needed"
        else:
            outlook = "Difficult"
            summary = "Significant challenges, consider alternative paths"
        
        return {
            "overall_rating": outlook,
            "summary": summary,
            "confidence": avg_confidence,
            "positive_indicators": positive_indicators,
            "negative_indicators": negative_indicators,
            "net_score": net_score
        }
    
    def _generate_strategic_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on analysis results"""
        recommendations = []
        
        # Job growth based recommendations
        if "job_growth" in results:
            recommendations.extend(results["job_growth"].recommendations[:2])
        
        # Automation impact recommendations
        if "automation_impact" in results:
            recommendations.extend(results["automation_impact"].recommendations[:2])
        
        # Skill trend recommendations
        if "skill_trends" in results:
            high_demand_skills = [
                trend for trend in results["skill_trends"]
                if "high demand" in trend.prediction.lower()
            ]
            if high_demand_skills:
                recommendations.append(f"Prioritize developing: {', '.join([trend.supporting_data['skill'] for trend in high_demand_skills[:3]])}")
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for rec in recommendations:
            if rec not in seen:
                unique_recommendations.append(rec)
                seen.add(rec)
        
        return unique_recommendations[:6]  # Limit to top 6 recommendations
    
    def _generate_disruption_implications(self, risk_level: str, industry_data: Dict[str, Any]) -> List[str]:
        """Generate implications based on disruption risk level"""
        implications = []
        
        if risk_level in ["Very High", "High"]:
            implications.extend([
                "Rapid skill evolution required to stay relevant",
                "New job categories will emerge while others disappear",
                "Early adoption of new technologies will be competitive advantage",
                "Traditional career paths may become obsolete"
            ])
        elif risk_level == "Medium":
            implications.extend([
                "Gradual shift in required skills and competencies",
                "Hybrid roles combining traditional and new skills",
                "Importance of continuous learning and adaptation",
                "Opportunities for those who prepare early"
            ])
        else:
            implications.extend([
                "Evolutionary rather than revolutionary changes",
                "Traditional skills remain valuable with digital enhancement",
                "Steady career progression paths likely to continue",
                "Focus on efficiency improvements and optimization"
            ])
        
        return implications
    
    def _generate_disruption_strategies(self, risk_level: str, industry_data: Dict[str, Any]) -> List[str]:
        """Generate preparation strategies for industry disruption"""
        strategies = []
        
        if risk_level in ["Very High", "High"]:
            strategies.extend([
                "Develop skills in emerging technologies immediately",
                "Build a diverse skill set to increase adaptability",
                "Network with professionals in adjacent industries",
                "Consider roles that involve managing change",
                "Stay informed about industry transformation trends"
            ])
        elif risk_level == "Medium":
            strategies.extend([
                "Gradually build digital and analytical skills",
                "Seek cross-functional experience and knowledge",
                "Maintain awareness of industry evolution",
                "Develop change management capabilities",
                "Build professional resilience and adaptability"
            ])
        else:
            strategies.extend([
                "Focus on continuous improvement and efficiency",
                "Develop deeper expertise in core competencies",
                "Stay updated with incremental technological advances",
                "Build strong professional relationships",
                "Maintain learning mindset for gradual evolution"
            ])
        
        return strategies
    
    def _parse_ai_disruption_analysis(self, analysis: str, industry: str) -> Dict[str, Any]:
        """Parse AI disruption analysis to extract structured data"""
        
        # Default values
        data = {
            "ai_impact": 0.5,
            "regulatory_risk": 0.5,
            "market_volatility": 0.5,
            "innovation_pace": 0.5,
            "key_disruptors": [],
            "timeline": "3-5 years",
            "ai_analysis": analysis
        }
        
        analysis_lower = analysis.lower()
        
        # Extract AI impact level
        if any(phrase in analysis_lower for phrase in ["high ai impact", "significant automation", "major ai disruption"]):
            data["ai_impact"] = 0.8
        elif any(phrase in analysis_lower for phrase in ["moderate ai", "gradual automation", "some ai impact"]):
            data["ai_impact"] = 0.6
        elif any(phrase in analysis_lower for phrase in ["low ai impact", "minimal automation", "limited ai"]):
            data["ai_impact"] = 0.3
        
        # Extract regulatory risk
        if any(phrase in analysis_lower for phrase in ["high regulatory", "significant regulation", "strict compliance"]):
            data["regulatory_risk"] = 0.8
        elif any(phrase in analysis_lower for phrase in ["moderate regulation", "some regulatory"]):
            data["regulatory_risk"] = 0.6
        elif any(phrase in analysis_lower for phrase in ["low regulatory", "minimal regulation"]):
            data["regulatory_risk"] = 0.3
        
        # Extract market volatility
        if any(phrase in analysis_lower for phrase in ["high volatility", "unstable market", "rapid changes"]):
            data["market_volatility"] = 0.8
        elif any(phrase in analysis_lower for phrase in ["moderate volatility", "some instability"]):
            data["market_volatility"] = 0.6
        elif any(phrase in analysis_lower for phrase in ["stable market", "low volatility"]):
            data["market_volatility"] = 0.3
        
        # Extract innovation pace
        if any(phrase in analysis_lower for phrase in ["rapid innovation", "fast-paced", "quick evolution"]):
            data["innovation_pace"] = 0.8
        elif any(phrase in analysis_lower for phrase in ["moderate innovation", "steady progress"]):
            data["innovation_pace"] = 0.6
        elif any(phrase in analysis_lower for phrase in ["slow innovation", "gradual change"]):
            data["innovation_pace"] = 0.3
        
        # Extract key disruptors (simple keyword extraction)
        potential_disruptors = [
            "artificial intelligence", "machine learning", "automation", "robotics",
            "blockchain", "cryptocurrency", "fintech", "regtech",
            "telemedicine", "digital health", "biotechnology", "gene therapy",
            "e-commerce", "social commerce", "augmented reality", "virtual reality",
            "cloud computing", "edge computing", "quantum computing",
            "sustainability", "green technology", "renewable energy",
            "remote work", "hybrid work", "gig economy", "digital transformation"
        ]
        
        found_disruptors = []
        for disruptor in potential_disruptors:
            if disruptor in analysis_lower:
                found_disruptors.append(disruptor.title())
        
        data["key_disruptors"] = found_disruptors[:4] if found_disruptors else ["Digital transformation", "Market evolution"]
        
        # Extract timeline
        if any(phrase in analysis_lower for phrase in ["1-2 years", "immediate", "short term", "near future"]):
            data["timeline"] = "1-2 years"
        elif any(phrase in analysis_lower for phrase in ["2-3 years", "medium term"]):
            data["timeline"] = "2-3 years"
        elif any(phrase in analysis_lower for phrase in ["3-5 years"]):
            data["timeline"] = "3-5 years"
        elif any(phrase in analysis_lower for phrase in ["5-10 years", "long term", "distant future"]):
            data["timeline"] = "5-10 years"
        
        return data
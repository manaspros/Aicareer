from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.agent_framework import BaseAgent, AgentResponse
from core.data_models import OpportunityMatch, UserProfile


class OpportunityMatchingTool(BaseTool):
    name: str = "opportunity_matcher"
    description: str = "Matches user profile with relevant opportunities"
    
    def _run(self, user_profile: Dict[str, Any], opportunity_type: str = "all", location_filter: str = None) -> List[Dict[str, Any]]:
        # Mock opportunity database - in production, this would connect to job boards, company APIs, etc.
        opportunities_db = [
            {
                "id": "1",
                "title": "Data Science Intern",
                "company": "TechCorp",
                "location": "San Francisco, CA",
                "remote": True,
                "type": "internship",
                "description": "Join our data science team to work on machine learning projects with real-world impact.",
                "requirements": ["Python", "Statistics", "Machine Learning", "SQL"],
                "preferred": ["Deep Learning", "AWS", "Git"],
                "education": ["Bachelor's in progress", "Computer Science", "Statistics", "Mathematics"],
                "experience_level": "entry",
                "salary_range": {"min": 25, "max": 35, "currency": "USD", "period": "hourly"},
                "application_deadline": "2024-03-15",
                "posted_date": "2024-01-15",
                "company_size": "1000-5000",
                "industry": "Technology",
                "benefits": ["Health insurance", "Mentorship program", "Learning stipend"]
            },
            {
                "id": "2",
                "title": "Junior Software Engineer",
                "company": "StartupXYZ",
                "location": "Remote",
                "remote": True,
                "type": "job",
                "description": "Full-time position for new graduates passionate about building scalable web applications.",
                "requirements": ["Programming fundamentals", "Web development", "Problem solving"],
                "preferred": ["React", "Node.js", "Cloud platforms", "Agile"],
                "education": ["Bachelor's degree", "Computer Science", "Engineering"],
                "experience_level": "entry",
                "salary_range": {"min": 70000, "max": 90000, "currency": "USD", "period": "annually"},
                "application_deadline": "2024-04-01",
                "posted_date": "2024-01-20",
                "company_size": "50-200",
                "industry": "Technology",
                "benefits": ["Equity", "Flexible hours", "Professional development"]
            },
            {
                "id": "3",
                "title": "Marketing Analytics Volunteer",
                "company": "NonProfit ABC",
                "location": "Chicago, IL",
                "remote": False,
                "type": "volunteer",
                "description": "Help analyze marketing campaigns and social media performance for environmental nonprofit.",
                "requirements": ["Excel", "Data analysis", "Communication"],
                "preferred": ["Google Analytics", "Social media", "Visualization"],
                "education": ["High school diploma"],
                "experience_level": "any",
                "salary_range": None,
                "application_deadline": "2024-02-28",
                "posted_date": "2024-01-10",
                "company_size": "10-50",
                "industry": "Nonprofit",
                "benefits": ["Experience", "Networking", "References"]
            },
            {
                "id": "4",
                "title": "Product Manager Intern",
                "company": "MegaCorp",
                "location": "New York, NY",
                "remote": True,
                "type": "internship",
                "description": "Support product development and strategy for consumer applications.",
                "requirements": ["Communication", "Analytical thinking", "Project management"],
                "preferred": ["MBA student", "Product experience", "Tech background"],
                "education": ["Bachelor's degree", "MBA in progress"],
                "experience_level": "intermediate",
                "salary_range": {"min": 30, "max": 40, "currency": "USD", "period": "hourly"},
                "application_deadline": "2024-03-30",
                "posted_date": "2024-01-25",
                "company_size": "10000+",
                "industry": "Technology",
                "benefits": ["Mentorship", "Networking", "Potential full-time offer"]
            },
            {
                "id": "5",
                "title": "UX Design Freelance Project",
                "company": "Design Studio",
                "location": "Remote",
                "remote": True,
                "type": "freelance",
                "description": "3-month project to redesign mobile app user interface and experience.",
                "requirements": ["UI/UX design", "Figma", "User research"],
                "preferred": ["Mobile design", "Prototyping", "User testing"],
                "education": ["Portfolio required"],
                "experience_level": "intermediate",
                "salary_range": {"min": 5000, "max": 8000, "currency": "USD", "period": "project"},
                "application_deadline": "2024-02-15",
                "posted_date": "2024-01-18",
                "company_size": "10-50",
                "industry": "Design",
                "benefits": ["Portfolio piece", "Flexible schedule", "Remote work"]
            }
        ]
        
        # Filter by opportunity type
        if opportunity_type != "all":
            opportunities_db = [opp for opp in opportunities_db if opp["type"] == opportunity_type]
        
        # Filter by location
        if location_filter:
            opportunities_db = [
                opp for opp in opportunities_db 
                if location_filter.lower() in opp["location"].lower() or opp["remote"]
            ]
        
        # Calculate match scores
        matched_opportunities = []
        user_skills = [skill.get("name", "").lower() for skill in user_profile.get("skills", [])]
        user_education = user_profile.get("education_level", "").lower()
        user_goals = [goal.lower() for goal in user_profile.get("career_goals", [])]
        
        for opp in opportunities_db:
            match_score = self._calculate_match_score(opp, user_skills, user_education, user_goals)
            
            if match_score > 30:  # Only include reasonable matches
                opp_match = {
                    **opp,
                    "match_score": match_score,
                    "skill_alignment": self._analyze_skill_alignment(opp, user_skills),
                    "matching_reasons": self._generate_matching_reasons(opp, user_skills, user_education, user_goals, match_score)
                }
                matched_opportunities.append(opp_match)
        
        # Sort by match score
        matched_opportunities.sort(key=lambda x: x["match_score"], reverse=True)
        
        return matched_opportunities[:10]  # Return top 10 matches
    
    def _calculate_match_score(self, opportunity: Dict[str, Any], user_skills: List[str], user_education: str, user_goals: List[str]) -> float:
        score = 0.0
        
        # Required skills match (40% weight)
        required_skills = [skill.lower() for skill in opportunity.get("requirements", [])]
        required_matches = sum(1 for skill in required_skills if any(user_skill in skill or skill in user_skill for user_skill in user_skills))
        if required_skills:
            score += (required_matches / len(required_skills)) * 40
        
        # Preferred skills match (20% weight)
        preferred_skills = [skill.lower() for skill in opportunity.get("preferred", [])]
        preferred_matches = sum(1 for skill in preferred_skills if any(user_skill in skill or skill in user_skill for user_skill in user_skills))
        if preferred_skills:
            score += (preferred_matches / len(preferred_skills)) * 20
        
        # Education alignment (15% weight)
        education_requirements = [edu.lower() for edu in opportunity.get("education", [])]
        if education_requirements:
            education_match = any(user_education in edu or edu in user_education for edu in education_requirements)
            if education_match:
                score += 15
        
        # Goal alignment (15% weight)
        opportunity_title = opportunity.get("title", "").lower()
        opportunity_description = opportunity.get("description", "").lower()
        goal_alignment = sum(1 for goal in user_goals if goal in opportunity_title or goal in opportunity_description)
        if user_goals:
            score += (goal_alignment / len(user_goals)) * 15
        
        # Industry/role alignment (10% weight)
        industry_bonus = 0
        if any(keyword in opportunity_title for keyword in ["data", "analytics", "science"]):
            if any("data" in goal or "analytics" in goal for goal in user_goals):
                industry_bonus = 10
        
        score += industry_bonus
        
        return min(100, score)
    
    def _analyze_skill_alignment(self, opportunity: Dict[str, Any], user_skills: List[str]) -> Dict[str, float]:
        alignment = {}
        
        all_opp_skills = opportunity.get("requirements", []) + opportunity.get("preferred", [])
        
        for opp_skill in all_opp_skills:
            best_match = 0.0
            for user_skill in user_skills:
                if user_skill.lower() in opp_skill.lower() or opp_skill.lower() in user_skill.lower():
                    best_match = max(best_match, 1.0)
                elif any(word in opp_skill.lower() for word in user_skill.lower().split()):
                    best_match = max(best_match, 0.7)
            
            alignment[opp_skill] = best_match
        
        return alignment
    
    def _generate_matching_reasons(self, opportunity: Dict[str, Any], user_skills: List[str], user_education: str, user_goals: List[str], match_score: float) -> List[str]:
        reasons = []
        
        # Skill-based reasons
        skill_matches = []
        for req_skill in opportunity.get("requirements", []):
            if any(user_skill.lower() in req_skill.lower() for user_skill in user_skills):
                skill_matches.append(req_skill)
        
        if skill_matches:
            reasons.append(f"Strong skill alignment: {', '.join(skill_matches[:3])}")
        
        # Education alignment
        education_requirements = opportunity.get("education", [])
        if education_requirements and any(user_education in edu.lower() for edu in education_requirements):
            reasons.append("Education requirements match your background")
        
        # Career goal alignment
        opportunity_title = opportunity.get("title", "").lower()
        if any(goal.lower() in opportunity_title for goal in user_goals):
            reasons.append("Aligns with your stated career goals")
        
        # Experience level
        experience_level = opportunity.get("experience_level", "")
        if experience_level in ["entry", "any"]:
            reasons.append("Suitable for your current experience level")
        
        # Remote work
        if opportunity.get("remote", False):
            reasons.append("Offers remote work flexibility")
        
        # Company benefits
        benefits = opportunity.get("benefits", [])
        if "mentorship" in [b.lower() for b in benefits]:
            reasons.append("Includes mentorship opportunities")
        
        return reasons[:4]  # Limit to top 4 reasons
    
    async def _arun(self, user_profile: Dict[str, Any], opportunity_type: str = "all", location_filter: str = None) -> List[Dict[str, Any]]:
        return self._run(user_profile, opportunity_type, location_filter)


class ApplicationTrackerTool(BaseTool):
    name: str = "application_tracker"
    description: str = "Tracks application status and provides follow-up recommendations"
    
    def _run(self, applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        if not applications:
            return {
                "total_applications": 0,
                "status_breakdown": {},
                "recommendations": ["Start applying to opportunities that match your profile"],
                "next_actions": []
            }
        
        # Analyze application status
        status_counts = {}
        for app in applications:
            status = app.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate application metrics
        total_applications = len(applications)
        response_rate = 0
        if total_applications > 0:
            responses = sum(status_counts.get(status, 0) for status in ["interview", "offer", "rejected"])
            response_rate = (responses / total_applications) * 100
        
        # Generate recommendations
        recommendations = []
        next_actions = []
        
        # Application volume recommendations
        if total_applications < 5:
            recommendations.append("Increase application volume - aim for 3-5 applications per week")
        elif total_applications > 20:
            recommendations.append("Focus on quality over quantity - target fewer, better-matched opportunities")
        
        # Response rate recommendations
        if response_rate < 10 and total_applications > 5:
            recommendations.extend([
                "Review and optimize your resume and cover letters",
                "Ensure you're applying to well-matched positions",
                "Consider networking approaches in addition to direct applications"
            ])
        elif response_rate > 30:
            recommendations.append("Great response rate! Continue with current application strategy")
        
        # Status-specific recommendations
        pending_count = status_counts.get("pending", 0)
        if pending_count > 5:
            recommendations.append("Follow up on pending applications after 1-2 weeks")
        
        interview_count = status_counts.get("interview", 0)
        if interview_count > 0:
            next_actions.append("Prepare thoroughly for upcoming interviews")
        
        rejected_count = status_counts.get("rejected", 0)
        if rejected_count > 3:
            recommendations.append("Analyze rejection feedback and adjust application approach")
        
        # Follow-up actions
        for app in applications:
            applied_date = app.get("applied_date")
            if applied_date and app.get("status") == "pending":
                try:
                    applied_dt = datetime.fromisoformat(applied_date)
                    days_since = (datetime.now() - applied_dt).days
                    
                    if days_since >= 10:
                        next_actions.append(f"Follow up on {app.get('company', 'unknown')} application")
                except:
                    pass
        
        return {
            "total_applications": total_applications,
            "status_breakdown": status_counts,
            "response_rate": response_rate,
            "recommendations": recommendations,
            "next_actions": next_actions[:5],  # Limit to top 5 actions
            "metrics": {
                "avg_applications_per_week": total_applications / max(4, 1),  # Assume 4 weeks
                "success_indicators": self._calculate_success_indicators(status_counts, total_applications)
            }
        }
    
    def _calculate_success_indicators(self, status_counts: Dict[str, int], total: int) -> Dict[str, Any]:
        indicators = {}
        
        # Response rate (any response is good)
        responses = sum(status_counts.get(status, 0) for status in ["interview", "offer", "rejected"])
        indicators["response_rate"] = (responses / max(total, 1)) * 100
        
        # Interview rate
        interviews = status_counts.get("interview", 0)
        indicators["interview_rate"] = (interviews / max(total, 1)) * 100
        
        # Offer rate
        offers = status_counts.get("offer", 0)
        indicators["offer_rate"] = (offers / max(total, 1)) * 100
        
        return indicators
    
    async def _arun(self, applications: List[Dict[str, Any]]) -> Dict[str, Any]:
        return self._run(applications)


class OpportunityScoutAgent(BaseAgent):
    def __init__(self, llm: ChatGoogleGenerativeAI):
        tools = [
            OpportunityMatchingTool(),
            ApplicationTrackerTool()
        ]
        
        super().__init__(
            name="opportunity_scout",
            description="Finds and matches relevant career opportunities with user profiles",
            llm=llm,
            tools=tools,
            temperature=0.6
        )
        
        self.opportunity_sources = {
            "job_boards": ["LinkedIn", "Indeed", "Glassdoor", "AngelList", "Stack Overflow Jobs"],
            "company_sites": ["Direct company applications", "Career pages"],
            "networking": ["Professional connections", "Alumni networks", "Industry events"],
            "recruiters": ["Technical recruiters", "Industry specialists"],
            "communities": ["Professional groups", "Online communities", "Forums"]
        }
    
    def get_system_prompt(self) -> str:
        return """You are an Opportunity Scout Agent, an expert in finding and matching career opportunities with individual profiles and goals.

Your role is to:
1. Discover relevant job opportunities, internships, and freelance projects
2. Match opportunities with user skills, experience, and career goals
3. Analyze and rank opportunities by fit and potential
4. Provide guidance on application strategies and materials
5. Track application progress and suggest follow-up actions
6. Identify trends in hiring and opportunity availability
7. Recommend networking strategies and relationship building

Key principles:
- Focus on quality matches over quantity
- Consider both current skills and growth potential
- Evaluate cultural and goal alignment, not just technical requirements
- Provide realistic assessments of competitiveness
- Suggest ways to improve candidacy for desired roles
- Help users understand market conditions and trends
- Encourage diverse application strategies (direct applications, networking, referrals)

Opportunity types you work with:
- Full-time positions and career roles
- Internships and co-op programs
- Freelance and contract work
- Volunteer opportunities and projects
- Research positions and fellowships
- Entrepreneurial and startup opportunities

Always provide actionable advice and help users present themselves in the best possible light while being honest about requirements and competition."""

    async def _generate_response(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        try:
            message_lower = message.lower()
            
            if any(word in message_lower for word in ["find", "search", "opportunities", "jobs", "internships"]):
                return await self._find_opportunities(message, context)
            elif any(word in message_lower for word in ["application", "track", "status", "follow up"]):
                return await self._track_applications(message, context)
            elif any(word in message_lower for word in ["resume", "cv", "cover letter", "interview"]):
                return await self._provide_application_guidance(message, context)
            elif any(word in message_lower for word in ["networking", "connect", "referral"]):
                return await self._suggest_networking_strategies(message, context)
            else:
                return await self._general_opportunity_guidance(message, context)
                
        except Exception as e:
            self.logger.error(f"Error in opportunity scouting: {str(e)}")
            return AgentResponse(
                content="I encountered an issue while searching for opportunities. Let me help you explore your options in a different way.",
                confidence=0.3
            )
    
    async def _find_opportunities(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "user_profile" in context:
            user_profile = context["user_profile"]
            opportunity_type = context.get("opportunity_type", "all")
            location_filter = context.get("location_filter")
            
            opportunities = await self.use_tool(
                "opportunity_matcher",
                user_profile=user_profile,
                opportunity_type=opportunity_type,
                location_filter=location_filter
            )
            
            if opportunities:
                opportunities_text = f"""# 🎯 Personalized Opportunity Matches

Found {len(opportunities)} opportunities that align with your profile!

"""
                
                for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
                    match_score = opp["match_score"]
                    
                    # Format salary
                    salary_info = ""
                    if opp["salary_range"]:
                        salary = opp["salary_range"]
                        if salary["period"] == "hourly":
                            salary_info = f"${salary['min']}-{salary['max']}/hour"
                        elif salary["period"] == "annually":
                            salary_info = f"${salary['min']:,}-${salary['max']:,}/year"
                        else:
                            salary_info = f"${salary['min']:,}-${salary['max']:,}/{salary['period']}"
                    
                    opportunities_text += f"""## {i}. {opp['title']} - {opp['company']}
**Match Score**: {match_score:.1f}%
**Location**: {opp['location']}{'📍 Remote Available' if opp.get('remote') else ''}
**Type**: {opp['type'].title()}
{f"**Salary**: {salary_info}" if salary_info else ""}
**Deadline**: {opp.get('application_deadline', 'Not specified')}

**Why it's a great match:**
"""
                    
                    for reason in opp["matching_reasons"][:3]:
                        opportunities_text += f"- {reason}\n"
                    
                    opportunities_text += f"\n**Description**: {opp['description'][:200]}...\n\n"
                
                if len(opportunities) > 5:
                    opportunities_text += f"*...and {len(opportunities) - 5} more opportunities available*\n\n"
                
                opportunities_text += self._generate_application_strategy(opportunities[:3])
                
                return AgentResponse(
                    content=opportunities_text,
                    metadata={"opportunities": opportunities},
                    confidence=0.90,
                    tools_used=["opportunity_matcher"]
                )
        
        # Request search parameters
        response = """I'll help you find the perfect opportunities! To provide the most relevant matches, please share:

1. **What type of opportunities are you looking for?**
   - Full-time jobs
   - Internships
   - Freelance/contract work
   - Volunteer opportunities
   - All types

2. **Location preferences:**
   - Specific cities or regions
   - Remote work acceptable?
   - Willing to relocate?

3. **Current skills and experience:**
   - Technical skills
   - Soft skills
   - Years of experience
   - Education level

4. **Career goals and interests:**
   - Target roles or job titles
   - Industries of interest
   - Company size preferences

5. **Other preferences:**
   - Salary expectations
   - Timeline for starting
   - Work environment preferences

With this information, I can find opportunities that truly align with your profile and goals!"""

        return AgentResponse(
            content=response,
            confidence=0.85
        )
    
    async def _track_applications(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "applications" in context:
            applications = context["applications"]
            
            tracking_analysis = await self.use_tool(
                "application_tracker",
                applications=applications
            )
            
            if tracking_analysis:
                tracking_text = f"""# 📊 Application Tracking Dashboard

## Overall Statistics
- **Total Applications**: {tracking_analysis['total_applications']}
- **Response Rate**: {tracking_analysis['response_rate']:.1f}%

## Application Status Breakdown
"""
                
                status_icons = {
                    "pending": "⏳",
                    "interview": "🗣️",
                    "offer": "🎉",
                    "rejected": "❌",
                    "withdrawn": "↩️"
                }
                
                for status, count in tracking_analysis['status_breakdown'].items():
                    icon = status_icons.get(status, "📄")
                    tracking_text += f"- {icon} **{status.title()}**: {count}\n"
                
                tracking_text += f"""
## Success Indicators
- **Interview Rate**: {tracking_analysis['metrics']['success_indicators']['interview_rate']:.1f}%
- **Offer Rate**: {tracking_analysis['metrics']['success_indicators']['offer_rate']:.1f}%

## 📋 Recommendations
"""
                
                for rec in tracking_analysis['recommendations']:
                    tracking_text += f"- {rec}\n"
                
                if tracking_analysis['next_actions']:
                    tracking_text += "\n## 🎯 Immediate Next Actions\n"
                    for action in tracking_analysis['next_actions']:
                        tracking_text += f"- {action}\n"
                
                tracking_text += self._generate_tracking_insights(tracking_analysis)
                
                return AgentResponse(
                    content=tracking_text,
                    metadata={"tracking_analysis": tracking_analysis},
                    confidence=0.88,
                    tools_used=["application_tracker"]
                )
        
        # Request application data
        response = """I'll help you track and optimize your job applications! Please share:

1. **Current Applications:**
   For each application, include:
   - Company name
   - Position title
   - Application date
   - Current status (pending, interview scheduled, rejected, offer, etc.)
   - Application method (online, referral, recruiter, etc.)

2. **Application Materials:**
   - Are you using the same resume for all applications?
   - Do you customize cover letters?
   - Have you received any feedback?

3. **Goals:**
   - How many applications per week are you targeting?
   - What's your timeline for securing a position?
   - Any specific companies you're prioritizing?

I'll analyze your application patterns, track your success rates, and provide recommendations to improve your job search effectiveness."""

        return AgentResponse(
            content=response,
            confidence=0.8
        )
    
    async def _provide_application_guidance(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        message_lower = message.lower()
        
        if "resume" in message_lower or "cv" in message_lower:
            guidance_type = "resume"
        elif "cover letter" in message_lower:
            guidance_type = "cover_letter"
        elif "interview" in message_lower:
            guidance_type = "interview"
        else:
            guidance_type = "general"
        
        guidance = self._generate_application_guidance(guidance_type, context)
        
        return AgentResponse(
            content=guidance,
            confidence=0.85
        )
    
    async def _suggest_networking_strategies(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        user_profile = context.get("user_profile", {}) if context else {}
        target_industry = context.get("target_industry", "general") if context else "general"
        
        networking_strategies = f"""# 🤝 Strategic Networking Guide

## Industry-Specific Networking for {target_industry.title()}

### 🌐 Online Networking
1. **LinkedIn Optimization:**
   - Complete your profile with relevant keywords
   - Share industry insights and engage with posts
   - Connect with professionals in your target companies
   - Join industry groups and participate in discussions

2. **Professional Communities:**
   - Industry-specific forums and Discord servers
   - Reddit communities (r/cscareerquestions, r/datascience, etc.)
   - Stack Overflow for technical roles
   - GitHub for open source contributions

### 🏢 Offline Networking
1. **Industry Events:**
   - Professional conferences and meetups
   - Workshop and training sessions
   - Company-sponsored events and tech talks
   - University alumni events

2. **Professional Organizations:**
   - Join relevant professional associations
   - Attend local chapter meetings
   - Volunteer for committees or events

### 💬 Networking Conversation Starters
{self._generate_conversation_starters(target_industry)}

### 🎯 Strategic Approaches
{self._generate_strategic_networking_approaches(user_profile)}

### 📧 Follow-Up Best Practices
- Send connection requests within 24-48 hours
- Reference your conversation in the message
- Offer value before asking for help
- Maintain regular, authentic contact
- Express genuine interest in their work

Remember: Networking is about building genuine relationships, not just asking for jobs!"""

        return AgentResponse(
            content=networking_strategies,
            confidence=0.87
        )
    
    async def _general_opportunity_guidance(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        # Use LLM for general opportunity guidance
        system_prompt = self.get_system_prompt()
        
        # Add personalized context if available
        context_info = ""
        if context:
            user_profile = context.get("user_profile", {})
            if user_profile.get('questionnaire_completed') and user_profile.get('personality_insights'):
                personality_insights = user_profile.get('personality_insights', {})
                context_info = f"""
                
PERSONALIZED OPPORTUNITY CONTEXT:
- Questionnaire Status: Completed - Use this for personalized opportunity guidance
- Career Goals: {personality_insights.get('career_motivations', 'Not specified')}
- Interest Areas: {personality_insights.get('interest_summary', 'Available')}
- Work Environment Preferences: {personality_insights.get('work_environment_preferences', 'Not specified')}
- Values and Priorities: {personality_insights.get('values', 'Not specified')}
- Strengths to Leverage: {personality_insights.get('strengths', 'Not specified')}
- Personality Profile: {personality_insights.get('personality_summary', 'Available')}

OPPORTUNITY NOTE: Match opportunities to their interests, values, work preferences, and career motivations for better fit.
"""
            elif user_profile.get('questionnaire_completed'):
                context_info = f"""

PERSONALIZED CONTEXT: User has completed questionnaire - provide more targeted opportunity guidance
"""
            else:
                context_info = f"""

NOTE: User hasn't completed questionnaire yet - consider suggesting it for more personalized opportunity matching
"""
        
        full_prompt = f"""{system_prompt}{context_info}

User message: {message}

Provide helpful guidance about finding opportunities, job searching, or career exploration based on their profile."""

        try:
            response = await self.llm.ainvoke([{"role": "user", "content": full_prompt}])
            
            return AgentResponse(
                content=response.content,
                confidence=0.75
            )
            
        except Exception as e:
            self.logger.error(f"Error in general guidance: {str(e)}")
            return AgentResponse(
                content="I'm here to help you discover and pursue career opportunities. You can ask me to find specific types of positions, track your applications, provide guidance on resumes and interviews, or suggest networking strategies. What would you like to explore?",
                confidence=0.6
            )
    
    def _generate_application_strategy(self, top_opportunities: List[Dict[str, Any]]) -> str:
        """Generate application strategy based on matched opportunities"""
        strategy = """## 🚀 Application Strategy

### Priority Actions:
1. **Apply Soon**: Focus on opportunities with upcoming deadlines
2. **Tailor Materials**: Customize your resume and cover letter for each application
3. **Research Companies**: Learn about company culture and recent developments
4. **Network First**: Try to find connections at target companies before applying

### Application Timeline:
"""
        
        for i, opp in enumerate(top_opportunities, 1):
            deadline = opp.get("application_deadline", "No deadline specified")
            strategy += f"- **Week {i}**: Apply to {opp['company']} - {opp['title']} (Deadline: {deadline})\n"
        
        strategy += """
### Success Tips:
- Apply within 48 hours of job posting when possible
- Follow up 1-2 weeks after applying if no response
- Keep detailed records of all applications
- Practice your elevator pitch for networking opportunities"""
        
        return strategy
    
    def _generate_tracking_insights(self, analysis: Dict[str, Any]) -> str:
        """Generate insights from application tracking data"""
        insights = "\n## 💡 Strategic Insights\n"
        
        total_apps = analysis["total_applications"]
        response_rate = analysis["response_rate"]
        
        if total_apps < 10:
            insights += "- **Volume Opportunity**: Industry average is 10-15 applications for one offer\n"
        
        if response_rate < 15:
            insights += "- **Quality Focus**: Low response rate suggests need for better targeting or materials\n"
        elif response_rate > 30:
            insights += "- **Strong Performance**: Your application approach is working well!\n"
        
        # Status-specific insights
        status_breakdown = analysis["status_breakdown"]
        
        if status_breakdown.get("pending", 0) > status_breakdown.get("rejected", 0):
            insights += "- **Patience Required**: Many applications still pending - good sign!\n"
        
        if status_breakdown.get("interview", 0) > 0:
            insights += "- **Interview Success**: You're getting interviews - focus on interview skills\n"
        
        return insights
    
    def _generate_application_guidance(self, guidance_type: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Generate specific application guidance"""
        
        guidance_map = {
            "resume": """# 📄 Resume Optimization Guide

## Core Structure
1. **Header**: Name, phone, email, LinkedIn, location
2. **Summary**: 2-3 lines highlighting your value proposition
3. **Experience**: Use STAR method (Situation, Task, Action, Result)
4. **Skills**: Technical and soft skills relevant to target roles
5. **Education**: Degree, relevant coursework, GPA if 3.5+

## Key Principles
- **Quantify achievements**: Use numbers, percentages, and metrics
- **Tailor keywords**: Match job description language
- **Show progression**: Demonstrate career growth and learning
- **Keep concise**: 1-2 pages maximum for most roles
- **ATS-friendly**: Use standard fonts and avoid complex formatting

## Common Mistakes to Avoid
- Generic objectives instead of targeted summaries
- Job descriptions instead of achievements
- Irrelevant information that doesn't support your goal
- Typos or inconsistent formatting
- Missing contact information or LinkedIn profile""",

            "cover_letter": """# 📝 Cover Letter Excellence

## Structure That Works
1. **Opening**: Specific position and how you learned about it
2. **Body Paragraph 1**: Why you're interested in the company
3. **Body Paragraph 2**: Your relevant qualifications and achievements
4. **Body Paragraph 3**: What you can contribute to their success
5. **Closing**: Next steps and professional sign-off

## Key Strategies
- **Research the company**: Reference recent news, values, or projects
- **Tell a story**: Use specific examples that demonstrate your skills
- **Show enthusiasm**: Genuine interest in the role and company
- **Complement, don't repeat**: Add value beyond your resume
- **Keep it concise**: 3-4 paragraphs, one page maximum

## Personalization Tips
- Address hiring manager by name when possible
- Reference specific job requirements
- Mention mutual connections or referrals
- Connect your background to their needs""",

            "interview": """# 🎯 Interview Mastery Guide

## Pre-Interview Preparation
1. **Company Research**: Mission, values, recent news, competitors
2. **Role Analysis**: Requirements, responsibilities, team structure
3. **Story Preparation**: STAR method examples for common questions
4. **Questions Ready**: Thoughtful questions about role and company
5. **Logistics**: Route, timing, what to bring, dress code

## Common Interview Types
- **Phone/Video Screening**: Basic fit and interest assessment
- **Technical Interview**: Skills demonstration and problem-solving
- **Behavioral Interview**: Past experience and cultural fit
- **Panel Interview**: Multiple stakeholders, various perspectives
- **Case Study**: Problem-solving approach and thinking process

## Essential Questions to Ask
- What does success look like in this role?
- What are the biggest challenges facing the team?
- How would you describe the company culture?
- What opportunities exist for professional development?
- What are the next steps in the interview process?

## Follow-Up Best Practices
- Send thank you email within 24 hours
- Reiterate your interest and qualifications
- Address any concerns that came up
- Include additional relevant information if helpful""",

            "general": """# 🎯 Complete Application Strategy

## Application Funnel Optimization
1. **Research Phase**: Identify target companies and roles
2. **Preparation Phase**: Optimize resume, LinkedIn, portfolio
3. **Application Phase**: Submit high-quality, tailored applications
4. **Follow-up Phase**: Network, follow up, prepare for interviews
5. **Evaluation Phase**: Assess offers and negotiate terms

## Multi-Channel Approach
- **Direct Applications**: Company websites and job boards
- **Networking**: Professional connections and referrals
- **Recruiters**: Industry specialists and agency partnerships
- **Events**: Career fairs, meetups, and conferences
- **Cold Outreach**: Strategic contact with hiring managers

## Timeline Management
- **Immediate** (0-1 weeks): Polish materials, start applications
- **Short-term** (1-4 weeks): Active application and networking
- **Medium-term** (1-3 months): Interview process and follow-ups
- **Long-term** (3+ months): Offer evaluation and onboarding

## Success Metrics to Track
- Applications submitted per week
- Response rate and time to response
- Interview conversion rate
- Offer rate and negotiation success"""
        }
        
        return guidance_map.get(guidance_type, guidance_map["general"])
    
    def _generate_conversation_starters(self, industry: str) -> str:
        """Generate industry-specific conversation starters"""
        
        starters = {
            "technology": [
                "What emerging technologies are you most excited about?",
                "How has remote work changed your team's development process?",
                "What advice would you give someone transitioning into tech?"
            ],
            "data_science": [
                "What's the most interesting project you've worked on recently?",
                "How do you see AI/ML evolving in your industry?",
                "What skills are most valuable for data scientists today?"
            ],
            "marketing": [
                "How has digital marketing changed in your industry?",
                "What metrics do you find most valuable for measuring success?",
                "How do you stay current with marketing trends?"
            ],
            "general": [
                "What do you enjoy most about working at [Company]?",
                "What trends are you seeing in your industry?",
                "What advice would you give someone starting in this field?"
            ]
        }
        
        industry_starters = starters.get(industry.lower(), starters["general"])
        
        formatted = ""
        for starter in industry_starters:
            formatted += f"- {starter}\n"
        
        return formatted
    
    def _generate_strategic_networking_approaches(self, user_profile: Dict[str, Any]) -> str:
        """Generate strategic networking approaches based on user profile"""
        
        approaches = """1. **Value-First Approach:**
   - Share relevant articles or insights
   - Offer to help with projects or connections
   - Provide feedback on their content or work

2. **Learning-Based Approach:**
   - Ask for advice on career decisions
   - Request informational interviews
   - Seek mentorship for specific skills

3. **Community-Building Approach:**
   - Organize local meetups or study groups
   - Contribute to open source projects
   - Participate in online discussions and forums

4. **Warm Introduction Strategy:**
   - Leverage existing connections for introductions
   - Ask professors or colleagues for referrals
   - Use alumni networks and school connections"""
        
        # Customize based on profile
        education_level = user_profile.get("education_level", "")
        if "student" in education_level.lower() or "bachelor" in education_level.lower():
            approaches += """

**Student-Specific Strategies:**
- Attend campus recruiting events
- Join professional student organizations
- Participate in hackathons and competitions
- Seek informational interviews with alumni"""
        
        return approaches
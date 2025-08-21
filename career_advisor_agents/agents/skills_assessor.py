from typing import Dict, List, Any, Optional
import json
from datetime import datetime
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI

from ..core.agent_framework import BaseAgent, AgentResponse
from ..core.data_models import SkillAssessmentResult, SkillLevel, Skill


class SkillBenchmarkTool(BaseTool):
    name = "skill_benchmark"
    description = "Benchmarks user's skill level against industry standards"
    
    def _run(self, skill_name: str, responses: List[str], experience_years: float) -> Dict[str, Any]:
        # Skill benchmarking logic
        skill_benchmarks = {
            "python": {
                "beginner": {"min_years": 0, "key_concepts": ["variables", "loops", "functions"]},
                "intermediate": {"min_years": 1, "key_concepts": ["oop", "libraries", "debugging"]},
                "advanced": {"min_years": 3, "key_concepts": ["frameworks", "testing", "performance"]},
                "expert": {"min_years": 5, "key_concepts": ["architecture", "mentoring", "system_design"]}
            },
            "machine learning": {
                "beginner": {"min_years": 0, "key_concepts": ["supervised", "algorithms", "data_prep"]},
                "intermediate": {"min_years": 1, "key_concepts": ["model_selection", "validation", "features"]},
                "advanced": {"min_years": 2, "key_concepts": ["deep_learning", "optimization", "production"]},
                "expert": {"min_years": 4, "key_concepts": ["research", "custom_algorithms", "mlops"]}
            },
            "communication": {
                "beginner": {"min_years": 0, "key_concepts": ["listening", "clarity", "feedback"]},
                "intermediate": {"min_years": 2, "key_concepts": ["presentation", "persuasion", "conflict"]},
                "advanced": {"min_years": 5, "key_concepts": ["leadership", "negotiation", "influence"]},
                "expert": {"min_years": 8, "key_concepts": ["strategic", "mentoring", "transformation"]}
            }
        }
        
        skill_lower = skill_name.lower()
        benchmark = skill_benchmarks.get(skill_lower, {
            "beginner": {"min_years": 0, "key_concepts": []},
            "intermediate": {"min_years": 1, "key_concepts": []},
            "advanced": {"min_years": 3, "key_concepts": []},
            "expert": {"min_years": 5, "key_concepts": []}
        })
        
        # Analyze responses for concept understanding
        concept_score = 0
        all_concepts = []
        for level_data in benchmark.values():
            all_concepts.extend(level_data["key_concepts"])
        
        for response in responses:
            response_lower = response.lower()
            for concept in all_concepts:
                if concept in response_lower:
                    concept_score += 1
        
        concept_understanding = concept_score / max(len(all_concepts), 1)
        
        # Determine skill level based on experience and concept understanding
        if experience_years >= benchmark["expert"]["min_years"] and concept_understanding > 0.8:
            assessed_level = "expert"
            confidence = 0.9
        elif experience_years >= benchmark["advanced"]["min_years"] and concept_understanding > 0.6:
            assessed_level = "advanced"
            confidence = 0.85
        elif experience_years >= benchmark["intermediate"]["min_years"] and concept_understanding > 0.4:
            assessed_level = "intermediate"
            confidence = 0.8
        else:
            assessed_level = "beginner"
            confidence = 0.75
        
        return {
            "assessed_level": assessed_level,
            "confidence": confidence,
            "concept_understanding": concept_understanding,
            "experience_factor": min(experience_years / 5, 1.0),
            "benchmark_level": benchmark[assessed_level]
        }
    
    async def _arun(self, skill_name: str, responses: List[str], experience_years: float) -> Dict[str, Any]:
        return self._run(skill_name, responses, experience_years)


class SkillGapAnalysisTool(BaseTool):
    name = "skill_gap_analysis"
    description = "Identifies gaps between current skills and target role requirements"
    
    def _run(self, current_skills: List[Dict[str, Any]], target_role: str) -> Dict[str, Any]:
        # Role requirements database
        role_requirements = {
            "data_scientist": {
                "required": [
                    {"skill": "Python", "level": "advanced"},
                    {"skill": "Machine Learning", "level": "advanced"},
                    {"skill": "Statistics", "level": "intermediate"},
                    {"skill": "SQL", "level": "intermediate"}
                ],
                "preferred": [
                    {"skill": "Deep Learning", "level": "intermediate"},
                    {"skill": "Big Data", "level": "beginner"},
                    {"skill": "Visualization", "level": "intermediate"}
                ]
            },
            "software_engineer": {
                "required": [
                    {"skill": "Programming", "level": "advanced"},
                    {"skill": "Algorithms", "level": "intermediate"},
                    {"skill": "System Design", "level": "intermediate"},
                    {"skill": "Testing", "level": "intermediate"}
                ],
                "preferred": [
                    {"skill": "Cloud Platforms", "level": "intermediate"},
                    {"skill": "DevOps", "level": "beginner"},
                    {"skill": "Security", "level": "beginner"}
                ]
            },
            "marketing_manager": {
                "required": [
                    {"skill": "Digital Marketing", "level": "advanced"},
                    {"skill": "Analytics", "level": "intermediate"},
                    {"skill": "Communication", "level": "advanced"},
                    {"skill": "Strategy", "level": "intermediate"}
                ],
                "preferred": [
                    {"skill": "Content Creation", "level": "intermediate"},
                    {"skill": "Social Media", "level": "intermediate"},
                    {"skill": "SEO", "level": "beginner"}
                ]
            }
        }
        
        role_req = role_requirements.get(target_role.lower().replace(" ", "_"), {
            "required": [],
            "preferred": []
        })
        
        # Convert skill levels to numeric values
        level_values = {"beginner": 1, "intermediate": 2, "advanced": 3, "expert": 4}
        
        # Create current skills lookup
        current_skills_lookup = {}
        for skill in current_skills:
            skill_name = skill.get("name", "").lower()
            skill_level = skill.get("level", "beginner")
            current_skills_lookup[skill_name] = level_values.get(skill_level, 1)
        
        # Analyze gaps
        skill_gaps = []
        skill_strengths = []
        missing_skills = []
        
        # Check required skills
        for req_skill in role_req["required"]:
            skill_name = req_skill["skill"].lower()
            required_level = level_values[req_skill["level"]]
            current_level = current_skills_lookup.get(skill_name, 0)
            
            if current_level == 0:
                missing_skills.append({
                    "skill": req_skill["skill"],
                    "required_level": req_skill["level"],
                    "gap_type": "missing",
                    "priority": "high"
                })
            elif current_level < required_level:
                skill_gaps.append({
                    "skill": req_skill["skill"],
                    "current_level": list(level_values.keys())[current_level - 1],
                    "required_level": req_skill["level"],
                    "gap_size": required_level - current_level,
                    "gap_type": "level",
                    "priority": "high"
                })
            else:
                skill_strengths.append({
                    "skill": req_skill["skill"],
                    "current_level": list(level_values.keys())[current_level - 1],
                    "required_level": req_skill["level"],
                    "strength_type": "meets_requirement"
                })
        
        # Check preferred skills
        for pref_skill in role_req["preferred"]:
            skill_name = pref_skill["skill"].lower()
            preferred_level = level_values[pref_skill["level"]]
            current_level = current_skills_lookup.get(skill_name, 0)
            
            if current_level == 0:
                missing_skills.append({
                    "skill": pref_skill["skill"],
                    "required_level": pref_skill["level"],
                    "gap_type": "missing",
                    "priority": "medium"
                })
            elif current_level < preferred_level:
                skill_gaps.append({
                    "skill": pref_skill["skill"],
                    "current_level": list(level_values.keys())[current_level - 1],
                    "required_level": pref_skill["level"],
                    "gap_size": preferred_level - current_level,
                    "gap_type": "level",
                    "priority": "medium"
                })
        
        # Calculate readiness score
        total_required = len(role_req["required"])
        met_required = len([s for s in skill_strengths if any(r["skill"] == s["skill"] for r in role_req["required"])])
        readiness_score = (met_required / max(total_required, 1)) * 100
        
        return {
            "target_role": target_role,
            "readiness_score": readiness_score,
            "skill_gaps": skill_gaps,
            "missing_skills": missing_skills,
            "skill_strengths": skill_strengths,
            "priority_gaps": [gap for gap in skill_gaps + missing_skills if gap["priority"] == "high"],
            "development_timeline": self._estimate_development_timeline(skill_gaps + missing_skills)
        }
    
    def _estimate_development_timeline(self, gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Estimate time to close gaps
        development_time = {
            "missing": {"beginner": 4, "intermediate": 8, "advanced": 16},  # weeks
            "level": 4  # weeks per level gap
        }
        
        high_priority_weeks = 0
        medium_priority_weeks = 0
        
        for gap in gaps:
            if gap["gap_type"] == "missing":
                weeks = development_time["missing"][gap["required_level"]]
            else:
                weeks = gap["gap_size"] * development_time["level"]
            
            if gap["priority"] == "high":
                high_priority_weeks += weeks
            else:
                medium_priority_weeks += weeks
        
        return {
            "high_priority_weeks": high_priority_weeks,
            "medium_priority_weeks": medium_priority_weeks,
            "total_weeks": high_priority_weeks + medium_priority_weeks,
            "estimated_months": (high_priority_weeks + medium_priority_weeks) / 4
        }
    
    async def _arun(self, current_skills: List[Dict[str, Any]], target_role: str) -> Dict[str, Any]:
        return self._run(current_skills, target_role)


class SkillsAssessorAgent(BaseAgent):
    def __init__(self, llm: ChatGoogleGenerativeAI):
        tools = [
            SkillBenchmarkTool(),
            SkillGapAnalysisTool()
        ]
        
        super().__init__(
            name="skills_assessor",
            description="Assesses current skills and identifies development needs",
            llm=llm,
            tools=tools,
            temperature=0.5
        )
        
        self.assessment_questions = {
            "technical": [
                "Describe a challenging technical problem you've solved recently.",
                "What tools and technologies do you use in your daily work?",
                "How do you stay updated with new developments in your field?",
                "Walk me through your approach to learning a new technical skill."
            ],
            "soft": [
                "Describe a situation where you had to communicate complex information to non-technical stakeholders.",
                "Tell me about a time you had to resolve a conflict in a team setting.",
                "How do you handle feedback and criticism?",
                "Describe your leadership style and give an example of when you've led a project."
            ]
        }
    
    def get_system_prompt(self) -> str:
        return """You are a Skills Assessor Agent, an expert in evaluating professional competencies and identifying skill development needs.

Your role is to:
1. Conduct comprehensive skill assessments through targeted questions
2. Benchmark skills against industry standards
3. Identify skill gaps for target roles or career goals
4. Provide specific, actionable development recommendations
5. Create personalized learning plans based on assessment results

Key guidelines:
- Use evidence-based assessment methods
- Ask probing questions to understand depth of knowledge
- Consider both technical and soft skills
- Provide constructive feedback that motivates growth
- Tailor recommendations to individual learning styles and goals
- Set realistic timelines for skill development
- Connect skill development to career advancement opportunities

Assessment areas:
- Technical competencies specific to user's field
- Soft skills (communication, leadership, problem-solving)
- Industry knowledge and awareness
- Learning agility and adaptability
- Professional experience and application of skills

Always maintain an encouraging tone while providing honest, actionable feedback."""

    async def _generate_response(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        try:
            message_lower = message.lower()
            
            if any(word in message_lower for word in ["assess", "evaluate", "skill"]):
                return await self._conduct_skill_assessment(message, context)
            elif any(word in message_lower for word in ["gap", "compare", "benchmark"]):
                return await self._analyze_skill_gaps(message, context)
            elif any(word in message_lower for word in ["improve", "develop", "learn"]):
                return await self._create_development_plan(message, context)
            else:
                return await self._general_skill_guidance(message, context)
                
        except Exception as e:
            self.logger.error(f"Error in skills assessment: {str(e)}")
            return AgentResponse(
                content="I encountered an issue while assessing your skills. Let me try a different approach.",
                confidence=0.3
            )
    
    async def _conduct_skill_assessment(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "skill_responses" in context:
            # Process assessment responses
            skill_name = context.get("skill_name", "")
            responses = context["skill_responses"]
            experience_years = context.get("experience_years", 0)
            
            assessment_result = await self.use_tool(
                "skill_benchmark",
                skill_name=skill_name,
                responses=responses,
                experience_years=experience_years
            )
            
            if assessment_result:
                level = assessment_result["assessed_level"]
                confidence = assessment_result["confidence"]
                
                analysis = f"""## Skill Assessment Results for {skill_name.title()}

**Assessed Level**: {level.title()}
**Confidence**: {confidence:.1%}

**Analysis:**
- **Concept Understanding**: {assessment_result['concept_understanding']:.1%}
- **Experience Factor**: {assessment_result['experience_factor']:.1%}

**Current Competencies:**
{self._format_competencies(assessment_result['benchmark_level']['key_concepts'])}

{self._generate_skill_feedback(level, skill_name, assessment_result)}

Would you like me to assess additional skills or analyze gaps for a specific role?"""

                return AgentResponse(
                    content=analysis,
                    metadata={"assessment_result": assessment_result},
                    confidence=0.85,
                    tools_used=["skill_benchmark"]
                )
        
        # Start assessment process
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(self.assessment_questions["technical"])])
        
        response = f"""I'll help you assess your skills comprehensively. Let's start with a structured evaluation.

Please choose a skill you'd like to assess and then answer these questions:

{questions_text}

Additionally, please tell me:
- How many years of experience you have with this skill
- Any certifications or formal training you've completed
- Recent projects where you've applied this skill

This will help me provide an accurate assessment and personalized recommendations."""

        return AgentResponse(
            content=response,
            metadata={"assessment_stage": "skill_questions"},
            confidence=0.9
        )
    
    async def _analyze_skill_gaps(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "current_skills" in context and "target_role" in context:
            current_skills = context["current_skills"]
            target_role = context["target_role"]
            
            gap_analysis = await self.use_tool(
                "skill_gap_analysis",
                current_skills=current_skills,
                target_role=target_role
            )
            
            if gap_analysis:
                readiness = gap_analysis["readiness_score"]
                
                analysis = f"""## Skill Gap Analysis for {target_role.title()}

**Role Readiness**: {readiness:.1f}%

### 🎯 **Current Strengths**
"""
                for strength in gap_analysis["skill_strengths"]:
                    analysis += f"- **{strength['skill']}**: {strength['current_level'].title()} (meets requirement)\n"
                
                analysis += "\n### 📈 **Priority Development Areas**\n"
                for gap in gap_analysis["priority_gaps"]:
                    if gap["gap_type"] == "missing":
                        analysis += f"- **{gap['skill']}**: Need to develop to {gap['required_level']} level\n"
                    else:
                        analysis += f"- **{gap['skill']}**: Upgrade from {gap['current_level']} to {gap['required_level']}\n"
                
                timeline = gap_analysis["development_timeline"]
                analysis += f"""
### ⏱️ **Development Timeline**
- High priority skills: {timeline['high_priority_weeks']} weeks
- Total estimated time: {timeline['estimated_months']:.1f} months

{self._generate_development_strategy(gap_analysis)}"""

                return AgentResponse(
                    content=analysis,
                    metadata={"gap_analysis": gap_analysis},
                    confidence=0.88,
                    tools_used=["skill_gap_analysis"]
                )
        
        # Request information for gap analysis
        response = """To analyze your skill gaps, I need to understand:

1. **Current Skills**: Please list your key skills with proficiency levels (beginner, intermediate, advanced, expert)
2. **Target Role**: What position or career path are you aiming for?
3. **Timeline**: When do you hope to be ready for this role?

Example format:
- Python: Advanced
- Machine Learning: Intermediate  
- Communication: Intermediate
- Target Role: Senior Data Scientist

This will help me identify specific gaps and create a development roadmap."""

        return AgentResponse(
            content=response,
            confidence=0.8
        )
    
    async def _create_development_plan(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if context and "skill_gaps" in context:
            gaps = context["skill_gaps"]
            
            plan = self._build_comprehensive_development_plan(gaps)
            
            return AgentResponse(
                content=plan,
                metadata={"development_plan": gaps},
                confidence=0.85
            )
        
        response = """I'd be happy to create a personalized skill development plan for you.

To build the most effective plan, I need to know:

1. **Specific skills** you want to develop
2. **Current level** for each skill
3. **Target level** you want to reach
4. **Available time** for learning (hours per week)
5. **Learning preferences** (online courses, books, hands-on projects, mentoring)
6. **Career goals** this development supports

This information will help me create a structured, achievable development roadmap with specific milestones and resources."""

        return AgentResponse(
            content=response,
            confidence=0.8
        )
    
    async def _general_skill_guidance(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        # Use LLM for general guidance
        system_prompt = self.get_system_prompt()
        
        full_prompt = f"""{system_prompt}

User message: {message}

Provide helpful guidance about skill assessment, development, or career-relevant skills."""

        try:
            response = await self.llm.ainvoke([{"role": "user", "content": full_prompt}])
            
            return AgentResponse(
                content=response.content,
                confidence=0.75
            )
            
        except Exception as e:
            self.logger.error(f"Error in general guidance: {str(e)}")
            return AgentResponse(
                content="I'm here to help with skill assessment and development. You can ask me to evaluate specific skills, analyze gaps for target roles, or create development plans. What would you like to explore?",
                confidence=0.6
            )
    
    def _format_competencies(self, concepts: List[str]) -> str:
        if not concepts:
            return "- No specific competencies identified"
        return "\n".join([f"- {concept.title()}" for concept in concepts])
    
    def _generate_skill_feedback(self, level: str, skill_name: str, assessment: Dict[str, Any]) -> str:
        feedback = {
            "expert": f"Excellent mastery of {skill_name}! You demonstrate expert-level understanding and can mentor others.",
            "advanced": f"Strong proficiency in {skill_name}. You're ready for complex projects and leadership roles.",
            "intermediate": f"Good foundation in {skill_name}. Focus on advanced concepts and real-world application.",
            "beginner": f"You're building your {skill_name} skills. Focus on fundamentals and hands-on practice."
        }
        
        base_feedback = feedback.get(level, f"You're developing your {skill_name} capabilities.")
        
        if assessment["confidence"] < 0.7:
            base_feedback += " Consider additional practice to strengthen your confidence."
        
        return base_feedback
    
    def _generate_development_strategy(self, gap_analysis: Dict[str, Any]) -> str:
        priority_gaps = gap_analysis["priority_gaps"]
        
        if not priority_gaps:
            return "🎉 **Great news!** You meet the core requirements. Focus on preferred skills for competitive advantage."
        
        strategy = "**Recommended Development Strategy:**\n"
        
        # High-priority items first
        high_priority = [gap for gap in priority_gaps if gap.get("priority") == "high"]
        if high_priority:
            strategy += "1. **Immediate Focus** (Next 2-3 months):\n"
            for gap in high_priority[:2]:  # Top 2 priorities
                strategy += f"   - {gap['skill']}: "
                if gap["gap_type"] == "missing":
                    strategy += f"Start with basics, aim for {gap['required_level']} level\n"
                else:
                    strategy += f"Advance from {gap['current_level']} to {gap['required_level']}\n"
        
        return strategy
    
    def _build_comprehensive_development_plan(self, gaps: List[Dict[str, Any]]) -> str:
        plan = """# 📚 Personalized Skill Development Plan

## Phase 1: Foundation Building (Months 1-2)
"""
        
        for gap in gaps[:2]:  # First 2 skills
            plan += f"""
### {gap['skill']}
- **Current**: {gap.get('current_level', 'Not started')}
- **Target**: {gap['required_level']}
- **Resources**: Online courses, practice projects
- **Timeline**: 4-6 weeks
- **Milestones**: Weekly progress checks
"""
        
        plan += """
## Phase 2: Skill Integration (Months 3-4)
- Combine newly learned skills in practical projects
- Seek feedback from experienced professionals
- Apply skills in real or simulated work scenarios

## Phase 3: Mastery & Application (Months 5-6)
- Advanced topics and specialization
- Mentor others or contribute to open projects
- Prepare for role applications or career transitions

Would you like me to elaborate on any specific skill or suggest detailed resources?"""

        return plan
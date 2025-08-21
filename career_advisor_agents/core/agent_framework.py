from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from langchain.schema import BaseMessage, HumanMessage, AIMessage
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import BaseTool
from langchain_google_genai import ChatGoogleGenerativeAI
import logging
import asyncio
from datetime import datetime
from pydantic import BaseModel


class AgentResponse(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}
    tools_used: List[str] = []
    confidence: float = 0.0
    timestamp: datetime = datetime.now()


class BaseAgent(ABC):
    def __init__(
        self,
        name: str,
        description: str,
        llm: ChatGoogleGenerativeAI,
        tools: Optional[List[BaseTool]] = None,
        memory_window: int = 10,
        temperature: float = 0.7
    ):
        self.name = name
        self.description = description
        self.llm = llm
        self.tools = tools or []
        self.memory = ConversationBufferWindowMemory(
            k=memory_window,
            return_messages=True
        )
        self.logger = self._setup_logger()
        
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger(f"agent.{self.name}")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass
    
    def add_to_memory(self, message: BaseMessage):
        self.memory.chat_memory.add_message(message)
    
    async def process_message(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        try:
            self.logger.info(f"Processing message: {message[:100]}...")
            
            human_message = HumanMessage(content=message)
            self.add_to_memory(human_message)
            
            response = await self._generate_response(message, context)
            
            ai_message = AIMessage(content=response.content)
            self.add_to_memory(ai_message)
            
            self.logger.info(f"Generated response with confidence: {response.confidence}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            return AgentResponse(
                content=f"I encountered an error while processing your request. Please try again.",
                metadata={"error": str(e)},
                confidence=0.0
            )
    
    @abstractmethod
    async def _generate_response(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        pass
    
    def get_conversation_history(self) -> List[BaseMessage]:
        return self.memory.chat_memory.messages
    
    def clear_memory(self):
        self.memory.clear()
        self.logger.info("Memory cleared")
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        for tool in self.tools:
            if tool.name == tool_name:
                try:
                    result = await tool.arun(**kwargs)
                    self.logger.info(f"Tool {tool_name} executed successfully")
                    return result
                except Exception as e:
                    self.logger.error(f"Error using tool {tool_name}: {str(e)}")
                    return None
        
        self.logger.warning(f"Tool {tool_name} not found")
        return None


class AgentOrchestrator:
    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.logger = logging.getLogger("orchestrator")
        
    def register_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        return self.agents.get(name)
    
    async def route_message(
        self, 
        message: str, 
        agent_name: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        if agent_name and agent_name in self.agents:
            return await self.agents[agent_name].process_message(message, context)
        
        best_agent = await self._select_best_agent(message, context)
        if best_agent:
            return await best_agent.process_message(message, context)
        
        return AgentResponse(
            content="I'm not sure which agent can help with that request.",
            confidence=0.0
        )
    
    async def _select_best_agent(
        self, 
        message: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[BaseAgent]:
        keywords_mapping = {
            "career": ["career_analyst", "mentor_bot"],
            "skill": ["skills_assessor", "learning_orchestrator"],
            "learn": ["learning_orchestrator", "progress_monitor"],
            "internship": ["opportunity_scout"],
            "job": ["opportunity_scout", "career_analyst"],
            "progress": ["progress_monitor"],
            "counseling": ["mentor_bot"]
        }
        
        message_lower = message.lower()
        for keyword, agent_names in keywords_mapping.items():
            if keyword in message_lower:
                for agent_name in agent_names:
                    if agent_name in self.agents:
                        return self.agents[agent_name]
        
        if self.agents:
            return list(self.agents.values())[0]
        
        return None
    
    def list_agents(self) -> List[str]:
        return list(self.agents.keys())


class AgentMetrics:
    def __init__(self):
        self.metrics = {}
        
    def record_interaction(self, agent_name: str, response_time: float, confidence: float):
        if agent_name not in self.metrics:
            self.metrics[agent_name] = {
                "total_interactions": 0,
                "avg_response_time": 0.0,
                "avg_confidence": 0.0,
                "response_times": [],
                "confidences": []
            }
        
        agent_metrics = self.metrics[agent_name]
        agent_metrics["total_interactions"] += 1
        agent_metrics["response_times"].append(response_time)
        agent_metrics["confidences"].append(confidence)
        
        agent_metrics["avg_response_time"] = sum(agent_metrics["response_times"]) / len(agent_metrics["response_times"])
        agent_metrics["avg_confidence"] = sum(agent_metrics["confidences"]) / len(agent_metrics["confidences"])
    
    def get_metrics(self, agent_name: str) -> Dict[str, Any]:
        return self.metrics.get(agent_name, {})
    
    def get_all_metrics(self) -> Dict[str, Any]:
        return self.metrics
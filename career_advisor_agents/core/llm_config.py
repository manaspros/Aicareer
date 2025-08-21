import os
from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import logging


class LLMConfig:
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        streaming: bool = False
    ):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming
        self.logger = logging.getLogger(__name__)
        
        if not self.api_key:
            raise ValueError("Google API key is required. Set GOOGLE_API_KEY environment variable.")
    
    def create_llm(self, **kwargs) -> ChatGoogleGenerativeAI:
        config = {
            "model": self.model,
            "google_api_key": self.api_key,
            "temperature": kwargs.get("temperature", self.temperature),
            "convert_system_message_to_human": True,
        }
        
        if self.max_tokens:
            config["max_output_tokens"] = kwargs.get("max_tokens", self.max_tokens)
        
        if self.streaming or kwargs.get("streaming", False):
            config["streaming"] = True
            config["callback_manager"] = CallbackManager([StreamingStdOutCallbackHandler()])
        
        try:
            llm = ChatGoogleGenerativeAI(**config)
            self.logger.info(f"Created LLM with model: {self.model}")
            return llm
        except Exception as e:
            self.logger.error(f"Failed to create LLM: {str(e)}")
            raise


class AgentLLMFactory:
    def __init__(self, config: LLMConfig):
        self.config = config
        self._llm_cache = {}
    
    def get_llm_for_agent(self, agent_type: str, **kwargs) -> ChatGoogleGenerativeAI:
        cache_key = f"{agent_type}_{hash(frozenset(kwargs.items()))}"
        
        if cache_key in self._llm_cache:
            return self._llm_cache[cache_key]
        
        agent_configs = {
            "career_analyst": {"temperature": 0.7},
            "skills_assessor": {"temperature": 0.5},
            "learning_orchestrator": {"temperature": 0.6},
            "progress_monitor": {"temperature": 0.4},
            "opportunity_scout": {"temperature": 0.6},
            "mentor_bot": {"temperature": 0.8}
        }
        
        agent_config = agent_configs.get(agent_type, {})
        agent_config.update(kwargs)
        
        llm = self.config.create_llm(**agent_config)
        self._llm_cache[cache_key] = llm
        
        return llm
    
    def clear_cache(self):
        self._llm_cache.clear()


def create_default_llm_config() -> LLMConfig:
    return LLMConfig(
        model="gemini-2.5-flash",
        temperature=0.7,
        streaming=False
    )


def create_llm_for_testing() -> ChatGoogleGenerativeAI:
    config = LLMConfig(
        model="gemini-2.5-flash",
        temperature=0.1
    )
    return config.create_llm()
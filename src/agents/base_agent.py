"""
Base agent class for the multi-agent research pipeline.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from langchain_community.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain_community.callbacks.manager import get_openai_callback

from ..config import get_llm_config


class BaseAgent(ABC):
    """Base class for all agents in the research pipeline."""
    
    def __init__(self, name: str, model_name: Optional[str] = None):
        self.name = name
        self.llm_config = get_llm_config()
        self.model_name = model_name or self.llm_config.get("model", "gpt-4-turbo-preview")
        self.llm = self._initialize_llm()
        self.system_prompt = self._get_system_prompt()
    
    def _initialize_llm(self):
        """Initialize the language model."""
        if self.llm_config["provider"] == "openai":
            return ChatOpenAI(
                model=self.model_name,
                temperature=0.1,
                api_key=self.llm_config["api_key"]
            )
        elif self.llm_config["provider"] == "local":
            # For local models like Ollama
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                model=self.model_name,
                base_url=self.llm_config["url"]
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_config['provider']}")
    
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass
    
    async def think(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a message and return a response."""
        messages = [SystemMessage(content=self.system_prompt)]
        
        if context:
            context_message = f"Context: {self._format_context(context)}"
            messages.append(HumanMessage(content=context_message))
        
        messages.append(HumanMessage(content=message))
        
        with get_openai_callback() as cb:
            response = await self.llm.ainvoke(messages)
            # Log token usage if needed
            if hasattr(cb, 'total_tokens'):
                print(f"{self.name} used {cb.total_tokens} tokens")
        
        return response.content
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context for the agent."""
        if isinstance(context, dict):
            return "\n".join([f"{k}: {v}" for k, v in context.items()])
        return str(context)
    
    async def complete_task(self, task_description: str) -> Dict[str, Any]:
        """Complete a specific task and return results."""
        result = await self.think(task_description)
        return {
            "agent": self.name,
            "task": task_description,
            "result": result,
            "timestamp": self._get_timestamp()
        }
    
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() 
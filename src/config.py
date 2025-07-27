"""
Configuration settings for the multi-agent research pipeline.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4-turbo-preview"
    local_model_url: Optional[str] = None  # For Ollama or other local models
    
    # Search Configuration
    search_engine: str = "duckduckgo"  # duckduckgo, serpapi, etc.
    max_search_results: int = 10
    search_delay: float = 2.0  # Delay between searches in seconds
    max_search_retries: int = 3  # Maximum retry attempts for searches
    subagent_start_delay: float = 3.0  # Delay between subagent starts
    
    # Memory Configuration
    memory_type: str = "chroma"  # chroma, in_memory
    chroma_persist_directory: str = "./chroma_db"
    
    # Agent Configuration
    max_iterations: int = 3
    max_subagents: int = 4
    research_timeout: int = 300  # seconds
    
    # Citation Configuration
    citation_style: str = "markdown"  # markdown, apa, mla
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_llm_config():
    """Get LLM configuration based on available settings."""
    if settings.openai_api_key:
        return {
            "provider": "openai",
            "model": settings.openai_model,
            "api_key": settings.openai_api_key
        }
    elif settings.local_model_url:
        return {
            "provider": "local",
            "url": settings.local_model_url
        }
    else:
        raise ValueError("No LLM configuration found. Set OPENAI_API_KEY or LOCAL_MODEL_URL")


def get_search_config():
    """Get search configuration."""
    return {
        "engine": settings.search_engine,
        "max_results": settings.max_search_results
    }


def get_memory_config():
    """Get memory configuration."""
    return {
        "type": settings.memory_type,
        "persist_directory": settings.chroma_persist_directory
    } 
"""
Tests for agent classes.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch

from src.agents import LeadResearcherAgent, Subagent, CitationAgent


class TestLeadResearcherAgent:
    """Test LeadResearcherAgent functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create a LeadResearcherAgent instance."""
        with patch('src.agents.base_agent.get_llm_config') as mock_config:
            mock_config.return_value = {
                "provider": "openai",
                "model": "gpt-4-turbo-preview",
                "api_key": "test_key"
            }
            return LeadResearcherAgent()
    
    @pytest.mark.asyncio
    async def test_plan_research(self, agent):
        """Test research planning."""
        query = "artificial intelligence trends 2024"
        
        with patch.object(agent, 'think') as mock_think:
            mock_think.return_value = '{"objectives": ["test"], "scope": "test scope"}'
            
            result = await agent.plan_research(query)
            
            assert isinstance(result, dict)
            assert "objectives" in result
            assert "scope" in result
    
    @pytest.mark.asyncio
    async def test_decompose_tasks(self, agent):
        """Test task decomposition."""
        query = "machine learning applications"
        plan = {"objectives": ["test"], "scope": "test"}
        
        with patch.object(agent, 'think') as mock_think:
            mock_think.return_value = '[{"id": "task_1", "title": "Test Task"}]'
            
            result = await agent.decompose_tasks(query, plan)
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert "id" in result[0]


class TestSubagent:
    """Test Subagent functionality."""
    
    @pytest.fixture
    def task(self):
        """Create a sample task."""
        return {
            "id": "test_task",
            "title": "Test Research Task",
            "description": "Test task description",
            "focus_area": "testing",
            "search_queries": ["test query"],
            "expected_output": "test output"
        }
    
    @pytest.fixture
    def agent(self, task):
        """Create a Subagent instance."""
        with patch('src.agents.base_agent.get_llm_config') as mock_config:
            mock_config.return_value = {
                "provider": "openai",
                "model": "gpt-4-turbo-preview",
                "api_key": "test_key"
            }
            return Subagent(task)
    
    @pytest.mark.asyncio
    async def test_research(self, agent):
        """Test research execution."""
        with patch.object(agent, '_web_search') as mock_search:
            mock_search.return_value = [{"title": "Test", "source": "test.com"}]
            
            with patch.object(agent, '_evaluate_results') as mock_eval:
                mock_eval.return_value = {"summary": "Test summary"}
                
                result = await agent.research()
                
                assert isinstance(result, dict)
                assert "agent" in result
                assert "task" in result
                assert "search_results" in result
                assert "evaluation" in result


class TestCitationAgent:
    """Test CitationAgent functionality."""
    
    @pytest.fixture
    def agent(self):
        """Create a CitationAgent instance."""
        with patch('src.agents.base_agent.get_llm_config') as mock_config:
            mock_config.return_value = {
                "provider": "openai",
                "model": "gpt-4-turbo-preview",
                "api_key": "test_key"
            }
            return CitationAgent()
    
    def test_extract_sources(self, agent):
        """Test source extraction."""
        subagent_results = [
            {
                "search_results": [
                    {"title": "Test", "source": "test.com", "snippet": "test"}
                ],
                "evaluation": {
                    "credible_sources": ["test2.com"]
                }
            }
        ]
        
        sources = agent._extract_sources(subagent_results)
        
        assert isinstance(sources, list)
        assert len(sources) > 0
        assert "url" in sources[0]
        assert "title" in sources[0]
    
    def test_extract_domain(self, agent):
        """Test domain extraction."""
        url = "https://example.com/path"
        domain = agent._extract_domain(url)
        
        assert domain == "example.com" 
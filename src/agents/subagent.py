"""
Subagent for performing focused web searches and evaluations.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from duckduckgo_search import DDGS

from .base_agent import BaseAgent
from ..config import get_search_config


class Subagent(BaseAgent):
    """Subagent for focused research on specific aspects."""
    
    def __init__(self, task: Dict[str, Any], model_name: Optional[str] = None):
        self.task = task
        self.search_config = get_search_config()
        super().__init__(f"Subagent_{task.get('id', 'unknown')}", model_name)
        self.search_engine = DDGS()
    
    def _get_system_prompt(self) -> str:
        return f"""You are a Subagent focused on: {self.task.get('focus_area', 'research')}

Your task: {self.task.get('description', 'Perform focused research')}

Your responsibilities:
1. Conduct focused web searches on your assigned topic
2. Evaluate and filter search results for relevance and quality
3. Extract key information and insights
4. Provide structured, factual responses
5. Identify credible sources and cite them properly

Always respond in JSON format for structured data processing.
Be thorough, objective, and focus on your specific research area."""

    async def research(self) -> Dict[str, Any]:
        """Perform the assigned research task."""
        search_queries = self.task.get("search_queries", [self.task.get("title", "")])
        
        # Perform web searches
        search_results = []
        for query in search_queries:
            results = await self._web_search(query)
            search_results.extend(results)
        
        # Evaluate and analyze results
        evaluation = await self._evaluate_results(search_results)
        
        return {
            "agent": self.name,
            "task": self.task,
            "search_results": search_results,
            "evaluation": evaluation,
            "timestamp": self._get_timestamp()
        }

    async def _web_search(self, query: str) -> List[Dict[str, Any]]:
        """Perform web search using DuckDuckGo."""
        try:
            # Use DuckDuckGo search
            results = []
            search_results = self.search_engine.text(
                query, 
                max_results=self.search_config["max_results"]
            )
            
            for result in search_results:
                results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("body", ""),
                    "source": result.get("link", ""),
                    "query": query
                })
            
            return results
        except Exception as e:
            print(f"Search error for query '{query}': {e}")
            return []

    async def _evaluate_results(self, search_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evaluate and analyze search results."""
        if not search_results:
            return {
                "summary": "No search results found",
                "key_insights": [],
                "credible_sources": [],
                "confidence": "low"
            }
        
        # Prepare results for evaluation
        results_text = "\n\n".join([
            f"Title: {r['title']}\nSource: {r['source']}\nContent: {r['snippet']}"
            for r in search_results
        ])
        
        prompt = f"""
        Task Focus: {self.task.get('focus_area', 'research')}
        Expected Output: {self.task.get('expected_output', 'comprehensive analysis')}
        
        Search Results:
        {results_text}
        
        Evaluate these search results and provide:
        1. Summary of findings
        2. Key insights relevant to the task
        3. Assessment of source credibility
        4. Gaps or limitations in the information
        
        Respond with a JSON object:
        {{
            "summary": "comprehensive summary of findings",
            "key_insights": ["list of key insights"],
            "credible_sources": ["list of most credible sources"],
            "limitations": ["list of limitations or gaps"],
            "confidence": "high/medium/low",
            "relevance_score": <0-100>
        }}
        """
        
        response = await self.think(prompt)
        try:
            evaluation = json.loads(response)
            evaluation["sources_analyzed"] = len(search_results)
            return evaluation
        except json.JSONDecodeError:
            # Fallback evaluation
            return {
                "summary": f"Analyzed {len(search_results)} search results for {self.task.get('focus_area', 'research')}",
                "key_insights": ["Information gathered from multiple sources"],
                "credible_sources": [r["source"] for r in search_results[:3]],
                "limitations": ["Limited evaluation due to parsing error"],
                "confidence": "medium",
                "relevance_score": 70,
                "sources_analyzed": len(search_results),
                "raw_response": response
            }

    async def complete_task(self, task_description: str) -> Dict[str, Any]:
        """Complete the assigned research task."""
        return await self.research() 
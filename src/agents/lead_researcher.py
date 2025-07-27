"""
LeadResearcher agent for planning, task decomposition, and synthesis.
"""

import json
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent


class LeadResearcherAgent(BaseAgent):
    """Lead researcher agent that orchestrates the research process."""
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__("LeadResearcher", model_name)
    
    def _get_system_prompt(self) -> str:
        return """You are a LeadResearcher agent responsible for planning, coordinating, and synthesizing research.

Your responsibilities:
1. Plan research approaches for complex queries
2. Decompose research tasks into parallelizable sub-tasks
3. Synthesize results from multiple subagents
4. Determine if additional research iterations are needed
5. Ensure comprehensive coverage of the research topic

Always respond in JSON format for structured data processing.
Be thorough, analytical, and systematic in your approach."""

    async def plan_research(self, query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Plan the research approach for a given query."""
        prompt = f"""
        Research Query: {query}
        
        Create a comprehensive research plan that includes:
        1. Research objectives and scope
        2. Key areas to investigate
        3. Potential sources and methodologies
        4. Success criteria
        5. Timeline considerations
        
        Respond with a JSON object containing:
        {{
            "objectives": ["list of research objectives"],
            "scope": "description of research scope",
            "key_areas": ["list of key areas to investigate"],
            "methodologies": ["list of research methodologies"],
            "success_criteria": ["list of success criteria"],
            "estimated_iterations": <number>
        }}
        """
        
        response = await self.think(prompt, context)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                "objectives": [query],
                "scope": "Comprehensive research on the given topic",
                "key_areas": ["General information", "Current trends", "Expert opinions"],
                "methodologies": ["Web search", "Content analysis"],
                "success_criteria": ["Comprehensive coverage", "Verified sources"],
                "estimated_iterations": 2,
                "raw_response": response
            }

    async def decompose_tasks(self, query: str, plan: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Decompose the research query into parallelizable sub-tasks."""
        prompt = f"""
        Research Query: {query}
        Research Plan: {json.dumps(plan, indent=2)}
        
        Decompose this research into 2-4 parallelizable sub-tasks that can be executed by different subagents.
        Each sub-task should focus on a specific aspect of the research.
        
        Respond with a JSON array of sub-tasks:
        [
            {{
                "id": "task_1",
                "title": "Task title",
                "description": "Detailed task description",
                "focus_area": "Specific area of focus",
                "search_queries": ["specific search terms to use"],
                "expected_output": "What this task should produce"
            }}
        ]
        """
        
        response = await self.think(prompt, context)
        try:
            tasks = json.loads(response)
            # Ensure tasks have proper structure
            for i, task in enumerate(tasks):
                if "id" not in task:
                    task["id"] = f"task_{i+1}"
            return tasks
        except json.JSONDecodeError:
            # Fallback decomposition
            return [
                {
                    "id": "task_1",
                    "title": "General Information Search",
                    "description": f"Search for general information about {query}",
                    "focus_area": "Overview and basics",
                    "search_queries": [query, f"what is {query}"],
                    "expected_output": "Comprehensive overview of the topic"
                },
                {
                    "id": "task_2", 
                    "title": "Current Trends and Developments",
                    "description": f"Find current trends and recent developments related to {query}",
                    "focus_area": "Recent developments",
                    "search_queries": [f"{query} 2024", f"{query} trends", f"{query} latest"],
                    "expected_output": "Current state and trends"
                }
            ]

    async def synthesize_results(self, query: str, results: List[Dict[str, Any]], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Synthesize results from multiple subagents into a coherent research report."""
        prompt = f"""
        Research Query: {query}
        Subagent Results: {json.dumps(results, indent=2)}
        
        Synthesize these results into a comprehensive research report.
        
        Respond with a JSON object containing:
        {{
            "executive_summary": "Brief overview of findings",
            "key_findings": ["list of main findings"],
            "detailed_analysis": "Comprehensive analysis of the research",
            "sources": ["list of sources used"],
            "gaps_identified": ["any gaps in the research"],
            "recommendations": ["recommendations for further research"],
            "confidence_level": "high/medium/low",
            "completeness_score": <0-100>
        }}
        """
        
        response = await self.think(prompt, context)
        try:
            synthesis = json.loads(response)
            synthesis["query"] = query
            synthesis["synthesis_timestamp"] = self._get_timestamp()
            return synthesis
        except json.JSONDecodeError:
            # Fallback synthesis
            return {
                "query": query,
                "executive_summary": f"Research completed on {query}",
                "key_findings": ["Research findings compiled from multiple sources"],
                "detailed_analysis": response,
                "sources": [],
                "gaps_identified": [],
                "recommendations": [],
                "confidence_level": "medium",
                "completeness_score": 70,
                "synthesis_timestamp": self._get_timestamp(),
                "raw_response": response
            }

    async def needs_more_research(self, synthesis: Dict[str, Any], iteration: int = 1) -> Dict[str, Any]:
        """Determine if additional research iterations are needed."""
        prompt = f"""
        Current Research Synthesis: {json.dumps(synthesis, indent=2)}
        Current Iteration: {iteration}
        
        Evaluate if additional research is needed based on:
        1. Completeness of findings
        2. Confidence level
        3. Identified gaps
        4. Quality of sources
        
        Respond with a JSON object:
        {{
            "needs_more_research": true/false,
            "reasoning": "explanation of decision",
            "specific_gaps": ["specific areas that need more research"],
            "refined_queries": ["specific queries for next iteration"],
            "priority": "high/medium/low"
        }}
        """
        
        response = await self.think(prompt)
        try:
            decision = json.loads(response)
            decision["current_iteration"] = iteration
            return decision
        except json.JSONDecodeError:
            # Default decision based on iteration count
            return {
                "needs_more_research": iteration < 3,  # Max 3 iterations
                "reasoning": f"Default decision based on iteration {iteration}",
                "specific_gaps": [],
                "refined_queries": [],
                "priority": "medium",
                "current_iteration": iteration,
                "raw_response": response
            } 
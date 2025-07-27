"""
Main orchestrator for the multi-agent research pipeline.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

from .agents import LeadResearcherAgent, Subagent, CitationAgent
from .memory import ResearchMemory
from .config import settings


class ResearchOrchestrator:
    """Main orchestrator for the multi-agent research pipeline."""
    
    def __init__(self):
        self.lead_researcher = LeadResearcherAgent()
        self.memory = ResearchMemory()
        self.citation_agent = CitationAgent()
        self.current_iteration = 0
    
    async def run_research(self, query: str, max_iterations: Optional[int] = None) -> Dict[str, Any]:
        """Run the complete research pipeline."""
        if max_iterations is None:
            max_iterations = settings.max_iterations
        
        print(f"🚀 Starting research on: {query}")
        
        # Step 1: LeadResearcher plans approach
        print("📋 Planning research approach...")
        plan = await self.lead_researcher.plan_research(query)
        context_id = self.memory.save_plan(query, plan)
        print(f"✅ Research plan created and saved (ID: {context_id})")
        
        # Step 2: Retrieve context from memory
        context = self.memory.get_latest_context(query)
        
        # Step 3: Decompose into sub-tasks
        print("🔍 Decomposing research into sub-tasks...")
        sub_tasks = await self.lead_researcher.decompose_tasks(query, plan, context)
        print(f"✅ Created {len(sub_tasks)} sub-tasks")
        
        # Main research loop
        all_results = []
        current_query = query
        
        for iteration in range(1, max_iterations + 1):
            self.current_iteration = iteration
            print(f"\n🔄 Starting iteration {iteration}/{max_iterations}")
            
            # Step 4: Create and run subagents in parallel
            subagent_results = await self._run_subagents(sub_tasks, current_query)
            all_results.extend(subagent_results)
            
            # Step 5: Synthesize results
            print("🧠 Synthesizing results...")
            synthesis = await self.lead_researcher.synthesize_results(
                current_query, 
                subagent_results, 
                context
            )
            
            # Step 6: Check if more research is needed
            print("🤔 Evaluating if more research is needed...")
            decision = await self.lead_researcher.needs_more_research(synthesis, iteration)
            
            if not decision.get("needs_more_research", False) or iteration >= max_iterations:
                print(f"✅ Research complete after {iteration} iteration(s)")
                break
            
            # Prepare for next iteration
            print(f"🔄 More research needed: {decision.get('reasoning', 'Unknown reason')}")
            if decision.get("refined_queries"):
                current_query = decision["refined_queries"][0]  # Use first refined query
                sub_tasks = await self._create_refined_tasks(current_query, decision)
            else:
                # Create new sub-tasks based on gaps
                sub_tasks = await self._create_gap_filling_tasks(synthesis, decision)
        
        # Step 7: Add citations
        print("📚 Adding citations...")
        final_report = await self.citation_agent.process_report(synthesis, all_results)
        
        # Step 8: Persist results
        self._persist_results(query, final_report, all_results)
        
        print("🎉 Research pipeline completed successfully!")
        return final_report
    
    async def _run_subagents(self, sub_tasks: List[Dict[str, Any]], query: str) -> List[Dict[str, Any]]:
        """Run subagents in parallel for the given tasks."""
        print(f"🤖 Running {len(sub_tasks)} subagents in parallel...")
        
        # Create subagents
        subagents = []
        for i, task in enumerate(sub_tasks[:settings.max_subagents]):
            subagent = Subagent(task)
            subagents.append(subagent)
            print(f"  - Created {subagent.name} for: {task.get('title', 'Unknown task')}")
        
        # Run subagents in parallel
        tasks = [subagent.research() for subagent in subagents]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"❌ Error in {subagents[i].name}: {result}")
                processed_results.append({
                    "agent": subagents[i].name,
                    "task": sub_tasks[i],
                    "error": str(result),
                    "timestamp": datetime.utcnow().isoformat()
                })
            else:
                processed_results.append(result)
                print(f"✅ {subagents[i].name} completed successfully")
        
        return processed_results
    
    async def _create_refined_tasks(self, refined_query: str, decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create refined sub-tasks based on the research decision."""
        plan = {
            "objectives": [f"Refined research on: {refined_query}"],
            "scope": "Addressing identified gaps",
            "key_areas": decision.get("specific_gaps", ["General research"]),
            "methodologies": ["Web search", "Content analysis"],
            "success_criteria": ["Address identified gaps"],
            "estimated_iterations": 1
        }
        
        return await self.lead_researcher.decompose_tasks(refined_query, plan)
    
    async def _create_gap_filling_tasks(self, synthesis: Dict[str, Any], decision: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create tasks to fill identified gaps in the research."""
        gaps = decision.get("specific_gaps", ["General follow-up research"])
        
        tasks = []
        for i, gap in enumerate(gaps):
            tasks.append({
                "id": f"gap_task_{i+1}",
                "title": f"Address Gap: {gap}",
                "description": f"Research to address the identified gap: {gap}",
                "focus_area": gap,
                "search_queries": [gap, f"{gap} research", f"{gap} latest"],
                "expected_output": f"Information to address the gap: {gap}"
            })
        
        return tasks
    
    def _persist_results(self, query: str, final_report: Dict[str, Any], all_results: List[Dict[str, Any]]):
        """Persist the final research results."""
        # Save to memory
        context = self.memory.get_latest_context(query)
        if context:
            context.synthesis = final_report["cited_report"]
            context.results = all_results
            context.iteration = self.current_iteration
            # Note: In a real implementation, you'd update the context in memory
        
        # Save to file (optional)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"research_results_{timestamp}.json"
        
        try:
            with open(filename, 'w') as f:
                json.dump({
                    "query": query,
                    "timestamp": timestamp,
                    "iteration": self.current_iteration,
                    "final_report": final_report,
                    "all_results": all_results
                }, f, indent=2)
            print(f"💾 Results saved to: {filename}")
        except Exception as e:
            print(f"⚠️  Warning: Could not save results to file: {e}")
    
    async def get_research_status(self, query: str) -> Dict[str, Any]:
        """Get the current status of research for a query."""
        context = self.memory.get_latest_context(query)
        if not context:
            return {"status": "not_found", "query": query}
        
        return {
            "status": "found",
            "query": query,
            "iteration": context.iteration,
            "created_at": context.created_at,
            "updated_at": context.updated_at,
            "has_synthesis": context.synthesis is not None
        } 
"""
CitationAgent for processing documents and inserting citations.
"""

import json
import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse

from .base_agent import BaseAgent


class CitationAgent(BaseAgent):
    """Agent responsible for citation detection and insertion."""
    
    def __init__(self, model_name: Optional[str] = None):
        super().__init__("CitationAgent", model_name)
    
    def _get_system_prompt(self) -> str:
        return """You are a CitationAgent responsible for processing research reports and inserting proper citations.

Your responsibilities:
1. Identify statements that need citations
2. Match statements to appropriate sources
3. Insert citations in the specified format
4. Ensure all claims are properly attributed
5. Maintain the original content while adding citations

Always respond in JSON format for structured data processing.
Be thorough in citation placement and maintain academic standards."""

    async def process_report(self, synthesis: Dict[str, Any], subagent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process the research report and add citations."""
        # Extract all sources from subagent results
        all_sources = self._extract_sources(subagent_results)
        
        # Process the synthesis for citation insertion
        cited_report = await self._add_citations(synthesis, all_sources)
        
        return {
            "original_synthesis": synthesis,
            "cited_report": cited_report,
            "sources_used": all_sources,
            "citation_count": len(cited_report.get("citations", [])),
            "timestamp": self._get_timestamp()
        }

    def _extract_sources(self, subagent_results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract and deduplicate sources from subagent results."""
        sources = []
        seen_urls = set()
        
        for result in subagent_results:
            # Extract sources from search results
            if "search_results" in result:
                for search_result in result["search_results"]:
                    url = search_result.get("source", "")
                    if url and url not in seen_urls:
                        seen_urls.add(url)
                        sources.append({
                            "url": url,
                            "title": search_result.get("title", ""),
                            "domain": self._extract_domain(url),
                            "context": search_result.get("snippet", "")
                        })
            
            # Extract sources from evaluation
            if "evaluation" in result and "credible_sources" in result["evaluation"]:
                for source in result["evaluation"]["credible_sources"]:
                    if source not in seen_urls:
                        seen_urls.add(source)
                        sources.append({
                            "url": source,
                            "title": f"Source from {result.get('agent', 'unknown')}",
                            "domain": self._extract_domain(source),
                            "context": "Credible source identified by subagent"
                        })
        
        return sources

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return url

    async def _add_citations(self, synthesis: Dict[str, Any], sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add citations to the research synthesis."""
        # Prepare content for citation analysis
        content_sections = []
        
        if "executive_summary" in synthesis:
            content_sections.append(("executive_summary", synthesis["executive_summary"]))
        
        if "detailed_analysis" in synthesis:
            content_sections.append(("detailed_analysis", synthesis["detailed_analysis"]))
        
        if "key_findings" in synthesis:
            content_sections.append(("key_findings", "\n".join(synthesis["key_findings"])))
        
        # Process each section for citations
        cited_sections = {}
        all_citations = []
        
        for section_name, content in content_sections:
            section_citations = await self._process_section_for_citations(content, sources)
            cited_sections[section_name] = section_citations["cited_content"]
            all_citations.extend(section_citations["citations"])
        
        # Create the final cited report
        cited_report = synthesis.copy()
        for section_name, cited_content in cited_sections.items():
            cited_report[section_name] = cited_content
        
        cited_report["citations"] = all_citations
        cited_report["citation_metadata"] = {
            "total_citations": len(all_citations),
            "sources_used": len(sources),
            "citation_style": "markdown"
        }
        
        return cited_report

    async def _process_section_for_citations(self, content: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Process a content section and add citations."""
        if not content or not sources:
            return {
                "cited_content": content,
                "citations": []
            }
        
        # Prepare sources for the agent
        sources_text = "\n".join([
            f"Source {i+1}: {source['title']} ({source['url']}) - {source['context'][:200]}..."
            for i, source in enumerate(sources)
        ])
        
        prompt = f"""
        Content to process:
        {content}
        
        Available sources:
        {sources_text}
        
        Analyze the content and identify statements that need citations. For each statement that requires a citation:
        1. Identify the specific claim or fact
        2. Match it to the most appropriate source
        3. Insert a citation in markdown format: [Source X](url)
        
        Respond with a JSON object:
        {{
            "cited_content": "content with citations inserted",
            "citations": [
                {{
                    "claim": "specific claim that was cited",
                    "source_index": <0-based index of source>,
                    "source_url": "url of the source",
                    "citation_markdown": "[Source X](url)"
                }}
            ]
        }}
        """
        
        response = await self.think(prompt)
        try:
            result = json.loads(response)
            
            # Validate and clean up citations
            validated_citations = []
            for citation in result.get("citations", []):
                source_index = citation.get("source_index", 0)
                if 0 <= source_index < len(sources):
                    citation["source_url"] = sources[source_index]["url"]
                    citation["source_title"] = sources[source_index]["title"]
                    validated_citations.append(citation)
            
            return {
                "cited_content": result.get("cited_content", content),
                "citations": validated_citations
            }
        except json.JSONDecodeError:
            # Fallback: simple citation insertion
            return {
                "cited_content": content,
                "citations": []
            }

    async def complete_task(self, task_description: str) -> Dict[str, Any]:
        """Complete citation processing task."""
        # This would be called with synthesis and subagent results
        # For now, return a placeholder
        return {
            "agent": self.name,
            "task": task_description,
            "result": "Citation processing completed",
            "timestamp": self._get_timestamp()
        } 
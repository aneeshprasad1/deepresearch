#!/usr/bin/env python3
"""
Example usage of the Multi-Agent Research Pipeline.

This script demonstrates how to use the research pipeline programmatically
and shows different configuration options.
"""

import asyncio
import json
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.orchestrator import ResearchOrchestrator
from src.config import settings


async def basic_research_example():
    """Basic research example."""
    print("🔍 Basic Research Example")
    print("=" * 50)
    
    orchestrator = ResearchOrchestrator()
    
    # Run research on a simple query
    query = "artificial intelligence trends 2024"
    result = await orchestrator.run_research(query, max_iterations=2)
    
    # Display key results
    cited_report = result.get("cited_report", {})
    
    print(f"\n📊 Research Results for: {query}")
    print(f"Confidence Level: {cited_report.get('confidence_level', 'Unknown')}")
    print(f"Completeness Score: {cited_report.get('completeness_score', 'Unknown')}")
    print(f"Sources Used: {len(result.get('sources_used', []))}")
    print(f"Citations Added: {result.get('citation_count', 0)}")
    
    # Save results
    with open("example_basic_results.json", "w") as f:
        json.dump(result, f, indent=2)
    print("💾 Results saved to: example_basic_results.json")


async def advanced_research_example():
    """Advanced research example with custom configuration."""
    print("\n🚀 Advanced Research Example")
    print("=" * 50)
    
    orchestrator = ResearchOrchestrator()
    
    # More complex query with multiple iterations
    query = "quantum computing applications in cryptography and machine learning"
    result = await orchestrator.run_research(query, max_iterations=3)
    
    # Display detailed results
    cited_report = result.get("cited_report", {})
    
    print(f"\n📊 Advanced Research Results for: {query}")
    print(f"Executive Summary: {cited_report.get('executive_summary', 'No summary available')[:200]}...")
    
    # Show key findings
    findings = cited_report.get("key_findings", [])
    if findings:
        print(f"\n🔑 Key Findings ({len(findings)}):")
        for i, finding in enumerate(findings[:3], 1):  # Show first 3
            print(f"  {i}. {finding}")
    
    # Show gaps identified
    gaps = cited_report.get("gaps_identified", [])
    if gaps:
        print(f"\n⚠️  Gaps Identified ({len(gaps)}):")
        for i, gap in enumerate(gaps[:2], 1):  # Show first 2
            print(f"  {i}. {gap}")
    
    # Save results
    with open("example_advanced_results.json", "w") as f:
        json.dump(result, f, indent=2)
    print("💾 Results saved to: example_advanced_results.json")


async def status_check_example():
    """Example of checking research status."""
    print("\n📋 Status Check Example")
    print("=" * 50)
    
    orchestrator = ResearchOrchestrator()
    
    # Check status for a query
    query = "artificial intelligence trends 2024"
    status = await orchestrator.get_research_status(query)
    
    print(f"Status for: {query}")
    print(f"Found: {status.get('status') == 'found'}")
    if status.get('status') == 'found':
        print(f"Iteration: {status.get('iteration')}")
        print(f"Created: {status.get('created_at')}")
        print(f"Has Synthesis: {status.get('has_synthesis')}")


def configuration_example():
    """Example of configuration options."""
    print("\n⚙️  Configuration Example")
    print("=" * 50)
    
    print("Current Configuration:")
    print(f"  Max Iterations: {settings.max_iterations}")
    print(f"  Max Subagents: {settings.max_subagents}")
    print(f"  Search Engine: {settings.search_engine}")
    print(f"  Memory Type: {settings.memory_type}")
    print(f"  Citation Style: {settings.citation_style}")
    
    # Show LLM configuration
    try:
        from src.config import get_llm_config
        llm_config = get_llm_config()
        print(f"  LLM Provider: {llm_config['provider']}")
        if llm_config['provider'] == 'openai':
            print(f"  OpenAI Model: {settings.openai_model}")
    except Exception as e:
        print(f"  LLM Configuration: {e}")


async def main():
    """Run all examples."""
    print("🎯 Multi-Agent Research Pipeline Examples")
    print("=" * 60)
    
    try:
        # Run examples
        await basic_research_example()
        await advanced_research_example()
        await status_check_example()
        configuration_example()
        
        print("\n✅ All examples completed successfully!")
        print("\n📁 Generated files:")
        print("  - example_basic_results.json")
        print("  - example_advanced_results.json")
        print("  - research_results_*.json (auto-generated)")
        
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        print("Make sure you have:")
        print("  1. Installed dependencies: pip install -r requirements.txt")
        print("  2. Set up configuration: python main.py init")
        print("  3. Added your OpenAI API key to .env file")


if __name__ == "__main__":
    asyncio.run(main()) 
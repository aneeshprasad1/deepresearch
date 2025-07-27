"""
CLI interface for the multi-agent research pipeline.
"""

import asyncio
import json
from typing import Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.markdown import Markdown

from .orchestrator import ResearchOrchestrator
from .config import settings

app = typer.Typer(help="Multi-Agent Research Pipeline CLI")
console = Console()


@app.command()
def research(
    query: str = typer.Argument(..., help="Research query to investigate"),
    max_iterations: Optional[int] = typer.Option(
        None, 
        "--iterations", "-i", 
        help="Maximum number of research iterations"
    ),
    output_file: Optional[str] = typer.Option(
        None, 
        "--output", "-o", 
        help="Output file for results (JSON format)"
    ),
    verbose: bool = typer.Option(
        False, 
        "--verbose", "-v", 
        help="Enable verbose output"
    )
):
    """Run research on a given query."""
    
    # Validate configuration
    try:
        from .config import get_llm_config
        llm_config = get_llm_config()
        console.print(f"✅ LLM configured: {llm_config['provider']}")
    except Exception as e:
        console.print(f"❌ Configuration error: {e}")
        raise typer.Exit(1)
    
    # Display research parameters
    console.print(Panel(
        f"[bold blue]Research Query:[/bold blue] {query}\n"
        f"[bold blue]Max Iterations:[/bold blue] {max_iterations or settings.max_iterations}\n"
        f"[bold blue]Output File:[/bold blue] {output_file or 'Auto-generated'}",
        title="Research Parameters",
        border_style="blue"
    ))
    
    # Run research
    async def run_research():
        orchestrator = ResearchOrchestrator()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Running research pipeline...", total=None)
            
            try:
                result = await orchestrator.run_research(query, max_iterations)
                progress.update(task, description="Research completed!")
                
                # Display results
                _display_results(result, output_file, verbose)
                
            except Exception as e:
                console.print(f"❌ Research failed: {e}")
                raise typer.Exit(1)
    
    asyncio.run(run_research())


@app.command()
def status(
    query: str = typer.Argument(..., help="Query to check status for")
):
    """Check the status of research for a query."""
    
    async def check_status():
        orchestrator = ResearchOrchestrator()
        status_info = await orchestrator.get_research_status(query)
        
        if status_info["status"] == "not_found":
            console.print(f"❌ No research found for: {query}")
            return
        
        # Create status table
        table = Table(title=f"Research Status: {query}")
        table.add_column("Field", style="cyan")
        table.add_column("Value", style="green")
        
        table.add_row("Status", "Found")
        table.add_row("Iteration", str(status_info["iteration"]))
        table.add_row("Created", status_info["created_at"])
        table.add_row("Updated", status_info["updated_at"])
        table.add_row("Has Synthesis", "✅" if status_info["has_synthesis"] else "❌")
        
        console.print(table)
    
    asyncio.run(check_status())


@app.command()
def config():
    """Display current configuration."""
    
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    # LLM Configuration
    try:
        llm_config = get_llm_config()
        table.add_row("LLM Provider", llm_config["provider"])
        if llm_config["provider"] == "openai":
            table.add_row("OpenAI Model", settings.openai_model)
        elif llm_config["provider"] == "local":
            table.add_row("Local Model URL", settings.local_model_url)
    except:
        table.add_row("LLM Provider", "❌ Not configured")
    
    # Search Configuration
    table.add_row("Search Engine", settings.search_engine)
    table.add_row("Max Search Results", str(settings.max_search_results))
    
    # Memory Configuration
    table.add_row("Memory Type", settings.memory_type)
    if settings.memory_type == "chroma":
        table.add_row("Chroma Directory", settings.chroma_persist_directory)
    
    # Agent Configuration
    table.add_row("Max Iterations", str(settings.max_iterations))
    table.add_row("Max Subagents", str(settings.max_subagents))
    table.add_row("Research Timeout", f"{settings.research_timeout}s")
    
    # Citation Configuration
    table.add_row("Citation Style", settings.citation_style)
    
    console.print(table)


def _display_results(result: dict, output_file: Optional[str], verbose: bool):
    """Display research results."""
    
    # Extract the cited report
    cited_report = result.get("cited_report", {})
    
    # Display executive summary
    if "executive_summary" in cited_report:
        console.print(Panel(
            Markdown(cited_report["executive_summary"]),
            title="Executive Summary",
            border_style="green"
        ))
    
    # Display key findings
    if "key_findings" in cited_report:
        console.print("\n[bold green]Key Findings:[/bold green]")
        for i, finding in enumerate(cited_report["key_findings"], 1):
            console.print(f"  {i}. {finding}")
    
    # Display detailed analysis
    if "detailed_analysis" in cited_report and verbose:
        console.print(Panel(
            Markdown(cited_report["detailed_analysis"]),
            title="Detailed Analysis",
            border_style="blue"
        ))
    
    # Display sources
    if "sources_used" in result:
        console.print(f"\n[bold blue]Sources Used:[/bold blue] {len(result['sources_used'])}")
        if verbose:
            for i, source in enumerate(result["sources_used"][:5], 1):  # Show first 5
                console.print(f"  {i}. {source.get('title', 'No title')} - {source.get('url', 'No URL')}")
    
    # Display citation metadata
    if "citation_metadata" in cited_report:
        metadata = cited_report["citation_metadata"]
        console.print(f"\n[bold blue]Citations:[/bold blue] {metadata.get('total_citations', 0)} citations added")
    
    # Save to file if specified
    if output_file:
        try:
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            console.print(f"\n💾 Results saved to: {output_file}")
        except Exception as e:
            console.print(f"⚠️  Warning: Could not save to {output_file}: {e}")


@app.command()
def init():
    """Initialize the research pipeline (create necessary directories)."""
    
    # Create necessary directories
    directories = [
        Path(settings.chroma_persist_directory),
        Path("data"),
        Path("logs")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        console.print(f"✅ Created directory: {directory}")
    
    # Create .env template if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        env_template = """# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4-turbo-preview
# LOCAL_MODEL_URL=http://localhost:11434  # For Ollama

# Search Configuration
SEARCH_ENGINE=duckduckgo
MAX_SEARCH_RESULTS=10

# Memory Configuration
MEMORY_TYPE=chroma
CHROMA_PERSIST_DIRECTORY=./chroma_db

# Agent Configuration
MAX_ITERATIONS=3
MAX_SUBAGENTS=4
RESEARCH_TIMEOUT=300

# Citation Configuration
CITATION_STYLE=markdown
"""
        with open(env_file, 'w') as f:
            f.write(env_template)
        console.print("✅ Created .env template file")
        console.print("📝 Please edit .env with your actual configuration values")
    else:
        console.print("ℹ️  .env file already exists")
    
    console.print("\n🎉 Research pipeline initialized successfully!")


if __name__ == "__main__":
    app() 
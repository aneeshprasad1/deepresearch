# Multi-Agent Research Pipeline - Implementation

A fully functional implementation of the multi-agent research pipeline using LangChain, featuring modular agents, memory management, citation handling, and a beautiful CLI interface.

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd deepresearch

# Install dependencies
pip install -r requirements.txt

# Initialize the pipeline
python main.py init
```

### 2. Configuration

Edit the `.env` file created during initialization:

```bash
# LLM Configuration
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
```

### 3. Run Research

```bash
# Basic research
python main.py research "artificial intelligence trends 2024"

# With custom iterations and output file
python main.py research "machine learning applications" --iterations 2 --output results.json --verbose

# Check research status
python main.py status "artificial intelligence trends 2024"

# View configuration
python main.py config
```

## 🏗️ Architecture

### Core Components

1. **ResearchOrchestrator** (`src/orchestrator.py`)
   - Main workflow coordinator
   - Manages agent creation and communication
   - Handles iterative research loops
   - Persists results and context

2. **LeadResearcherAgent** (`src/agents/lead_researcher.py`)
   - Plans research approach
   - Decomposes tasks into parallelizable sub-tasks
   - Synthesizes results from subagents
   - Determines if additional research is needed

3. **Subagent** (`src/agents/subagent.py`)
   - Performs focused web searches
   - Evaluates and filters search results
   - Extracts key insights and information
   - Identifies credible sources

4. **CitationAgent** (`src/agents/citation_agent.py`)
   - Processes research reports
   - Identifies statements needing citations
   - Inserts proper citations in markdown format
   - Maintains academic standards

5. **ResearchMemory** (`src/memory/research_memory.py`)
   - Stores research context and iterations
   - Supports ChromaDB for vector storage
   - Enables context retrieval across sessions
   - Maintains research history

### Workflow

```
User Query → LeadResearcher (Plan) → Task Decomposition → Subagents (Parallel Research) 
    ↓
Synthesis → More Research Needed? → Yes: Refine & Loop / No: Citation Processing
    ↓
Final Cited Report → Persistence → User
```

## 🎯 Features

### ✅ Implemented

- **Modular Agent Architecture**: Clean separation of concerns with base agent class
- **Parallel Research**: Subagents run concurrently for efficiency
- **Iterative Refinement**: Automatic detection of research gaps and refinement
- **Memory Management**: Persistent storage with ChromaDB or in-memory options
- **Citation Handling**: Automatic citation insertion in markdown format
- **Beautiful CLI**: Rich terminal interface with progress indicators
- **Configuration Management**: Environment-based configuration with validation
- **Error Handling**: Robust error handling and graceful degradation
- **Testing**: Unit tests for all major components
- **Documentation**: Comprehensive docstrings and type hints

### 🔄 Research Process

1. **Planning Phase**: LeadResearcher creates comprehensive research plan
2. **Decomposition**: Query broken into 2-4 parallelizable sub-tasks
3. **Parallel Execution**: Subagents conduct focused research simultaneously
4. **Synthesis**: Results combined into coherent research report
5. **Evaluation**: Assessment of completeness and identification of gaps
6. **Refinement**: Additional iterations if needed (up to max_iterations)
7. **Citation**: Automatic citation insertion for all claims
8. **Persistence**: Results saved to memory and optional JSON file

## 🛠️ Usage Examples

### Basic Research

```bash
python main.py research "quantum computing applications"
```

### Advanced Research with Custom Parameters

```bash
python main.py research "blockchain technology trends" \
  --iterations 4 \
  --output blockchain_research.json \
  --verbose
```

### Check Research Status

```bash
python main.py status "quantum computing applications"
```

### View Configuration

```bash
python main.py config
```

## 🔧 Configuration Options

### LLM Configuration
- **OpenAI**: GPT-4, GPT-3.5-turbo, or custom models
- **Local Models**: Ollama, Llama.cpp, or other local LLM servers
- **Temperature**: Configurable for different research styles

### Search Configuration
- **Search Engine**: DuckDuckGo (default), SerpAPI, or custom
- **Max Results**: Number of search results per query
- **Timeout**: Search operation timeout

### Memory Configuration
- **Storage Type**: ChromaDB (vector storage) or in-memory
- **Persistence**: Automatic saving of research context
- **Retrieval**: Semantic search for similar research

### Agent Configuration
- **Max Iterations**: Maximum research refinement cycles
- **Max Subagents**: Maximum parallel agents (default: 4)
- **Research Timeout**: Overall research timeout

## 📊 Output Format

Research results are returned in a structured JSON format:

```json
{
  "cited_report": {
    "executive_summary": "Research summary with citations",
    "key_findings": ["Finding 1", "Finding 2"],
    "detailed_analysis": "Comprehensive analysis with citations",
    "sources": ["source1.com", "source2.com"],
    "gaps_identified": ["gap1", "gap2"],
    "recommendations": ["recommendation1"],
    "confidence_level": "high",
    "completeness_score": 85,
    "citations": [...],
    "citation_metadata": {
      "total_citations": 12,
      "sources_used": 8,
      "citation_style": "markdown"
    }
  },
  "sources_used": [...],
  "citation_count": 12,
  "timestamp": "2024-01-15T10:30:00"
}
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_agents.py
```

## 🔮 Future Extensions

### Planned Features

1. **CritiqueAgent**: Review and critique research reports before delivery
2. **SummarizationAgent**: Generate abstracts, executive summaries, and slide decks
3. **TranslationAgent**: Multi-language research support
4. **Web Interface**: Beautiful web UI for research management
5. **API Endpoints**: RESTful API for integration with other systems
6. **Advanced Memory**: Vector embeddings for semantic retrieval
7. **Research Templates**: Pre-defined research frameworks for common topics
8. **Collaborative Research**: Multi-user research sessions

### Integration Possibilities

- **Vector Databases**: Pinecone, Weaviate, or Qdrant for advanced memory
- **Document Processing**: PDF, Word, and web page content extraction
- **Academic Databases**: Integration with arXiv, PubMed, etc.
- **Social Media**: Twitter, Reddit, and forum research
- **Real-time Data**: Live data feeds and news sources

## 🐛 Troubleshooting

### Common Issues

1. **Configuration Errors**
   ```bash
   # Check configuration
   python main.py config
   
   # Verify .env file exists and has correct values
   cat .env
   ```

2. **Memory Issues**
   ```bash
   # Clear ChromaDB storage
   rm -rf ./chroma_db
   python main.py init
   ```

3. **Search Failures**
   - Check internet connection
   - Verify search engine configuration
   - Try different search queries

4. **LLM Errors**
   - Verify API key is correct
   - Check model availability
   - Ensure sufficient API credits

### Debug Mode

Enable verbose output for debugging:

```bash
python main.py research "your query" --verbose
```

## 📝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LangChain**: For the excellent agent framework
- **DuckDuckGo**: For free search API access
- **ChromaDB**: For vector storage capabilities
- **Rich**: For beautiful terminal interfaces
- **Typer**: For CLI framework

---

**Ready to revolutionize your research workflow?** 🚀

Start with a simple query and watch the multi-agent system work its magic! 
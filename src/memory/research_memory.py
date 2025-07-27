"""
Research memory management for storing and retrieving context across research iterations.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

import chromadb
from chromadb.config import Settings as ChromaSettings

from ..config import get_memory_config


@dataclass
class ResearchContext:
    """Research context data structure."""
    query: str
    plan: Dict[str, Any]
    sub_tasks: List[Dict[str, Any]]
    results: List[Dict[str, Any]]
    synthesis: Optional[Dict[str, Any]] = None
    iteration: int = 1
    created_at: str = None
    updated_at: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        self.updated_at = datetime.utcnow().isoformat()


class ResearchMemory:
    """Memory management for research context and iterations."""
    
    def __init__(self):
        self.config = get_memory_config()
        self.client = None
        self.collection = None
        self._initialize_memory()
    
    def _initialize_memory(self):
        """Initialize the memory storage."""
        if self.config["type"] == "chroma":
            self.client = chromadb.PersistentClient(
                path=self.config["persist_directory"],
                settings=ChromaSettings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name="research_memory",
                metadata={"description": "Research context and iterations"}
            )
        else:
            # In-memory storage for development/testing
            self._in_memory_storage = {}
    
    def save_context(self, context: ResearchContext) -> str:
        """Save research context to memory."""
        context_id = str(uuid.uuid4())
        context.updated_at = datetime.utcnow().isoformat()
        
        if self.config["type"] == "chroma":
            # Store in ChromaDB
            self.collection.add(
                documents=[json.dumps(asdict(context))],
                metadatas=[{
                    "query": context.query,
                    "iteration": context.iteration,
                    "created_at": context.created_at,
                    "updated_at": context.updated_at
                }],
                ids=[context_id]
            )
        else:
            # Store in memory
            self._in_memory_storage[context_id] = context
        
        return context_id
    
    def retrieve_context(self, query: str, max_results: int = 5) -> List[ResearchContext]:
        """Retrieve relevant research context based on query similarity."""
        if self.config["type"] == "chroma":
            # Query ChromaDB for similar contexts
            results = self.collection.query(
                query_texts=[query],
                n_results=max_results
            )
            
            contexts = []
            for i, doc in enumerate(results["documents"][0]):
                if doc:
                    context_data = json.loads(doc)
                    contexts.append(ResearchContext(**context_data))
            
            return contexts
        else:
            # Simple keyword matching for in-memory storage
            contexts = []
            for context in self._in_memory_storage.values():
                if query.lower() in context.query.lower():
                    contexts.append(context)
            
            return sorted(contexts, key=lambda x: x.updated_at, reverse=True)[:max_results]
    
    def get_latest_context(self, query: str) -> Optional[ResearchContext]:
        """Get the most recent context for a specific query."""
        contexts = self.retrieve_context(query, max_results=1)
        return contexts[0] if contexts else None
    
    def update_context(self, context_id: str, context: ResearchContext) -> bool:
        """Update existing research context."""
        context.updated_at = datetime.utcnow().isoformat()
        
        if self.config["type"] == "chroma":
            try:
                self.collection.update(
                    ids=[context_id],
                    documents=[json.dumps(asdict(context))],
                    metadatas=[{
                        "query": context.query,
                        "iteration": context.iteration,
                        "created_at": context.created_at,
                        "updated_at": context.updated_at
                    }]
                )
                return True
            except Exception:
                return False
        else:
            if context_id in self._in_memory_storage:
                self._in_memory_storage[context_id] = context
                return True
            return False
    
    def save_plan(self, query: str, plan: Dict[str, Any]) -> str:
        """Save a research plan."""
        context = ResearchContext(
            query=query,
            plan=plan,
            sub_tasks=[],
            results=[]
        )
        return self.save_context(context)
    
    def save_results(self, context_id: str, results: List[Dict[str, Any]]) -> bool:
        """Save research results to existing context."""
        if self.config["type"] == "chroma":
            # Retrieve existing context
            try:
                existing = self.collection.get(ids=[context_id])
                if existing["documents"]:
                    context_data = json.loads(existing["documents"][0])
                    context = ResearchContext(**context_data)
                    context.results = results
                    context.updated_at = datetime.utcnow().isoformat()
                    
                    return self.update_context(context_id, context)
            except Exception:
                pass
        else:
            if context_id in self._in_memory_storage:
                self._in_memory_storage[context_id].results = results
                self._in_memory_storage[context_id].updated_at = datetime.utcnow().isoformat()
                return True
        
        return False 
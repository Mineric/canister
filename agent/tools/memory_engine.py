"""
Memory & Context Engine - Canister Agent
Copyright (c) 2024 Thant Min Htet. All rights reserved.

Memory system integrating Google ADK memory capabilities
with codebase indexer for context awareness.

This software is proprietary and confidential. No usage, modification,
or distribution rights are granted without explicit written permission.
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
from google.adk.tools import FunctionTool
from google.adk.sessions import InMemorySessionService, VertexAiSessionService
from google.adk.memory import InMemoryMemoryService, VertexAiRagMemoryService


class MemoryMode(Enum):
    """Memory system operation modes."""
    DEVELOPMENT = "development"  # In-memory only
    PRODUCTION = "production"    # Vertex AI with persistence
    HYBRID = "hybrid"           # Both local and cloud


@dataclass
class MemoryConfig:
    """Configuration for memory system."""
    mode: MemoryMode = MemoryMode.DEVELOPMENT
    
    # Google Cloud Configuration
    project_id: Optional[str] = None
    location: str = "us-central1"
    rag_corpus_name: Optional[str] = None
    
    # Local Configuration
    cache_dir: str = ".memory_cache"
    session_retention_days: int = 30
    memory_retention_days: int = 90
    
    # Performance Configuration
    max_context_tokens: int = 32000
    similarity_threshold: float = 0.7
    max_memory_results: int = 10
    
    # Integration Configuration
    enable_codebase_integration: bool = True
    enable_conversation_memory: bool = True
    enable_cross_session_learning: bool = True


@dataclass
class ContextPriority:
    """Context prioritization for large codebases."""
    relevance_score: float
    recency_score: float
    importance_score: float
    token_cost: int
    
    @property
    def total_score(self) -> float:
        """Calculate weighted total score."""
        return (
            self.relevance_score * 0.5 +
            self.recency_score * 0.3 +
            self.importance_score * 0.2
        )


@dataclass
class MemoryEntry:
    """Structured memory entry for context storage."""
    id: str
    content: str
    context_type: str  # 'conversation', 'codebase', 'analysis', 'decision'
    timestamp: datetime
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: Optional[ContextPriority] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.priority:
            data['priority'] = asdict(self.priority)
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if 'priority' in data and data['priority']:
            data['priority'] = ContextPriority(**data['priority'])
        return cls(**data)


class MemoryEngine:
    """
    Memory and context engine integrating Google ADK
    memory capabilities with codebase awareness.
    """
    
    def __init__(self, config: MemoryConfig):
        """Initialize the memory engine."""
        self.config = config
        self.cache_dir = Path(config.cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize services based on mode
        self.session_service = None
        self.memory_service = None
        
        # Local memory cache
        self.local_memory: Dict[str, MemoryEntry] = {}
        self.context_cache: Dict[str, List[MemoryEntry]] = {}
        
        # Integration with existing codebase indexer
        self.codebase_indexer = None
        if config.enable_codebase_integration:
            try:
                from .codebase_indexer import get_global_indexer
                self.codebase_indexer = get_global_indexer()
            except ImportError:
                print("Warning: Codebase indexer not available")
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize ADK memory services based on configuration."""
        if self.config.mode == MemoryMode.DEVELOPMENT:
            self.session_service = InMemorySessionService()
            self.memory_service = InMemoryMemoryService()
            
        elif self.config.mode == MemoryMode.PRODUCTION:
            if not self.config.project_id or not self.config.rag_corpus_name:
                raise ValueError("Production mode requires project_id and rag_corpus_name")
            
            self.session_service = VertexAiSessionService(
                project=self.config.project_id,
                location=self.config.location
            )
            self.memory_service = VertexAiRagMemoryService(
                rag_corpus=self.config.rag_corpus_name,
                similarity_top_k=self.config.max_memory_results,
                vector_distance_threshold=self.config.similarity_threshold
            )
            
        elif self.config.mode == MemoryMode.HYBRID:
            # Use both local and cloud services
            self.session_service = InMemorySessionService()
            self.memory_service = InMemoryMemoryService()
            print("Hybrid mode: Using local services with cloud backup")
    
    async def add_memory(
        self,
        content: str,
        session_id: str,
        user_id: str,
        context_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add content to memory."""
        entry_id = f"{context_type}_{session_id}_{datetime.now().timestamp()}"
        
        # Calculate priority
        priority = self._calculate_priority(content, context_type)
        
        # Create memory entry
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            context_type=context_type,
            timestamp=datetime.now(),
            session_id=session_id,
            user_id=user_id,
            metadata=metadata or {},
            priority=priority
        )
        
        # Store locally
        self.local_memory[entry_id] = entry
        
        # Save to local cache
        self._save_local_memory()
        
        return entry_id
    
    def _calculate_priority(self, content: str, context_type: str) -> ContextPriority:
        """Calculate priority scores for content."""
        # Relevance based on content analysis
        relevance_score = self._analyze_content_relevance(content)
        
        # Recency (always high for new content)
        recency_score = 1.0
        
        # Importance based on context type
        importance_map = {
            "conversation": 0.6,
            "codebase": 0.9,
            "analysis": 0.8,
            "decision": 0.95,
            "error": 0.85
        }
        importance_score = importance_map.get(context_type, 0.5)
        
        # Estimate token cost
        token_cost = len(content.split()) * 1.3  # Rough estimate
        
        return ContextPriority(
            relevance_score=relevance_score,
            recency_score=recency_score,
            importance_score=importance_score,
            token_cost=int(token_cost)
        )
    
    def _analyze_content_relevance(self, content: str) -> float:
        """Analyze content relevance using keyword and pattern matching."""
        # High-value keywords for software engineering
        high_value_keywords = [
            "error", "bug", "fix", "implement", "refactor", "optimize",
            "architecture", "design", "pattern", "security", "performance",
            "test", "deploy", "merge", "conflict", "dependency"
        ]
        
        content_lower = content.lower()
        keyword_matches = sum(1 for keyword in high_value_keywords if keyword in content_lower)
        
        # Base relevance on keyword density
        relevance = min(keyword_matches / len(high_value_keywords), 1.0)
        
        # Boost for code-related content
        if any(indicator in content for indicator in ["def ", "class ", "import ", "function"]):
            relevance = min(relevance + 0.3, 1.0)
        
        return max(relevance, 0.1)  # Minimum relevance
    
    def _save_local_memory(self):
        """Save local memory to disk."""
        memory_file = self.cache_dir / "local_memory.json"
        
        # Convert entries to serializable format
        serializable_memory = {
            entry_id: entry.to_dict()
            for entry_id, entry in self.local_memory.items()
        }
        
        with open(memory_file, 'w') as f:
            json.dump(serializable_memory, f, indent=2)
    
    def _load_local_memory(self):
        """Load local memory from disk."""
        memory_file = self.cache_dir / "local_memory.json"
        
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                
                self.local_memory = {
                    entry_id: MemoryEntry.from_dict(entry_data)
                    for entry_id, entry_data in data.items()
                }
            except Exception as e:
                print(f"Warning: Could not load local memory: {e}")


    async def search_memory(
        self,
        query: str,
        user_id: Optional[str] = None,
        context_types: Optional[List[str]] = None,
        max_results: Optional[int] = None,
        include_codebase: bool = True
    ) -> List[MemoryEntry]:
        """Search memory with intelligent context prioritization."""
        max_results = max_results or self.config.max_memory_results
        results = []

        # Search local memory
        local_results = self._search_local_memory(query, user_id, context_types)
        results.extend(local_results)

        # Search codebase if enabled
        if include_codebase and self.codebase_indexer:
            codebase_results = self._search_codebase_memory(query)
            results.extend(codebase_results)

        # Sort by priority and limit results
        results.sort(key=lambda x: x.priority.total_score if x.priority else 0, reverse=True)
        return results[:max_results]

    def _search_local_memory(
        self,
        query: str,
        user_id: Optional[str] = None,
        context_types: Optional[List[str]] = None
    ) -> List[MemoryEntry]:
        """Search local memory cache."""
        results = []
        query_lower = query.lower()

        for entry in self.local_memory.values():
            # Filter by user if specified
            if user_id and entry.user_id != user_id:
                continue

            # Filter by context types if specified
            if context_types and entry.context_type not in context_types:
                continue

            # Simple text matching
            if query_lower in entry.content.lower():
                results.append(entry)

        return results

    def _search_codebase_memory(self, query: str) -> List[MemoryEntry]:
        """Search codebase and convert results to memory entries."""
        if not self.codebase_indexer:
            return []

        try:
            # Search codebase using existing indexer
            search_results = self.codebase_indexer.search_code_elements(query)

            memory_entries = []
            for result in search_results[:5]:  # Limit codebase results
                content = f"Code: {result.name} ({result.element_type}) in {result.file_path}"
                if hasattr(result, 'signature') and result.signature:
                    content += f"\nSignature: {result.signature}"

                entry = MemoryEntry(
                    id=f"codebase_{result.file_path}_{result.name}_{datetime.now().timestamp()}",
                    content=content,
                    context_type="codebase",
                    timestamp=datetime.now(),
                    metadata={
                        "file_path": result.file_path,
                        "element_type": result.element_type,
                        "line_number": result.line_number,
                        "source": "codebase_indexer"
                    },
                    priority=ContextPriority(
                        relevance_score=0.8,
                        recency_score=0.5,
                        importance_score=0.9,
                        token_cost=len(content.split()) * 1.3
                    )
                )
                memory_entries.append(entry)

            return memory_entries

        except Exception as e:
            print(f"Warning: Codebase search failed: {e}")
            return []

    async def get_context_summary(
        self,
        session_id: str,
        max_tokens: Optional[int] = None
    ) -> str:
        """Get intelligent contextual summary for a session."""
        max_tokens = max_tokens or self.config.max_context_tokens

        # Get session-specific memories
        session_memories = [
            entry for entry in self.local_memory.values()
            if entry.session_id == session_id
        ]

        # Sort by priority
        session_memories.sort(
            key=lambda x: x.priority.total_score if x.priority else 0,
            reverse=True
        )

        # Build summary within token limit
        summary_parts = []
        current_tokens = 0

        for memory in session_memories:
            entry_tokens = memory.priority.token_cost if memory.priority else 100

            if current_tokens + entry_tokens > max_tokens:
                break

            summary_parts.append(f"[{memory.context_type}] {memory.content}")
            current_tokens += entry_tokens

        return "\n\n".join(summary_parts)

    async def cleanup_old_memories(self):
        """Clean up old memories based on retention policies."""
        now = datetime.now()

        # Remove old session memories
        session_cutoff = now - timedelta(days=self.config.session_retention_days)
        memory_cutoff = now - timedelta(days=self.config.memory_retention_days)

        to_remove = []
        for entry_id, entry in self.local_memory.items():
            if entry.context_type == "conversation" and entry.timestamp < session_cutoff:
                to_remove.append(entry_id)
            elif entry.timestamp < memory_cutoff:
                to_remove.append(entry_id)

        for entry_id in to_remove:
            del self.local_memory[entry_id]

        if to_remove:
            self._save_local_memory()
            print(f"Cleaned up {len(to_remove)} old memory entries")


# Global memory engine instance
_global_memory_engine: Optional[MemoryEngine] = None


def get_memory_engine(config: Optional[MemoryConfig] = None) -> MemoryEngine:
    """Get or create the global memory engine."""
    global _global_memory_engine

    if _global_memory_engine is None:
        if config is None:
            config = MemoryConfig()  # Use default configuration
        _global_memory_engine = MemoryEngine(config)
        _global_memory_engine._load_local_memory()

    return _global_memory_engine


# ============================================================================
# Memory Tools for Google ADK Integration
# ============================================================================

def memory_search_tool() -> FunctionTool:
    """
    Create a memory search tool for intelligent context retrieval.
    """

    async def search_memory(
        query: str,
        context_types: str = "conversation,codebase,analysis",
        max_results: int = 10,
        include_codebase: bool = True,
        user_id: str = "default_user"
    ) -> str:
        """
        Search memory with intelligent context prioritization.

        Args:
            query: Search query for finding relevant context
            context_types: Comma-separated list of context types to search
            max_results: Maximum number of results to return
            include_codebase: Whether to include codebase search results
            user_id: User ID for personalized search

        Returns:
            Formatted search results with prioritized context
        """
        try:
            memory_engine = get_memory_engine()

            # Parse context types
            context_list = [ct.strip() for ct in context_types.split(",")]

            # Search memory
            results = await memory_engine.search_memory(
                query=query,
                user_id=user_id,
                context_types=context_list,
                max_results=max_results,
                include_codebase=include_codebase
            )

            if not results:
                return f"No relevant context found for query: '{query}'"

            # Format results
            formatted_results = []
            for i, result in enumerate(results, 1):
                priority_info = ""
                if result.priority:
                    priority_info = f" (Score: {result.priority.total_score:.2f})"

                formatted_results.append(
                    f"{i}. [{result.context_type.upper()}]{priority_info}\n"
                    f"   Time: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"   Content: {result.content[:200]}{'...' if len(result.content) > 200 else ''}\n"
                )

            return (
                f"Found {len(results)} relevant context entries for '{query}':\n\n" +
                "\n".join(formatted_results)
            )

        except Exception as e:
            return f"Error searching memory: {str(e)}"

    return FunctionTool(search_memory)


def context_tool() -> FunctionTool:
    """
    Create a tool for getting contextual summaries.
    """

    async def get_context(
        session_id: str = "current_session",
        max_tokens: int = 8000
    ) -> str:
        """
        Get intelligent contextual summary for current session.

        Args:
            session_id: Session ID to get context for
            max_tokens: Maximum tokens for context summary

        Returns:
            Contextual summary optimized for current session
        """
        try:
            memory_engine = get_memory_engine()

            # Get session summary
            summary = await memory_engine.get_context_summary(
                session_id=session_id,
                max_tokens=max_tokens
            )

            if not summary:
                return f"No context available for session: {session_id}"

            return (
                f"📋 **Context Summary** (Session: {session_id})\n"
                f"Token Budget: {max_tokens}\n\n"
                f"{summary}\n\n"
                f"---\n"
                f"Context generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )

        except Exception as e:
            return f"Error getting context: {str(e)}"

    return FunctionTool(get_context)


def memory_management_tool() -> FunctionTool:
    """
    Create a tool for memory management operations.
    """

    async def manage_memory(
        action: str,
        content: str = "",
        context_type: str = "conversation",
        session_id: str = "current_session",
        user_id: str = "default_user",
        metadata: str = "{}"
    ) -> str:
        """
        Manage memory system operations.

        Args:
            action: Action to perform (add, cleanup, status, configure)
            content: Content to add to memory (for 'add' action)
            context_type: Type of context (conversation, codebase, analysis, decision)
            session_id: Session ID for the memory entry
            user_id: User ID for the memory entry
            metadata: JSON string with additional metadata

        Returns:
            Result of the memory management operation
        """
        try:
            memory_engine = get_memory_engine()

            if action == "add":
                if not content:
                    return "Error: Content is required for 'add' action"

                # Parse metadata
                try:
                    metadata_dict = json.loads(metadata) if metadata != "{}" else {}
                except json.JSONDecodeError:
                    metadata_dict = {}

                # Add to memory
                entry_id = await memory_engine.add_memory(
                    content=content,
                    session_id=session_id,
                    user_id=user_id,
                    context_type=context_type,
                    metadata=metadata_dict
                )

                return f"✅ Added memory entry: {entry_id}"

            elif action == "cleanup":
                await memory_engine.cleanup_old_memories()
                return "✅ Memory cleanup completed"

            elif action == "status":
                total_memories = len(memory_engine.local_memory)
                config_info = (
                    f"Mode: {memory_engine.config.mode.value}\n"
                    f"Total Memories: {total_memories}\n"
                    f"Cache Directory: {memory_engine.cache_dir}\n"
                    f"Codebase Integration: {memory_engine.config.enable_codebase_integration}\n"
                    f"Max Context Tokens: {memory_engine.config.max_context_tokens}"
                )
                return f"📊 **Memory Status**\n{config_info}"

            elif action == "configure":
                return (
                    "⚙️ **Memory Configuration**\n"
                    "Available actions: add, cleanup, status, configure\n"
                    "Context types: conversation, codebase, analysis, decision, error\n"
                    "Use 'status' to see current configuration"
                )

            else:
                return f"Error: Unknown action '{action}'. Use: add, cleanup, status, configure"

        except Exception as e:
            return f"Error managing memory: {str(e)}"

    return FunctionTool(manage_memory)

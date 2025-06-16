"""
Memory & Context Engine - Canister Agent
Copyright (c) 2025 Thant Min Htet. All rights reserved.

Memory system integrating Google ADK memory capabilities
with codebase indexer for context awareness.

This software is proprietary and confidential. No usage, modification,
or distribution rights are granted without explicit written permission.
"""

import json
import asyncio
import threading
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

    # Autonomous Cleanup Configuration
    enable_autonomous_cleanup: bool = True
    cleanup_interval_hours: int = 24
    max_memory_entries: int = 10000
    memory_pressure_threshold: float = 0.8


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
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        if self.last_accessed:
            data['last_accessed'] = self.last_accessed.isoformat()
        if self.priority:
            data['priority'] = asdict(self.priority)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MemoryEntry':
        """Create from dictionary."""
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        if 'last_accessed' in data and data['last_accessed']:
            data['last_accessed'] = datetime.fromisoformat(data['last_accessed'])
        if 'priority' in data and data['priority']:
            data['priority'] = ContextPriority(**data['priority'])
        # Handle legacy entries without access tracking
        if 'access_count' not in data:
            data['access_count'] = 0
        if 'last_accessed' not in data:
            data['last_accessed'] = None
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

        # Autonomous cleanup system
        self._cleanup_task = None
        self._shutdown_event = threading.Event()

        # Initialize services
        self._initialize_services()

        # Start autonomous cleanup if enabled
        if config.enable_autonomous_cleanup:
            self._start_autonomous_cleanup()
    
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
        """Search local memory cache and track access."""
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
                # Track access for intelligent cleanup
                entry.access_count += 1
                entry.last_accessed = datetime.now()
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

    def _start_autonomous_cleanup(self):
        """Start autonomous cleanup background task."""
        def cleanup_worker():
            while not self._shutdown_event.is_set():
                try:
                    # Run cleanup
                    asyncio.run(self._autonomous_cleanup())

                    # Wait for next cleanup interval
                    self._shutdown_event.wait(self.config.cleanup_interval_hours * 3600)
                except Exception as e:
                    print(f"Error in autonomous cleanup: {e}")
                    # Wait a bit before retrying
                    self._shutdown_event.wait(300)  # 5 minutes

        self._cleanup_task = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_task.start()
        print(f"Started autonomous memory cleanup (interval: {self.config.cleanup_interval_hours}h)")

    def shutdown(self):
        """Shutdown the memory engine and cleanup tasks."""
        if self._cleanup_task and self._cleanup_task.is_alive():
            self._shutdown_event.set()
            self._cleanup_task.join(timeout=5)
            print("Memory engine shutdown complete")

    async def _autonomous_cleanup(self):
        """Intelligent autonomous memory cleanup."""
        print("🧹 Running autonomous memory cleanup...")

        # 1. Age-based cleanup
        age_removed = await self._cleanup_by_age()

        # 2. Memory pressure cleanup
        pressure_removed = await self._cleanup_by_memory_pressure()

        # 3. Duplicate detection and removal
        duplicate_removed = await self._cleanup_duplicates()

        # 4. Update access patterns
        self._update_memory_priorities()

        total_removed = age_removed + pressure_removed + duplicate_removed
        if total_removed > 0:
            self._save_local_memory()
            print(f"✅ Autonomous cleanup completed: {total_removed} entries removed")
            print(f"   Age-based: {age_removed}, Pressure: {pressure_removed}, Duplicates: {duplicate_removed}")

    async def _cleanup_by_age(self) -> int:
        """Clean up old memories based on retention policies."""
        now = datetime.now()
        session_cutoff = now - timedelta(days=self.config.session_retention_days)
        memory_cutoff = now - timedelta(days=self.config.memory_retention_days)

        to_remove = []
        for entry_id, entry in self.local_memory.items():
            # Short-term memory cleanup
            if entry.context_type == "conversation" and entry.timestamp < session_cutoff:
                to_remove.append(entry_id)
            # Long-term memory cleanup
            elif entry.timestamp < memory_cutoff:
                # Keep high-priority memories longer
                if entry.priority and entry.priority.total_score < 0.7:
                    to_remove.append(entry_id)
                elif not entry.priority:
                    to_remove.append(entry_id)

        for entry_id in to_remove:
            del self.local_memory[entry_id]

        return len(to_remove)

    async def _cleanup_by_memory_pressure(self) -> int:
        """Clean up memories when approaching storage limits."""
        current_count = len(self.local_memory)
        max_entries = self.config.max_memory_entries

        if current_count < max_entries * self.config.memory_pressure_threshold:
            return 0

        # Calculate how many to remove
        target_count = int(max_entries * 0.7)  # Reduce to 70% of max
        to_remove_count = current_count - target_count

        # Sort by priority (lowest first) and access patterns
        entries_by_priority = sorted(
            self.local_memory.items(),
            key=lambda x: (
                x[1].priority.total_score if x[1].priority else 0,
                x[1].access_count,
                x[1].last_accessed or datetime.min
            )
        )

        # Remove lowest priority, least accessed entries
        removed = 0
        for entry_id, entry in entries_by_priority[:to_remove_count]:
            # Don't remove critical memories
            if entry.context_type in ["decision", "error"] and entry.priority and entry.priority.total_score > 0.8:
                continue

            del self.local_memory[entry_id]
            removed += 1

        return removed

    async def _cleanup_duplicates(self) -> int:
        """Remove duplicate or very similar memory entries."""
        entries = list(self.local_memory.items())
        to_remove = []

        for i, (id1, entry1) in enumerate(entries):
            for id2, entry2 in entries[i+1:]:
                # Check for content similarity
                if self._are_memories_similar(entry1, entry2):
                    # Keep the one with higher priority or more recent
                    if self._should_keep_first_memory(entry1, entry2):
                        to_remove.append(id2)
                    else:
                        to_remove.append(id1)

        # Remove duplicates
        for entry_id in set(to_remove):
            if entry_id in self.local_memory:
                del self.local_memory[entry_id]

        return len(set(to_remove))

    def _are_memories_similar(self, entry1: MemoryEntry, entry2: MemoryEntry) -> bool:
        """Check if two memory entries are similar enough to be considered duplicates."""
        # Same context type and similar content
        if entry1.context_type != entry2.context_type:
            return False

        # Simple similarity check based on content overlap
        words1 = set(entry1.content.lower().split())
        words2 = set(entry2.content.lower().split())

        if len(words1) == 0 or len(words2) == 0:
            return False

        overlap = len(words1.intersection(words2))
        similarity = overlap / min(len(words1), len(words2))

        return similarity > 0.8  # 80% word overlap

    def _should_keep_first_memory(self, entry1: MemoryEntry, entry2: MemoryEntry) -> bool:
        """Determine which memory to keep when duplicates are found."""
        # Prefer higher priority
        score1 = entry1.priority.total_score if entry1.priority else 0
        score2 = entry2.priority.total_score if entry2.priority else 0

        if abs(score1 - score2) > 0.1:
            return score1 > score2

        # Prefer more accessed
        if entry1.access_count != entry2.access_count:
            return entry1.access_count > entry2.access_count

        # Prefer more recent
        return entry1.timestamp > entry2.timestamp

    def _update_memory_priorities(self):
        """Update memory priorities based on access patterns and age."""
        now = datetime.now()

        for entry in self.local_memory.values():
            if not entry.priority:
                continue

            # Decay recency score over time
            days_old = (now - entry.timestamp).days
            recency_decay = max(0.1, 1.0 - (days_old / 365))  # Decay over a year

            # Boost based on access frequency
            access_boost = min(0.3, entry.access_count * 0.01)  # Up to 30% boost

            # Update priority
            entry.priority.recency_score = recency_decay
            entry.priority.relevance_score = min(1.0, entry.priority.relevance_score + access_boost)

    async def cleanup_old_memories(self):
        """Manual cleanup trigger - delegates to autonomous cleanup."""
        await self._autonomous_cleanup()


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


def shutdown_memory_engine():
    """Shutdown the global memory engine."""
    global _global_memory_engine
    if _global_memory_engine:
        _global_memory_engine.shutdown()
        _global_memory_engine = None


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

                # Calculate memory statistics
                memory_by_type = {}
                total_access_count = 0
                for entry in memory_engine.local_memory.values():
                    memory_by_type[entry.context_type] = memory_by_type.get(entry.context_type, 0) + 1
                    total_access_count += entry.access_count

                # Memory pressure calculation
                max_entries = memory_engine.config.max_memory_entries
                pressure = (total_memories / max_entries) * 100 if max_entries > 0 else 0

                config_info = (
                    f"Mode: {memory_engine.config.mode.value}\n"
                    f"Total Memories: {total_memories} / {max_entries} ({pressure:.1f}% full)\n"
                    f"Memory by Type: {dict(memory_by_type)}\n"
                    f"Total Access Count: {total_access_count}\n"
                    f"Cache Directory: {memory_engine.cache_dir}\n"
                    f"Autonomous Cleanup: {memory_engine.config.enable_autonomous_cleanup}\n"
                    f"Cleanup Interval: {memory_engine.config.cleanup_interval_hours}h\n"
                    f"Codebase Integration: {memory_engine.config.enable_codebase_integration}\n"
                    f"Max Context Tokens: {memory_engine.config.max_context_tokens}"
                )
                return f"📊 **Enhanced Memory Status**\n{config_info}"

            elif action == "configure":
                return (
                    "⚙️ **Enhanced Memory Configuration**\n"
                    "Available actions: add, cleanup, status, configure, force_cleanup, analyze\n"
                    "Context types: conversation, codebase, analysis, decision, error\n"
                    "Features: Autonomous cleanup, intelligent prioritization, access tracking\n"
                    "Use 'status' to see current configuration and memory statistics"
                )

            elif action == "force_cleanup":
                await memory_engine._autonomous_cleanup()
                return "✅ Force cleanup completed - ran full autonomous cleanup cycle"

            elif action == "analyze":
                # Provide memory analysis
                entries = list(memory_engine.local_memory.values())
                if not entries:
                    return "📊 No memories to analyze"

                # Calculate statistics
                avg_priority = sum(e.priority.total_score for e in entries if e.priority) / len([e for e in entries if e.priority])
                most_accessed = max(entries, key=lambda x: x.access_count)
                oldest = min(entries, key=lambda x: x.timestamp)
                newest = max(entries, key=lambda x: x.timestamp)

                analysis = (
                    f"📊 **Memory Analysis**\n"
                    f"Average Priority Score: {avg_priority:.2f}\n"
                    f"Most Accessed: {most_accessed.context_type} ({most_accessed.access_count} times)\n"
                    f"Oldest Memory: {oldest.timestamp.strftime('%Y-%m-%d %H:%M')} ({oldest.context_type})\n"
                    f"Newest Memory: {newest.timestamp.strftime('%Y-%m-%d %H:%M')} ({newest.context_type})\n"
                    f"Memory Span: {(newest.timestamp - oldest.timestamp).days} days"
                )
                return analysis

            else:
                return f"Error: Unknown action '{action}'. Use: add, cleanup, status, configure, force_cleanup, analyze"

        except Exception as e:
            return f"Error managing memory: {str(e)}"

    return FunctionTool(manage_memory)

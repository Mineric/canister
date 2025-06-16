# Memory & Context Engine

A robust memory and context management system integrating ADK memory capabilities with codebase awareness for professional-level context retention and retrieval.

## 🎯 **Overview**

The Memory Engine provides persistent conversation memory, intelligent context prioritization, and hybrid search capabilities that combine conversation history with codebase knowledge.

### **Key Features**
- **Persistent Memory**: Context survives agent restarts
- **Intelligent Prioritization**: Smart context ranking and retrieval
- **Google ADK Integration**: Enterprise-grade memory services
- **Hybrid Search**: Conversation + codebase knowledge
- **Automatic Management**: Cleanup and retention policies

## 🏗️ **Architecture**

### **Core Components**

```python
# Memory Engine Architecture
MemoryEngine
├── MemoryConfig (configuration)
├── MemoryEntry (structured storage)
├── ContextPriority (intelligent ranking)
├── Local Storage (JSON + caching)
├── ADK Integration (cloud services)
└── Codebase Integration (hybrid search)
```

### **Memory Modes**

```python
class MemoryMode(Enum):
    DEVELOPMENT = "development"  # In-memory with local persistence
    PRODUCTION = "production"    # Vertex AI with RAG semantic search
    HYBRID = "hybrid"           # Local + cloud backup
```

### **Context Types**

- **conversation**: User interactions and responses
- **codebase**: Code elements and structure information
- **analysis**: Code analysis results and insights
- **decision**: Important decisions and reasoning
- **error**: Error handling and debugging information

## 🧠 **Intelligent Prioritization**

### **Priority Scoring System**

```python
@dataclass
class ContextPriority:
    relevance_score: float   # Content analysis (50% weight)
    recency_score: float     # Time-based importance (30% weight)
    importance_score: float  # Context type weighting (20% weight)
    token_cost: int         # Estimated token usage
    
    @property
    def total_score(self) -> float:
        return (
            self.relevance_score * 0.5 +
            self.recency_score * 0.3 +
            self.importance_score * 0.2
        )
```

### **Relevance Analysis**
- **Keyword Matching**: High-value software engineering terms
- **Code Pattern Detection**: Function, class, import recognition
- **Context Type Weighting**: Different importance levels
- **Token Cost Optimization**: Efficient context selection

## 🛠️ **Memory Tools**

### **1. Memory Search Tool**

```python
memory_search_tool()
```

**Function**: `search_memory(query, context_types, max_results, include_codebase, user_id)`

Intelligent context retrieval with prioritization.

**Example**:
```python
# Search for authentication-related context
result = await search_tool.func(
    query="authentication JWT",
    context_types="conversation,analysis,decision",
    max_results=10,
    include_codebase=True,
    user_id="user_123"
)
```

### **2. Context Tool**

```python
context_tool()
```

**Function**: `get_context(session_id, max_tokens)`

Session-specific context summaries optimized for token limits.

**Example**:
```python
# Get context summary for current session
summary = await context_tool.func(
    session_id="current_session",
    max_tokens=8000
)
```

### **3. Memory Management Tool**

```python
memory_management_tool()
```

**Function**: `manage_memory(action, content, context_type, session_id, user_id, metadata)`

Memory operations: add, cleanup, status, configure.

**Example**:
```python
# Add important decision to memory
result = await mgmt_tool.func(
    action="add",
    content="Decided to use FastAPI with OAuth2 + JWT",
    context_type="decision",
    session_id="session_123",
    user_id="user_456"
)
```

## ⚙️ **Configuration**

### **Memory Configuration**

```python
@dataclass
class MemoryConfig:
    # Operation mode
    mode: MemoryMode = MemoryMode.DEVELOPMENT
    
    # Google Cloud settings
    project_id: Optional[str] = None
    location: str = "us-central1"
    rag_corpus_name: Optional[str] = None
    
    # Local storage
    cache_dir: str = ".memory_cache"
    session_retention_days: int = 30
    memory_retention_days: int = 90
    
    # Performance tuning
    max_context_tokens: int = 32000
    similarity_threshold: float = 0.7
    max_memory_results: int = 10
    
    # Feature flags
    enable_codebase_integration: bool = True
    enable_conversation_memory: bool = True
    enable_cross_session_learning: bool = True
```

### **Setup Examples**

#### **Development Mode**
```python
from agent.tools.memory_engine import get_memory_engine, MemoryConfig, MemoryMode

config = MemoryConfig(
    mode=MemoryMode.DEVELOPMENT,
    cache_dir=".dev_memory",
    max_memory_results=5
)
memory_engine = get_memory_engine(config)
```

#### **Production Mode**
```python
config = MemoryConfig(
    mode=MemoryMode.PRODUCTION,
    project_id="your-gcp-project",
    rag_corpus_name="projects/your-project/locations/us-central1/ragCorpora/your-corpus",
    max_context_tokens=16000
)
memory_engine = get_memory_engine(config)
```

## 🔍 **Usage Examples**

### **Adding Memories**

```python
# Add conversation memory
entry_id = await memory_engine.add_memory(
    content="User asked about implementing OAuth2 authentication",
    session_id="session_123",
    user_id="user_456",
    context_type="conversation"
)

# Add analysis memory
entry_id = await memory_engine.add_memory(
    content="Analyzed auth flow - recommend JWT with refresh tokens",
    session_id="session_123",
    user_id="user_456",
    context_type="analysis",
    metadata={"priority": "high", "feature": "authentication"}
)
```

### **Searching Memories**

```python
# Search with intelligent prioritization
results = await memory_engine.search_memory(
    query="authentication security",
    user_id="user_456",
    context_types=["conversation", "analysis", "decision"],
    max_results=10,
    include_codebase=True
)

# Process results
for result in results:
    print(f"[{result.context_type}] Score: {result.priority.total_score:.2f}")
    print(f"Content: {result.content[:100]}...")
```

### **Context Summaries**

```python
# Get session context within token limit
summary = await memory_engine.get_context_summary(
    session_id="session_123",
    max_tokens=8000
)

print(f"Context Summary:\n{summary}")
```

## 🔗 **Google ADK Integration**

### **Memory Services**

#### **Development**
```python
# In-memory services for development
self.session_service = InMemorySessionService()
self.memory_service = InMemoryMemoryService()
```

#### **Production**
```python
# Vertex AI services for production
self.session_service = VertexAiSessionService(
    project=self.config.project_id,
    location=self.config.location
)
self.memory_service = VertexAiRagMemoryService(
    rag_corpus=self.config.rag_corpus_name,
    similarity_top_k=self.config.max_memory_results,
    vector_distance_threshold=self.config.similarity_threshold
)
```

### **Session Management**

The memory engine integrates with ADK session services for:
- **Persistent conversations**: Sessions survive restarts
- **User isolation**: Per-user memory spaces
- **Cross-session learning**: Knowledge sharing between sessions
- **Automatic cleanup**: Based on retention policies

## 🔄 **Codebase Integration**

### **Hybrid Search**

The memory engine seamlessly integrates with the codebase indexer:

```python
def _search_codebase_memory(self, query: str) -> List[MemoryEntry]:
    """Search codebase and convert results to memory entries."""
    if not self.codebase_indexer:
        return []
    
    # Search using existing indexer
    search_results = self.codebase_indexer.search_code_elements(query)
    
    # Convert to memory entries with priority scoring
    memory_entries = []
    for result in search_results[:5]:
        entry = MemoryEntry(
            content=f"Code: {result.name} ({result.element_type})",
            context_type="codebase",
            priority=ContextPriority(
                relevance_score=0.8,
                recency_score=0.5,
                importance_score=0.9,
                token_cost=len(content.split()) * 1.3
            )
        )
        memory_entries.append(entry)
    
    return memory_entries
```

## 💾 **Data Persistence**

### **Local Storage**
- **JSON files**: Structured memory storage
- **Automatic loading**: On engine initialization
- **Incremental updates**: Efficient storage management
- **Backup capabilities**: Data safety measures

### **Cloud Storage**
- **Vertex AI RAG**: Semantic search capabilities
- **Automatic persistence**: No manual management needed
- **Scalable storage**: Enterprise-grade infrastructure
- **Cross-instance sharing**: Multi-agent coordination

## 🧹 **Memory Management**

### **Automatic Cleanup**

```python
async def cleanup_old_memories(self):
    """Clean up based on retention policies."""
    now = datetime.now()
    
    session_cutoff = now - timedelta(days=self.config.session_retention_days)
    memory_cutoff = now - timedelta(days=self.config.memory_retention_days)
    
    # Remove old memories based on type and age
    for entry_id, entry in list(self.local_memory.items()):
        if entry.context_type == "conversation" and entry.timestamp < session_cutoff:
            del self.local_memory[entry_id]
        elif entry.timestamp < memory_cutoff:
            del self.local_memory[entry_id]
```

### **Retention Policies**
- **Session memories**: 30 days (conversations, temporary analysis)
- **Important memories**: 90 days (decisions, major analysis)
- **Error logs**: 60 days (debugging information)
- **Code context**: Persistent (until codebase changes)

## 📊 **Performance Optimization**

### **Token Management**
- **Smart truncation**: Respects LLM context limits
- **Priority-based selection**: Most relevant content first
- **Cost estimation**: Token usage prediction
- **Efficient encoding**: Optimized storage format

### **Search Optimization**
- **Indexed storage**: Fast retrieval mechanisms
- **Caching strategies**: Frequently accessed content
- **Batch operations**: Efficient bulk processing
- **Lazy loading**: Memory-efficient operations

## 🎯 **Best Practices**

### **Memory Usage**
1. **Categorize properly**: Use appropriate context types
2. **Add metadata**: Include relevant tags and information
3. **Regular cleanup**: Use automatic retention policies
4. **Monitor usage**: Check memory status regularly

### **Search Strategies**
1. **Specific queries**: Use targeted search terms
2. **Context filtering**: Limit to relevant types
3. **Result limits**: Control response size
4. **Include codebase**: Leverage hybrid search

### **Configuration**
1. **Choose appropriate mode**: Development vs Production
2. **Set retention policies**: Based on usage patterns
3. **Configure token limits**: Match your LLM capabilities
4. **Enable integrations**: Use codebase awareness

---

**Next**: Explore the [Codebase Indexer](./codebase-indexer.md) for code analysis capabilities.

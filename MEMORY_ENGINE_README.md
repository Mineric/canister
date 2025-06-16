# Memory & Context Engine

A robust memory and context management system for the Canister agent, integrating Google ADK memory capabilities with codebase awareness for professional-level context retention and retrieval.

## 🎯 **Overview**

The Memory Engine provides:
- **Persistent conversation memory** across sessions
- **Intelligent context prioritization** for large codebases
- **Hybrid search** combining conversation history and codebase knowledge
- **Google ADK integration** for enterprise-scale memory management
- **Automatic cleanup** and retention policies

## 🏗️ **Architecture**

### **Core Components**

1. **MemoryEngine**: Main memory management system
2. **MemoryEntry**: Structured memory storage with priority scoring
3. **ContextPriority**: Intelligent context ranking system
4. **MemoryConfig**: Flexible configuration for different deployment modes

### **Integration Points**

- **Google ADK Memory Services**: `InMemoryMemoryService`, `VertexAiRagMemoryService`
- **Google ADK Session Services**: `InMemorySessionService`, `VertexAiSessionService`
- **Codebase Indexer**: Seamless integration with existing code analysis
- **FunctionTool Wrappers**: Native Google ADK tool integration

## 🚀 **Features**

### **Memory Modes**

```python
class MemoryMode(Enum):
    DEVELOPMENT = "development"  # In-memory only
    PRODUCTION = "production"    # Vertex AI with persistence  
    HYBRID = "hybrid"           # Both local and cloud
```

### **Context Types**

- **conversation**: User interactions and responses
- **codebase**: Code elements and structure information
- **analysis**: Code analysis results and insights
- **decision**: Important decisions and reasoning
- **error**: Error handling and debugging information

### **Priority Scoring**

Intelligent context prioritization based on:
- **Relevance Score** (50%): Content analysis and keyword matching
- **Recency Score** (30%): Time-based importance
- **Importance Score** (20%): Context type weighting

## 🛠️ **Usage**

### **Basic Setup**

```python
from agent.tools.memory_engine import get_memory_engine, MemoryConfig, MemoryMode

# Development mode (in-memory)
config = MemoryConfig(mode=MemoryMode.DEVELOPMENT)
memory_engine = get_memory_engine(config)

# Production mode (Vertex AI)
config = MemoryConfig(
    mode=MemoryMode.PRODUCTION,
    project_id="your-gcp-project",
    rag_corpus_name="projects/your-project/locations/us-central1/ragCorpora/your-corpus"
)
memory_engine = get_memory_engine(config)
```

### **Adding Memory**

```python
# Add conversation memory
entry_id = await memory_engine.add_memory(
    content="Implemented JWT authentication system",
    session_id="session_123",
    user_id="user_456",
    context_type="analysis",
    metadata={"feature": "auth", "priority": "high"}
)
```

### **Searching Memory**

```python
# Search with context prioritization
results = await memory_engine.search_memory(
    query="authentication",
    user_id="user_456",
    context_types=["conversation", "analysis"],
    max_results=10,
    include_codebase=True
)
```

### **Context Summaries**

```python
# Get session context summary
summary = await memory_engine.get_context_summary(
    session_id="session_123",
    max_tokens=8000
)
```

## 🔧 **Tools Integration**

The memory system provides three Google ADK tools:

### **1. Memory Search Tool**

```python
memory_search_tool()
```

**Function**: `search_memory(query, context_types, max_results, include_codebase, user_id)`

Search memory with intelligent context prioritization.

### **2. Context Tool**

```python
context_tool()
```

**Function**: `get_context(session_id, max_tokens)`

Get intelligent contextual summary for current session.

### **3. Memory Management Tool**

```python
memory_management_tool()
```

**Function**: `manage_memory(action, content, context_type, session_id, user_id, metadata)`

Manage memory system operations (add, cleanup, status, configure).

## 📊 **Configuration Options**

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

## 🔍 **Agent Integration**

The memory tools are automatically integrated into the Canister agent:

```python
# In agent/agent.py
from .tools.memory_engine import (
    memory_search_tool,
    context_tool,
    memory_management_tool
)

tools = [
    # ... other tools
    memory_search_tool(),
    context_tool(),
    memory_management_tool(),
]
```

## 💾 **Data Persistence**

### **Development Mode**
- Local JSON file storage in `.memory_cache/`
- Automatic loading on startup
- Manual cleanup required

### **Production Mode**
- Google Cloud Vertex AI RAG storage
- Automatic persistence and backup
- Scalable semantic search

### **Hybrid Mode**
- Local cache with cloud backup
- Best of both worlds approach
- Fallback capabilities

## 🧹 **Memory Management**

### **Automatic Cleanup**

```python
# Clean up old memories based on retention policies
await memory_engine.cleanup_old_memories()
```

### **Retention Policies**

- **Session memories**: 30 days (configurable)
- **General memories**: 90 days (configurable)
- **Important decisions**: Longer retention
- **Error logs**: Medium retention

## 🔧 **Advanced Features**

### **Codebase Integration**

Seamless integration with the existing codebase indexer:
- Automatic code element search
- Cross-reference between conversations and code
- Intelligent code context inclusion

### **Priority-Based Retrieval**

Smart context selection based on:
- Content relevance to current query
- Recency of information
- Importance of context type
- Token cost optimization

### **Cross-Session Learning**

- Memory persists across agent restarts
- Context awareness between different sessions
- Learning from previous interactions

## 📈 **Performance Optimization**

- **Token-aware context management**: Respects LLM token limits
- **Intelligent caching**: Fast retrieval of frequently accessed memories
- **Lazy loading**: Efficient memory usage
- **Batch operations**: Optimized for large-scale operations

## 🛡️ **Error Handling**

- Graceful degradation when services unavailable
- Fallback to local storage if cloud services fail
- Comprehensive error logging and recovery
- Data integrity protection

## 🎯 **Use Cases**

1. **Long-term project context**: Remember decisions and analysis across sessions
2. **Code understanding**: Maintain context about codebase structure and changes
3. **Debugging assistance**: Recall previous error patterns and solutions
4. **Learning from interactions**: Improve responses based on past conversations
5. **Cross-session continuity**: Seamless experience across agent restarts

## 🔮 **Future Enhancements**

- **Semantic search improvements**: Enhanced relevance scoring
- **Multi-user support**: User-specific memory isolation
- **Memory analytics**: Usage patterns and optimization insights
- **Integration with more ADK services**: Expanded cloud capabilities
- **Custom memory types**: Domain-specific memory categories

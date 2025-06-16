# Google ADK Integration

Comprehensive guide to Google Agent Development Kit (ADK) integration in the Canister Agent, providing enterprise-scale capabilities and cloud deployment options.

## 🎯 **Overview**

The Canister Agent is built on Google's Agent Development Kit (ADK), providing:
- **Professional Agent Framework**: LlmAgent with advanced capabilities
- **Memory Services**: InMemory + VertexAI RAG integration
- **Session Management**: Persistent conversation handling
- **Enterprise Deployment**: Production-ready cloud infrastructure
- **FunctionTool System**: Native tool integration

## 🏗️ **ADK Architecture**

### **Core Components**

```python
# ADK Integration Architecture
Canister Agent
├── LlmAgent (Google ADK)
├── LiteLlm (Multi-model support)
├── FunctionTool System (19 tools)
├── Memory Services (InMemory + VertexAI)
├── Session Services (InMemory + VertexAI)
└── Runner (Execution framework)
```

### **Agent Framework**

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

# Create ADK-based agent
agent = LlmAgent(
    model=LiteLlm(model="gpt-4"),
    tools=tools  # 19 FunctionTool instances
)
```

## 🧠 **Memory Integration**

### **Memory Services**

#### **Development Mode**
```python
from google.adk.memory import InMemoryMemoryService
from google.adk.sessions import InMemorySessionService

# In-memory services for development
session_service = InMemorySessionService()
memory_service = InMemoryMemoryService()
```

#### **Production Mode**
```python
from google.adk.memory import VertexAiRagMemoryService
from google.adk.sessions import VertexAiSessionService

# Vertex AI services for production
session_service = VertexAiSessionService(
    project="your-gcp-project",
    location="us-central1"
)

memory_service = VertexAiRagMemoryService(
    rag_corpus="projects/your-project/locations/us-central1/ragCorpora/your-corpus",
    similarity_top_k=10,
    vector_distance_threshold=0.7
)
```

### **Memory Configuration**

```python
from agent.tools.memory_engine import MemoryConfig, MemoryMode

# Development configuration
dev_config = MemoryConfig(
    mode=MemoryMode.DEVELOPMENT,
    cache_dir=".memory_cache",
    max_memory_results=10
)

# Production configuration
prod_config = MemoryConfig(
    mode=MemoryMode.PRODUCTION,
    project_id="your-gcp-project",
    location="us-central1",
    rag_corpus_name="projects/your-project/locations/us-central1/ragCorpora/your-corpus",
    max_context_tokens=32000,
    similarity_threshold=0.7
)
```

## 🛠️ **FunctionTool Integration**

### **Tool Creation Pattern**

All Canister tools follow the ADK FunctionTool pattern:

```python
from google.adk.tools import FunctionTool

def example_tool() -> FunctionTool:
    """Create an example tool following ADK patterns."""
    
    def example_function(
        param1: str,
        param2: int = 10,
        param3: bool = True
    ) -> str:
        """
        Example function with proper typing and documentation.
        
        Args:
            param1: Required string parameter
            param2: Optional integer parameter (default: 10)
            param3: Optional boolean parameter (default: True)
        
        Returns:
            Formatted result string
        """
        try:
            # Tool implementation
            result = f"Processed {param1} with {param2}, enabled: {param3}"
            return result
            
        except Exception as e:
            return f"Error: {str(e)}"
    
    return FunctionTool(example_function)
```

### **Tool Categories in ADK Context**

#### **Basic Utilities**
```python
# ADK-compatible basic tools
basic_tools = [
    get_current_time_tool(),      # Time utilities
    calculator_tool(),            # Mathematical operations
    text_analyzer_tool(),         # Text processing
    directory_operations_tool(),  # File system operations
    file_management_tool(),       # File operations
    terminal_command_tool(),      # System commands
    docker_sandbox_tool()         # Safe code execution
]
```

#### **Advanced Tools**
```python
# Professional SWE tools with ADK integration
advanced_tools = [
    ast_code_merger_tool(),           # AST-based merging
    enhanced_ast_code_merger_tool(),  # Enhanced merging
    code_structure_analyzer_tool(),   # Structure analysis
    intelligent_merger_tool(),       # Professional merging
    code_comprehension_tool()         # Architectural analysis
]
```

#### **Memory Tools**
```python
# Memory system with ADK services
memory_tools = [
    memory_search_tool(),      # Context retrieval
    context_tool(),           # Session summaries
    memory_management_tool()  # Memory operations
]
```

#### **Codebase Tools**
```python
# Codebase analysis with ADK integration
codebase_tools = [
    codebase_indexer_tool(),  # Project indexing
    code_search_tool(),       # Code search
    file_analysis_tool(),     # File analysis
    self_awareness_tool()     # Agent introspection
]
```

## 🚀 **Deployment Options**

### **Local Development**

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from agent.tools.memory_engine import MemoryConfig, MemoryMode

# Local development setup
config = MemoryConfig(mode=MemoryMode.DEVELOPMENT)
agent = create_agent()

# Run locally
response = agent.run("Analyze this codebase")
```

### **Cloud Deployment**

#### **Vertex AI Integration**
```python
# Production deployment with Vertex AI
config = MemoryConfig(
    mode=MemoryMode.PRODUCTION,
    project_id="your-gcp-project",
    location="us-central1",
    rag_corpus_name="your-rag-corpus"
)

# Create agent with cloud services
agent = create_agent()

# Deploy with ADK Runner
from google.adk.runners import Runner

runner = Runner(
    agent=agent,
    app_name="canister-agent",
    session_service=session_service,
    memory_service=memory_service
)
```

#### **Agent Engine Deployment**
```python
# Deploy to Google Cloud Agent Engine
# See: https://google.github.io/adk-docs/deploy/agent-engine/

PROJECT_ID = "your-gcp-project"
LOCATION = "us-central1"
REASONING_ENGINE_ID = "your-engine-id"

# Configure for Agent Engine
session_service = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION
)

# Use Reasoning Engine app name
app_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/reasoningEngines/{REASONING_ENGINE_ID}"
```

## 🔧 **Configuration Management**

### **Environment Variables**

```bash
# Google Cloud Configuration
export GOOGLE_CLOUD_PROJECT=your-gcp-project
export GOOGLE_CLOUD_LOCATION=us-central1
export GOOGLE_API_KEY=your-api-key

# Memory Configuration
export MEMORY_MODE=production
export RAG_CORPUS_NAME=your-rag-corpus
export CACHE_DIR=.memory_cache

# Agent Configuration
export MAX_CONTEXT_TOKENS=32000
export SIMILARITY_THRESHOLD=0.7
```

### **Configuration Files**

```python
# config/production.py
from agent.tools.memory_engine import MemoryConfig, MemoryMode
import os

PRODUCTION_CONFIG = MemoryConfig(
    mode=MemoryMode.PRODUCTION,
    project_id=os.getenv("GOOGLE_CLOUD_PROJECT"),
    location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    rag_corpus_name=os.getenv("RAG_CORPUS_NAME"),
    max_context_tokens=int(os.getenv("MAX_CONTEXT_TOKENS", "32000")),
    similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))
)
```

## 📊 **Monitoring & Observability**

### **ADK Callbacks**

```python
from google.adk.callbacks import BaseCallback

class CanisterCallback(BaseCallback):
    """Custom callback for monitoring Canister agent."""
    
    def on_agent_start(self, agent, inputs):
        """Called when agent starts processing."""
        print(f"Agent started with inputs: {inputs}")
    
    def on_tool_start(self, tool, inputs):
        """Called when tool starts executing."""
        print(f"Tool {tool.name} started with: {inputs}")
    
    def on_tool_end(self, tool, outputs):
        """Called when tool completes."""
        print(f"Tool {tool.name} completed with: {outputs}")
    
    def on_agent_end(self, agent, outputs):
        """Called when agent completes."""
        print(f"Agent completed with: {outputs}")

# Use callback with agent
agent = create_agent()
agent.callbacks = [CanisterCallback()]
```

### **Performance Metrics**

```python
# Monitor tool usage
tool_usage = {}
for tool in agent.tools:
    tool_name = tool.func.__name__
    tool_usage[tool_name] = {
        "calls": 0,
        "total_time": 0,
        "errors": 0
    }

# Memory usage monitoring
memory_stats = {
    "total_memories": len(memory_engine.local_memory),
    "cache_size": memory_engine.cache_dir.stat().st_size,
    "last_cleanup": memory_engine.last_cleanup_time
}
```

## 🛡️ **Security & Authentication**

### **Google Cloud Authentication**

```python
# Service account authentication
import os
from google.oauth2 import service_account

# Set up credentials
credentials = service_account.Credentials.from_service_account_file(
    "path/to/service-account-key.json"
)

# Use with ADK services
session_service = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION,
    credentials=credentials
)
```

### **API Key Management**

```python
# Secure API key handling
import os
from google.adk.models.lite_llm import LiteLlm

# Use environment variables
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable required")

model = LiteLlm(
    model="gpt-4",
    api_key=api_key
)
```

## 🔄 **Session Management**

### **Session Lifecycle**

```python
from google.adk.runners import Runner

# Create runner with session management
runner = Runner(
    agent=agent,
    app_name="canister-agent",
    session_service=session_service,
    memory_service=memory_service
)

# Session operations
session = await runner.session_service.create_session(
    app_name="canister-agent",
    user_id="user_123",
    session_id="session_456"
)

# Add memory to session
await memory_service.add_session_to_memory(session)
```

### **Cross-Session Context**

```python
# Search across sessions
from google.adk.tools import load_memory

# Built-in ADK memory tool
memory_tool = load_memory

# Custom memory search
results = await memory_service.search_memory(
    app_name="canister-agent",
    user_id="user_123",
    query="authentication implementation"
)
```

## 📈 **Scaling & Performance**

### **Horizontal Scaling**

```python
# Multiple agent instances
agents = []
for i in range(5):
    agent = create_agent()
    agents.append(agent)

# Load balancing
import random

def get_agent():
    return random.choice(agents)
```

### **Caching Strategies**

```python
# Multi-level caching
class CacheManager:
    def __init__(self):
        self.memory_cache = {}      # In-memory cache
        self.redis_cache = None     # Redis for distributed cache
        self.disk_cache = None      # Disk-based cache
    
    def get(self, key):
        # Check memory first
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # Check Redis
        if self.redis_cache:
            value = self.redis_cache.get(key)
            if value:
                self.memory_cache[key] = value
                return value
        
        # Check disk
        return self.disk_cache.get(key)
```

## 🎯 **Best Practices**

### **ADK Integration**
1. **Use native patterns**: Follow ADK conventions
2. **Leverage services**: Use built-in memory and session services
3. **Handle errors gracefully**: Implement proper error handling
4. **Monitor performance**: Use callbacks and metrics

### **Tool Development**
1. **Consistent interface**: Follow FunctionTool patterns
2. **Proper typing**: Use type hints for all parameters
3. **Comprehensive docs**: Include detailed docstrings
4. **Error handling**: Graceful degradation and recovery

### **Deployment**
1. **Environment separation**: Different configs for dev/prod
2. **Secure credentials**: Use proper authentication
3. **Monitor resources**: Track usage and performance
4. **Scale appropriately**: Plan for growth

---

**Next**: Explore [Configuration Guide](./configuration.md) for detailed setup instructions.

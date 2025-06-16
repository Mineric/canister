# Canister Agent Documentation

Comprehensive documentation for the Canister Agent - a coding agent designed to improve itself.

## 📚 **Documentation Structure**

### **Core Systems**
- [**Agent Overview**](./agent-overview.md) - Main agent architecture and capabilities
- [**Tools System**](./tools-system.md) - Complete tool ecosystem and usage
- [**Memory Engine**](./memory-engine.md) - Memory & context management system
- [**Codebase Indexer**](./codebase-indexer.md) - Code analysis and indexing system

### **Advanced Features**
- [**AST Code Tools**](./ast-code-tools.md) - AST-based code manipulation and merging
- [**Professional SWE**](./professional-swe.md) - Professional software engineering capabilities

### **Integration & Deployment**
- [**Google ADK Integration**](./adk-integration.md) - Google Agent Development Kit integration
- [**Configuration Guide**](./configuration.md) - Setup and configuration options
- [**API Reference**](./api-reference.md) - Complete API documentation

### **Development**
- [**Development Guide**](./development.md) - Development setup and guidelines
- [**Testing Guide**](./testing.md) - Testing strategies and examples
- [**Contributing**](./contributing.md) - Contribution guidelines

## 🚀 **Quick Start**

### **Basic Usage**
```python
from agent.agent import create_agent

# Create agent with all tools
agent = create_agent()

# Agent has 19 tools including:
# - Basic utilities (time, calculator, text analysis)
# - File system operations (directory, file management)
# - Code tools (AST merging, structure analysis)
# - Professional SWE (intelligent merging, code comprehension)
# - Memory system (search, context, management)
# - Codebase indexing (indexing, search, analysis, self-awareness)
```

### **Memory System**
```python
from agent.tools.memory_engine import get_memory_engine, MemoryConfig

# Initialize memory engine
memory_engine = get_memory_engine()

# Add memory
await memory_engine.add_memory(
    content="Implemented JWT authentication",
    session_id="session_123",
    user_id="user_456",
    context_type="analysis"
)

# Search memory
results = await memory_engine.search_memory(
    query="authentication",
    include_codebase=True
)
```

### **Codebase Analysis**
```python
from agent.tools.codebase_indexer import get_global_indexer

# Index codebase
indexer = get_global_indexer()
stats = indexer.index_codebase("/path/to/project")

# Search code elements
results = indexer.search_code_elements("authentication")

# Analyze file
summary = indexer.get_file_summary("src/auth.py")
```

## 🎯 **Key Features**

### **Professional SWE Capabilities**
- ✅ **Intelligent Code Merging** - AST-based with conflict resolution
- ✅ **Advanced Code Comprehension** - Deep architectural analysis
- ✅ **Codebase Awareness** - Full project understanding
- ✅ **Memory & Context** - Persistent learning across sessions
- ✅ **Professional Tools** - Enterprise-grade development assistance

### **Google ADK Integration**
- ✅ **Native FunctionTool** integration
- ✅ **Memory Services** - InMemory + VertexAI RAG
- ✅ **Session Management** - Persistent conversations
- ✅ **Enterprise Scale** - Production-ready architecture

### **Advanced Code Tools**
- ✅ **AST Code Merger** - Intelligent code integration
- ✅ **Structure Analyzer** - Code architecture analysis
- ✅ **Dependency Tracking** - Cross-file relationship mapping
- ✅ **Conflict Detection** - Smart merge conflict resolution

## 📊 **System Architecture**

```
Canister Agent
├── Core Agent (Google ADK LlmAgent)
├── Tools System (19 tools)
│   ├── Basic Tools (7) - utilities, file ops, terminal
│   ├── AST Tools (3) - code merging, structure analysis
│   ├── Professional SWE (2) - intelligent merger, comprehension
│   ├── Memory Tools (3) - search, context, management
│   └── Codebase Tools (4) - indexing, search, analysis, self-awareness
├── Memory Engine (ADK integration)
│   ├── Local Storage (JSON + SQLite)
│   ├── Cloud Storage (Vertex AI RAG)
│   └── Hybrid Architecture
└── Codebase Indexer (SQLite + AST)
    ├── Code Element Tracking
    ├── Dependency Mapping
    └── Cross-file Analysis
```

## 🛠️ **Tool Categories**

### **Basic Utilities (7 tools)**
- `get_current_time` - Date/time utilities
- `calculator` - Mathematical operations
- `text_analyzer` - Text processing and analysis
- `directory_operations` - File system navigation
- `file_management` - File operations
- `terminal_command` - System command execution
- `run_code_in_sandbox` - Safe code execution

### **AST Code Tools (3 tools)**
- `merge_code_intelligently` - Basic AST-based merging
- `merge_code_with_codebase_awareness` - Enhanced merging with context
- `analyze_code_structure` - Code structure analysis

### **Professional SWE (2 tools)**
- `merge_code_professionally` - Professional-grade code merging
- `analyze_codebase_architecture` - Deep architectural analysis

### **Memory System (3 tools)**
- `search_memory` - Intelligent context retrieval
- `get_context` - Session-specific summaries
- `manage_memory` - Memory operations

### **Codebase Indexing (4 tools)**
- `index_codebase` - Project indexing and analysis
- `search_code` - Code element search
- `analyze_file` - File-specific analysis
- `analyze_self` - Agent self-awareness

## 🔧 **Configuration**

### **Memory Modes**
- **Development**: In-memory with local persistence
- **Production**: Google Cloud Vertex AI with RAG
- **Hybrid**: Local + cloud backup

### **Deployment Options**
- **Local Development**: All tools with local storage
- **Cloud Production**: ADK + Vertex AI integration
- **Enterprise**: Full-scale with persistent memory

## 📈 **Performance & Scale**

- **Memory**: Intelligent context prioritization with token limits
- **Codebase**: SQLite indexing for fast search and retrieval
- **Tools**: Optimized for large-scale enterprise codebases
- **Integration**: Native Google ADK for production deployment

## 🎯 **Use Cases**

1. **Enterprise Development** - Large codebase analysis and modification
2. **Code Review** - Intelligent code understanding and suggestions
3. **Architecture Analysis** - Deep system design comprehension
4. **Learning Assistant** - Context-aware development guidance
5. **Debugging Support** - Memory-based error pattern recognition

## 📝 **Documentation Navigation**

Start with the [**Agent Overview**](./agent-overview.md) for a comprehensive introduction, then explore specific systems based on your needs:

- **New Users**: Agent Overview → Tools System → Configuration
- **Developers**: Development Guide → API Reference → Testing Guide
- **Advanced Users**: Memory Engine → Professional SWE → AST Code Tools
- **Enterprise**: ADK Integration → Configuration → Professional SWE

## 📊 **Documentation Overview**

This documentation covers **13 comprehensive guides** organized into 4 main categories:
- **4 Core Systems**: Agent, Tools, Memory, Codebase Indexer
- **2 Advanced Features**: AST Tools, Professional SWE
- **3 Integration & Deployment**: ADK, Configuration, API Reference
- **3 Development**: Development, Testing, Contributing

All **19 tools**, **memory system**, **codebase indexer**, and **professional SWE capabilities** are fully documented with examples, API references, and best practices.

## 🔗 **External Resources**

- [Google ADK Documentation](https://google.github.io/adk-docs/)
- [Python AST Module](https://docs.python.org/3/library/ast.html)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

---

**Copyright (c) 2024 Thant Min Htet. All rights reserved.**

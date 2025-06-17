# Tool Structure Redesign Plan

## 🎯 **Problems with Current Structure**

### **Current Issues**
1. **Fragmented Tools**: 7 separate tool files with overlapping functionality
2. **Redundant Code**: File operations in multiple places  
3. **Inconsistent Patterns**: Mix of `_tool()` functions and direct implementations
4. **Poor Categorization**: Basic utilities mixed with complex analysis
5. **Naming Confusion**: No clear hierarchy or grouping

### **Current Tool Count: 17 Tools** 
```python
# Basic utilities (should be consolidated)
get_current_time_tool()
calculator_tool() 
text_analyzer_tool()
directory_operations_tool()
file_management_tool()
terminal_command_tool()
docker_sandbox_tool()

# Code tools (overlapping functionality)
ast_code_merger_tool()
enhanced_ast_code_merger_tool()    # Redundant naming
code_structure_analyzer_tool()
code_comprehension_tool()
intelligent_merger_tool()          # Similar to ast tools

# Indexing tools (good separation)
codebase_indexer_tool()
code_search_tool()
file_analysis_tool()
self_awareness_tool()

# Memory tools (good separation)
memory_search_tool()
context_tool()
memory_management_tool()
```

## 🏗️ **New Generic Tool Architecture**

### **Design Principles**
- **Single Responsibility**: Each tool file handles one domain
- **Generic Operations**: Tools work with any content type
- **Consistent Patterns**: Uniform interface across all tools
- **Extensible Design**: Easy to add new capabilities
- **Clean Naming**: Intuitive, hierarchical naming

### **Consolidated Structure: 5 Tool Categories**

```python
agent/
├── core/                        # Core functionality (not tools)
│   ├── vector_store.py         
│   ├── semantic_engine.py      
│   ├── embedding_manager.py    
│   └── embedding_cache.py      
└── tools/                       # Tool interface layer
    ├── system.py               # System operations
    ├── code.py                 # Code operations  
    ├── memory.py               # Memory operations
    ├── search.py               # Search operations
    └── analysis.py             # Analysis operations
```

## 📋 **Tool Consolidation Plan**

### **1. `tools/system.py` - System Operations**
**Consolidates**: `tools.py` (all basic utilities)

```python
class SystemTools:
    """System-level operations: files, processes, time, calculations."""
    
    @staticmethod 
    def filesystem(operation: str, path: str = "", content: str = "", **kwargs) -> str:
        """Unified file system operations."""
        # Consolidates: directory_operations_tool + file_management_tool
        operations = {
            "read": lambda: Path(path).read_text(),
            "write": lambda: Path(path).write_text(content),
            "list": lambda: list(Path(path).iterdir()),
            "exists": lambda: Path(path).exists(),
            "mkdir": lambda: Path(path).mkdir(parents=True, exist_ok=True)
        }
        
    @staticmethod
    def process(command: str, timeout: int = 30, cwd: str = "") -> str:
        """Execute system commands safely."""
        # Consolidates: terminal_command_tool + docker_sandbox_tool
        
    @staticmethod  
    def calculate(expression: str) -> str:
        """Safe mathematical calculations."""
        # Consolidates: calculator_tool
        
    @staticmethod
    def analyze_text(text: str) -> Dict[str, Any]:
        """Text analysis and statistics."""
        # Consolidates: text_analyzer_tool
        
    @staticmethod
    def get_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Current time in specified format."""
        # Consolidates: get_current_time_tool
```

### **2. `tools/code.py` - Code Operations**
**Consolidates**: `code_tools.py` + `intelligent_merger.py` + parts of `codebase_indexer.py`

```python
class CodeTools:
    """Code analysis, manipulation, and merging operations."""
    
    @staticmethod
    def merge(source_file: str, new_code: str, strategy: str = "intelligent") -> str:
        """Intelligent code merging with multiple strategies."""
        # Consolidates: ast_code_merger_tool + enhanced_ast_code_merger_tool + intelligent_merger_tool
        
    @staticmethod 
    def analyze_structure(file_path: str) -> Dict[str, Any]:
        """Analyze code structure and patterns."""
        # Consolidates: code_structure_analyzer_tool
        
    @staticmethod
    def index_codebase(root_path: str, **options) -> Dict[str, Any]:
        """Index codebase for analysis and search."""
        # Consolidates: codebase_indexer_tool
        
    @staticmethod
    def analyze_file(file_path: str) -> Dict[str, Any]:
        """Detailed file analysis with metrics."""
        # Consolidates: file_analysis_tool
```

### **3. `tools/search.py` - Search Operations**
**New unified search interface**

```python
class SearchTools:
    """Unified search across code, memory, and documentation."""
    
    @staticmethod
    def code(query: str, search_type: str = "hybrid", **filters) -> List[Dict]:
        """Search code elements with semantic + keyword."""
        # Consolidates: code_search_tool + semantic search
        
    @staticmethod  
    def memory(query: str, search_type: str = "hybrid", **filters) -> List[Dict]:
        """Search memory with context awareness."""
        # Consolidates: memory_search_tool + semantic memory search
        
    @staticmethod
    def similarity(item: Union[str, Dict], item_type: str = "auto") -> List[Dict]:
        """Find similar items (code, memory, docs)."""
        # New: unified similarity search
        
    @staticmethod
    def context(session_id: str, max_tokens: int = 8000) -> str:
        """Get contextual information for session."""
        # Consolidates: context_tool
```

### **4. `tools/memory.py` - Memory Operations**
**Consolidates**: `memory_engine.py` tools

```python
class MemoryTools:
    """Memory and context management operations."""
    
    @staticmethod
    def store(content: str, context_type: str = "conversation", **metadata) -> str:
        """Store information in memory."""
        
    @staticmethod
    def retrieve(query: str, **filters) -> List[Dict]:
        """Retrieve relevant memories."""
        
    @staticmethod
    def manage(action: str, **params) -> str:
        """Memory management operations."""
        # Consolidates: memory_management_tool
        
    @staticmethod
    def cluster(memories: List[Dict], method: str = "semantic") -> List[List[Dict]]:
        """Group related memories."""
```

### **5. `tools/analysis.py` - Analysis Operations**
**Consolidates**: `code_comprehension.py` + new analysis tools

```python
class AnalysisTools:
    """Deep analysis and comprehension operations."""
    
    @staticmethod
    def comprehend_code(file_path: str, analysis_type: str = "full") -> Dict[str, Any]:
        """Deep code comprehension and pattern analysis."""
        # Consolidates: code_comprehension_tool
        
    @staticmethod
    def self_analyze(include_structure: bool = True, include_capabilities: bool = True) -> Dict[str, Any]:
        """Agent self-awareness and capability analysis."""
        # Consolidates: self_awareness_tool
        
    @staticmethod
    def architectural_patterns(root_path: str) -> List[Dict]:
        """Detect architectural patterns in codebase."""
        
    @staticmethod
    def quality_metrics(target: str, target_type: str = "file") -> Dict[str, Any]:
        """Calculate quality metrics for code or project."""
```

## 🔄 **Tool Registration Pattern**

### **New Generic Registration**
```python
# agent/tools/__init__.py
from google.adk.tools import FunctionTool
from .system import SystemTools
from .code import CodeTools  
from .search import SearchTools
from .memory import MemoryTools
from .analysis import AnalysisTools

def create_tool(tool_class, method_name: str) -> FunctionTool:
    """Generic tool creation from class methods."""
    method = getattr(tool_class, method_name)
    return FunctionTool(method)

def get_all_tools() -> List[FunctionTool]:
    """Get all available tools with clean names."""
    return [
        # System tools
        create_tool(SystemTools, "filesystem"),
        create_tool(SystemTools, "process"), 
        create_tool(SystemTools, "calculate"),
        create_tool(SystemTools, "analyze_text"),
        create_tool(SystemTools, "get_time"),
        
        # Code tools
        create_tool(CodeTools, "merge"),
        create_tool(CodeTools, "analyze_structure"),
        create_tool(CodeTools, "index_codebase"),
        create_tool(CodeTools, "analyze_file"),
        
        # Search tools
        create_tool(SearchTools, "code"),
        create_tool(SearchTools, "memory"),
        create_tool(SearchTools, "similarity"),
        create_tool(SearchTools, "context"),
        
        # Memory tools
        create_tool(MemoryTools, "store"),
        create_tool(MemoryTools, "retrieve"),
        create_tool(MemoryTools, "manage"),
        create_tool(MemoryTools, "cluster"),
        
        # Analysis tools
        create_tool(AnalysisTools, "comprehend_code"),
        create_tool(AnalysisTools, "self_analyze"),
        create_tool(AnalysisTools, "architectural_patterns"),
        create_tool(AnalysisTools, "quality_metrics"),
    ]
```

### **Simplified Agent Creation**
```python
# agent/agent.py
from .tools import get_all_tools

def create_agent():
    """Create agent with consolidated tools."""
    tools = get_all_tools()
    
    agent = LlmAgent(
        name="CanisterAgent",
        model=LiteLlm(model="openai/gpt-4o"),
        instruction="Professional SWE-level AI agent with semantic understanding...",
        tools=tools
    )
    return agent
```

## 📊 **Benefits of New Structure**

### **Reduced Complexity**
- **From 17 tools → 13 tools**: 23% reduction
- **From 7 files → 5 files**: Cleaner organization
- **From mixed patterns → uniform interface**: Consistent API

### **Improved Maintainability** 
- **Single domain per file**: Easy to find and modify functionality
- **Generic patterns**: Add new operations easily
- **Clear separation**: Core logic vs tool interface

### **Better User Experience**
- **Intuitive naming**: `search.code()`, `memory.store()`, `system.filesystem()`
- **Consistent parameters**: Uniform interface across all tools
- **Comprehensive operations**: Each tool handles its domain completely

### **Enhanced Extensibility**
- **Easy tool addition**: Just add methods to appropriate class
- **Vector integration ready**: Search tools designed for semantic enhancement
- **Plugin architecture**: Core functionality separate from tool interface

## 🚀 **Implementation Strategy with Git Workflow**

### **Phase 1: Tool Restructure Foundation**
**Branch**: `feature/tool-restructure-foundation`
1. Create new `core/` and `tools/` directories structure
2. Implement `SystemTools` class consolidating basic utilities
3. **PR Size**: ~300-400 lines, easy review scope

### **Phase 2: Core Tool Classes**  
**Branch**: `feature/tool-restructure-core`
4. Implement `CodeTools` and `SearchTools` classes
5. Create generic tool registration pattern
6. **PR Size**: ~400-500 lines, focused on core functionality

### **Phase 3: Memory & Analysis Tools**
**Branch**: `feature/tool-restructure-complete`
7. Implement `MemoryTools` and `AnalysisTools` classes
8. Update `agent.py` to use new tool structure
9. **PR Size**: ~300-400 lines, completes restructure

### **Phase 4: Vector Infrastructure Foundation**
**Branch**: `feature/vector-core-infrastructure`  
10. Implement `EmbeddingEngine` and `VectorStore` core classes
11. Add basic semantic search infrastructure
12. **PR Size**: ~500-600 lines, new core functionality

### **Phase 5: Vector Integration**
**Branch**: `feature/vector-semantic-search`
13. Add semantic capabilities to `SearchTools` 
14. Enhance `MemoryTools` with vector support
15. **PR Size**: ~400-500 lines, semantic enhancements

### **Phase 6: Testing & Optimization**
**Branch**: `feature/vector-testing-optimization`
16. Comprehensive test suite for all new functionality
17. Performance optimization and documentation
18. **PR Size**: ~300-400 lines, tests and polish

## ✅ **Success Criteria**

- [ ] **Reduced Tool Count**: From 17 to 13 tools
- [ ] **Consolidated Files**: From 7 to 5 tool files  
- [ ] **Consistent Interface**: All tools follow same pattern
- [ ] **Maintained Functionality**: No feature regression
- [ ] **Improved Discoverability**: Clear tool categories
- [ ] **Ready for Vectors**: Architecture supports semantic enhancement

---

*This restructure creates a solid foundation for vector integration while dramatically simplifying the tool landscape.*
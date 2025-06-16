# API Reference

Complete API reference for the Canister Agent tools and systems.

## 🎯 **Overview**

This reference covers all 19 tools and their APIs, organized by category:
- [Basic Utilities](#basic-utilities) (7 tools)
- [AST Code Tools](#ast-code-tools) (3 tools)
- [Professional SWE](#professional-swe) (2 tools)
- [Memory System](#memory-system) (3 tools)
- [Codebase Indexing](#codebase-indexing) (4 tools)

## 🛠️ **Basic Utilities**

### **get_current_time_tool()**

```python
def get_current_time() -> str
```

**Purpose**: Get current date and time

**Returns**: Current timestamp in YYYY-MM-DD HH:MM:SS format

**Example**:
```python
result = await tool.func()
# Returns: "2024-01-15 14:30:25"
```

### **calculator_tool()**

```python
def calculator(operation: str, a: float, b: float) -> str
```

**Purpose**: Perform mathematical operations

**Parameters**:
- `operation`: Operation type ("add", "subtract", "multiply", "divide")
- `a`: First number
- `b`: Second number

**Returns**: Calculation result or error message

**Example**:
```python
result = await tool.func("add", 5, 3)
# Returns: "Result: 8"
```

### **text_analyzer_tool()**

```python
def text_analyzer(text: str, analysis_type: str = "basic") -> str
```

**Purpose**: Analyze and process text

**Parameters**:
- `text`: Text to analyze
- `analysis_type`: Type of analysis ("basic", "detailed", "sentiment")

**Returns**: Analysis results

### **directory_operations_tool()**

```python
def directory_operations(
    action: str,
    path: str = ".",
    pattern: str = "*"
) -> str
```

**Purpose**: File system navigation and directory management

**Parameters**:
- `action`: Operation ("list", "create", "delete", "info")
- `path`: Directory path (default: current directory)
- `pattern`: File pattern for filtering (default: all files)

**Returns**: Operation result

### **file_management_tool()**

```python
def file_management(
    action: str,
    file_path: str,
    content: str = "",
    encoding: str = "utf-8"
) -> str
```

**Purpose**: File operations

**Parameters**:
- `action`: Operation ("read", "write", "create", "delete", "append")
- `file_path`: Path to file
- `content`: Content for write operations
- `encoding`: File encoding (default: utf-8)

**Returns**: Operation result or file content

### **terminal_command_tool()**

```python
def terminal_command(
    command: str,
    working_directory: str = ".",
    timeout: int = 30
) -> str
```

**Purpose**: Execute system commands

**Parameters**:
- `command`: Command to execute
- `working_directory`: Working directory (default: current)
- `timeout`: Command timeout in seconds

**Returns**: Command output or error

### **docker_sandbox_tool()**

```python
def run_code_in_sandbox(
    code: str,
    language: str = "python",
    timeout: int = 30
) -> str
```

**Purpose**: Safe code execution in isolated environment

**Parameters**:
- `code`: Code to execute
- `language`: Programming language ("python", "javascript", "bash")
- `timeout`: Execution timeout

**Returns**: Execution result

## 🔧 **AST Code Tools**

### **ast_code_merger_tool()**

```python
def merge_code_intelligently(
    file_path: str,
    ai_generated_code: str,
    backup: bool = True,
    dry_run: bool = False,
    use_indexer: bool = True,
    analyze_impact: bool = True
) -> str
```

**Purpose**: Intelligent AST-based code merging

**Parameters**:
- `file_path`: Target file path
- `ai_generated_code`: Code to merge
- `backup`: Create backup before merging
- `dry_run`: Preview changes without applying
- `use_indexer`: Use codebase indexer for context
- `analyze_impact`: Perform impact analysis

**Returns**: Merge result with details

### **enhanced_ast_code_merger_tool()**

```python
def merge_code_with_codebase_awareness(
    file_path: str,
    ai_generated_code: str,
    backup: bool = True,
    dry_run: bool = False,
    force_index_update: bool = False
) -> str
```

**Purpose**: Enhanced merging with full codebase awareness

**Parameters**:
- `file_path`: Target file path
- `ai_generated_code`: Code to merge
- `backup`: Create backup
- `dry_run`: Preview mode
- `force_index_update`: Force codebase reindexing

**Returns**: Enhanced merge result

### **code_structure_analyzer_tool()**

```python
def analyze_code_structure(
    file_path: str,
    include_metrics: bool = True,
    include_dependencies: bool = True,
    include_suggestions: bool = True
) -> str
```

**Purpose**: Comprehensive code structure analysis

**Parameters**:
- `file_path`: File to analyze
- `include_metrics`: Include complexity metrics
- `include_dependencies`: Include dependency analysis
- `include_suggestions`: Include improvement suggestions

**Returns**: Detailed structure analysis

## 🎓 **Professional SWE**

### **intelligent_merger_tool()**

```python
def merge_code_professionally(
    file_path: str,
    ai_generated_code: str,
    merge_strategy: str = "intelligent",
    conflict_resolution: str = "interactive",
    preserve_architecture: bool = True,
    validate_changes: bool = True
) -> str
```

**Purpose**: Professional-grade code merging

**Parameters**:
- `file_path`: Target file
- `ai_generated_code`: Code to merge
- `merge_strategy`: Strategy ("intelligent", "conservative", "aggressive")
- `conflict_resolution`: Resolution method ("interactive", "auto", "manual")
- `preserve_architecture`: Maintain architectural patterns
- `validate_changes`: Validate merged code

**Returns**: Professional merge result

### **code_comprehension_tool()**

```python
def analyze_codebase_architecture(
    root_path: str,
    analysis_depth: str = "comprehensive",
    include_patterns: str = "*.py",
    exclude_patterns: str = "__pycache__,*.pyc",
    focus_areas: str = "all"
) -> str
```

**Purpose**: Deep architectural analysis

**Parameters**:
- `root_path`: Project root directory
- `analysis_depth`: Analysis level ("basic", "detailed", "comprehensive")
- `include_patterns`: File patterns to include
- `exclude_patterns`: File patterns to exclude
- `focus_areas`: Areas to focus on ("all", "patterns", "quality", "dependencies")

**Returns**: Architectural analysis report

## 🧠 **Memory System**

### **memory_search_tool()**

```python
def search_memory(
    query: str,
    context_types: str = "conversation,codebase,analysis",
    max_results: int = 10,
    include_codebase: bool = True,
    user_id: str = "default_user"
) -> str
```

**Purpose**: Intelligent context retrieval

**Parameters**:
- `query`: Search query
- `context_types`: Comma-separated context types
- `max_results`: Maximum results to return
- `include_codebase`: Include codebase search
- `user_id`: User identifier

**Returns**: Formatted search results

### **context_tool()**

```python
def get_context(
    session_id: str = "current_session",
    max_tokens: int = 8000
) -> str
```

**Purpose**: Session-specific context summaries

**Parameters**:
- `session_id`: Session identifier
- `max_tokens`: Maximum tokens for summary

**Returns**: Context summary

### **memory_management_tool()**

```python
def manage_memory(
    action: str,
    content: str = "",
    context_type: str = "conversation",
    session_id: str = "current_session",
    user_id: str = "default_user",
    metadata: str = "{}"
) -> str
```

**Purpose**: Memory operations

**Parameters**:
- `action`: Action ("add", "cleanup", "status", "configure")
- `content`: Content to add (for "add" action)
- `context_type`: Context type ("conversation", "codebase", "analysis", "decision")
- `session_id`: Session identifier
- `user_id`: User identifier
- `metadata`: JSON metadata string

**Returns**: Operation result

## 📊 **Codebase Indexing**

### **codebase_indexer_tool()**

```python
def index_codebase(
    root_path: str,
    exclude_patterns: str = "__pycache__,*.pyc,.git",
    include_patterns: str = "*.py",
    force_reindex: bool = False
) -> str
```

**Purpose**: Project indexing and analysis

**Parameters**:
- `root_path`: Project root directory
- `exclude_patterns`: Comma-separated exclude patterns
- `include_patterns`: Comma-separated include patterns
- `force_reindex`: Force complete reindexing

**Returns**: Indexing statistics

### **code_search_tool()**

```python
def search_code(
    query: str,
    element_type: str = "",
    file_pattern: str = "",
    max_results: int = 20
) -> str
```

**Purpose**: Code element search

**Parameters**:
- `query`: Search query
- `element_type`: Element type filter ("function", "class", "variable")
- `file_pattern`: File pattern filter
- `max_results`: Maximum results

**Returns**: Search results

### **file_analysis_tool()**

```python
def analyze_file(file_path: str) -> str
```

**Purpose**: Detailed file analysis

**Parameters**:
- `file_path`: File to analyze

**Returns**: Comprehensive file analysis

### **self_awareness_tool()**

```python
def analyze_self(
    include_tools: bool = True,
    include_structure: bool = True,
    include_dependencies: bool = True
) -> str
```

**Purpose**: Agent introspection

**Parameters**:
- `include_tools`: Include tool analysis
- `include_structure`: Include structure analysis
- `include_dependencies`: Include dependency analysis

**Returns**: Self-analysis report

## 🔧 **Core Classes**

### **MemoryEngine**

```python
class MemoryEngine:
    def __init__(self, config: MemoryConfig)
    
    async def add_memory(
        self,
        content: str,
        session_id: str,
        user_id: str,
        context_type: str = "conversation",
        metadata: Optional[Dict[str, Any]] = None
    ) -> str
    
    async def search_memory(
        self,
        query: str,
        user_id: Optional[str] = None,
        context_types: Optional[List[str]] = None,
        max_results: Optional[int] = None,
        include_codebase: bool = True
    ) -> List[MemoryEntry]
    
    async def get_context_summary(
        self,
        session_id: str,
        max_tokens: Optional[int] = None
    ) -> str
```

### **CodebaseIndexer**

```python
class CodebaseIndexer:
    def __init__(self, cache_dir: Optional[str] = None)
    
    def index_codebase(
        self,
        root_path: Union[str, Path],
        exclude_patterns: Optional[List[str]] = None,
        include_patterns: Optional[List[str]] = None,
        force_reindex: bool = False
    ) -> Dict[str, Any]
    
    def search_code_elements(
        self,
        query: str,
        element_type: Optional[str] = None,
        file_pattern: Optional[str] = None
    ) -> List[CodeElement]
    
    def get_file_summary(self, file_path: str) -> Dict[str, Any]
```

## 📋 **Data Models**

### **MemoryEntry**

```python
@dataclass
class MemoryEntry:
    id: str
    content: str
    context_type: str
    timestamp: datetime
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    priority: Optional[ContextPriority] = None
```

### **CodeElement**

```python
@dataclass
class CodeElement:
    name: str
    element_type: str
    file_path: str
    line_number: int
    end_line_number: Optional[int] = None
    signature: Optional[str] = None
    docstring: Optional[str] = None
    parent_class: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    complexity_score: int = 0
```

### **MemoryConfig**

```python
@dataclass
class MemoryConfig:
    mode: MemoryMode = MemoryMode.DEVELOPMENT
    project_id: Optional[str] = None
    location: str = "us-central1"
    rag_corpus_name: Optional[str] = None
    cache_dir: str = ".memory_cache"
    session_retention_days: int = 30
    memory_retention_days: int = 90
    max_context_tokens: int = 32000
    similarity_threshold: float = 0.7
    max_memory_results: int = 10
    enable_codebase_integration: bool = True
    enable_conversation_memory: bool = True
    enable_cross_session_learning: bool = True
```

## 🎯 **Usage Examples**

### **Basic Agent Usage**

```python
from agent.agent import create_agent

# Create agent
agent = create_agent()

# Use tools
response = await agent.run("Analyze this codebase and suggest improvements")
```

### **Memory System Usage**

```python
from agent.tools.memory_engine import get_memory_engine

# Get memory engine
memory = get_memory_engine()

# Add memory
await memory.add_memory(
    content="Implemented authentication system",
    session_id="session_123",
    user_id="user_456",
    context_type="analysis"
)

# Search memory
results = await memory.search_memory("authentication")
```

### **Codebase Indexing Usage**

```python
from agent.tools.codebase_indexer import get_global_indexer

# Get indexer
indexer = get_global_indexer()

# Index project
stats = indexer.index_codebase("/path/to/project")

# Search code
results = indexer.search_code_elements("authenticate")
```

---

**Next**: Explore [Development Guide](./development.md) for development setup and guidelines.

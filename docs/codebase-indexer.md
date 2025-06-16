# Codebase Indexing & Self-Awareness System

Comprehensive codebase indexing and self-awareness system providing deep understanding and navigation capabilities for codebases using AST analysis and SQLite storage.

## 🎯 **Overview**

The Codebase Indexer creates a searchable knowledge base of Python codebases, providing:
- **Deep Code Understanding**: AST-based analysis of code structure
- **Intelligent Search**: Fast, accurate code element retrieval
- **Dependency Tracking**: Cross-file relationship mapping
- **Self-Awareness**: Agent introspection capabilities
- **Persistent Storage**: SQLite backend for reliability

## 🏗️ **Architecture**

### **Core Components**

```python
# Codebase Indexer Architecture
CodebaseIndexer
├── SQLite Database (structured storage)
├── In-Memory Cache (fast access)
├── AST Parser (code analysis)
├── Dependency Graph (relationship tracking)
└── Search Engine (intelligent retrieval)
```

### **Data Models**

```python
@dataclass
class CodeElement:
    """Represents a code element (function, class, variable)."""
    name: str
    element_type: str  # 'function', 'class', 'variable', 'import'
    file_path: str
    line_number: int
    end_line_number: Optional[int]
    signature: Optional[str]
    docstring: Optional[str]
    parent_class: Optional[str]
    decorators: List[str]
    complexity_score: int

@dataclass
class ImportInfo:
    """Represents import relationships."""
    module: str
    imported_names: List[str]
    import_type: str  # 'import', 'from_import', 'relative_import'
    file_path: str
    line_number: int
    alias: Optional[str]

@dataclass
class FileInfo:
    """File-level metadata and statistics."""
    file_path: str
    size: int
    lines_of_code: int
    last_modified: datetime
    file_hash: str
    encoding: str
    syntax_errors: List[str]
```

## 🛠️ **Indexing Tools**

### **1. Codebase Indexer Tool**

```python
codebase_indexer_tool()
```

**Function**: `index_codebase(root_path, exclude_patterns, include_patterns, force_reindex)`

Comprehensive codebase analysis and indexing.

**Example**:
```python
# Index entire project
result = await indexer_tool.func(
    root_path="/path/to/project",
    exclude_patterns="__pycache__,*.pyc,.git",
    include_patterns="*.py",
    force_reindex=False
)
```

### **2. Code Search Tool**

```python
code_search_tool()
```

**Function**: `search_code(query, element_type, file_pattern, max_results)`

Intelligent code element search with filtering.

**Example**:
```python
# Search for authentication functions
result = await search_tool.func(
    query="authenticate",
    element_type="function",
    file_pattern="auth*.py",
    max_results=10
)
```

### **3. File Analysis Tool**

```python
file_analysis_tool()
```

**Function**: `analyze_file(file_path)`

Detailed analysis of specific files.

**Example**:
```python
# Analyze specific file
result = await analysis_tool.func(
    file_path="src/auth/models.py"
)
```

### **4. Self-Awareness Tool**

```python
self_awareness_tool()
```

**Function**: `analyze_self(include_tools, include_structure, include_dependencies)`

Agent introspection and capability analysis.

**Example**:
```python
# Analyze agent capabilities
result = await self_tool.func(
    include_tools=True,
    include_structure=True,
    include_dependencies=True
)
```

## 🔍 **Search Capabilities**

### **Code Element Search**

```python
# Search by name
results = indexer.search_code_elements("authenticate")

# Search by type
results = indexer.search_code_elements("User", element_type="class")

# Search with file pattern
results = indexer.search_code_elements(
    "login", 
    file_pattern="auth/*"
)
```

### **Advanced Filtering**

```python
# Complex search with multiple criteria
results = indexer.search_code_elements(
    query="process_payment",
    element_type="function",
    file_pattern="payment/*.py"
)

# Filter by complexity
high_complexity = [
    element for element in results 
    if element.complexity_score > 10
]
```

## 📊 **Database Schema**

### **SQLite Tables**

#### **code_elements**
```sql
CREATE TABLE code_elements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    end_line_number INTEGER,
    signature TEXT,
    docstring TEXT,
    parent_class TEXT,
    decorators TEXT,
    complexity_score INTEGER DEFAULT 0
);
```

#### **imports**
```sql
CREATE TABLE imports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    module TEXT NOT NULL,
    imported_names TEXT,
    import_type TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    alias TEXT
);
```

#### **files**
```sql
CREATE TABLE files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT UNIQUE NOT NULL,
    size INTEGER NOT NULL,
    lines_of_code INTEGER NOT NULL,
    last_modified TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    encoding TEXT NOT NULL,
    syntax_errors TEXT
);
```

## 🔄 **Dependency Tracking**

### **Dependency Graph**

```python
# Build dependency relationships
def _build_dependency_graphs(self):
    """Build forward and reverse dependency graphs."""
    for import_info in self.imports:
        file_path = import_info.file_path
        dependency = import_info.module
        
        # Forward dependencies (what this file imports)
        if file_path not in self.dependency_graph:
            self.dependency_graph[file_path] = set()
        self.dependency_graph[file_path].add(dependency)
        
        # Reverse dependencies (what imports this file)
        if dependency not in self.reverse_dependency_graph:
            self.reverse_dependency_graph[dependency] = set()
        self.reverse_dependency_graph[dependency].add(file_path)
```

### **Relationship Analysis**

```python
# Get file dependencies
dependencies = indexer.get_dependencies("src/auth/models.py")

# Get files that depend on this module
dependents = indexer.get_dependents("auth.models")

# Analyze circular dependencies
circular_deps = indexer.find_circular_dependencies()
```

## 📈 **Performance Features**

### **Incremental Indexing**

```python
def _is_file_modified(self, file_path: Path) -> bool:
    """Check if file has been modified since last index."""
    current_hash = self._calculate_file_hash(file_path)
    
    if str(file_path) in self.files:
        stored_hash = self.files[str(file_path)].file_hash
        return current_hash != stored_hash
    
    return True  # New file
```

### **Caching Strategy**

- **In-Memory Cache**: Fast access to frequently used data
- **SQLite Storage**: Persistent, reliable storage
- **Hash-based Updates**: Only reindex modified files
- **Lazy Loading**: Load data on demand

### **Search Optimization**

- **Indexed Queries**: Fast SQLite-based search
- **Pattern Matching**: Efficient regex and wildcard support
- **Result Ranking**: Relevance-based ordering
- **Pagination**: Handle large result sets

## 🧠 **Self-Awareness Capabilities**

### **Agent Introspection**

```python
def analyze_agent_structure(self) -> Dict[str, Any]:
    """Analyze the agent's own code structure."""
    agent_root = Path(__file__).parent.parent
    
    # Index agent's own codebase
    self.index_codebase(agent_root)
    
    # Analyze structure
    analysis = {
        "total_files": len(self.files),
        "total_functions": len([e for e in self.code_elements.values() 
                              if e.element_type == "function"]),
        "total_classes": len([e for e in self.code_elements.values() 
                             if e.element_type == "class"]),
        "tool_modules": self._identify_tool_modules(),
        "dependencies": self._analyze_dependencies(),
        "complexity_metrics": self._calculate_complexity_metrics()
    }
    
    return analysis
```

### **Tool Discovery**

```python
def _identify_tool_modules(self) -> List[Dict[str, Any]]:
    """Identify and analyze tool modules."""
    tool_modules = []
    
    for element in self.code_elements.values():
        if (element.element_type == "function" and 
            element.name.endswith("_tool") and
            "FunctionTool" in element.signature):
            
            tool_modules.append({
                "name": element.name,
                "file": element.file_path,
                "line": element.line_number,
                "signature": element.signature
            })
    
    return tool_modules
```

## 🔧 **Usage Examples**

### **Basic Indexing**

```python
from agent.tools.codebase_indexer import get_global_indexer

# Get indexer instance
indexer = get_global_indexer()

# Index a project
stats = indexer.index_codebase("/path/to/project")
print(f"Indexed {stats['total_elements']} code elements")
```

### **Search Operations**

```python
# Search for functions
functions = indexer.search_code_elements("process", element_type="function")

# Search for classes
classes = indexer.search_code_elements("User", element_type="class")

# Search in specific files
auth_elements = indexer.search_code_elements("login", file_pattern="auth/*")
```

### **File Analysis**

```python
# Analyze specific file
file_summary = indexer.get_file_summary("src/models.py")

print(f"File: {file_summary['file_path']}")
print(f"Functions: {len(file_summary['functions'])}")
print(f"Classes: {len(file_summary['classes'])}")
print(f"Dependencies: {file_summary['dependencies']}")
```

### **Dependency Analysis**

```python
# Get dependencies
deps = indexer.get_dependencies("src/auth/models.py")
print(f"Dependencies: {deps}")

# Get dependents
dependents = indexer.get_dependents("auth.models")
print(f"Files that depend on this: {dependents}")
```

## 🛡️ **Error Handling**

### **Syntax Error Management**

```python
def _parse_file_safely(self, file_path: Path) -> Optional[ast.AST]:
    """Parse file with comprehensive error handling."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return ast.parse(content, filename=str(file_path))
    
    except SyntaxError as e:
        self._record_syntax_error(file_path, e)
        return None
    except UnicodeDecodeError:
        # Try different encodings
        for encoding in ['latin1', 'cp1252']:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return ast.parse(content, filename=str(file_path))
            except:
                continue
        return None
```

### **Recovery Mechanisms**

- **Graceful degradation**: Continue indexing despite errors
- **Error logging**: Track and report issues
- **Partial results**: Return available data
- **Retry logic**: Attempt recovery strategies

## 📊 **Statistics & Metrics**

### **Indexing Statistics**

```python
{
    "start_time": "2024-01-01T10:00:00",
    "end_time": "2024-01-01T10:05:30",
    "duration": 330.5,
    "files_processed": 150,
    "total_elements": 1250,
    "total_imports": 300,
    "errors": [],
    "skipped_files": 5
}
```

### **Code Metrics**

- **Complexity scores**: Cyclomatic complexity analysis
- **Line counts**: Accurate LOC measurements
- **Dependency depth**: Import chain analysis
- **Coverage metrics**: Indexing completeness

## 🎯 **Integration Points**

### **Memory Engine Integration**

The indexer seamlessly integrates with the memory engine:

```python
# Memory engine uses indexer for codebase search
def _search_codebase_memory(self, query: str) -> List[MemoryEntry]:
    search_results = self.codebase_indexer.search_code_elements(query)
    return self._convert_to_memory_entries(search_results)
```

### **AST Tools Integration**

AST-based tools leverage indexer data:

```python
# Enhanced merging uses indexer for context
if self.use_indexer:
    file_summary = self.indexer.get_file_summary(self.file_path)
    dependencies = self.indexer.get_dependencies(self.file_path)
```

---

**Next**: Explore the [AST Code Tools](./ast-code-tools.md) for advanced code manipulation.

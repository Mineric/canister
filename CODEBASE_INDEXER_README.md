# Codebase Indexing and Self-Awareness System

## Overview

The Codebase Indexing and Self-Awareness System is a comprehensive solution that enables the Google ADK agent to deeply understand and navigate both its own codebase and external Python codebases. This system provides intelligent code search, dependency analysis, and self-reflection capabilities.

## Key Features

### 🧠 Deep Code Understanding
- **AST-Based Analysis**: Uses Python's Abstract Syntax Tree for precise code parsing
- **Comprehensive Indexing**: Indexes functions, classes, methods, imports, and dependencies
- **Intelligent Search**: Natural language queries across code elements
- **Dependency Mapping**: Builds complete dependency graphs and reverse dependencies

### 🔍 Advanced Search Capabilities
- **Multi-Criteria Search**: Search by name, docstring, signature, or file pattern
- **Type Filtering**: Filter by element type (function, class, method, etc.)
- **Complexity Analysis**: Calculates and indexes cyclomatic complexity
- **Decorator Recognition**: Identifies and indexes function/class decorators

### 🤖 Self-Awareness Features
- **Own Codebase Analysis**: Automatically analyzes the agent's own code structure
- **Tool Discovery**: Identifies and catalogs available tools and capabilities
- **Capability Mapping**: Maps code patterns to functional capabilities
- **Structure Visualization**: Provides hierarchical view of codebase organization

### 💾 Persistent Storage
- **SQLite Database**: Structured storage for fast queries
- **Caching System**: Intelligent caching for performance optimization
- **Incremental Updates**: Efficient reindexing of changed files
- **Cross-Platform**: Works on all major operating systems

## System Architecture

### Core Components

1. **CodebaseIndexer**: Main indexing engine
2. **CodeElement**: Data structure for code components
3. **ImportInfo**: Import relationship tracking
4. **FileInfo**: File-level metadata and statistics
5. **FunctionTool Wrappers**: Google ADK integration layer

### Data Models

```python
@dataclass
class CodeElement:
    name: str
    type: str  # 'function', 'class', 'method', 'async_function'
    file_path: str
    line_number: int
    signature: str
    docstring: Optional[str]
    parent_class: Optional[str]
    decorators: List[str]
    complexity_score: int
    dependencies: List[str]
```

## Available Tools

### 1. `codebase_indexer_tool()`
Indexes entire codebases to create searchable knowledge bases.

**Parameters:**
- `root_path` (str): Root directory to start indexing
- `exclude_patterns` (str): Comma-separated exclusion patterns
- `include_patterns` (str): Comma-separated inclusion patterns (default: "*.py")
- `force_reindex` (bool): Force reindexing even if cache exists

**Example:**
```python
indexer_tool = codebase_indexer_tool()
result = indexer_tool.func("/path/to/project")
```

### 2. `code_search_tool()`
Searches for code elements in the indexed codebase.

**Parameters:**
- `query` (str): Search query (names, docstrings, signatures)
- `element_type` (str): Filter by type (function, class, method, etc.)
- `file_pattern` (str): Filter by file path pattern
- `max_results` (int): Maximum results to return (default: 20)

**Example:**
```python
search_tool = code_search_tool()
results = search_tool.func("validate", element_type="function")
```

### 3. `file_analysis_tool()`
Provides detailed analysis of specific files.

**Parameters:**
- `file_path` (str): Path to the file to analyze

**Returns:**
- File statistics and metrics
- Code element breakdown
- Dependency information
- Complexity analysis

### 4. `self_awareness_tool()`
Analyzes the agent's own codebase for self-understanding.

**Parameters:**
- `include_tools` (bool): Include detailed tool analysis
- `include_structure` (bool): Include codebase structure analysis

**Returns:**
- Comprehensive self-analysis report
- Available tools and capabilities
- Codebase structure overview
- Key capability identification

## Usage Examples

### Basic Codebase Indexing
```python
from agent.tools.codebase_indexer import codebase_indexer_tool

# Create and use the indexer tool
indexer = codebase_indexer_tool()
result = indexer.func(
    root_path="/path/to/project",
    exclude_patterns="__pycache__,*.pyc,.git",
    include_patterns="*.py"
)
print(result)
```

### Intelligent Code Search
```python
from agent.tools.codebase_indexer import code_search_tool

# Search for specific patterns
search = code_search_tool()

# Find all classes
classes = search.func("", element_type="class")

# Find functions containing "validate"
validators = search.func("validate", element_type="function")

# Find code in specific files
utils_code = search.func("helper", file_pattern="utils/")
```

### File Analysis
```python
from agent.tools.codebase_indexer import file_analysis_tool

# Analyze a specific file
analyzer = file_analysis_tool()
analysis = analyzer.func("/path/to/file.py")
print(analysis)
```

### Self-Awareness
```python
from agent.tools.codebase_indexer import self_awareness_tool

# Perform self-analysis
self_aware = self_awareness_tool()
report = self_aware.func(include_tools=True, include_structure=True)
print(report)
```

## Integration with Google ADK

The system is fully integrated with the Google ADK agent framework:

```python
# In agent/agent.py
from .tools.codebase_indexer import (
    codebase_indexer_tool,
    code_search_tool,
    file_analysis_tool,
    self_awareness_tool
)

tools = [
    # ... other tools
    codebase_indexer_tool(),
    code_search_tool(),
    file_analysis_tool(),
    self_awareness_tool(),
]
```

## Performance Considerations

### Optimization Features
- **Incremental Indexing**: Only reprocesses changed files
- **SQLite Storage**: Fast queries with proper indexing
- **Memory Management**: Efficient handling of large codebases
- **Caching**: Intelligent caching of frequently accessed data

### Scalability
- **Large Codebases**: Handles projects with thousands of files
- **Concurrent Access**: Thread-safe operations
- **Memory Efficient**: Streaming processing for large files
- **Configurable Limits**: Adjustable result limits and timeouts

## Error Handling

The system provides comprehensive error handling:

- **File Access Errors**: Graceful handling of permission issues
- **Syntax Errors**: Continues indexing despite malformed files
- **Encoding Issues**: Automatic encoding detection and fallback
- **Path Resolution**: Robust path handling across platforms

## Advanced Features

### Dependency Analysis
- **Import Tracking**: Complete import relationship mapping
- **Circular Dependencies**: Detection and reporting
- **Local vs External**: Distinguishes project vs external dependencies
- **Dependency Graphs**: Visual representation of relationships

### Code Quality Metrics
- **Complexity Scoring**: Cyclomatic complexity calculation
- **Documentation Coverage**: Docstring presence analysis
- **Code Patterns**: Recognition of common design patterns
- **Best Practices**: Identification of code quality indicators

### Self-Improvement Capabilities
- **Tool Discovery**: Automatic identification of available tools
- **Capability Mapping**: Understanding of functional capabilities
- **Structure Analysis**: Hierarchical codebase organization
- **Evolution Tracking**: Changes and improvements over time

## Future Enhancements

- **Multi-Language Support**: Extend beyond Python to other languages
- **Real-Time Monitoring**: File system watching for automatic updates
- **Code Metrics Dashboard**: Visual representation of codebase health
- **Integration APIs**: RESTful APIs for external tool integration
- **Machine Learning**: Pattern recognition and code suggestion improvements

## Best Practices

1. **Regular Indexing**: Keep indexes up-to-date with code changes
2. **Selective Exclusions**: Use appropriate exclusion patterns for performance
3. **Query Optimization**: Use specific search criteria for better results
4. **Cache Management**: Monitor cache size and performance
5. **Error Monitoring**: Review indexing errors and syntax issues

---

This system represents a significant advancement in AI agent self-awareness and codebase understanding, providing the foundation for intelligent code assistance and automated development workflows.

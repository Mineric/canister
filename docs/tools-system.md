# Tools System

Comprehensive documentation for the Canister Agent's 19-tool ecosystem, providing professional software engineering capabilities.

## 🎯 **Overview**

The Canister Agent features a sophisticated tool system with 19 specialized tools organized into 5 categories:
- **Basic Utilities** (7 tools): Essential development utilities
- **AST Code Tools** (3 tools): Advanced code manipulation
- **Professional SWE** (2 tools): engineering capabilities
- **Memory System** (3 tools): Context and memory management
- **Codebase Indexing** (4 tools): Code analysis and search

## 🛠️ **Tool Categories**

### **1. Basic Utilities (7 tools)**

Essential development utilities for everyday tasks.

#### **Time Tool**
```python
get_current_time_tool() -> FunctionTool
```
- **Function**: `get_current_time() -> str`
- **Purpose**: Get current date and time
- **Usage**: Timestamps, logging, time-based operations

#### **Calculator Tool**
```python
calculator_tool() -> FunctionTool
```
- **Function**: `calculator(operation, a, b) -> str`
- **Purpose**: Mathematical operations (add, subtract, multiply, divide)
- **Usage**: Calculations, data processing, algorithm development

#### **Text Analyzer Tool**
```python
text_analyzer_tool() -> FunctionTool
```
- **Function**: `text_analyzer(text, analysis_type) -> str`
- **Purpose**: Text processing and analysis
- **Usage**: Content analysis, documentation processing, string manipulation

#### **Directory Operations Tool**
```python
directory_operations_tool() -> FunctionTool
```
- **Function**: `directory_operations(action, path, pattern) -> str`
- **Purpose**: File system navigation and directory management
- **Usage**: Project exploration, file discovery, directory structure analysis

#### **File Management Tool**
```python
file_management_tool() -> FunctionTool
```
- **Function**: `file_management(action, file_path, content, encoding) -> str`
- **Purpose**: File operations (read, write, create, delete)
- **Usage**: Code file manipulation, configuration management, data processing

#### **Terminal Command Tool**
```python
terminal_command_tool() -> FunctionTool
```
- **Function**: `terminal_command(command, working_directory, timeout) -> str`
- **Purpose**: System command execution
- **Usage**: Build processes, testing, system integration, package management

#### **Docker Sandbox Tool**
```python
docker_sandbox_tool() -> FunctionTool
```
- **Function**: `run_code_in_sandbox(code, language, timeout) -> str`
- **Purpose**: Safe code execution in isolated environment
- **Usage**: Code testing, validation, security analysis

### **2. AST Code Tools (3 tools)**

Advanced Abstract Syntax Tree-based code manipulation.

#### **AST Code Merger Tool**
```python
ast_code_merger_tool() -> FunctionTool
```
- **Function**: `merge_code_intelligently(file_path, ai_generated_code, backup, dry_run, use_indexer, analyze_impact) -> str`
- **Purpose**: Intelligent AST-based code merging
- **Features**:
  - Structure-preserving merging
  - Import management
  - Conflict detection
  - Backup creation
  - Impact analysis

#### **Enhanced AST Code Merger Tool**
```python
enhanced_ast_code_merger_tool() -> FunctionTool
```
- **Function**: `merge_code_with_codebase_awareness(file_path, ai_generated_code, backup, dry_run, force_index_update) -> str`
- **Purpose**: Enhanced merging with full codebase awareness
- **Features**:
  - Codebase indexer integration
  - Cross-file dependency analysis
  - Reference resolution
  - Architectural consistency

#### **Code Structure Analyzer Tool**
```python
code_structure_analyzer_tool() -> FunctionTool
```
- **Function**: `analyze_code_structure(file_path, include_metrics, include_dependencies, include_suggestions) -> str`
- **Purpose**: Comprehensive code structure analysis
- **Features**:
  - AST-based analysis
  - Complexity metrics
  - Dependency mapping
  - Improvement suggestions

### **3. Professional SWE (2 tools)**

Professional software engineering capabilities.

#### **Intelligent Merger Tool**
```python
intelligent_merger_tool() -> FunctionTool
```
- **Function**: `merge_code_professionally(file_path, ai_generated_code, merge_strategy, conflict_resolution, preserve_architecture, validate_changes) -> str`
- **Purpose**: Professional-grade code merging
- **Features**:
  - Multiple merge strategies
  - Architectural preservation
  - Advanced conflict resolution
  - Change validation
  - Impact assessment

#### **Code Comprehension Tool**
```python
code_comprehension_tool() -> FunctionTool
```
- **Function**: `analyze_codebase_architecture(root_path, analysis_depth, include_patterns, exclude_patterns, focus_areas) -> str`
- **Purpose**: Deep architectural analysis and comprehension
- **Features**:
  - Architectural pattern detection
  - Design principle analysis
  - Code quality assessment
  - Refactoring recommendations

### **4. Memory System (3 tools)**

Persistent memory and context management.

#### **Memory Search Tool**
```python
memory_search_tool() -> FunctionTool
```
- **Function**: `search_memory(query, context_types, max_results, include_codebase, user_id) -> str`
- **Purpose**: Intelligent context retrieval with prioritization
- **Features**:
  - Smart relevance scoring
  - Context type filtering
  - Codebase integration
  - User-specific search

#### **Context Tool**
```python
context_tool() -> FunctionTool
```
- **Function**: `get_context(session_id, max_tokens) -> str`
- **Purpose**: Session-specific context summaries
- **Features**:
  - Token-aware summarization
  - Priority-based selection
  - Session isolation
  - Intelligent truncation

#### **Memory Management Tool**
```python
memory_management_tool() -> FunctionTool
```
- **Function**: `manage_memory(action, content, context_type, session_id, user_id, metadata) -> str`
- **Purpose**: Memory operations and management
- **Actions**:
  - `add`: Add new memory entries
  - `cleanup`: Remove old memories
  - `status`: System status information
  - `configure`: Configuration options

### **5. Codebase Indexing (4 tools)**

Comprehensive codebase analysis and indexing.

#### **Codebase Indexer Tool**
```python
codebase_indexer_tool() -> FunctionTool
```
- **Function**: `index_codebase(root_path, exclude_patterns, include_patterns, force_reindex) -> str`
- **Purpose**: Project indexing and analysis
- **Features**:
  - AST-based parsing
  - SQLite storage
  - Incremental updates
  - Error handling

#### **Code Search Tool**
```python
code_search_tool() -> FunctionTool
```
- **Function**: `search_code(query, element_type, file_pattern, max_results) -> str`
- **Purpose**: Intelligent code element search
- **Features**:
  - Multi-criteria filtering
  - Pattern matching
  - Result ranking
  - Type-specific search

#### **File Analysis Tool**
```python
file_analysis_tool() -> FunctionTool
```
- **Function**: `analyze_file(file_path) -> str`
- **Purpose**: Detailed file-specific analysis
- **Features**:
  - Structure analysis
  - Dependency mapping
  - Metrics calculation
  - Quality assessment

#### **Self-Awareness Tool**
```python
self_awareness_tool() -> FunctionTool
```
- **Function**: `analyze_self(include_tools, include_structure, include_dependencies) -> str`
- **Purpose**: Agent introspection and capability analysis
- **Features**:
  - Tool discovery
  - Structure analysis
  - Capability mapping
  - Self-documentation

## 🔧 **Tool Integration**

### **Cross-Tool Coordination**

Tools work together seamlessly:

```python
# Example: Enhanced code merging workflow
1. codebase_indexer_tool()    # Index project for context
2. memory_search_tool()       # Find relevant past decisions
3. intelligent_merger_tool()  # Perform professional merge
4. memory_management_tool()   # Store merge results
```

### **Shared Context**

- **Codebase Indexer**: Provides code structure to all tools
- **Memory Engine**: Maintains context across tool usage
- **AST Tools**: Share parsing and analysis capabilities
- **Professional SWE**: Leverages all lower-level tools

## 📊 **Tool Usage Patterns**

### **Development Workflow**
```python
# 1. Project Setup
directory_operations_tool()  # Explore project structure
codebase_indexer_tool()     # Index for understanding

# 2. Analysis Phase
code_comprehension_tool()   # Understand architecture
file_analysis_tool()       # Analyze specific files
memory_search_tool()       # Find relevant context

# 3. Implementation
ast_code_merger_tool()     # Merge new code
terminal_command_tool()    # Run tests
memory_management_tool()   # Store decisions

# 4. Validation
code_structure_analyzer_tool()  # Verify structure
self_awareness_tool()          # Check capabilities
```

### **Code Review Workflow**
```python
# 1. Understanding
codebase_indexer_tool()    # Index codebase
search_code_tool()         # Find relevant elements
get_context_tool()         # Get session context

# 2. Analysis
analyze_codebase_architecture()  # Deep analysis
analyze_code_structure()         # Structure review
search_memory()                  # Past insights

# 3. Recommendations
merge_code_professionally()  # Suggest improvements
manage_memory()             # Store findings
```

## 🎯 **Best Practices**

### **Tool Selection**
1. **Start with indexing**: Always index before complex operations
2. **Use memory**: Leverage context for better decisions
3. **Professional tools**: Use for production-quality work
4. **Combine tools**: Leverage cross-tool coordination

### **Error Handling**
1. **Graceful degradation**: Tools continue working with partial data
2. **Error reporting**: Clear error messages and recovery suggestions
3. **Fallback mechanisms**: Alternative approaches when tools fail
4. **Data validation**: Input validation and sanitization

### **Performance**
1. **Caching**: Tools cache results for efficiency
2. **Incremental updates**: Only process changed data
3. **Lazy loading**: Load data on demand
4. **Resource management**: Efficient memory and storage usage

## 🔍 **Tool Discovery**

### **Available Tools Query**
```python
# Get all available tools
agent = create_agent()
tool_names = [tool.func.__name__ for tool in agent.tools]
print(f"Available tools: {tool_names}")

# Tool categories
basic_tools = [name for name in tool_names if name in [
    'get_current_time', 'calculator', 'text_analyzer',
    'directory_operations', 'file_management', 'terminal_command',
    'run_code_in_sandbox'
]]

memory_tools = [name for name in tool_names if name in [
    'search_memory', 'get_context', 'manage_memory'
]]

# And so on...
```

### **Self-Documentation**
```python
# Use self-awareness tool for capability discovery
self_tool = self_awareness_tool()
capabilities = await self_tool.func(
    include_tools=True,
    include_structure=True,
    include_dependencies=True
)
```

## 📈 **Advanced Features**

### **Tool Composition**
- Tools can call other tools internally
- Shared state and context
- Coordinated error handling
- Unified logging and monitoring

### **Extensibility**
- Easy to add new tools
- Consistent FunctionTool interface
- Shared utilities and helpers
- Plugin architecture support

### **Monitoring**
- Tool usage tracking
- Performance metrics
- Error rate monitoring
- Resource utilization

---

**Next**: Explore specific tool categories in detail:
- [AST Code Tools](./ast-code-tools.md)
- [Professional SWE](./professional-swe.md)
- [Memory Engine](./memory-engine.md)
- [Codebase Indexer](./codebase-indexer.md)

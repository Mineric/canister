# AST-Based Code Merger Tool

## Overview

The AST-Based Code Merger Tool is an code integration tools for the Canister agent. It uses Python's Abstract Syntax Tree (AST) module to surgically merge LLM-generated code snippets into existing Python source files while preserving structure, avoiding duplicates, and maintaining code quality.

## Key Features

### 🧠 Intelligent Merging
- **Function Replacement**: Replaces existing functions with updated versions instead of creating duplicates
- **Class-Aware Merging**: Adds new methods to existing classes while preserving existing class structure
- **Import Management**: Prevents redundant imports while ensuring all dependencies are included
- **Structure Preservation**: Maintains original code formatting, comments, and overall file organization

### 🔧 Advanced Capabilities
- **AST-Based Analysis**: Uses Python's built-in `ast` module for precise code parsing and manipulation
- **Error Handling**: Comprehensive validation and error handling for malformed code or parsing failures
- **Cross-Platform Compatibility**: Works across different operating systems
- **Backup Support**: Automatically creates backups before modifying files
- **Dry Run Mode**: Preview changes before applying them

## Tools Available

### 1. `ast_code_merger_tool()`
The main tool for merging AI-generated code into existing Python files.

**Parameters:**
- `file_path` (str): Path to the existing Python file to modify
- `ai_generated_code` (str): The AI-generated code snippet to merge
- `backup` (bool, default=True): Whether to create a backup of the original file
- `dry_run` (bool, default=False): If True, return merged code without writing to file

**Returns:**
- Success message with merge details, or merged code if `dry_run=True`

### 2. `code_structure_analyzer_tool()`
Analyzes Python file structure to understand what would be merged.

**Parameters:**
- `file_path` (str): Path to the Python file to analyze

**Returns:**
- Detailed analysis of file structure including functions, classes, imports, and statistics

## Usage Examples

### Basic Usage
```python
from agent.tools.code_tools import ast_code_merger_tool

# Create the tool
merger_tool = ast_code_merger_tool()

# Merge code (dry run first to preview)
result = merger_tool.func(
    file_path="my_module.py",
    ai_generated_code="""
def new_function():
    print("This is a new function")
    
class ExistingClass:
    def new_method(self):
        return "New method added"
""",
    dry_run=True
)
print(result)

# Apply the merge
result = merger_tool.func(
    file_path="my_module.py",
    ai_generated_code=ai_code,
    backup=True,
    dry_run=False
)
```

### Code Analysis
```python
from agent.tools.code_tools import code_structure_analyzer_tool

# Create the analyzer tool
analyzer_tool = code_structure_analyzer_tool()

# Analyze file structure
analysis = analyzer_tool.func("my_module.py")
print(analysis)
```

## Merge Scenarios

### 1. Function Replacement
**Original:**
```python
def greet(name):
    print(f"Hello, {name}!")
```

**AI-Generated:**
```python
def greet(name, greeting="Hello"):
    print(f"{greeting}, {name}!")
```

**Result:** The original function is replaced with the enhanced version.

### 2. Class Method Addition
**Original:**
```python
class Calculator:
    def add(self, a, b):
        return a + b
```

**AI-Generated:**
```python
class Calculator:
    def subtract(self, a, b):
        return a - b
    
    def multiply(self, a, b):
        return a * b
```

**Result:** New methods are added to the existing class without affecting the original `add` method.

### 3. Import Management
**Original:**
```python
import os
import sys
```

**AI-Generated:**
```python
import json
from pathlib import Path
```

**Result:**
```python
import os
import sys
import json
from pathlib import Path
```

## Error Handling

The tool provides comprehensive error handling for various scenarios:

- **File Not Found**: Clear error message when the target file doesn't exist
- **Invalid Python Syntax**: Detailed syntax error reporting for both source and AI-generated code
- **Permission Errors**: Handles read/write permission issues gracefully
- **Non-Python Files**: Validates that target files have `.py` extension
- **Empty Files**: Handles empty source files appropriately

## Integration with Google ADK

The tools are automatically integrated into the Google ADK agent system:

```python
# In agent/agent.py
from .tools.code_tools import (
    ast_code_merger_tool,
    code_structure_analyzer_tool
)

tools = [
    # ... other tools
    ast_code_merger_tool(),
    code_structure_analyzer_tool(),
]
```

## Best Practices

1. **Always Use Dry Run First**: Preview changes before applying them
2. **Enable Backups**: Keep backups enabled for safety
3. **Analyze Before Merging**: Use the structure analyzer to understand the target file
4. **Test Merged Code**: Always test the merged code to ensure functionality
5. **Handle Large Files Carefully**: Be cautious with very large files

## Technical Implementation

- **AST Parsing**: Uses `ast.parse()` for converting code to Abstract Syntax Trees
- **Node Comparison**: Implements intelligent comparison of AST nodes to identify duplicates
- **Code Generation**: Uses `astor.to_source()` to convert modified AST back to source code
- **File Handling**: Cross-platform file operations with proper encoding support
- **Error Recovery**: Graceful handling of parsing and merging errors

## Limitations

- **Python Only**: Currently supports Python files only (`.py` extension required)
- **Syntax Dependency**: Both source and AI-generated code must be syntactically valid Python
- **Complex Merges**: Very complex code structures may require manual review
- **Comments**: Some comment positioning may change during AST conversion

## Future Enhancements

- Support for other programming languages
- Enhanced comment preservation
- Conflict resolution strategies
- Integration with version control systems
- Advanced merge statistics and reporting

---

This tool represents a significant advancement in AI-assisted code development, providing surgical precision in code integration while maintaining the integrity and structure of existing codebases.

# Contributing Guide

Guidelines for contributing to the Canister Agent project.

## 🎯 **Overview**

We welcome contributions to the Canister Agent! This guide covers:
- Code contribution process
- Development standards
- Testing requirements
- Documentation guidelines
- Review process

## 🚀 **Getting Started**

### **Development Setup**

```bash
# Fork and clone the repository
git clone https://github.com/your-username/canister.git
cd canister

# Create development branch
git checkout -b feature/your-feature-name

# Set up development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install
```

### **Development Dependencies**

```bash
# requirements-dev.txt
pytest>=7.0.0
pytest-asyncio>=0.21.0
pytest-cov>=4.0.0
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0
pre-commit>=3.0.0
```

## 📋 **Contribution Types**

### **1. Bug Fixes**

```bash
# Branch naming
git checkout -b fix/issue-description

# Example: fix/memory-search-performance
# Example: fix/indexer-unicode-handling
```

**Requirements**:
- Clear issue description
- Minimal reproduction case
- Comprehensive tests
- Documentation updates if needed

### **2. New Features**

```bash
# Branch naming
git checkout -b feature/feature-name

# Example: feature/advanced-search
# Example: feature/custom-memory-backends
```

**Requirements**:
- Feature proposal discussion
- Design document for complex features
- Comprehensive tests (>95% coverage)
- Documentation and examples
- Performance impact analysis

### **3. Tool Development**

```bash
# Branch naming
git checkout -b tool/tool-name

# Example: tool/database-analyzer
# Example: tool/security-scanner
```

**Requirements**:
- Follow tool development pattern
- Google ADK FunctionTool integration
- Comprehensive error handling
- Performance benchmarks
- Usage examples

### **4. Documentation**

```bash
# Branch naming
git checkout -b docs/documentation-area

# Example: docs/api-reference-update
# Example: docs/tutorial-improvements
```

**Requirements**:
- Clear, accurate content
- Code examples that work
- Proper markdown formatting
- Cross-references where appropriate

## 🛠️ **Development Standards**

### **Code Style**

```python
# Use Black for formatting
black agent/ tests/

# Use isort for import sorting
isort agent/ tests/

# Follow PEP 8 with Black's line length (88 chars)
# Use type hints for all functions
def process_data(data: List[str], options: Dict[str, Any]) -> Optional[str]:
    """Process data with given options."""
    pass

# Use dataclasses for structured data
@dataclass
class ProcessingResult:
    success: bool
    data: Optional[str] = None
    errors: List[str] = field(default_factory=list)
```

### **Naming Conventions**

```python
# Functions and variables: snake_case
def calculate_complexity_score(node: ast.AST) -> int:
    pass

# Classes: PascalCase
class MemoryEngine:
    pass

# Constants: UPPER_SNAKE_CASE
MAX_CONTEXT_TOKENS = 32000

# Private methods: _leading_underscore
def _internal_helper(self) -> None:
    pass

# Tool functions: descriptive names ending with _tool
def memory_search_tool() -> FunctionTool:
    pass
```

### **Documentation Standards**

```python
def well_documented_function(
    data: List[str],
    options: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> ProcessingResult:
    """
    Process data with configurable options.
    
    This function processes a list of strings according to the provided
    options and returns a structured result.
    
    Args:
        data: List of strings to process. Cannot be empty.
        options: Optional processing options. Defaults to standard options.
        timeout: Processing timeout in seconds. Must be positive.
    
    Returns:
        ProcessingResult containing success status, processed data, and any errors.
    
    Raises:
        ValueError: If data is empty or timeout is non-positive.
        RuntimeError: If processing fails due to system issues.
    
    Example:
        >>> data = ["hello", "world"]
        >>> result = well_documented_function(data, timeout=60)
        >>> if result.success:
        ...     print(f"Processed: {result.data}")
    """
    pass
```

## 🧪 **Testing Requirements**

### **Test Coverage**

- **New features**: 100% test coverage
- **Bug fixes**: Tests that reproduce the bug
- **Tool development**: Comprehensive unit and integration tests
- **Performance**: Benchmark tests for performance-critical code

### **Test Categories**

```python
# Unit tests - test individual components
def test_memory_engine_add_memory():
    """Test adding memory entries."""
    pass

# Integration tests - test component interactions
def test_memory_indexer_integration():
    """Test memory engine with codebase indexer."""
    pass

# Performance tests - test speed and resource usage
def test_indexing_performance():
    """Test indexing performance with large codebases."""
    pass

# End-to-end tests - test complete workflows
def test_development_workflow():
    """Test complete development workflow."""
    pass
```

### **Test Naming**

```python
# Test class naming: Test + ComponentName
class TestMemoryEngine:
    pass

# Test method naming: test_ + what_is_being_tested
def test_search_memory_with_filters():
    pass

def test_add_memory_with_invalid_input():
    pass

def test_cleanup_old_memories():
    pass
```

## 📝 **Pull Request Process**

### **1. Pre-submission Checklist**

```bash
# Run all checks before submitting
black agent/ tests/                    # Format code
isort agent/ tests/                    # Sort imports
flake8 agent/ tests/                   # Lint code
mypy agent/ --strict                   # Type checking
pytest tests/ --cov=agent             # Run tests with coverage
```

### **2. Pull Request Template**

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Performance tests added (if applicable)
- [ ] All tests pass

## Documentation
- [ ] Code comments updated
- [ ] API documentation updated
- [ ] User documentation updated
- [ ] Examples added/updated

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Tests added for new functionality
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

### **3. Review Process**

1. **Automated Checks**: All CI checks must pass
2. **Code Review**: At least one maintainer review required
3. **Testing**: Comprehensive test coverage verified
4. **Documentation**: Documentation completeness checked
5. **Performance**: Performance impact assessed

## 🔧 **Tool Development Guidelines**

### **Tool Structure**

```python
# agent/tools/example_tool.py
from google.adk.tools import FunctionTool
from typing import Optional, List, Dict, Any

def example_tool() -> FunctionTool:
    """
    Create an example tool following Canister patterns.
    
    This tool demonstrates the standard pattern for creating
    new tools in the Canister Agent ecosystem.
    """
    
    def example_function(
        required_param: str,
        optional_param: int = 10,
        flag_param: bool = True
    ) -> str:
        """
        Example function with comprehensive documentation.
        
        Args:
            required_param: Description of required parameter
            optional_param: Optional parameter with default
            flag_param: Boolean flag parameter
        
        Returns:
            Formatted result string
        """
        try:
            # 1. Input validation
            if not required_param or not required_param.strip():
                return "Error: required_param cannot be empty"
            
            if optional_param < 0:
                return "Error: optional_param must be non-negative"
            
            # 2. Core functionality
            result = process_data(required_param, optional_param, flag_param)
            
            # 3. Result formatting
            return format_result(result)
            
        except Exception as e:
            # 4. Error handling
            return f"Error in example_function: {str(e)}"
    
    return FunctionTool(example_function)

def process_data(param: str, value: int, flag: bool) -> Dict[str, Any]:
    """Core processing logic separated for testability."""
    return {
        "processed": param.upper(),
        "value": value * 2 if flag else value,
        "timestamp": datetime.now().isoformat()
    }

def format_result(data: Dict[str, Any]) -> str:
    """Format result for user display."""
    return f"Processed: {data['processed']} (value: {data['value']})"
```

### **Tool Testing**

```python
# tests/unit/test_example_tool.py
import pytest
from agent.tools.example_tool import example_tool

class TestExampleTool:
    """Test example tool functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.tool = example_tool()
    
    def test_basic_functionality(self):
        """Test basic tool functionality."""
        result = self.tool.func("test_input", 5, True)
        assert "Processed: TEST_INPUT" in result
        assert "value: 10" in result
    
    def test_error_handling(self):
        """Test error handling."""
        result = self.tool.func("", 5, True)
        assert "Error" in result
        assert "cannot be empty" in result
    
    def test_optional_parameters(self):
        """Test optional parameters."""
        result = self.tool.func("test")
        assert "value: 20" in result  # Default: 10 * 2
    
    @pytest.mark.parametrize("input_val,expected", [
        ("hello", "HELLO"),
        ("world", "WORLD"),
        ("test123", "TEST123")
    ])
    def test_parameter_variations(self, input_val, expected):
        """Test various parameter combinations."""
        result = self.tool.func(input_val)
        assert expected in result
```

## 📊 **Performance Guidelines**

### **Performance Requirements**

- **Tool execution**: < 5 seconds for typical operations
- **Memory usage**: Efficient memory management
- **Caching**: Implement caching for expensive operations
- **Scalability**: Consider performance with large inputs

### **Performance Testing**

```python
# tests/performance/test_example_tool_performance.py
import time
import pytest
from agent.tools.example_tool import example_tool

class TestExampleToolPerformance:
    """Test example tool performance."""
    
    def test_execution_speed(self):
        """Test tool execution speed."""
        tool = example_tool()
        
        start_time = time.time()
        for i in range(100):
            result = tool.func(f"test_{i}")
        end_time = time.time()
        
        duration = end_time - start_time
        operations_per_second = 100 / duration
        
        # Performance requirements
        assert duration < 5  # Should complete within 5 seconds
        assert operations_per_second > 20  # At least 20 ops/second
```

## 🎯 **Best Practices**

### **Code Quality**

1. **Single Responsibility**: Each function/class has one clear purpose
2. **Error Handling**: Comprehensive error handling and recovery
3. **Type Safety**: Use type hints throughout
4. **Documentation**: Clear, comprehensive documentation
5. **Testing**: High test coverage with meaningful tests

### **Git Workflow**

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes with clear commits
git add .
git commit -m "feat: add new memory search algorithm

- Implement semantic search using embeddings
- Add performance benchmarks
- Update documentation"

# 3. Keep branch updated
git fetch origin
git rebase origin/main

# 4. Push and create PR
git push origin feature/new-feature
```

### **Commit Messages**

```bash
# Format: type(scope): description
feat(memory): add semantic search capability
fix(indexer): handle unicode characters correctly
docs(api): update memory engine documentation
test(tools): add performance tests for AST merger
refactor(core): simplify agent creation logic
```

## 🔍 **Code Review Guidelines**

### **For Contributors**

1. **Self-review**: Review your own code before submitting
2. **Clear description**: Explain what and why in PR description
3. **Small PRs**: Keep changes focused and manageable
4. **Tests included**: Ensure comprehensive test coverage
5. **Documentation**: Update relevant documentation

### **For Reviewers**

1. **Functionality**: Does the code work as intended?
2. **Design**: Is the design clean and maintainable?
3. **Performance**: Are there performance implications?
4. **Security**: Are there security considerations?
5. **Tests**: Is test coverage adequate?

## 📞 **Getting Help**

### **Communication Channels**

- **Issues**: GitHub issues for bugs and feature requests
- **Discussions**: GitHub discussions for questions and ideas
- **Documentation**: Check existing documentation first
- **Code Examples**: Look at existing tools for patterns

### **Issue Templates**

```markdown
## Bug Report
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior.

**Expected behavior**
What you expected to happen.

**Environment**
- OS: [e.g., macOS, Linux, Windows]
- Python version: [e.g., 3.11]
- Canister version: [e.g., 1.0.0]

## Feature Request
**Is your feature request related to a problem?**
A clear description of what the problem is.

**Describe the solution you'd like**
A clear description of what you want to happen.

**Additional context**
Any other context about the feature request.
```

---

Thank you for contributing to the Canister Agent! Your contributions help make this project better for everyone.

# Cannister Agent Test Suite

This directory contains comprehensive tests for the Cannister Agent functionality.

## 📁 Test Structure

```
agent/tests/
├── __init__.py              # Package initialization
├── conftest.py              # Pytest configuration and fixtures
├── test_runner.py           # Comprehensive test runner
├── test_tools.py            # Unit tests for agent tools
├── test_agent.py            # Agent integration tests
├── test_ast_merger.py       # AST merger functionality tests
├── test_codebase_indexer.py # Codebase indexer tests
├── test_imports.py          # Import and dependency tests
├── demo_ast_merger.py       # AST merger demonstration
└── README.md               # This file
```

## 🚀 Running Tests

### Run All Tests
```bash
# Using the custom test runner
python agent/tests/test_runner.py

# Using pytest (if available)
pytest agent/tests/

# Using unittest
python -m unittest discover agent/tests/
```

### Run Specific Tests
```bash
# Test specific functionality
python agent/tests/test_tools.py
python agent/tests/test_imports.py

# Run with verbose output
python agent/tests/test_runner.py -v
```

## 📊 Test Categories

### **Unit Tests** (`test_tools.py`)
- Individual tool functionality
- Input/output validation
- Error handling
- Performance benchmarks

### **Integration Tests** (`test_agent.py`)
- Agent creation and initialization
- Tool integration
- Workflow testing

### **System Tests** (`test_imports.py`)
- Import dependency validation
- Module loading performance
- Timeout handling for hanging imports

### **Functional Tests** (`test_ast_merger.py`, `test_codebase_indexer.py`)
- Complex feature testing
- Real-world scenario simulation
- End-to-end workflows

## 🔧 Test Configuration

### Fixtures (in `conftest.py`)
- `temp_dir`: Temporary directory for file operations
- `sample_python_file`: Sample Python file for testing
- `project_root`: Project root directory reference

### Test Utilities
- Colored output for better readability
- Timeout handling for hanging operations
- Comprehensive error reporting
- Performance measurement

## 📈 Test Metrics

The test suite tracks:
- **Success Rate**: Percentage of passing tests
- **Execution Time**: Performance metrics
- **Coverage**: Code coverage analysis
- **Error Types**: Categorized failure analysis

## 🛠️ Adding New Tests

1. Create test file following naming convention: `test_*.py`
2. Import required modules and fixtures
3. Use descriptive test method names: `test_feature_scenario`
4. Include docstrings explaining test purpose
5. Add appropriate assertions and error handling

### Example Test Structure
```python
import unittest
from agent.tests.conftest import temp_dir

class TestNewFeature(unittest.TestCase):
    def test_feature_basic_functionality(self):
        """Test basic functionality of new feature."""
        # Test implementation
        pass
    
    def test_feature_error_handling(self):
        """Test error handling in new feature."""
        # Error case testing
        pass
```

## 🐛 Debugging Tests

### Common Issues
- **Import Errors**: Check Python path and dependencies
- **Timeout Issues**: Increase timeout values in `test_imports.py`
- **File Permission Errors**: Ensure proper cleanup in tearDown methods
- **Path Issues**: Use `project_root` fixture for relative paths

### Debug Mode
```bash
# Run with debug output
python agent/tests/test_runner.py -v

# Run specific test with debugging
python -m unittest agent.tests.test_tools.TestBasicTools.test_calculator_tool -v
```

## 📋 Test Checklist

Before committing new code:
- [ ] All existing tests pass
- [ ] New functionality has corresponding tests
- [ ] Tests cover both success and failure cases
- [ ] Performance tests show acceptable metrics
- [ ] Import tests complete without hanging
- [ ] Documentation is updated

## 🔗 Related

- See `../evals/` for evaluation and benchmarking
- See `../tools/` for the actual tool implementations
- See project root for integration examples

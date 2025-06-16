# Testing Guide

Comprehensive testing strategies and examples for the Canister Agent.

## 🎯 **Testing Overview**

The Canister Agent uses a multi-layered testing approach:
- **Unit Tests**: Individual tool and component testing
- **Integration Tests**: Cross-component interaction testing
- **Performance Tests**: Speed and resource usage testing
- **End-to-End Tests**: Complete workflow testing

## 🧪 **Test Structure**

### **Test Organization**

```
tests/
├── unit/                    # Unit tests
│   ├── test_tools.py       # Basic tool tests
│   ├── test_memory_engine.py # Memory system tests
│   ├── test_codebase_indexer.py # Indexer tests
│   └── test_ast_tools.py   # AST tool tests
├── integration/            # Integration tests
│   ├── test_agent_integration.py
│   ├── test_memory_integration.py
│   └── test_tool_coordination.py
├── performance/            # Performance tests
│   ├── test_indexing_performance.py
│   ├── test_memory_performance.py
│   └── test_search_performance.py
├── e2e/                   # End-to-end tests
│   ├── test_development_workflow.py
│   └── test_code_analysis_workflow.py
├── fixtures/              # Test data and fixtures
│   ├── sample_code/
│   ├── test_projects/
│   └── mock_data/
└── conftest.py           # Pytest configuration
```

## 🛠️ **Unit Testing**

### **Tool Testing Pattern**

```python
# tests/unit/test_tools.py
import pytest
from agent.tools.tools import calculator_tool, text_analyzer_tool

class TestBasicTools:
    """Test basic utility tools."""
    
    def setup_method(self):
        """Set up test environment."""
        self.calculator = calculator_tool()
        self.text_analyzer = text_analyzer_tool()
    
    def test_calculator_addition(self):
        """Test calculator addition operation."""
        result = self.calculator.func("add", 5, 3)
        assert "8" in result
        assert "Result:" in result
    
    def test_calculator_division_by_zero(self):
        """Test calculator error handling."""
        result = self.calculator.func("divide", 5, 0)
        assert "Error" in result
        assert "division by zero" in result.lower()
    
    def test_text_analyzer_basic(self):
        """Test text analyzer basic functionality."""
        result = self.text_analyzer.func("Hello world", "basic")
        assert "Hello world" in result
        assert "Length:" in result
    
    @pytest.mark.parametrize("operation,a,b,expected", [
        ("add", 2, 3, "5"),
        ("subtract", 10, 4, "6"),
        ("multiply", 3, 4, "12"),
        ("divide", 8, 2, "4")
    ])
    def test_calculator_operations(self, operation, a, b, expected):
        """Test all calculator operations."""
        result = self.calculator.func(operation, a, b)
        assert expected in result
```

### **Memory System Testing**

```python
# tests/unit/test_memory_engine.py
import pytest
import asyncio
import tempfile
import shutil
from pathlib import Path
from agent.tools.memory_engine import (
    MemoryEngine, MemoryConfig, MemoryMode, MemoryEntry
)

class TestMemoryEngine:
    """Test memory engine functionality."""
    
    @pytest.fixture
    def temp_cache_dir(self):
        """Create temporary cache directory."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def memory_config(self, temp_cache_dir):
        """Create test memory configuration."""
        return MemoryConfig(
            mode=MemoryMode.DEVELOPMENT,
            cache_dir=temp_cache_dir,
            session_retention_days=1,
            memory_retention_days=7,
            max_memory_results=5
        )
    
    @pytest.fixture
    def memory_engine(self, memory_config):
        """Create memory engine for testing."""
        return MemoryEngine(memory_config)
    
    @pytest.mark.asyncio
    async def test_add_memory(self, memory_engine):
        """Test adding memory entries."""
        entry_id = await memory_engine.add_memory(
            content="Test memory content",
            session_id="test_session",
            user_id="test_user",
            context_type="conversation"
        )
        
        assert entry_id.startswith("conversation_test_session_")
        assert len(memory_engine.local_memory) == 1
        
        # Verify entry details
        entry = memory_engine.local_memory[entry_id]
        assert entry.content == "Test memory content"
        assert entry.session_id == "test_session"
        assert entry.user_id == "test_user"
        assert entry.context_type == "conversation"
    
    @pytest.mark.asyncio
    async def test_search_memory(self, memory_engine):
        """Test memory search functionality."""
        # Add test memories
        await memory_engine.add_memory(
            content="Authentication implementation using JWT",
            session_id="test_session",
            user_id="test_user",
            context_type="analysis"
        )
        
        await memory_engine.add_memory(
            content="Database connection setup",
            session_id="test_session",
            user_id="test_user",
            context_type="conversation"
        )
        
        # Search for authentication
        results = await memory_engine.search_memory(
            query="authentication",
            user_id="test_user"
        )
        
        assert len(results) == 1
        assert "authentication" in results[0].content.lower()
        assert results[0].context_type == "analysis"
    
    @pytest.mark.asyncio
    async def test_context_summary(self, memory_engine):
        """Test context summary generation."""
        # Add multiple memories
        for i in range(3):
            await memory_engine.add_memory(
                content=f"Memory entry {i}",
                session_id="test_session",
                user_id="test_user",
                context_type="conversation"
            )
        
        # Get context summary
        summary = await memory_engine.get_context_summary(
            session_id="test_session",
            max_tokens=1000
        )
        
        assert summary
        assert "Memory entry" in summary
        assert len(summary.split('\n\n')) <= 3  # Should have entries
    
    @pytest.mark.asyncio
    async def test_memory_persistence(self, memory_engine, temp_cache_dir):
        """Test memory persistence across engine restarts."""
        # Add memory
        entry_id = await memory_engine.add_memory(
            content="Persistent memory test",
            session_id="test_session",
            user_id="test_user"
        )
        
        # Create new engine with same config
        new_config = MemoryConfig(
            mode=MemoryMode.DEVELOPMENT,
            cache_dir=temp_cache_dir
        )
        new_engine = MemoryEngine(new_config)
        new_engine._load_local_memory()
        
        # Verify memory persisted
        assert len(new_engine.local_memory) == 1
        assert entry_id in new_engine.local_memory
        assert new_engine.local_memory[entry_id].content == "Persistent memory test"
```

### **Codebase Indexer Testing**

```python
# tests/unit/test_codebase_indexer.py
import pytest
import tempfile
import shutil
from pathlib import Path
from agent.tools.codebase_indexer import CodebaseIndexer, CodeElement

class TestCodebaseIndexer:
    """Test codebase indexer functionality."""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create sample Python files
        (temp_dir / "main.py").write_text('''
def main():
    """Main function."""
    print("Hello, world!")

class Calculator:
    """Simple calculator class."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
''')
        
        (temp_dir / "utils.py").write_text('''
import os
from typing import List

def process_files(files: List[str]) -> int:
    """Process a list of files."""
    return len(files)

class FileManager:
    """File management utilities."""
    pass
''')
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def indexer(self):
        """Create indexer for testing."""
        return CodebaseIndexer()
    
    def test_index_codebase(self, indexer, temp_project):
        """Test codebase indexing."""
        stats = indexer.index_codebase(temp_project)
        
        assert stats['files_processed'] == 2
        assert stats['total_elements'] > 0
        assert len(stats['errors']) == 0
        
        # Verify elements were indexed
        assert len(indexer.code_elements) > 0
        assert len(indexer.files) == 2
    
    def test_search_functions(self, indexer, temp_project):
        """Test searching for functions."""
        indexer.index_codebase(temp_project)
        
        # Search for functions
        functions = indexer.search_code_elements("", element_type="function")
        function_names = [f.name for f in functions]
        
        assert "main" in function_names
        assert "add" in function_names
        assert "process_files" in function_names
    
    def test_search_classes(self, indexer, temp_project):
        """Test searching for classes."""
        indexer.index_codebase(temp_project)
        
        # Search for classes
        classes = indexer.search_code_elements("", element_type="class")
        class_names = [c.name for c in classes]
        
        assert "Calculator" in class_names
        assert "FileManager" in class_names
    
    def test_file_summary(self, indexer, temp_project):
        """Test file summary generation."""
        indexer.index_codebase(temp_project)
        
        main_py = str(temp_project / "main.py")
        summary = indexer.get_file_summary(main_py)
        
        assert summary['file_path'] == main_py
        assert len(summary['functions']) >= 1
        assert len(summary['classes']) >= 1
        assert 'main' in [f['name'] for f in summary['functions']]
        assert 'Calculator' in [c['name'] for c in summary['classes']]
```

## 🔗 **Integration Testing**

### **Agent Integration Tests**

```python
# tests/integration/test_agent_integration.py
import pytest
from agent.agent import create_agent

class TestAgentIntegration:
    """Test agent integration with all tools."""
    
    @pytest.fixture
    def agent(self):
        """Create agent for integration testing."""
        return create_agent()
    
    def test_agent_creation(self, agent):
        """Test agent creation with all tools."""
        assert agent is not None
        assert len(agent.tools) == 19  # Expected number of tools
    
    def test_tool_availability(self, agent):
        """Test that all expected tools are available."""
        tool_names = [tool.func.__name__ for tool in agent.tools]
        
        expected_tools = [
            # Basic tools
            'get_current_time', 'calculator', 'text_analyzer',
            'directory_operations', 'file_management', 'terminal_command',
            'run_code_in_sandbox',
            
            # AST tools
            'merge_code_intelligently', 'merge_code_with_codebase_awareness',
            'analyze_code_structure',
            
            # Professional SWE tools
            'merge_code_professionally', 'analyze_codebase_architecture',
            
            # Memory tools
            'search_memory', 'get_context', 'manage_memory',
            
            # Codebase tools
            'index_codebase', 'search_code', 'analyze_file', 'analyze_self'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_names, f"Tool {tool_name} not found"
    
    @pytest.mark.asyncio
    async def test_memory_workflow(self, agent):
        """Test complete memory workflow."""
        # Find memory tools
        memory_tools = {}
        for tool in agent.tools:
            if tool.func.__name__ in ['search_memory', 'manage_memory']:
                memory_tools[tool.func.__name__] = tool
        
        # Add memory
        mgmt_tool = memory_tools['manage_memory']
        result = await mgmt_tool.func(
            action="add",
            content="Test integration memory",
            context_type="conversation",
            session_id="integration_test"
        )
        assert "Added memory entry" in result
        
        # Search memory
        search_tool = memory_tools['search_memory']
        result = await search_tool.func(
            query="integration",
            user_id="default_user"
        )
        assert "Test integration memory" in result
    
    @pytest.mark.asyncio
    async def test_codebase_workflow(self, agent, temp_project):
        """Test codebase analysis workflow."""
        # Find codebase tools
        codebase_tools = {}
        for tool in agent.tools:
            if tool.func.__name__ in ['index_codebase', 'search_code']:
                codebase_tools[tool.func.__name__] = tool
        
        # Index codebase
        index_tool = codebase_tools['index_codebase']
        result = await index_tool.func(root_path=str(temp_project))
        assert "files processed" in result
        
        # Search code
        search_tool = codebase_tools['search_code']
        result = await search_tool.func(query="main")
        assert "main" in result
```

## ⚡ **Performance Testing**

### **Indexing Performance**

```python
# tests/performance/test_indexing_performance.py
import pytest
import time
import tempfile
import shutil
from pathlib import Path
from agent.tools.codebase_indexer import get_global_indexer

class TestIndexingPerformance:
    """Test codebase indexing performance."""
    
    @pytest.fixture
    def large_project(self):
        """Create large project for performance testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create multiple files with various sizes
        for i in range(50):  # 50 files
            file_content = f'''
def function_{i}_1():
    """Function {i}_1 documentation."""
    return {i}

def function_{i}_2():
    """Function {i}_2 documentation."""
    return {i} * 2

class Class_{i}:
    """Class {i} documentation."""
    
    def method_{i}(self):
        """Method {i} documentation."""
        return {i}
    
    def another_method_{i}(self):
        """Another method {i} documentation."""
        return {i} + 1
'''
            (temp_dir / f"module_{i}.py").write_text(file_content)
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    def test_indexing_speed(self, large_project):
        """Test indexing speed for large projects."""
        indexer = get_global_indexer()
        
        start_time = time.time()
        stats = indexer.index_codebase(large_project)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 30  # Should complete within 30 seconds
        assert stats['files_processed'] == 50
        assert stats['total_elements'] > 200  # Should find many elements
        
        # Calculate performance metrics
        files_per_second = stats['files_processed'] / duration
        elements_per_second = stats['total_elements'] / duration
        
        print(f"Indexing performance:")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Files per second: {files_per_second:.2f}")
        print(f"  Elements per second: {elements_per_second:.2f}")
        
        # Performance requirements
        assert files_per_second > 1  # At least 1 file per second
        assert elements_per_second > 10  # At least 10 elements per second
    
    def test_search_speed(self, large_project):
        """Test search speed after indexing."""
        indexer = get_global_indexer()
        indexer.index_codebase(large_project)
        
        # Test multiple searches
        search_times = []
        for query in ["function", "class", "method", "return"]:
            start_time = time.time()
            results = indexer.search_code_elements(query)
            end_time = time.time()
            
            search_time = end_time - start_time
            search_times.append(search_time)
            
            # Each search should be fast
            assert search_time < 1  # Less than 1 second
            assert len(results) > 0  # Should find results
        
        avg_search_time = sum(search_times) / len(search_times)
        print(f"Average search time: {avg_search_time:.3f} seconds")
        
        # Average search should be very fast
        assert avg_search_time < 0.5
```

### **Memory Performance**

```python
# tests/performance/test_memory_performance.py
import pytest
import asyncio
import time
from agent.tools.memory_engine import get_memory_engine, MemoryConfig, MemoryMode

class TestMemoryPerformance:
    """Test memory system performance."""
    
    @pytest.fixture
    def memory_engine(self):
        """Create memory engine for performance testing."""
        config = MemoryConfig(
            mode=MemoryMode.DEVELOPMENT,
            cache_dir=".test_memory_perf",
            max_memory_results=100
        )
        return get_memory_engine(config)
    
    @pytest.mark.asyncio
    async def test_bulk_memory_operations(self, memory_engine):
        """Test performance with many memory operations."""
        num_memories = 1000
        
        # Test bulk addition
        start_time = time.time()
        for i in range(num_memories):
            await memory_engine.add_memory(
                content=f"Memory entry {i} with some content",
                session_id=f"session_{i % 10}",
                user_id="perf_test_user",
                context_type="conversation"
            )
        add_time = time.time() - start_time
        
        print(f"Added {num_memories} memories in {add_time:.2f} seconds")
        print(f"Rate: {num_memories / add_time:.2f} memories/second")
        
        # Performance requirements
        assert add_time < 60  # Should complete within 1 minute
        assert num_memories / add_time > 10  # At least 10 memories/second
        
        # Test bulk search
        start_time = time.time()
        for i in range(100):  # 100 searches
            results = await memory_engine.search_memory(
                query=f"entry {i}",
                user_id="perf_test_user",
                max_results=10
            )
        search_time = time.time() - start_time
        
        print(f"Performed 100 searches in {search_time:.2f} seconds")
        print(f"Rate: {100 / search_time:.2f} searches/second")
        
        # Search performance requirements
        assert search_time < 30  # Should complete within 30 seconds
        assert 100 / search_time > 3  # At least 3 searches/second
```

## 🎯 **End-to-End Testing**

### **Development Workflow Test**

```python
# tests/e2e/test_development_workflow.py
import pytest
import tempfile
import shutil
from pathlib import Path
from agent.agent import create_agent

class TestDevelopmentWorkflow:
    """Test complete development workflows."""
    
    @pytest.fixture
    def agent(self):
        """Create agent for E2E testing."""
        return create_agent()
    
    @pytest.fixture
    def project_dir(self):
        """Create test project directory."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Create a simple Python project
        (temp_dir / "main.py").write_text('''
def main():
    """Main application entry point."""
    print("Hello, World!")

if __name__ == "__main__":
    main()
''')
        
        (temp_dir / "utils.py").write_text('''
def helper_function(x):
    """A helper function."""
    return x * 2
''')
        
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.mark.asyncio
    async def test_complete_analysis_workflow(self, agent, project_dir):
        """Test complete code analysis workflow."""
        # Get tools
        tools = {tool.func.__name__: tool for tool in agent.tools}
        
        # Step 1: Index the codebase
        index_result = await tools['index_codebase'].func(
            root_path=str(project_dir)
        )
        assert "files processed" in index_result
        
        # Step 2: Search for functions
        search_result = await tools['search_code'].func(
            query="main",
            element_type="function"
        )
        assert "main" in search_result
        
        # Step 3: Analyze specific file
        analyze_result = await tools['analyze_file'].func(
            file_path=str(project_dir / "main.py")
        )
        assert "main.py" in analyze_result
        
        # Step 4: Add analysis to memory
        memory_result = await tools['manage_memory'].func(
            action="add",
            content="Analyzed main.py - contains main function",
            context_type="analysis",
            session_id="e2e_test"
        )
        assert "Added memory entry" in memory_result
        
        # Step 5: Search memory for analysis
        memory_search = await tools['search_memory'].func(
            query="main function",
            context_types="analysis"
        )
        assert "main function" in memory_search
        
        # Step 6: Get context summary
        context_result = await tools['get_context'].func(
            session_id="e2e_test"
        )
        assert "main function" in context_result
```

## 🔧 **Test Configuration**

### **pytest Configuration**

```python
# conftest.py
import pytest
import tempfile
import shutil
from pathlib import Path

@pytest.fixture(scope="session")
def temp_cache_dir():
    """Session-wide temporary cache directory."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_python_file():
    """Create sample Python file for testing."""
    content = '''
"""Sample module for testing."""

import os
from typing import List, Optional

def sample_function(param: str) -> str:
    """Sample function with documentation."""
    return f"Processed: {param}"

class SampleClass:
    """Sample class for testing."""
    
    def __init__(self, name: str):
        self.name = name
    
    def get_name(self) -> str:
        """Get the name."""
        return self.name

# Global variable
SAMPLE_CONSTANT = "test_value"
'''
    
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
    temp_file.write(content)
    temp_file.close()
    
    yield temp_file.name
    
    Path(temp_file.name).unlink()

# Pytest markers
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "e2e: marks tests as end-to-end tests"
    )
```

### **Test Running Commands**

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest tests/performance/             # Performance tests only
pytest tests/e2e/                     # End-to-end tests only

# Run tests with markers
pytest -m "not slow"                  # Skip slow tests
pytest -m "integration"               # Run integration tests only
pytest -m "e2e"                       # Run E2E tests only

# Run with coverage
pytest --cov=agent --cov-report=html

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/unit/test_memory_engine.py

# Run specific test method
pytest tests/unit/test_memory_engine.py::TestMemoryEngine::test_add_memory
```

## 📊 **Test Metrics**

### **Coverage Requirements**

- **Overall coverage**: > 90%
- **Critical components**: > 95%
- **Tool functions**: 100%
- **Error handling**: > 85%

### **Performance Benchmarks**

- **Indexing**: < 30 seconds for 1000 files
- **Search**: < 1 second per query
- **Memory operations**: > 10 operations/second
- **Tool execution**: < 5 seconds per tool call

---

**Next**: Explore [Contributing](./contributing.md) for contribution guidelines.

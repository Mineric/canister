# Development Guide

Comprehensive guide for developing with and extending the Canister Agent.

## 🎯 **Overview**

This guide covers:
- Development environment setup
- Code organization and architecture
- Adding new tools and features
- Testing strategies
- Best practices and conventions

## 🚀 **Getting Started**

### **Prerequisites**

```bash
# Python 3.11 or higher
python --version

# Required packages
pip install google-adk
pip install openai
pip install litellm
```

### **Development Setup**

```bash
# Clone repository
git clone https://github.com/your-org/canister.git
cd canister

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### **Project Structure**

```
canister/
├── agent/                    # Main agent code
│   ├── __init__.py
│   ├── agent.py             # Agent creation and configuration
│   └── tools/               # Tool implementations
│       ├── __init__.py
│       ├── tools.py         # Basic utility tools
│       ├── code_tools.py    # AST-based code tools
│       ├── memory_engine.py # Memory and context system
│       ├── codebase_indexer.py # Codebase analysis
│       ├── code_comprehension.py # Professional code analysis
│       └── intelligent_merger.py # Professional merging
├── docs/                    # Documentation
├── tests/                   # Test files
├── config/                  # Configuration files
├── requirements.txt         # Dependencies
├── requirements-dev.txt     # Development dependencies
└── README.md               # Project overview
```

## 🛠️ **Development Workflow**

### **1. Environment Configuration**

```python
# config/development.py
from agent.tools.memory_engine import MemoryConfig, MemoryMode

DEVELOPMENT_CONFIG = MemoryConfig(
    mode=MemoryMode.DEVELOPMENT,
    cache_dir=".dev_memory",
    session_retention_days=7,
    memory_retention_days=30,
    max_context_tokens=16000,
    enable_codebase_integration=True
)
```

### **2. Running the Agent**

```python
# main.py
from agent.agent import create_agent
from config.development import DEVELOPMENT_CONFIG
from agent.tools.memory_engine import get_memory_engine

# Initialize memory with dev config
memory_engine = get_memory_engine(DEVELOPMENT_CONFIG)

# Create agent
agent = create_agent()

# Test agent
response = agent.run("What tools do you have available?")
print(response)
```

### **3. Development Commands**

```bash
# Run agent
python main.py

# Run tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_memory_engine.py

# Code formatting
black agent/ tests/
isort agent/ tests/

# Linting
flake8 agent/ tests/
mypy agent/

# Type checking
mypy agent/ --strict
```

## 🔧 **Adding New Tools**

### **Tool Development Pattern**

```python
# agent/tools/example_tool.py
from google.adk.tools import FunctionTool
from typing import Optional

def example_tool() -> FunctionTool:
    """
    Create an example tool following Canister patterns.
    """
    
    def example_function(
        required_param: str,
        optional_param: int = 10,
        flag_param: bool = True
    ) -> str:
        """
        Example function with proper documentation.
        
        Args:
            required_param: Description of required parameter
            optional_param: Description with default value
            flag_param: Boolean flag description
        
        Returns:
            Formatted result string
        
        Raises:
            ValueError: When invalid parameters provided
        """
        try:
            # Input validation
            if not required_param.strip():
                raise ValueError("required_param cannot be empty")
            
            if optional_param < 0:
                raise ValueError("optional_param must be non-negative")
            
            # Tool implementation
            result = f"Processed '{required_param}' with value {optional_param}"
            if flag_param:
                result += " (flag enabled)"
            
            return result
            
        except Exception as e:
            return f"Error in example_function: {str(e)}"
    
    return FunctionTool(example_function)
```

### **Tool Integration**

```python
# agent/agent.py
from .tools.example_tool import example_tool

def create_agent():
    tools = [
        # ... existing tools
        example_tool(),  # Add new tool
    ]
    
    return LlmAgent(
        model=LiteLlm(model="gpt-4"),
        tools=tools
    )
```

### **Tool Testing**

```python
# tests/test_example_tool.py
import pytest
from agent.tools.example_tool import example_tool

class TestExampleTool:
    def setup_method(self):
        """Set up test environment."""
        self.tool = example_tool()
    
    def test_basic_functionality(self):
        """Test basic tool functionality."""
        result = self.tool.func("test_input", 5, True)
        assert "Processed 'test_input' with value 5" in result
        assert "(flag enabled)" in result
    
    def test_error_handling(self):
        """Test error handling."""
        result = self.tool.func("", 5, True)
        assert "Error" in result
        assert "cannot be empty" in result
    
    def test_optional_parameters(self):
        """Test optional parameters."""
        result = self.tool.func("test")
        assert "with value 10" in result  # Default value
```

## 🧠 **Memory System Development**

### **Adding New Context Types**

```python
# agent/tools/memory_engine.py
def _calculate_priority(self, content: str, context_type: str) -> ContextPriority:
    """Calculate priority scores for content."""
    # Add new context type
    importance_map = {
        "conversation": 0.6,
        "codebase": 0.9,
        "analysis": 0.8,
        "decision": 0.95,
        "error": 0.85,
        "custom_type": 0.7  # New context type
    }
    importance_score = importance_map.get(context_type, 0.5)
    
    # ... rest of implementation
```

### **Custom Memory Backends**

```python
# agent/tools/custom_memory.py
from agent.tools.memory_engine import MemoryEngine, MemoryConfig

class CustomMemoryEngine(MemoryEngine):
    """Custom memory engine with additional features."""
    
    def __init__(self, config: MemoryConfig):
        super().__init__(config)
        self.custom_storage = {}  # Custom storage backend
    
    async def add_memory(self, content: str, **kwargs) -> str:
        """Override with custom logic."""
        # Custom preprocessing
        processed_content = self._preprocess_content(content)
        
        # Call parent implementation
        entry_id = await super().add_memory(processed_content, **kwargs)
        
        # Custom post-processing
        self._post_process_memory(entry_id)
        
        return entry_id
    
    def _preprocess_content(self, content: str) -> str:
        """Custom content preprocessing."""
        # Add custom logic here
        return content.strip().lower()
    
    def _post_process_memory(self, entry_id: str):
        """Custom post-processing."""
        # Add custom logic here
        pass
```

## 📊 **Codebase Indexer Development**

### **Adding New Code Element Types**

```python
# agent/tools/codebase_indexer.py
def _extract_code_elements(self, node: ast.AST, file_path: str) -> List[CodeElement]:
    """Extract code elements from AST node."""
    elements = []
    
    for child in ast.walk(node):
        if isinstance(child, ast.FunctionDef):
            # Existing function handling
            elements.append(self._create_function_element(child, file_path))
        
        elif isinstance(child, ast.ClassDef):
            # Existing class handling
            elements.append(self._create_class_element(child, file_path))
        
        elif isinstance(child, ast.AsyncFunctionDef):
            # New: async function handling
            elements.append(self._create_async_function_element(child, file_path))
        
        elif isinstance(child, ast.Assign):
            # New: variable assignment handling
            elements.extend(self._create_variable_elements(child, file_path))
    
    return elements

def _create_async_function_element(self, node: ast.AsyncFunctionDef, file_path: str) -> CodeElement:
    """Create code element for async function."""
    return CodeElement(
        name=node.name,
        element_type="async_function",
        file_path=file_path,
        line_number=node.lineno,
        end_line_number=getattr(node, 'end_lineno', None),
        signature=self._get_function_signature(node),
        docstring=ast.get_docstring(node),
        decorators=[self._get_decorator_name(d) for d in node.decorator_list],
        complexity_score=self._calculate_complexity(node)
    )
```

### **Custom Analysis Features**

```python
# agent/tools/custom_analyzer.py
from agent.tools.codebase_indexer import CodebaseIndexer

class EnhancedCodebaseIndexer(CodebaseIndexer):
    """Enhanced indexer with custom analysis features."""
    
    def analyze_code_quality(self, file_path: str) -> Dict[str, Any]:
        """Analyze code quality metrics."""
        elements = self.search_code_elements("", file_pattern=file_path)
        
        quality_metrics = {
            "complexity_score": self._calculate_average_complexity(elements),
            "documentation_coverage": self._calculate_doc_coverage(elements),
            "naming_consistency": self._analyze_naming_patterns(elements),
            "design_patterns": self._detect_design_patterns(elements)
        }
        
        return quality_metrics
    
    def _calculate_average_complexity(self, elements: List[CodeElement]) -> float:
        """Calculate average complexity score."""
        if not elements:
            return 0.0
        
        total_complexity = sum(e.complexity_score for e in elements)
        return total_complexity / len(elements)
    
    def _calculate_doc_coverage(self, elements: List[CodeElement]) -> float:
        """Calculate documentation coverage percentage."""
        if not elements:
            return 0.0
        
        documented = sum(1 for e in elements if e.docstring)
        return (documented / len(elements)) * 100
```

## 🧪 **Testing Strategies**

### **Unit Testing**

```python
# tests/test_memory_engine.py
import pytest
import asyncio
from agent.tools.memory_engine import MemoryEngine, MemoryConfig, MemoryMode

class TestMemoryEngine:
    @pytest.fixture
    def memory_engine(self):
        """Create memory engine for testing."""
        config = MemoryConfig(
            mode=MemoryMode.DEVELOPMENT,
            cache_dir=".test_memory"
        )
        return MemoryEngine(config)
    
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
    
    @pytest.mark.asyncio
    async def test_search_memory(self, memory_engine):
        """Test memory search functionality."""
        # Add test memories
        await memory_engine.add_memory(
            content="Authentication implementation",
            session_id="test_session",
            user_id="test_user",
            context_type="analysis"
        )
        
        # Search memories
        results = await memory_engine.search_memory(
            query="authentication",
            user_id="test_user"
        )
        
        assert len(results) == 1
        assert "authentication" in results[0].content.lower()
```

### **Integration Testing**

```python
# tests/test_integration.py
import pytest
from agent.agent import create_agent

class TestAgentIntegration:
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
            'get_current_time',
            'calculator',
            'search_memory',
            'index_codebase'
        ]
        
        for tool_name in expected_tools:
            assert tool_name in tool_names
    
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
            context_type="conversation"
        )
        assert "Added memory entry" in result
        
        # Search memory
        search_tool = memory_tools['search_memory']
        result = await search_tool.func(query="integration")
        assert "Test integration memory" in result
```

### **Performance Testing**

```python
# tests/test_performance.py
import time
import pytest
from agent.tools.codebase_indexer import get_global_indexer

class TestPerformance:
    def test_indexing_performance(self):
        """Test codebase indexing performance."""
        indexer = get_global_indexer()
        
        start_time = time.time()
        stats = indexer.index_codebase("./agent")
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 30  # Should complete within 30 seconds
        assert stats['total_elements'] > 0
        assert len(stats['errors']) == 0
    
    def test_search_performance(self):
        """Test search performance."""
        indexer = get_global_indexer()
        indexer.index_codebase("./agent")
        
        start_time = time.time()
        results = indexer.search_code_elements("function")
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Performance assertions
        assert duration < 1  # Search should be fast
        assert len(results) > 0
```

## 🎯 **Best Practices**

### **Code Style**

```python
# Use type hints
def process_data(data: List[str], options: Dict[str, Any]) -> Optional[str]:
    """Process data with given options."""
    pass

# Use dataclasses for structured data
@dataclass
class ProcessingResult:
    success: bool
    data: Optional[str] = None
    errors: List[str] = field(default_factory=list)

# Use enums for constants
class ProcessingMode(Enum):
    FAST = "fast"
    THOROUGH = "thorough"
    CUSTOM = "custom"
```

### **Error Handling**

```python
def robust_function(param: str) -> str:
    """Function with proper error handling."""
    try:
        # Validate inputs
        if not param or not param.strip():
            raise ValueError("Parameter cannot be empty")
        
        # Process data
        result = process_data(param)
        
        # Validate outputs
        if not result:
            raise RuntimeError("Processing failed to produce result")
        
        return result
        
    except ValueError as e:
        # Handle validation errors
        return f"Validation error: {str(e)}"
    
    except RuntimeError as e:
        # Handle processing errors
        return f"Processing error: {str(e)}"
    
    except Exception as e:
        # Handle unexpected errors
        return f"Unexpected error: {str(e)}"
```

### **Documentation**

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

## 🔧 **Debugging**

### **Logging Setup**

```python
# debug_config.py
import logging

def setup_debug_logging():
    """Set up detailed logging for debugging."""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('debug.log'),
            logging.StreamHandler()
        ]
    )
    
    # Configure specific loggers
    logging.getLogger("agent.tools").setLevel(logging.DEBUG)
    logging.getLogger("agent.memory").setLevel(logging.DEBUG)
    logging.getLogger("agent.codebase").setLevel(logging.DEBUG)
```

### **Debug Tools**

```python
# debug_tools.py
def debug_memory_state(memory_engine):
    """Debug memory engine state."""
    print(f"Total memories: {len(memory_engine.local_memory)}")
    print(f"Cache directory: {memory_engine.cache_dir}")
    
    for entry_id, entry in memory_engine.local_memory.items():
        print(f"  {entry_id}: {entry.context_type} - {entry.content[:50]}...")

def debug_indexer_state(indexer):
    """Debug codebase indexer state."""
    print(f"Total elements: {len(indexer.code_elements)}")
    print(f"Total files: {len(indexer.files)}")
    print(f"Database path: {indexer.db_path}")
    
    for element_type in ["function", "class", "variable"]:
        count = len([e for e in indexer.code_elements.values() 
                    if e.element_type == element_type])
        print(f"  {element_type}s: {count}")
```

---

**Next**: Explore [Testing Guide](./testing.md) for comprehensive testing strategies.

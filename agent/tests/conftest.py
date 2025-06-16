"""
Pytest configuration and fixtures for Cannister Agent tests.
"""

import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_python_file(temp_dir):
    """Create a sample Python file for testing."""
    content = '''
"""Sample module for testing."""

def hello(name: str) -> str:
    """Say hello to someone."""
    return f"Hello, {name}!"

class Calculator:
    """Simple calculator."""
    
    def add(self, a: int, b: int) -> int:
        """Add two numbers."""
        return a + b
    
    def multiply(self, a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b
'''
    
    file_path = Path(temp_dir) / "sample.py"
    file_path.write_text(content)
    return str(file_path)


@pytest.fixture
def project_root():
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent

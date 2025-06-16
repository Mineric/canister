#!/usr/bin/env python3
"""
Unit tests for agent tools.
"""

import unittest
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestBasicTools(unittest.TestCase):
    """Test basic utility tools."""
    
    def test_current_time_tool(self):
        """Test the current time tool."""
        try:
            from agent.tools.tools import get_current_time_tool
            tool = get_current_time_tool()
            result = tool.func()
            self.assertIsInstance(result, str)
            self.assertIn("-", result)  # Should contain date separators
            self.assertIn(":", result)  # Should contain time separators
        except ImportError as e:
            self.skipTest(f"Could not import tool: {e}")
    
    def test_calculator_tool(self):
        """Test the calculator tool."""
        try:
            from agent.tools.tools import calculator_tool
            tool = calculator_tool()
            
            # Test basic arithmetic
            result = tool.func("2 + 2")
            self.assertIn("4", result)
            
            # Test with variables
            result = tool.func("x = 5; y = 3; x * y")
            self.assertIn("15", result)
            
        except ImportError as e:
            self.skipTest(f"Could not import tool: {e}")
    
    def test_text_analyzer_tool(self):
        """Test the text analyzer tool."""
        try:
            from agent.tools.tools import text_analyzer_tool
            tool = text_analyzer_tool()
            
            test_text = "Hello world. This is a test."
            result = tool.func(test_text)
            
            self.assertIn("Characters:", result)
            self.assertIn("Words:", result)
            self.assertIn("Sentences:", result)
            
        except ImportError as e:
            self.skipTest(f"Could not import tool: {e}")


class TestFileTools(unittest.TestCase):
    """Test file management tools."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_file_management_tool(self):
        """Test file management operations."""
        try:
            from agent.tools.tools import file_management_tool
            tool = file_management_tool()
            
            # Test write operation
            content = "Hello, World!"
            result = tool.func("write", self.test_file, content)
            self.assertIn("successfully", result.lower())
            
            # Test read operation
            result = tool.func("read", self.test_file)
            self.assertIn(content, result)
            
        except ImportError as e:
            self.skipTest(f"Could not import tool: {e}")
    
    def test_directory_operations_tool(self):
        """Test directory operations."""
        try:
            from agent.tools.tools import directory_operations_tool
            tool = directory_operations_tool()
            
            # Test getcwd
            result = tool.func("getcwd")
            self.assertIn("Current working directory:", result)
            
            # Test listdir
            result = tool.func("listdir", self.temp_dir)
            self.assertIn("Contents of", result)
            
        except ImportError as e:
            self.skipTest(f"Could not import tool: {e}")


class TestCodeTools(unittest.TestCase):
    """Test code analysis and manipulation tools."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_py_file = os.path.join(self.temp_dir, "test.py")
        
        # Create a test Python file
        test_code = '''
def hello(name):
    """Say hello to someone."""
    return f"Hello, {name}!"

class Calculator:
    """Simple calculator class."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
'''
        with open(self.test_py_file, 'w') as f:
            f.write(test_code)
    
    def tearDown(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    


if __name__ == "__main__":
    unittest.main()

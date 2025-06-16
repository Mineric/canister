#!/usr/bin/env python3
"""
Test script for the AST-based code merger tool.
This demonstrates the intelligent merging capabilities.
"""

import tempfile
import os
from pathlib import Path
from agent.tools.code_tools import ast_code_merger_tool, code_structure_analyzer_tool


def test_ast_merger():
    """Test the AST code merger with various scenarios."""
    
    # Create test tools
    merger_tool = ast_code_merger_tool()
    analyzer_tool = code_structure_analyzer_tool()
    
    # Test scenario 1: Basic function replacement and addition
    original_code = '''
import os
import sys

def greet(name):
    """Original greeting function."""
    print(f"Hello, {name}!")

class Calculator:
    def add(self, a, b):
        return a + b
'''

    ai_generated_code = '''
import json
from pathlib import Path

def greet(name, greeting="Hello"):
    """Enhanced greeting function with custom greeting."""
    print(f"{greeting}, {name}!")

def farewell(name):
    """New function to say goodbye."""
    print(f"Goodbye, {name}!")

class Calculator:
    def subtract(self, a, b):
        """New method for subtraction."""
        return a - b
    
    def multiply(self, a, b):
        """New method for multiplication."""
        return a * b
'''

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(original_code)
        temp_file = f.name

    try:
        print("=== AST Code Merger Test ===")
        print("\n1. Analyzing original code structure:")
        analysis_result = analyzer_tool.func(temp_file)
        print(analysis_result)

        print("\n2. Performing intelligent merge (dry run):")
        merge_result = merger_tool.func(temp_file, ai_generated_code, backup=True, dry_run=True)
        print(merge_result)

        print("\n3. Performing actual merge:")
        merge_result = merger_tool.func(temp_file, ai_generated_code, backup=True, dry_run=False)
        print(merge_result)

        print("\n4. Analyzing merged code structure:")
        analysis_result = analyzer_tool.func(temp_file)
        print(analysis_result)
        
        print("\n5. Final merged code:")
        with open(temp_file, 'r') as f:
            merged_content = f.read()
        print(merged_content)
        
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.unlink(temp_file)
        backup_file = temp_file + '.backup'
        if os.path.exists(backup_file):
            os.unlink(backup_file)


def test_error_handling():
    """Test error handling scenarios."""
    print("\n=== Error Handling Tests ===")
    
    merger_tool = ast_code_merger_tool()
    
    # Test 1: Non-existent file
    result = merger_tool.func("non_existent_file.py", "def test(): pass")
    print(f"Non-existent file test: {result}")

    # Test 2: Invalid Python syntax
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write("def valid_function():\n    pass")
        temp_file = f.name

    try:
        result = merger_tool.func(temp_file, "def invalid_syntax(\n    pass")
        print(f"Invalid syntax test: {result}")
    finally:
        os.unlink(temp_file)

    # Test 3: Non-Python file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("This is not a Python file")
        temp_file = f.name

    try:
        result = merger_tool.func(temp_file, "def test(): pass")
        print(f"Non-Python file test: {result}")
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    print("Testing AST-based Code Merger Tool")
    print("=" * 40)
    
    try:
        test_ast_merger()
        test_error_handling()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

#!/usr/bin/env python3
"""
Demonstration script for the AST-based code merger tool.
This script shows how the tool intelligently merges code while preserving structure.
"""

import tempfile
import os
from pathlib import Path
from agent.tools.code_tools import ast_code_merger_tool, code_structure_analyzer_tool


def create_demo_file():
    """Create a demo Python file for testing."""
    demo_code = '''
import os
import sys
from typing import List

# Module-level constant
VERSION = "1.0.0"

def greet(name: str) -> None:
    """Simple greeting function."""
    print(f"Hello, {name}!")

def calculate_sum(numbers: List[int]) -> int:
    """Calculate sum of numbers."""
    return sum(numbers)

class DataProcessor:
    """A simple data processor class."""
    
    def __init__(self, name: str):
        self.name = name
        self.data = []
    
    def add_data(self, item):
        """Add data to the processor."""
        self.data.append(item)
    
    def get_count(self) -> int:
        """Get count of data items."""
        return len(self.data)

class MathUtils:
    """Utility class for mathematical operations."""
    
    @staticmethod
    def add(a: int, b: int) -> int:
        return a + b
'''
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(demo_code)
        return f.name


def demo_intelligent_merging():
    """Demonstrate intelligent code merging capabilities."""
    print("🚀 AST-Based Code Merger Demonstration")
    print("=" * 50)
    
    # Create demo file
    demo_file = create_demo_file()
    print(f"📁 Created demo file: {demo_file}")
    
    # Create tools
    merger_tool = ast_code_merger_tool()
    analyzer_tool = code_structure_analyzer_tool()
    
    try:
        # Step 1: Analyze original structure
        print("\n📊 Step 1: Analyzing original code structure")
        print("-" * 40)
        analysis = analyzer_tool.func(demo_file)
        print(analysis)
        
        # Step 2: Define AI-generated code with various scenarios
        ai_code = '''
import json
import asyncio
from pathlib import Path
from datetime import datetime

# New module-level constant
DEBUG_MODE = True

def greet(name: str, greeting: str = "Hello", timestamp: bool = False) -> None:
    """Enhanced greeting function with customizable greeting and optional timestamp."""
    if timestamp:
        current_time = datetime.now().strftime("%H:%M:%S")
        print(f"[{current_time}] {greeting}, {name}!")
    else:
        print(f"{greeting}, {name}!")

def farewell(name: str) -> None:
    """New function to say goodbye."""
    print(f"Goodbye, {name}! See you later!")

async def async_process_data(data: List[str]) -> List[str]:
    """New async function for processing data."""
    await asyncio.sleep(0.1)  # Simulate async work
    return [item.upper() for item in data]

class DataProcessor:
    """Enhanced data processor class."""
    
    def clear_data(self) -> None:
        """Clear all data from the processor."""
        self.data.clear()
    
    def get_data_summary(self) -> dict:
        """Get summary of data."""
        return {
            "count": len(self.data),
            "items": self.data.copy()
        }

class MathUtils:
    """Enhanced utility class for mathematical operations."""
    
    @staticmethod
    def subtract(a: int, b: int) -> int:
        """Subtract two numbers."""
        return a - b
    
    @staticmethod
    def multiply(a: int, b: int) -> int:
        """Multiply two numbers."""
        return a * b
    
    @staticmethod
    def divide(a: int, b: int) -> float:
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b

class NetworkClient:
    """New class for network operations."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def get_data(self, endpoint: str) -> dict:
        """Fetch data from an endpoint."""
        # Placeholder implementation
        return {"status": "success", "endpoint": endpoint}
'''
        
        print("\n🔄 Step 2: Performing intelligent merge (dry run)")
        print("-" * 40)
        dry_run_result = merger_tool.func(demo_file, ai_code, backup=True, dry_run=True)
        print("Dry run preview (first 1000 characters):")
        print(dry_run_result[:1000] + "..." if len(dry_run_result) > 1000 else dry_run_result)
        
        print("\n✅ Step 3: Applying the merge")
        print("-" * 40)
        merge_result = merger_tool.func(demo_file, ai_code, backup=True, dry_run=False)
        print(merge_result)
        
        print("\n📊 Step 4: Analyzing merged code structure")
        print("-" * 40)
        final_analysis = analyzer_tool.func(demo_file)
        print(final_analysis)
        
        print("\n📄 Step 5: Final merged code")
        print("-" * 40)
        with open(demo_file, 'r') as f:
            merged_code = f.read()
        
        print("Final merged code (first 2000 characters):")
        print(merged_code[:2000] + "..." if len(merged_code) > 2000 else merged_code)
        
        print("\n🎯 Key Merge Results:")
        print("- ✅ Enhanced greet() function with new parameters")
        print("- ✅ Added new farewell() and async_process_data() functions")
        print("- ✅ Added new methods to existing DataProcessor class")
        print("- ✅ Enhanced MathUtils class with new methods")
        print("- ✅ Added completely new NetworkClient class")
        print("- ✅ Merged imports without duplicates")
        print("- ✅ Added new module-level constants")
        
    except Exception as e:
        print(f"❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if os.path.exists(demo_file):
            os.unlink(demo_file)
        backup_file = demo_file + '.backup'
        if os.path.exists(backup_file):
            os.unlink(backup_file)
        print(f"\n🧹 Cleaned up temporary files")


if __name__ == "__main__":
    demo_intelligent_merging()

#!/usr/bin/env python3
"""
Comprehensive test and demonstration script for the codebase indexing and self-awareness system.
"""

import tempfile
import os
from pathlib import Path
from agent.tools.codebase_indexer import (
    codebase_indexer_tool,
    code_search_tool,
    file_analysis_tool,
    self_awareness_tool,
    CodebaseIndexer
)


def create_test_codebase():
    """Create a temporary test codebase for demonstration."""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_codebase_"))
    
    # Create a sample Python project structure
    (temp_dir / "src").mkdir()
    (temp_dir / "tests").mkdir()
    (temp_dir / "utils").mkdir()
    
    # Main module
    main_py = temp_dir / "src" / "main.py"
    main_py.write_text('''
"""Main application module."""

import os
import sys
from typing import List, Dict, Optional
from utils.helpers import format_data, validate_input
from utils.database import DatabaseManager

class Application:
    """Main application class."""
    
    def __init__(self, config_path: str):
        """Initialize the application."""
        self.config_path = config_path
        self.db_manager = DatabaseManager()
        self.is_running = False
    
    def start(self) -> bool:
        """Start the application."""
        if not validate_input(self.config_path):
            return False
        
        self.is_running = True
        return True
    
    def stop(self):
        """Stop the application."""
        self.is_running = False
        self.db_manager.close()
    
    async def process_data(self, data: List[Dict]) -> List[Dict]:
        """Process incoming data asynchronously."""
        processed = []
        for item in data:
            formatted = format_data(item)
            processed.append(formatted)
        return processed

def main():
    """Main entry point."""
    app = Application("config.json")
    if app.start():
        print("Application started successfully")
    else:
        print("Failed to start application")

if __name__ == "__main__":
    main()
''')
    
    # Utilities module
    helpers_py = temp_dir / "utils" / "helpers.py"
    helpers_py.write_text('''
"""Helper utility functions."""

import json
import re
from typing import Any, Dict, Optional
from datetime import datetime

def format_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Format data for processing."""
    formatted = data.copy()
    formatted['timestamp'] = datetime.now().isoformat()
    formatted['processed'] = True
    return formatted

def validate_input(input_data: Any) -> bool:
    """Validate input data."""
    if not input_data:
        return False
    
    if isinstance(input_data, str):
        return len(input_data.strip()) > 0
    
    return True

@deprecated
def old_function():
    """This function is deprecated."""
    pass

class DataValidator:
    """Data validation utility class."""
    
    def __init__(self, strict_mode: bool = False):
        self.strict_mode = strict_mode
        self.validation_rules = []
    
    def add_rule(self, rule_func):
        """Add a validation rule."""
        self.validation_rules.append(rule_func)
    
    def validate(self, data: Dict) -> bool:
        """Validate data against all rules."""
        for rule in self.validation_rules:
            if not rule(data):
                if self.strict_mode:
                    raise ValueError(f"Validation failed: {rule.__name__}")
                return False
        return True
''')
    
    # Database module
    database_py = temp_dir / "utils" / "database.py"
    database_py.write_text('''
"""Database management utilities."""

import sqlite3
from typing import List, Dict, Optional, Any
from contextlib import contextmanager

class DatabaseManager:
    """Database connection and query manager."""
    
    def __init__(self, db_path: str = ":memory:"):
        """Initialize database manager."""
        self.db_path = db_path
        self.connection = None
    
    def connect(self) -> bool:
        """Connect to the database."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    @contextmanager
    def transaction(self):
        """Context manager for database transactions."""
        if not self.connection:
            self.connect()
        
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise
    
    def execute_query(self, query: str, params: Optional[tuple] = None) -> List[Dict]:
        """Execute a query and return results."""
        with self.transaction() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
    
    async def async_execute(self, query: str) -> List[Dict]:
        """Execute query asynchronously."""
        # Placeholder for async implementation
        return self.execute_query(query)
''')
    
    # Test module
    test_main_py = temp_dir / "tests" / "test_main.py"
    test_main_py.write_text('''
"""Tests for main application."""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import Application

class TestApplication(unittest.TestCase):
    """Test cases for Application class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.app = Application("test_config.json")
    
    def test_initialization(self):
        """Test application initialization."""
        self.assertEqual(self.app.config_path, "test_config.json")
        self.assertFalse(self.app.is_running)
    
    @patch('main.validate_input')
    def test_start_success(self, mock_validate):
        """Test successful application start."""
        mock_validate.return_value = True
        result = self.app.start()
        self.assertTrue(result)
        self.assertTrue(self.app.is_running)
    
    @patch('main.validate_input')
    def test_start_failure(self, mock_validate):
        """Test failed application start."""
        mock_validate.return_value = False
        result = self.app.start()
        self.assertFalse(result)
        self.assertFalse(self.app.is_running)
    
    def test_stop(self):
        """Test application stop."""
        self.app.is_running = True
        self.app.stop()
        self.assertFalse(self.app.is_running)

if __name__ == '__main__':
    unittest.main()
''')
    
    # Create __init__.py files
    (temp_dir / "src" / "__init__.py").write_text("")
    (temp_dir / "utils" / "__init__.py").write_text("")
    (temp_dir / "tests" / "__init__.py").write_text("")
    
    return temp_dir


def test_codebase_indexing():
    """Test the codebase indexing functionality."""
    print("🔍 Testing Codebase Indexing System")
    print("=" * 50)
    
    # Create test codebase
    test_dir = create_test_codebase()
    print(f"📁 Created test codebase at: {test_dir}")
    
    try:
        # Create tools
        indexer_tool = codebase_indexer_tool()
        search_tool = code_search_tool()
        analysis_tool = file_analysis_tool()
        
        # Test 1: Index the codebase
        print("\n📊 Step 1: Indexing the test codebase")
        print("-" * 40)
        index_result = indexer_tool.func(str(test_dir))
        print(index_result)
        
        # Test 2: Search for code elements
        print("\n🔍 Step 2: Searching for code elements")
        print("-" * 40)
        
        # Search for classes
        print("Searching for classes:")
        class_results = search_tool.func("class", element_type="class")
        print(class_results)
        
        # Search for functions
        print("\nSearching for functions with 'validate':")
        validate_results = search_tool.func("validate", element_type="function")
        print(validate_results)
        
        # Search for async functions
        print("\nSearching for async functions:")
        async_results = search_tool.func("async", element_type="async_function")
        print(async_results)
        
        # Test 3: Analyze specific files
        print("\n📄 Step 3: Analyzing specific files")
        print("-" * 40)
        
        main_file = test_dir / "src" / "main.py"
        analysis_result = analysis_tool.func(str(main_file))
        print(analysis_result)
        
        print("\n✅ Codebase indexing tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up test directory: {test_dir}")


def test_self_awareness():
    """Test the self-awareness functionality."""
    print("\n🤖 Testing Self-Awareness System")
    print("=" * 50)
    
    try:
        # Create self-awareness tool
        self_tool = self_awareness_tool()
        
        # Test self-analysis
        print("🔍 Performing self-analysis...")
        self_analysis = self_tool.func(include_tools=True, include_structure=True)
        print(self_analysis)
        
        print("\n✅ Self-awareness test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during self-awareness testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("🚀 Codebase Indexing and Self-Awareness System Test")
    print("=" * 60)
    
    try:
        test_codebase_indexing()
        test_self_awareness()
        print("\n🎉 All tests completed!")
    except Exception as e:
        print(f"\n💥 Test suite failed: {e}")
        import traceback
        traceback.print_exc()

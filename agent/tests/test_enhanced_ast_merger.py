#!/usr/bin/env python3
"""
Test script for the enhanced AST-based code merger with codebase indexer integration.
This demonstrates the intelligent merging capabilities with reference resolution.
"""

import tempfile
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agent.tools.code_tools import enhanced_ast_code_merger_tool, ast_code_merger_tool


def test_enhanced_merger_with_indexer():
    """Test the enhanced AST merger with codebase indexer integration."""
    
    print("🧪 Testing Enhanced AST Code Merger with Codebase Indexer")
    print("=" * 60)
    
    # Create temporary directory for test files
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create a test module with dependencies
        main_file = temp_path / "main_module.py"
        main_file.write_text('''
"""Main module for testing enhanced merger."""

import os
import sys
from typing import List, Dict

def process_data(data: List[str]) -> Dict[str, int]:
    """Process a list of strings and return counts."""
    result = {}
    for item in data:
        result[item] = len(item)
    return result

class DataProcessor:
    """A class for processing data."""
    
    def __init__(self, name: str):
        self.name = name
        self.processed_count = 0
    
    def process(self, data: str) -> str:
        """Process a single data item."""
        self.processed_count += 1
        return data.upper()
''')
        
        # Create a dependent file
        utils_file = temp_path / "utils.py"
        utils_file.write_text('''
"""Utility functions that depend on main_module."""

from main_module import process_data, DataProcessor

def analyze_data(data_list):
    """Analyze data using main_module functions."""
    counts = process_data(data_list)
    processor = DataProcessor("analyzer")
    
    results = []
    for item in data_list:
        processed = processor.process(item)
        results.append(processed)
    
    return counts, results
''')
        
        # AI-generated code to merge
        ai_code = '''
import json
from pathlib import Path

def process_data(data: List[str], include_empty: bool = False) -> Dict[str, int]:
    """Enhanced process function with empty string handling."""
    result = {}
    for item in data:
        if not include_empty and not item.strip():
            continue
        result[item] = len(item)
    return result

def save_results(data: Dict[str, int], output_path: str) -> bool:
    """Save processing results to a JSON file."""
    try:
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving results: {e}")
        return False

class DataProcessor:
    """Enhanced data processor with logging."""
    
    def __init__(self, name: str, log_enabled: bool = True):
        self.name = name
        self.processed_count = 0
        self.log_enabled = log_enabled
        self.processing_history = []
    
    def process(self, data: str) -> str:
        """Process a single data item with logging."""
        self.processed_count += 1
        result = data.upper()
        
        if self.log_enabled:
            self.processing_history.append({
                'input': data,
                'output': result,
                'timestamp': self.processed_count
            })
        
        return result
    
    def get_stats(self) -> Dict[str, any]:
        """Get processing statistics."""
        return {
            'name': self.name,
            'processed_count': self.processed_count,
            'history_length': len(self.processing_history)
        }
'''
        
        print(f"📁 Created test files in: {temp_dir}")
        print(f"   - main_module.py ({main_file.stat().st_size} bytes)")
        print(f"   - utils.py ({utils_file.stat().st_size} bytes)")
        print()
        
        # Test 1: Basic enhanced merger
        print("🔧 Test 1: Enhanced Merger with Indexer Integration")
        print("-" * 50)
        
        try:
            enhanced_tool = enhanced_ast_code_merger_tool()
            result = enhanced_tool.func(
                file_path=str(main_file),
                ai_generated_code=ai_code,
                backup=True,
                dry_run=True,  # Don't actually modify for this test
                force_index_update=True
            )
            
            print("✅ Enhanced merger result:")
            print(result)
            print()
            
        except Exception as e:
            print(f"❌ Enhanced merger failed: {e}")
            print()
        
        # Test 2: Compare with basic merger
        print("🔧 Test 2: Comparison with Basic Merger")
        print("-" * 50)
        
        try:
            basic_tool = ast_code_merger_tool()
            basic_result = basic_tool.func(
                file_path=str(main_file),
                ai_generated_code=ai_code,
                backup=True,
                dry_run=True,
                use_indexer=False  # Disable indexer for comparison
            )
            
            print("📊 Basic merger result:")
            print(basic_result)
            print()
            
        except Exception as e:
            print(f"❌ Basic merger failed: {e}")
            print()
        
        # Test 3: Actual merge with enhanced features
        print("🔧 Test 3: Actual Enhanced Merge")
        print("-" * 50)
        
        try:
            enhanced_tool = enhanced_ast_code_merger_tool()
            actual_result = enhanced_tool.func(
                file_path=str(main_file),
                ai_generated_code=ai_code,
                backup=True,
                dry_run=False,  # Actually perform the merge
                force_index_update=True
            )
            
            print("✅ Actual merge completed:")
            print(actual_result)
            print()
            
            # Show the merged file content (first 20 lines)
            print("📄 Merged file preview (first 20 lines):")
            with open(main_file, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines[:20], 1):
                    print(f"{i:2d}: {line.rstrip()}")
                if len(lines) > 20:
                    print(f"... and {len(lines) - 20} more lines")
            print()
            
        except Exception as e:
            print(f"❌ Actual merge failed: {e}")
            print()


def test_indexer_integration():
    """Test the indexer integration specifically."""
    print("🔍 Testing Codebase Indexer Integration")
    print("=" * 40)
    
    try:
        from agent.tools.codebase_indexer import get_global_indexer
        
        indexer = get_global_indexer()
        print("✅ Indexer initialized successfully")
        
        # Test indexing current project
        project_root = Path(__file__).parent.parent
        stats = indexer.index_codebase(project_root)
        print(f"✅ Indexed project: {stats}")
        
        # Test search functionality
        search_results = indexer.search_code_elements("merge", element_type="function")
        print(f"✅ Found {len(search_results)} functions with 'merge' in name/docs")
        
        for result in search_results[:3]:  # Show first 3
            print(f"   - {result.name} in {result.file_path}:{result.line_number}")
        
    except Exception as e:
        print(f"❌ Indexer integration test failed: {e}")
    
    print()


if __name__ == "__main__":
    print("🚀 Enhanced AST Code Merger Test Suite")
    print("=" * 50)
    print()
    
    # Test indexer integration first
    test_indexer_integration()
    
    # Test enhanced merger
    test_enhanced_merger_with_indexer()
    
    print("🎉 Test suite completed!")

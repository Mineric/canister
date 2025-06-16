#!/usr/bin/env python3
"""
Test script to isolate import issues.
"""

import sys
import time

def test_import(module_name, import_statement, timeout=10):
    """Test a specific import and measure time with timeout."""
    print(f"Testing: {module_name}")
    start_time = time.time()

    try:
        # Use timeout to prevent hanging
        import signal

        def timeout_handler(signum, frame):
            raise TimeoutError(f"Import timed out after {timeout}s")

        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(timeout)

        try:
            exec(import_statement)
            signal.alarm(0)  # Cancel alarm
            end_time = time.time()
            print(f"✅ {module_name} - Success ({end_time - start_time:.2f}s)")
            return True
        except TimeoutError as e:
            end_time = time.time()
            print(f"⏰ {module_name} - Timeout ({end_time - start_time:.2f}s): {e}")
            return False
        finally:
            signal.alarm(0)  # Ensure alarm is cancelled

    except Exception as e:
        end_time = time.time()
        print(f"❌ {module_name} - Failed ({end_time - start_time:.2f}s): {e}")
        return False

def main():
    """Run import tests."""
    print("🧪 Testing imports to identify hanging issue...")
    print("=" * 50)
    
    tests = [
        ("Standard library", "import os, sys, json"),
        ("Google ADK base", "from google.adk.tools import FunctionTool"),
        ("Google ADK agents", "from google.adk.agents import LlmAgent"),
        ("Google ADK models", "from google.adk.models.lite_llm import LiteLlm"),
        ("Basic tools", "from agent.tools.tools import get_current_time_tool"),
        ("Code tools", "from agent.tools.code_tools import ast_code_merger_tool"),
        ("Codebase indexer", "from agent.tools.codebase_indexer import codebase_indexer_tool"),
        ("Agent creation", "from agent.agent import create_agent"),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, import_stmt in tests:
        if test_import(name, import_stmt):
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed}/{total} imports successful")
    
    if passed < total:
        print("⚠️  Some imports failed - this may explain the terminal issue")
    else:
        print("✅ All imports successful - issue may be elsewhere")

if __name__ == "__main__":
    main()

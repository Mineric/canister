#!/usr/bin/env python3
"""
Comprehensive test runner for Cannister Agent.

This script runs all tests in the test suite and provides detailed reporting.
"""

import sys
import unittest
import time
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class ColoredTestResult(unittest.TextTestResult):
    """Test result with colored output."""
    
    def addSuccess(self, test):
        super().addSuccess(test)
        if self.showAll:
            self.stream.writeln("✅ PASS")
        elif self.dots:
            self.stream.write("✅")
            self.stream.flush()

    def addError(self, test, err):
        super().addError(test, err)
        if self.showAll:
            self.stream.writeln("❌ ERROR")
        elif self.dots:
            self.stream.write("❌")
            self.stream.flush()

    def addFailure(self, test, err):
        super().addFailure(test, err)
        if self.showAll:
            self.stream.writeln("❌ FAIL")
        elif self.dots:
            self.stream.write("❌")
            self.stream.flush()

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        if self.showAll:
            self.stream.writeln("⏭️ SKIP")
        elif self.dots:
            self.stream.write("⏭️")
            self.stream.flush()


def discover_tests():
    """Discover all test files in the tests directory."""
    test_dir = Path(__file__).parent
    loader = unittest.TestLoader()
    
    # Discover tests in the current directory
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    return suite


def run_tests(verbosity=2):
    """Run all tests with colored output."""
    print("🧪 Cannister Agent Test Suite")
    print("=" * 50)
    
    # Discover tests
    suite = discover_tests()
    
    # Create test runner with colored results
    runner = unittest.TextTestRunner(
        verbosity=verbosity,
        resultclass=ColoredTestResult,
        stream=sys.stdout
    )
    
    # Run tests
    start_time = time.time()
    result = runner.run(suite)
    end_time = time.time()
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Skipped: {len(result.skipped)}")
    print(f"   Time: {end_time - start_time:.2f}s")
    
    if result.wasSuccessful():
        print("🎉 All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Cannister Agent tests")
    parser.add_argument("-v", "--verbose", action="store_true", 
                       help="Verbose output")
    parser.add_argument("-q", "--quiet", action="store_true",
                       help="Quiet output")
    
    args = parser.parse_args()
    
    if args.quiet:
        verbosity = 0
    elif args.verbose:
        verbosity = 2
    else:
        verbosity = 1
    
    sys.exit(run_tests(verbosity))

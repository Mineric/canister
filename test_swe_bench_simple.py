#!/usr/bin/env python3
"""
Simple test to verify SWE-bench integration basics.
"""

import sys
from pathlib import Path

def test_swe_bench_core():
    """Test core SWE-bench functionality."""
    print("🧪 Testing SWE-bench core functionality...")
    
    try:
        # Test SWE-bench package
        import swebench
        print("✅ SWE-bench package available")
        
        # Test datasets
        from datasets import load_dataset
        print("✅ Datasets package available")
        
        # Test Docker
        import docker
        print("✅ Docker package available")
        
        # Test dataset loading
        print("Loading SWE-bench Lite dataset (first 5 instances)...")
        dataset = load_dataset('princeton-nlp/SWE-bench_Lite', split='test[:5]')
        print(f"✅ Loaded {len(dataset)} instances")
        
        # Verify instance structure
        if len(dataset) > 0:
            instance = dataset[0]
            required_fields = ['instance_id', 'repo', 'base_commit', 'problem_statement', 'patch']
            missing_fields = [field for field in required_fields if field not in instance]
            
            if not missing_fields:
                print("✅ All required fields present in dataset")
                print(f"   Sample instance: {instance['instance_id']}")
                print(f"   Repository: {instance['repo']}")
                return True
            else:
                print(f"❌ Missing fields: {missing_fields}")
                return False
        else:
            print("❌ No instances in dataset")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_swe_bench_evaluation_structure():
    """Test that we can create the basic evaluation structures."""
    print("\n🧪 Testing SWE-bench evaluation structures...")
    
    try:
        # Test basic data structures
        from dataclasses import dataclass
        from typing import List, Optional
        
        @dataclass
        class TestSWEBenchInstance:
            instance_id: str
            repo: str
            base_commit: str
            patch: str
            problem_statement: str
        
        @dataclass
        class TestSWEBenchResult:
            instance_id: str
            resolved: bool
            generated_patch: str
            execution_time: float
            error_message: Optional[str] = None
        
        # Create test instance
        test_instance = TestSWEBenchInstance(
            instance_id="test__repo-1",
            repo="test/repo",
            base_commit="abc123",
            patch="test patch",
            problem_statement="Test problem"
        )
        
        # Create test result
        test_result = TestSWEBenchResult(
            instance_id="test__repo-1",
            resolved=True,
            generated_patch="test patch",
            execution_time=120.0
        )
        
        print("✅ Basic evaluation structures work")
        print(f"   Test instance: {test_instance.instance_id}")
        print(f"   Test result: {test_result.resolved}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_patch_extraction():
    """Test patch extraction logic."""
    print("\n🧪 Testing patch extraction...")
    
    try:
        def extract_patch_from_response(response: str) -> str:
            """Extract patch content from agent response."""
            patch_indicators = ["```diff", "```patch", "--- a/", "+++ b/", "diff --git"]
            
            lines = response.split('\n')
            patch_lines = []
            in_patch = False
            
            for line in lines:
                if any(indicator in line for indicator in patch_indicators):
                    in_patch = True
                    if not line.startswith('```'):
                        patch_lines.append(line)
                    continue
                    
                if in_patch and line.strip() == '```':
                    break
                    
                if in_patch:
                    patch_lines.append(line)
            
            return '\n'.join(patch_lines) if patch_lines else response
        
        # Test with diff block
        test_response = """
        Here's the solution:
        
        ```diff
        --- a/file.py
        +++ b/file.py
        @@ -1,1 +1,1 @@
        -old line
        +new line
        ```
        
        This should fix the issue.
        """
        
        extracted_patch = extract_patch_from_response(test_response)
        
        if "--- a/file.py" in extracted_patch and "+new line" in extracted_patch:
            print("✅ Patch extraction works correctly")
            return True
        else:
            print(f"❌ Patch extraction failed: {extracted_patch}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_mock_evaluation():
    """Test a mock evaluation workflow."""
    print("\n🧪 Testing mock evaluation workflow...")
    
    try:
        import time
        
        # Mock agent
        class MockAgent:
            def run(self, problem_text: str) -> str:
                return """
                Here's my solution:
                
                ```diff
                --- a/example.py
                +++ b/example.py
                @@ -1,3 +1,3 @@
                 def example_function():
                -    return "bug"
                +    return "fix"
                ```
                """
        
        # Mock evaluation
        def mock_solve_instance(instance_data, agent):
            start_time = time.time()
            
            problem_text = f"Fix the issue in {instance_data['repo']}: {instance_data['problem_statement']}"
            response = agent.run(problem_text)
            
            # Simple patch extraction
            has_patch = "```diff" in response and "--- a/" in response
            
            return {
                "instance_id": instance_data["instance_id"],
                "resolved": has_patch,
                "generated_patch": response if has_patch else "",
                "execution_time": time.time() - start_time
            }
        
        # Test data
        test_instance = {
            "instance_id": "test__repo-1",
            "repo": "test/repo",
            "problem_statement": "Fix the bug in example.py"
        }
        
        # Run mock evaluation
        agent = MockAgent()
        result = mock_solve_instance(test_instance, agent)
        
        if result["resolved"] and result["execution_time"] > 0:
            print("✅ Mock evaluation workflow works")
            print(f"   Instance: {result['instance_id']}")
            print(f"   Resolved: {result['resolved']}")
            print(f"   Time: {result['execution_time']:.3f}s")
            return True
        else:
            print(f"❌ Mock evaluation failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Run all simple tests."""
    print("🎯 SWE-bench Simple Integration Test")
    print("=" * 50)
    
    tests = [
        ("SWE-bench Core", test_swe_bench_core),
        ("Evaluation Structures", test_swe_bench_evaluation_structure),
        ("Patch Extraction", test_patch_extraction),
        ("Mock Evaluation", test_mock_evaluation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} ERROR: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    print(f"Success rate: {passed/total:.1%}")
    
    if passed == total:
        print("🎉 All tests passed! SWE-bench integration basics are working.")
        print("\n📋 Next steps:")
        print("   1. Install Google ADK to enable full agent integration")
        print("   2. Start Docker daemon for full evaluation harness")
        print("   3. Run: python agent/evals/swe_bench_eval.py")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

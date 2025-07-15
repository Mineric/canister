#!/usr/bin/env python3
"""
Basic test for SWE-bench integration without requiring full agent setup.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_swe_bench_imports():
    """Test that SWE-bench related modules can be imported."""
    print("🧪 Testing SWE-bench imports...")
    
    try:
        # Test basic imports
        import swebench
        print("✅ swebench package imported successfully")
        
        from datasets import load_dataset
        print("✅ datasets package imported successfully")
        
        import docker
        print("✅ docker package imported successfully")
        
        # Test our SWE-bench modules (without agent dependency)
        try:
            from agent.evals.swe_bench_config import (
                EvaluationConfiguration, SWEBenchConfigurationManager,
                SWEBenchDataset, EvaluationMode, DifficultyLevel
            )
            print("✅ SWE-bench configuration modules imported successfully")
        except ImportError as e:
            print(f"⚠️ SWE-bench configuration import issue: {e}")

        try:
            from agent.evals.swe_bench_metrics import (
                SWEBenchMetricsCollector, SWEBenchMetric
            )
            print("✅ SWE-bench metrics modules imported successfully")
        except ImportError as e:
            print(f"⚠️ SWE-bench metrics import issue: {e}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_swe_bench_dataset_access():
    """Test that we can access SWE-bench datasets."""
    print("\n🧪 Testing SWE-bench dataset access...")
    
    try:
        from datasets import load_dataset
        
        # Test loading a small subset
        print("Loading SWE-bench Lite dataset...")
        dataset = load_dataset('princeton-nlp/SWE-bench_Lite', split='test')
        
        print(f"✅ Dataset loaded successfully: {len(dataset)} instances")
        
        # Test accessing first instance
        if len(dataset) > 0:
            first_instance = dataset[0]
            required_fields = ['instance_id', 'repo', 'base_commit', 'problem_statement']
            
            for field in required_fields:
                if field in first_instance:
                    print(f"✅ Field '{field}' present")
                else:
                    print(f"❌ Field '{field}' missing")
                    return False
        
        return True
        
    except Exception as e:
        print(f"❌ Dataset access error: {e}")
        return False

def test_configuration_system():
    """Test the configuration system."""
    print("\n🧪 Testing configuration system...")
    
    try:
        from agent.evals.swe_bench_config import (
            SWEBenchConfigurationManager, create_evaluation_config,
            SWEBenchDataset, EvaluationMode
        )
        
        # Test configuration manager
        config_manager = SWEBenchConfigurationManager()
        print("✅ Configuration manager created")
        
        # Test preset configurations
        presets = config_manager.list_available_configs()["presets"]
        print(f"✅ Available presets: {presets}")
        
        # Test getting a preset
        quick_config = config_manager.get_preset_config("quick_test")
        print(f"✅ Quick test config: {quick_config.max_instances} instances")
        
        # Test custom configuration
        custom_config = create_evaluation_config(
            preset="development",
            max_instances=10,
            timeout_per_instance=600
        )
        print(f"✅ Custom config created: {custom_config.max_instances} instances")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration system error: {e}")
        return False

def test_metrics_system():
    """Test the metrics collection system."""
    print("\n🧪 Testing metrics system...")
    
    try:
        from agent.evals.swe_bench_metrics import SWEBenchMetricsCollector
        from agent.evals.swe_bench_eval import SWEBenchResult
        
        # Create metrics collector
        collector = SWEBenchMetricsCollector()
        print("✅ Metrics collector created")
        
        # Create sample results
        sample_results = [
            SWEBenchResult(
                instance_id="test__repo-1",
                resolved=True,
                generated_patch="test patch",
                execution_time=120.0
            ),
            SWEBenchResult(
                instance_id="test__repo-2",
                resolved=False,
                generated_patch="",
                execution_time=300.0,
                error_message="Test error"
            )
        ]
        
        # Test metrics calculation
        metrics = collector.calculate_overall_metrics(sample_results, "princeton-nlp/SWE-bench_Lite")
        print(f"✅ Calculated {len(metrics)} metrics")
        
        # Test repository analysis
        repo_metrics = collector.analyze_repository_performance(sample_results)
        print(f"✅ Analyzed {len(repo_metrics)} repositories")
        
        return True
        
    except Exception as e:
        print(f"❌ Metrics system error: {e}")
        return False

def test_docker_availability():
    """Test Docker availability for SWE-bench evaluation."""
    print("\n🧪 Testing Docker availability...")
    
    try:
        import subprocess
        
        # Check if Docker is installed and running
        result = subprocess.run(['docker', '--version'], 
                              capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print(f"✅ Docker available: {result.stdout.strip()}")
            
            # Test Docker daemon
            result = subprocess.run(['docker', 'info'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Docker daemon running")
                return True
            else:
                print("⚠️ Docker installed but daemon not running")
                return False
        else:
            print("⚠️ Docker not available")
            return False
            
    except subprocess.TimeoutExpired:
        print("⚠️ Docker command timed out")
        return False
    except Exception as e:
        print(f"⚠️ Docker check error: {e}")
        return False

def main():
    """Run all basic tests."""
    print("🎯 SWE-bench Integration Basic Tests")
    print("=" * 50)
    
    tests = [
        ("SWE-bench Imports", test_swe_bench_imports),
        ("Dataset Access", test_swe_bench_dataset_access),
        ("Configuration System", test_configuration_system),
        ("Metrics System", test_metrics_system),
        ("Docker Availability", test_docker_availability),
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
        print("🎉 All tests passed! SWE-bench integration is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

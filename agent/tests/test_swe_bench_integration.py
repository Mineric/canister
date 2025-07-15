#!/usr/bin/env python3
"""
Tests for SWE-bench integration with Canister Agent.

This module contains comprehensive tests to verify that the SWE-bench
integration works correctly.
"""

import os
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
import sys
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agent.evals.swe_bench_eval import (
    SWEBenchInstance, SWEBenchResult, SWEBenchAgentInterface, 
    SWEBenchEvaluator, SWEBenchEvaluationReport
)
from agent.evals.swe_bench_config import (
    EvaluationConfiguration, SWEBenchConfigurationManager,
    SWEBenchDataset, EvaluationMode, DifficultyLevel
)
from agent.evals.swe_bench_metrics import (
    SWEBenchMetricsCollector, SWEBenchMetric, ComprehensiveMetricsReport
)


class TestSWEBenchInstance(unittest.TestCase):
    """Test SWE-bench instance data structure."""
    
    def setUp(self):
        """Set up test instance."""
        self.instance = SWEBenchInstance(
            instance_id="test__repo-123",
            repo="test/repo",
            base_commit="abc123",
            patch="--- a/file.py\n+++ b/file.py\n@@ -1,1 +1,1 @@\n-old\n+new",
            test_patch="test patch content",
            problem_statement="Fix the bug in file.py",
            hints_text="Look at line 1",
            created_at="2024-01-01",
            version="1.0",
            FAIL_TO_PASS=["test_function"],
            PASS_TO_PASS=["test_other"]
        )
    
    def test_instance_creation(self):
        """Test instance creation and attributes."""
        self.assertEqual(self.instance.instance_id, "test__repo-123")
        self.assertEqual(self.instance.repo, "test/repo")
        self.assertEqual(self.instance.base_commit, "abc123")
        self.assertIn("Fix the bug", self.instance.problem_statement)


class TestSWEBenchAgentInterface(unittest.TestCase):
    """Test agent interface for SWE-bench."""
    
    def setUp(self):
        """Set up test interface."""
        self.mock_agent = Mock()
        self.interface = SWEBenchAgentInterface(self.mock_agent)
        
        self.test_instance = SWEBenchInstance(
            instance_id="test__repo-123",
            repo="test/repo",
            base_commit="abc123",
            patch="test patch",
            test_patch="test patch",
            problem_statement="Test problem",
            hints_text="Test hints",
            created_at="2024-01-01",
            version="1.0",
            FAIL_TO_PASS=["test_function"],
            PASS_TO_PASS=["test_other"]
        )
    
    def test_format_problem_for_agent(self):
        """Test problem formatting for agent."""
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_path = Path(temp_dir)
            formatted = self.interface.format_problem_for_agent(self.test_instance, repo_path)
            
            self.assertIn("Software Engineering Task", formatted)
            self.assertIn("test/repo", formatted)
            self.assertIn("Test problem", formatted)
            self.assertIn("abc123", formatted)
    
    def test_extract_patch_from_response(self):
        """Test patch extraction from agent response."""
        # Test with diff block
        response_with_diff = """
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
        
        patch = self.interface.extract_patch_from_response(response_with_diff)
        self.assertIn("--- a/file.py", patch)
        self.assertIn("+++ b/file.py", patch)
        self.assertIn("-old line", patch)
        self.assertIn("+new line", patch)
    
    @patch('subprocess.run')
    @patch('tempfile.mkdtemp')
    def test_setup_workspace(self, mock_mkdtemp, mock_subprocess):
        """Test workspace setup."""
        mock_mkdtemp.return_value = "/tmp/test_workspace"
        mock_subprocess.return_value = Mock(returncode=0)
        
        # Mock Path.exists() to return True
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.mkdir'):
                repo_path = self.interface.setup_workspace(self.test_instance)
                
                # Verify git commands were called
                self.assertTrue(mock_subprocess.called)
                self.assertIsInstance(repo_path, Path)
    
    @patch.object(SWEBenchAgentInterface, 'setup_workspace')
    @patch.object(SWEBenchAgentInterface, 'cleanup_workspace')
    def test_solve_instance(self, mock_cleanup, mock_setup):
        """Test solving an instance."""
        # Mock workspace setup
        mock_setup.return_value = Path("/tmp/test_repo")
        
        # Mock agent response
        self.mock_agent.run.return_value = """
        Here's the fix:
        ```diff
        --- a/file.py
        +++ b/file.py
        @@ -1,1 +1,1 @@
        -bug
        +fix
        ```
        """
        
        result = self.interface.solve_instance(self.test_instance)
        
        self.assertIsInstance(result, SWEBenchResult)
        self.assertEqual(result.instance_id, "test__repo-123")
        self.assertTrue(result.resolved)  # Should be True since patch was generated
        self.assertIn("--- a/file.py", result.generated_patch)
        self.assertGreater(result.execution_time, 0)
        
        # Verify cleanup was called
        mock_cleanup.assert_called_once()


class TestSWEBenchConfiguration(unittest.TestCase):
    """Test SWE-bench configuration management."""
    
    def setUp(self):
        """Set up configuration manager."""
        self.config_manager = SWEBenchConfigurationManager()
    
    def test_preset_configurations(self):
        """Test preset configurations."""
        presets = self.config_manager.list_available_configs()["presets"]
        
        self.assertIn("quick_test", presets)
        self.assertIn("development", presets)
        self.assertIn("lite_benchmark", presets)
        
        # Test getting a preset
        config = self.config_manager.get_preset_config("quick_test")
        self.assertEqual(config.dataset, SWEBenchDataset.LITE)
        self.assertEqual(config.max_instances, 5)
        self.assertEqual(config.mode, EvaluationMode.QUICK_TEST)
    
    def test_custom_configuration(self):
        """Test custom configuration creation."""
        custom_config = self.config_manager.create_custom_config(
            base_preset="development",
            max_instances=10,
            timeout_per_instance=600
        )
        
        self.assertEqual(custom_config.max_instances, 10)
        self.assertEqual(custom_config.timeout_per_instance, 600)
        self.assertEqual(custom_config.dataset, SWEBenchDataset.LITE)  # From base preset
    
    def test_difficulty_filtering(self):
        """Test difficulty-based instance filtering."""
        # Mock instances
        instances = [
            {"instance_id": "easy__1", "repo": "simple/repo", "problem_statement": "Simple fix"},
            {"instance_id": "hard__1", "repo": "complex/repo", "problem_statement": "Complex issue with multiple components"},
            {"instance_id": "medium__1", "repo": "medium/repo", "problem_statement": "Moderate complexity"}
        ]
        
        # Test filtering
        easy_instances = self.config_manager.filter_instances_by_difficulty(instances, DifficultyLevel.EASY)
        hard_instances = self.config_manager.filter_instances_by_difficulty(instances, DifficultyLevel.HARD)
        
        self.assertLessEqual(len(easy_instances), len(instances))
        self.assertLessEqual(len(hard_instances), len(instances))
    
    def test_configuration_validation(self):
        """Test configuration validation."""
        # Valid configuration
        valid_config = EvaluationConfiguration(max_instances=10, timeout_per_instance=600)
        warnings = self.config_manager.validate_config(valid_config)
        self.assertEqual(len(warnings), 0)
        
        # Configuration with warnings
        warning_config = EvaluationConfiguration(max_instances=2000, timeout_per_instance=60)
        warnings = self.config_manager.validate_config(warning_config)
        self.assertGreater(len(warnings), 0)


class TestSWEBenchMetrics(unittest.TestCase):
    """Test SWE-bench metrics collection."""
    
    def setUp(self):
        """Set up metrics collector."""
        self.metrics_collector = SWEBenchMetricsCollector()
        
        # Create sample results
        self.sample_results = [
            SWEBenchResult(
                instance_id="repo1__issue1",
                resolved=True,
                generated_patch="--- a/file.py\n+++ b/file.py\n@@ -1,1 +1,1 @@\n-old\n+new",
                execution_time=120.5
            ),
            SWEBenchResult(
                instance_id="repo1__issue2",
                resolved=False,
                generated_patch="",
                execution_time=300.0,
                error_message="Timeout error"
            ),
            SWEBenchResult(
                instance_id="repo2__issue1",
                resolved=True,
                generated_patch="patch content",
                execution_time=90.0
            )
        ]
    
    def test_calculate_overall_metrics(self):
        """Test overall metrics calculation."""
        metrics = self.metrics_collector.calculate_overall_metrics(
            self.sample_results, "princeton-nlp/SWE-bench_Lite"
        )
        
        # Check that we get expected metrics
        metric_names = [m.name for m in metrics]
        self.assertIn("resolve_rate", metric_names)
        self.assertIn("patch_generation_rate", metric_names)
        self.assertIn("error_rate", metric_names)
        self.assertIn("average_execution_time", metric_names)
        
        # Check resolve rate calculation
        resolve_rate_metric = next(m for m in metrics if m.name == "resolve_rate")
        self.assertAlmostEqual(resolve_rate_metric.value, 2/3, places=2)  # 2 out of 3 resolved
    
    def test_repository_performance_analysis(self):
        """Test repository performance analysis."""
        repo_metrics = self.metrics_collector.analyze_repository_performance(self.sample_results)
        
        self.assertEqual(len(repo_metrics), 2)  # repo1 and repo2
        
        # Check repo1 metrics
        repo1_metrics = next(r for r in repo_metrics if r.repo_name == "repo1")
        self.assertEqual(repo1_metrics.total_instances, 2)
        self.assertEqual(repo1_metrics.resolved_instances, 1)
        self.assertEqual(repo1_metrics.resolve_rate, 0.5)
    
    def test_performance_patterns_analysis(self):
        """Test performance patterns analysis."""
        analysis = self.metrics_collector.analyze_performance_patterns(self.sample_results)
        
        self.assertIn("execution_time_distribution", analysis)
        self.assertIn("success_vs_failure_timing", analysis)
        self.assertIn("error_analysis", analysis)
        
        # Check execution time stats
        time_dist = analysis["execution_time_distribution"]
        self.assertGreater(time_dist["mean"], 0)
        self.assertGreater(time_dist["max"], time_dist["min"])
    
    def test_recommendations_generation(self):
        """Test recommendations generation."""
        metrics = self.metrics_collector.calculate_overall_metrics(
            self.sample_results, "princeton-nlp/SWE-bench_Lite"
        )
        repo_metrics = self.metrics_collector.analyze_repository_performance(self.sample_results)
        performance_analysis = self.metrics_collector.analyze_performance_patterns(self.sample_results)
        
        recommendations = self.metrics_collector.generate_recommendations(
            metrics, repo_metrics, performance_analysis
        )
        
        self.assertIsInstance(recommendations, list)
        # Should have some recommendations based on the sample data
        self.assertGreater(len(recommendations), 0)


class TestSWEBenchIntegration(unittest.TestCase):
    """Integration tests for the complete SWE-bench system."""
    
    @patch('agent.evals.swe_bench_eval.load_dataset')
    def test_end_to_end_evaluation(self, mock_load_dataset):
        """Test end-to-end evaluation flow."""
        # Mock dataset
        mock_dataset = [
            {
                'instance_id': 'test__repo-1',
                'repo': 'test/repo',
                'base_commit': 'abc123',
                'patch': 'test patch',
                'test_patch': 'test patch',
                'problem_statement': 'Test problem',
                'hints_text': 'Test hints',
                'created_at': '2024-01-01',
                'version': '1.0',
                'FAIL_TO_PASS': ['test_function'],
                'PASS_TO_PASS': ['test_other']
            }
        ]
        mock_load_dataset.return_value = mock_dataset
        
        # Mock agent
        mock_agent = Mock()
        mock_agent.run.return_value = "```diff\n--- a/file.py\n+++ b/file.py\n@@ -1,1 +1,1 @@\n-old\n+new\n```"
        
        # Create evaluator with mocked agent
        evaluator = SWEBenchEvaluator(mock_agent)
        
        # Mock workspace operations
        with patch.object(SWEBenchAgentInterface, 'setup_workspace') as mock_setup:
            with patch.object(SWEBenchAgentInterface, 'cleanup_workspace'):
                mock_setup.return_value = Path("/tmp/test_repo")
                
                # Run evaluation
                report = evaluator.run_evaluation(max_instances=1)
                
                # Verify report
                self.assertIsInstance(report, SWEBenchEvaluationReport)
                self.assertEqual(report.total_instances, 1)
                self.assertGreaterEqual(report.resolved_count, 0)
                self.assertIsInstance(report.results, list)
                self.assertEqual(len(report.results), 1)


class TestSWEBenchCLI(unittest.TestCase):
    """Test command-line interface functionality."""
    
    def test_configuration_presets(self):
        """Test that configuration presets work correctly."""
        from agent.evals.swe_bench_config import create_evaluation_config
        
        # Test different presets
        quick_config = create_evaluation_config("quick_test")
        self.assertEqual(quick_config.max_instances, 5)
        self.assertEqual(quick_config.mode, EvaluationMode.QUICK_TEST)
        
        dev_config = create_evaluation_config("development")
        self.assertEqual(dev_config.max_instances, 50)
        self.assertEqual(dev_config.mode, EvaluationMode.DEVELOPMENT)
    
    def test_custom_overrides(self):
        """Test custom configuration overrides."""
        from agent.evals.swe_bench_config import create_evaluation_config
        
        custom_config = create_evaluation_config(
            "development",
            max_instances=25,
            timeout_per_instance=900
        )
        
        self.assertEqual(custom_config.max_instances, 25)
        self.assertEqual(custom_config.timeout_per_instance, 900)


def run_integration_tests():
    """Run all integration tests."""
    print("🧪 Running SWE-bench Integration Tests")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestSWEBenchInstance,
        TestSWEBenchAgentInterface,
        TestSWEBenchConfiguration,
        TestSWEBenchMetrics,
        TestSWEBenchIntegration,
        TestSWEBenchCLI
    ]
    
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print(f"\n📊 Test Results:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {(result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun:.1%}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)

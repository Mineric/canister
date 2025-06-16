#!/usr/bin/env python3
"""
Performance evaluation framework for Cannister Agent.

This module provides benchmarks and performance metrics for agent capabilities.
"""

import time
import sys
import json
import statistics
from pathlib import Path
from typing import Dict, List, Any, Callable
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    name: str
    value: float
    unit: str
    description: str
    timestamp: float


@dataclass
class EvaluationResult:
    """Evaluation result data structure."""
    test_name: str
    success: bool
    duration: float
    metrics: List[PerformanceMetric]
    error_message: str = ""


class PerformanceEvaluator:
    """Performance evaluation framework."""
    
    def __init__(self):
        """Initialize the evaluator."""
        self.results: List[EvaluationResult] = []
    
    def time_function(self, func: Callable, *args, **kwargs) -> tuple:
        """Time a function execution."""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            return result, end_time - start_time, None
        except Exception as e:
            end_time = time.time()
            return None, end_time - start_time, str(e)
    
    def evaluate_tool_performance(self, tool_name: str, tool_func: Callable, 
                                test_cases: List[tuple], iterations: int = 5) -> EvaluationResult:
        """Evaluate tool performance across multiple test cases."""
        print(f"🔍 Evaluating {tool_name} performance...")
        
        all_durations = []
        success_count = 0
        total_tests = len(test_cases) * iterations
        
        start_time = time.time()
        
        for test_case in test_cases:
            for _ in range(iterations):
                result, duration, error = self.time_function(tool_func, *test_case)
                all_durations.append(duration)
                
                if error is None:
                    success_count += 1
        
        total_duration = time.time() - start_time
        
        # Calculate metrics
        metrics = [
            PerformanceMetric(
                name="average_duration",
                value=statistics.mean(all_durations),
                unit="seconds",
                description="Average execution time",
                timestamp=time.time()
            ),
            PerformanceMetric(
                name="median_duration",
                value=statistics.median(all_durations),
                unit="seconds", 
                description="Median execution time",
                timestamp=time.time()
            ),
            PerformanceMetric(
                name="success_rate",
                value=success_count / total_tests,
                unit="ratio",
                description="Success rate (0-1)",
                timestamp=time.time()
            ),
            PerformanceMetric(
                name="throughput",
                value=total_tests / total_duration,
                unit="operations/second",
                description="Operations per second",
                timestamp=time.time()
            )
        ]
        
        result = EvaluationResult(
            test_name=f"{tool_name}_performance",
            success=success_count == total_tests,
            duration=total_duration,
            metrics=metrics
        )
        
        self.results.append(result)
        return result
    
    def evaluate_basic_tools(self):
        """Evaluate basic tool performance."""
        print("📊 Evaluating Basic Tools Performance")
        print("=" * 40)
        
        # Test calculator tool
        try:
            from agent.tools.tools import calculator_tool
            tool = calculator_tool()
            
            test_cases = [
                ("2 + 2",),
                ("10 * 5",),
                ("100 / 4",),
                ("2 ** 8",),
                ("import math; math.sqrt(16)",)
            ]
            
            self.evaluate_tool_performance("calculator", tool.func, test_cases)
            
        except ImportError as e:
            print(f"⚠️ Skipping calculator tool: {e}")
        
        # Test text analyzer tool
        try:
            from agent.tools.tools import text_analyzer_tool
            tool = text_analyzer_tool()
            
            test_cases = [
                ("Hello world",),
                ("This is a longer text with multiple sentences. It has more words.",),
                ("Short",),
                ("A" * 1000,),  # Long text
            ]
            
            self.evaluate_tool_performance("text_analyzer", tool.func, test_cases)
            
        except ImportError as e:
            print(f"⚠️ Skipping text analyzer tool: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate a comprehensive performance report."""
        report = {
            "timestamp": time.time(),
            "total_evaluations": len(self.results),
            "evaluations": [asdict(result) for result in self.results],
            "summary": {}
        }
        
        # Calculate summary statistics
        if self.results:
            success_rates = [r.metrics[2].value for r in self.results if len(r.metrics) > 2]
            avg_durations = [r.metrics[0].value for r in self.results if len(r.metrics) > 0]
            
            report["summary"] = {
                "overall_success_rate": statistics.mean(success_rates) if success_rates else 0,
                "average_execution_time": statistics.mean(avg_durations) if avg_durations else 0,
                "total_duration": sum(r.duration for r in self.results)
            }
        
        return report
    
    def save_report(self, filename: str = None):
        """Save the evaluation report to a file."""
        if filename is None:
            timestamp = int(time.time())
            filename = f"performance_report_{timestamp}.json"
        
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {filename}")
        return filename


def main():
    """Run performance evaluations."""
    print("🚀 Cannister Agent Performance Evaluation")
    print("=" * 50)
    
    evaluator = PerformanceEvaluator()
    
    # Run evaluations
    evaluator.evaluate_basic_tools()
    
    # Generate and display report
    report = evaluator.generate_report()
    
    print("\n📊 Performance Summary:")
    print(f"   Total evaluations: {report['total_evaluations']}")
    if report['summary']:
        print(f"   Overall success rate: {report['summary']['overall_success_rate']:.2%}")
        print(f"   Average execution time: {report['summary']['average_execution_time']:.4f}s")
        print(f"   Total evaluation time: {report['summary']['total_duration']:.2f}s")
    
    # Save report
    evaluator.save_report()


if __name__ == "__main__":
    main()

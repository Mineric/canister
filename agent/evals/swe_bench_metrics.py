#!/usr/bin/env python3
"""
SWE-bench metrics collection and analysis for Canister Agent.

This module provides comprehensive metrics collection, analysis, and reporting
for SWE-bench evaluation results.
"""

import json
import time
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter

try:
    from .swe_bench_eval import SWEBenchResult, SWEBenchEvaluationReport
except ImportError:
    # Define minimal classes for standalone testing
    from dataclasses import dataclass
    from typing import List, Optional

    @dataclass
    class SWEBenchResult:
        instance_id: str
        resolved: bool
        generated_patch: str
        execution_time: float
        error_message: Optional[str] = None
        agent_reasoning: Optional[str] = None

    @dataclass
    class SWEBenchEvaluationReport:
        dataset_name: str
        total_instances: int
        resolved_count: int
        resolve_rate: float
        total_time: float
        average_time_per_instance: float
        results: List[SWEBenchResult]
        timestamp: str
        agent_config: dict


@dataclass
class SWEBenchMetric:
    """Individual metric for SWE-bench evaluation."""
    name: str
    value: float
    unit: str
    description: str
    category: str
    benchmark_value: Optional[float] = None
    passed: Optional[bool] = None


@dataclass
class RepositoryMetrics:
    """Metrics for a specific repository."""
    repo_name: str
    total_instances: int
    resolved_instances: int
    resolve_rate: float
    average_time: float
    error_rate: float
    difficulty_score: float


@dataclass
class ComprehensiveMetricsReport:
    """Comprehensive metrics report for SWE-bench evaluation."""
    evaluation_id: str
    timestamp: str
    dataset_info: Dict[str, Any]
    overall_metrics: List[SWEBenchMetric]
    repository_metrics: List[RepositoryMetrics]
    performance_analysis: Dict[str, Any]
    comparison_analysis: Dict[str, Any]
    recommendations: List[str]
    raw_data: Dict[str, Any]


class SWEBenchMetricsCollector:
    """Collects and analyzes SWE-bench evaluation metrics."""
    
    def __init__(self):
        """Initialize metrics collector."""
        self.benchmark_data = self._load_benchmark_data()
    
    def _load_benchmark_data(self) -> Dict[str, float]:
        """Load benchmark data for comparison."""
        # These are approximate benchmark values from SWE-bench leaderboard
        return {
            "swe_bench_lite_resolve_rate": 0.30,  # ~30% for top systems
            "swe_bench_verified_resolve_rate": 0.25,  # ~25% for top systems
            "swe_bench_full_resolve_rate": 0.15,  # ~15% for top systems
            "average_time_per_instance": 300.0,  # 5 minutes benchmark
            "patch_generation_rate": 0.95,  # 95% should generate patches
            "error_rate_threshold": 0.05  # <5% error rate
        }
    
    def calculate_overall_metrics(self, results: List[SWEBenchResult], 
                                dataset_name: str) -> List[SWEBenchMetric]:
        """Calculate overall evaluation metrics."""
        if not results:
            return []
        
        total_instances = len(results)
        resolved_count = sum(1 for r in results if r.resolved)
        patch_generated_count = sum(1 for r in results if r.generated_patch.strip())
        error_count = sum(1 for r in results if r.error_message)
        
        execution_times = [r.execution_time for r in results if r.execution_time > 0]
        
        # Determine benchmark key
        benchmark_key = "swe_bench_lite_resolve_rate"
        if "verified" in dataset_name.lower():
            benchmark_key = "swe_bench_verified_resolve_rate"
        elif "lite" not in dataset_name.lower():
            benchmark_key = "swe_bench_full_resolve_rate"
        
        metrics = [
            SWEBenchMetric(
                name="resolve_rate",
                value=resolved_count / total_instances,
                unit="ratio",
                description="Percentage of instances successfully resolved",
                category="effectiveness",
                benchmark_value=self.benchmark_data.get(benchmark_key),
                passed=resolved_count / total_instances >= self.benchmark_data.get(benchmark_key, 0) * 0.8
            ),
            SWEBenchMetric(
                name="patch_generation_rate", 
                value=patch_generated_count / total_instances,
                unit="ratio",
                description="Percentage of instances that generated patches",
                category="reliability",
                benchmark_value=self.benchmark_data.get("patch_generation_rate"),
                passed=patch_generated_count / total_instances >= 0.9
            ),
            SWEBenchMetric(
                name="error_rate",
                value=error_count / total_instances,
                unit="ratio", 
                description="Percentage of instances that encountered errors",
                category="reliability",
                benchmark_value=self.benchmark_data.get("error_rate_threshold"),
                passed=error_count / total_instances <= 0.1
            ),
            SWEBenchMetric(
                name="average_execution_time",
                value=statistics.mean(execution_times) if execution_times else 0,
                unit="seconds",
                description="Average time per instance",
                category="performance",
                benchmark_value=self.benchmark_data.get("average_time_per_instance"),
                passed=statistics.mean(execution_times) <= 600 if execution_times else False  # 10 minutes
            ),
            SWEBenchMetric(
                name="median_execution_time",
                value=statistics.median(execution_times) if execution_times else 0,
                unit="seconds",
                description="Median time per instance",
                category="performance"
            ),
            SWEBenchMetric(
                name="execution_time_std",
                value=statistics.stdev(execution_times) if len(execution_times) > 1 else 0,
                unit="seconds",
                description="Standard deviation of execution times",
                category="performance"
            )
        ]
        
        return metrics
    
    def analyze_repository_performance(self, results: List[SWEBenchResult]) -> List[RepositoryMetrics]:
        """Analyze performance by repository."""
        repo_data = defaultdict(list)
        
        # Group results by repository (extract from instance_id)
        for result in results:
            # Instance ID format: repo__issue_number
            repo_name = result.instance_id.split('__')[0] if '__' in result.instance_id else 'unknown'
            repo_data[repo_name].append(result)
        
        repo_metrics = []
        for repo_name, repo_results in repo_data.items():
            total = len(repo_results)
            resolved = sum(1 for r in repo_results if r.resolved)
            errors = sum(1 for r in repo_results if r.error_message)
            times = [r.execution_time for r in repo_results if r.execution_time > 0]
            
            # Calculate difficulty score based on resolve rate and average time
            resolve_rate = resolved / total if total > 0 else 0
            avg_time = statistics.mean(times) if times else 0
            difficulty_score = (1 - resolve_rate) * 0.7 + (avg_time / 600) * 0.3  # Normalized difficulty
            
            repo_metrics.append(RepositoryMetrics(
                repo_name=repo_name,
                total_instances=total,
                resolved_instances=resolved,
                resolve_rate=resolve_rate,
                average_time=avg_time,
                error_rate=errors / total if total > 0 else 0,
                difficulty_score=min(difficulty_score, 1.0)  # Cap at 1.0
            ))
        
        # Sort by difficulty score (hardest first)
        repo_metrics.sort(key=lambda x: x.difficulty_score, reverse=True)
        return repo_metrics
    
    def analyze_performance_patterns(self, results: List[SWEBenchResult]) -> Dict[str, Any]:
        """Analyze performance patterns and trends."""
        if not results:
            return {}
        
        # Time-based analysis
        execution_times = [r.execution_time for r in results if r.execution_time > 0]
        
        # Success/failure patterns
        successful_times = [r.execution_time for r in results if r.resolved and r.execution_time > 0]
        failed_times = [r.execution_time for r in results if not r.resolved and r.execution_time > 0]
        
        # Error analysis
        error_types = Counter()
        for result in results:
            if result.error_message:
                # Categorize errors
                error_msg = result.error_message.lower()
                if 'timeout' in error_msg:
                    error_types['timeout'] += 1
                elif 'git' in error_msg or 'clone' in error_msg:
                    error_types['repository_access'] += 1
                elif 'patch' in error_msg:
                    error_types['patch_generation'] += 1
                else:
                    error_types['other'] += 1
        
        analysis = {
            "execution_time_distribution": {
                "min": min(execution_times) if execution_times else 0,
                "max": max(execution_times) if execution_times else 0,
                "mean": statistics.mean(execution_times) if execution_times else 0,
                "median": statistics.median(execution_times) if execution_times else 0,
                "std": statistics.stdev(execution_times) if len(execution_times) > 1 else 0
            },
            "success_vs_failure_timing": {
                "successful_avg_time": statistics.mean(successful_times) if successful_times else 0,
                "failed_avg_time": statistics.mean(failed_times) if failed_times else 0,
                "time_correlation": "faster_success" if (successful_times and failed_times and 
                                                      statistics.mean(successful_times) < statistics.mean(failed_times)) else "no_correlation"
            },
            "error_analysis": {
                "total_errors": sum(error_types.values()),
                "error_distribution": dict(error_types),
                "most_common_error": error_types.most_common(1)[0] if error_types else None
            },
            "patch_quality_indicators": {
                "empty_patches": sum(1 for r in results if not r.generated_patch.strip()),
                "short_patches": sum(1 for r in results if len(r.generated_patch.strip()) < 100),
                "long_patches": sum(1 for r in results if len(r.generated_patch.strip()) > 1000)
            }
        }
        
        return analysis
    
    def generate_recommendations(self, metrics: List[SWEBenchMetric], 
                               repo_metrics: List[RepositoryMetrics],
                               performance_analysis: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on metrics."""
        recommendations = []
        
        # Analyze overall performance
        resolve_rate_metric = next((m for m in metrics if m.name == "resolve_rate"), None)
        if resolve_rate_metric and resolve_rate_metric.value < 0.2:
            recommendations.append(
                "🎯 Low resolve rate detected. Consider improving problem understanding and solution generation capabilities."
            )
        
        error_rate_metric = next((m for m in metrics if m.name == "error_rate"), None)
        if error_rate_metric and error_rate_metric.value > 0.1:
            recommendations.append(
                "🔧 High error rate detected. Improve error handling and repository access reliability."
            )
        
        time_metric = next((m for m in metrics if m.name == "average_execution_time"), None)
        if time_metric and time_metric.value > 600:
            recommendations.append(
                "⚡ Slow execution detected. Optimize agent reasoning and tool usage for faster problem solving."
            )
        
        # Repository-specific recommendations
        if repo_metrics:
            hardest_repos = [r for r in repo_metrics[:3] if r.difficulty_score > 0.7]
            if hardest_repos:
                repo_names = [r.repo_name for r in hardest_repos]
                recommendations.append(
                    f"📚 Focus on improving performance for challenging repositories: {', '.join(repo_names)}"
                )
        
        # Error-specific recommendations
        error_analysis = performance_analysis.get("error_analysis", {})
        if error_analysis.get("most_common_error"):
            error_type, count = error_analysis["most_common_error"]
            if error_type == "timeout":
                recommendations.append("⏱️ Implement better timeout handling and incremental progress saving.")
            elif error_type == "repository_access":
                recommendations.append("🔗 Improve repository cloning and access reliability.")
            elif error_type == "patch_generation":
                recommendations.append("🔨 Enhance patch generation logic and validation.")
        
        # Patch quality recommendations
        patch_quality = performance_analysis.get("patch_quality_indicators", {})
        if patch_quality.get("empty_patches", 0) > len(repo_metrics) * 0.1:
            recommendations.append("📝 Reduce empty patch generation by improving problem analysis.")
        
        return recommendations
    
    def create_comprehensive_report(self, evaluation_report: SWEBenchEvaluationReport) -> ComprehensiveMetricsReport:
        """Create comprehensive metrics report from evaluation results."""
        # Calculate metrics
        overall_metrics = self.calculate_overall_metrics(evaluation_report.results, evaluation_report.dataset_name)
        repo_metrics = self.analyze_repository_performance(evaluation_report.results)
        performance_analysis = self.analyze_performance_patterns(evaluation_report.results)
        
        # Generate recommendations
        recommendations = self.generate_recommendations(overall_metrics, repo_metrics, performance_analysis)
        
        # Create comparison analysis
        comparison_analysis = {
            "benchmark_comparison": {},
            "performance_grade": self._calculate_performance_grade(overall_metrics)
        }
        
        for metric in overall_metrics:
            if metric.benchmark_value is not None:
                comparison_analysis["benchmark_comparison"][metric.name] = {
                    "agent_value": metric.value,
                    "benchmark_value": metric.benchmark_value,
                    "relative_performance": metric.value / metric.benchmark_value if metric.benchmark_value > 0 else 0,
                    "passed": metric.passed
                }
        
        return ComprehensiveMetricsReport(
            evaluation_id=f"swe_bench_{int(time.time())}",
            timestamp=evaluation_report.timestamp,
            dataset_info={
                "name": evaluation_report.dataset_name,
                "total_instances": evaluation_report.total_instances,
                "agent_config": evaluation_report.agent_config
            },
            overall_metrics=overall_metrics,
            repository_metrics=repo_metrics,
            performance_analysis=performance_analysis,
            comparison_analysis=comparison_analysis,
            recommendations=recommendations,
            raw_data={
                "results": [asdict(r) for r in evaluation_report.results],
                "summary": {
                    "resolved_count": evaluation_report.resolved_count,
                    "resolve_rate": evaluation_report.resolve_rate,
                    "total_time": evaluation_report.total_time
                }
            }
        )
    
    def _calculate_performance_grade(self, metrics: List[SWEBenchMetric]) -> str:
        """Calculate overall performance grade."""
        passed_count = sum(1 for m in metrics if m.passed is True)
        total_graded = sum(1 for m in metrics if m.passed is not None)
        
        if total_graded == 0:
            return "N/A"
        
        pass_rate = passed_count / total_graded
        
        if pass_rate >= 0.9:
            return "A"
        elif pass_rate >= 0.8:
            return "B"
        elif pass_rate >= 0.7:
            return "C"
        elif pass_rate >= 0.6:
            return "D"
        else:
            return "F"
    
    def save_metrics_report(self, report: ComprehensiveMetricsReport, output_path: Optional[str] = None):
        """Save comprehensive metrics report."""
        if not output_path:
            timestamp = int(time.time())
            output_path = f"swe_bench_metrics_report_{timestamp}.json"
        
        with open(output_path, 'w') as f:
            json.dump(asdict(report), f, indent=2, default=str)
        
        print(f"📊 Metrics report saved to: {output_path}")
        return output_path
    
    def print_metrics_summary(self, report: ComprehensiveMetricsReport):
        """Print a formatted summary of metrics."""
        print(f"\n📊 SWE-bench Metrics Summary")
        print(f"{'='*60}")
        print(f"Evaluation ID: {report.evaluation_id}")
        print(f"Dataset: {report.dataset_info['name']}")
        print(f"Total Instances: {report.dataset_info['total_instances']}")
        print(f"Performance Grade: {report.comparison_analysis['performance_grade']}")
        
        print(f"\n🎯 Overall Metrics:")
        for metric in report.overall_metrics:
            status = "✅" if metric.passed else "❌" if metric.passed is False else "ℹ️"
            value_str = f"{metric.value:.3f}" if isinstance(metric.value, float) else str(metric.value)
            print(f"   {status} {metric.name}: {value_str} {metric.unit}")
        
        print(f"\n📚 Top 5 Most Challenging Repositories:")
        for i, repo in enumerate(report.repository_metrics[:5]):
            print(f"   {i+1}. {repo.repo_name}: {repo.resolve_rate:.1%} resolve rate, {repo.difficulty_score:.2f} difficulty")
        
        print(f"\n💡 Recommendations:")
        for rec in report.recommendations:
            print(f"   {rec}")


def main():
    """Demo metrics collection and analysis."""
    print("📊 SWE-bench Metrics Collection Demo")
    print("="*50)
    
    # This would normally be called with real evaluation results
    print("This module provides metrics collection for SWE-bench evaluations.")
    print("Use it in conjunction with swe_bench_eval.py and swe_bench_harness.py")


if __name__ == "__main__":
    main()

# SWE-bench Integration Guide

This guide explains how to use the SWE-bench evaluation capabilities integrated into the Canister Agent system.

## Overview

SWE-bench (Software Engineering Benchmark) is a benchmark for evaluating large language models on real-world software engineering tasks. Our integration allows you to:

- Evaluate the Canister agent on standardized software engineering problems
- Compare performance against other AI coding systems
- Track improvements over time with comprehensive metrics
- Run evaluations on different difficulty levels and datasets

## Quick Start

### 1. Basic Evaluation

Run a quick test evaluation with 5 instances:

```bash
# Run from the project root
# Optionally point to a local dataset snapshot
export SWE_BENCH_DATASET_PATH=agent/evals/sample_data/swe_bench_sample.json
python agent/evals/swe_bench_eval.py
```

This will:
- Load 5 instances from SWE-bench Lite
- Run the agent on each instance
- Generate patches and measure performance
- Save a detailed report

### 2. Comprehensive Evaluation

For a full evaluation with official SWE-bench harness:

```bash
python agent/evals/swe_bench_harness.py
```

This includes:
- Agent patch generation
- Official Docker-based evaluation
- Comprehensive metrics and comparison

### 3. Integration with Existing Evaluation Suite

Add SWE-bench to your regular evaluations:

```bash
python agent/evals/eval_runner.py
```

This runs all evaluations including SWE-bench alongside performance and code quality tests.

## Configuration Options

### Preset Configurations

Use predefined configurations for common scenarios:

```python
from agent.evals.swe_bench_config import create_evaluation_config

# Quick test (5 instances, 10 minutes)
config = create_evaluation_config("quick_test")

# Development (50 instances, 20 minutes each)
config = create_evaluation_config("development")

# Full benchmark (all instances, 30 minutes each)
config = create_evaluation_config("lite_benchmark")
```

### Custom Configuration

Create custom configurations:

```python
config = create_evaluation_config(
    preset="development",
    max_instances=25,
    timeout_per_instance=900,  # 15 minutes
    dataset="verified"  # Use SWE-bench Verified
)
```

### Available Datasets

- **SWE-bench Lite** (300 instances): Curated subset for faster evaluation
- **SWE-bench Verified** (500 instances): Human-verified solvable problems
- **SWE-bench Full** (2,294 instances): Complete benchmark dataset
- **SWE-bench Multimodal** (517 instances): Issues with visual elements
- **Local snapshots**: Point `SWE_BENCH_DATASET_PATH` to a JSON file (see `agent/evals/sample_data/swe_bench_sample.json` for the expected schema) to run offline experiments.

## Advanced Usage

### 1. Programmatic Evaluation

```python
from agent.evals.swe_bench_eval import SWEBenchEvaluator
from agent.evals.swe_bench_config import EvaluationConfiguration, SWEBenchDataset

# Create custom configuration
config = EvaluationConfiguration(
    dataset=SWEBenchDataset.LITE,
    max_instances=10,
    timeout_per_instance=600
)

# Run evaluation
evaluator = SWEBenchEvaluator()
report = evaluator.run_evaluation(
    dataset_name=config.dataset.value,
    max_instances=config.max_instances
)

print(f"Resolved: {report.resolved_count}/{report.total_instances}")
print(f"Success rate: {report.resolve_rate:.1%}")
```

### 2. Metrics Analysis

```python
from agent.evals.swe_bench_metrics import SWEBenchMetricsCollector

# Analyze results
metrics_collector = SWEBenchMetricsCollector()
comprehensive_report = metrics_collector.create_comprehensive_report(report)

# Print detailed metrics
metrics_collector.print_metrics_summary(comprehensive_report)

# Save metrics report
metrics_collector.save_metrics_report(comprehensive_report)
```

### 3. Repository-Specific Evaluation

Focus on specific repositories:

```python
config = create_evaluation_config(
    "development",
    repository_filter=["django/django", "scikit-learn/scikit-learn"],
    max_instances=20
)
```

### 4. Difficulty-Based Evaluation

Evaluate on specific difficulty levels:

```python
from agent.evals.swe_bench_config import DifficultyLevel

config = create_evaluation_config(
    "development",
    difficulty_level=DifficultyLevel.EASY,
    max_instances=30
)
```

## Understanding Results

### Key Metrics

- **Resolve Rate**: Percentage of instances successfully resolved
- **Patch Generation Rate**: Percentage of instances that generated patches
- **Average Execution Time**: Time per instance
- **Error Rate**: Percentage of instances with errors

### Benchmark Comparison

Results are automatically compared against SWE-bench leaderboard benchmarks:

- **SWE-bench Lite**: ~30% resolve rate for top systems
- **SWE-bench Verified**: ~25% resolve rate for top systems
- **SWE-bench Full**: ~15% resolve rate for top systems

### Performance Grades

- **A (90-100%)**: Excellent performance across all metrics
- **B (80-89%)**: Good performance with minor improvements needed
- **C (70-79%)**: Acceptable performance with notable improvement areas
- **D (60-69%)**: Below expectations, significant improvements needed
- **F (<60%)**: Failing performance, major issues require attention

## Troubleshooting

### Common Issues

1. **Docker Not Available**
   ```bash
   # Install Docker and ensure it's running
   docker --version
   ```

2. **Memory Issues**
   ```python
   # Reduce max_instances or max_workers
   config = create_evaluation_config("quick_test", max_instances=3)
   ```

3. **Timeout Errors**
   ```python
   # Increase timeout
   config = create_evaluation_config("development", timeout_per_instance=1800)
   ```

4. **Repository Access Issues**
   ```bash
   # Ensure git is configured and GitHub is accessible
   git config --global user.name "Your Name"
   git config --global user.email "your.email@example.com"
   ```

### ARM/M1 Mac Support

For ARM-based systems (M1/M2 Macs):

```python
from agent.evals.swe_bench_harness import SWEBenchHarnessConfig

config = SWEBenchHarnessConfig(
    namespace="",  # Build Docker images locally
    max_workers=1  # Reduce parallelism
)
```

## Integration with CI/CD

### GitHub Actions

```yaml
name: SWE-bench Evaluation
on: [push, pull_request]

jobs:
  swe-bench:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: pip install -e .
    - name: Run SWE-bench evaluation
      run: python agent/evals/swe_bench_eval.py
    - name: Upload results
      uses: actions/upload-artifact@v2
      with:
        name: swe-bench-results
        path: swe_bench_evaluation_*.json
```

### Quality Gates

Set up quality gates based on SWE-bench performance:

```python
# In your CI script
from agent.evals.swe_bench_eval import SWEBenchEvaluator

evaluator = SWEBenchEvaluator()
report = evaluator.run_evaluation(max_instances=10)

# Fail CI if resolve rate is below threshold
if report.resolve_rate < 0.2:  # 20% threshold
    print("❌ SWE-bench performance below threshold")
    exit(1)
```

## Best Practices

### 1. Start Small
Begin with quick_test configuration to validate setup before running full evaluations.

### 2. Monitor Resources
SWE-bench evaluation is resource-intensive. Monitor CPU, memory, and disk usage.

### 3. Regular Evaluation
Run evaluations regularly to track performance improvements:
- Daily: Quick tests (5-10 instances)
- Weekly: Development evaluation (50 instances)
- Monthly: Full benchmark evaluation

### 4. Analyze Failures
Review failed instances to identify improvement opportunities:

```python
# Filter failed results
failed_results = [r for r in report.results if not r.resolved]
for result in failed_results:
    print(f"Failed: {result.instance_id}")
    if result.error_message:
        print(f"Error: {result.error_message}")
```

### 5. Track Progress
Save evaluation reports and compare over time:

```bash
# Compare two reports
python -c "
import json
with open('report1.json') as f: r1 = json.load(f)
with open('report2.json') as f: r2 = json.load(f)
print(f'Improvement: {r2[\"resolve_rate\"] - r1[\"resolve_rate\"]:.1%}')
"
```

## Contributing

To contribute improvements to the SWE-bench integration:

1. Run the test suite: `python agent/tests/test_swe_bench_integration.py`
2. Add new features with corresponding tests
3. Update documentation for new capabilities
4. Ensure backward compatibility

## Support

For issues with SWE-bench integration:

1. Check the troubleshooting section above
2. Review the test suite for examples
3. Consult the official SWE-bench documentation
4. File an issue with detailed error information

## References

- [SWE-bench Official Website](https://www.swebench.com/)
- [SWE-bench GitHub Repository](https://github.com/SWE-bench/SWE-bench)
- [SWE-bench Paper](https://arxiv.org/abs/2310.06770)
- [SWE-bench Leaderboard](https://www.swebench.com/)

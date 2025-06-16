# Cannister Agent Evaluation Suite

This directory contains comprehensive evaluation frameworks for assessing agent performance, code quality, and capabilities.

## 📁 Evaluation Structure

```
agent/evals/
├── __init__.py              # Package initialization
├── eval_runner.py           # Comprehensive evaluation runner
├── performance_eval.py      # Performance benchmarking
├── code_quality_eval.py     # Code quality assessment
└── README.md               # This file
```

## 🎯 Evaluation Categories

### **Performance Evaluation** (`performance_eval.py`)
Measures and benchmarks:
- **Tool Execution Speed**: Average and median response times
- **Throughput**: Operations per second
- **Success Rate**: Reliability metrics
- **Resource Usage**: Memory and CPU utilization
- **Scalability**: Performance under load

### **Code Quality Evaluation** (`code_quality_eval.py`)
Assesses:
- **Syntax Validity**: Error-free code generation
- **Complexity Metrics**: Cyclomatic complexity analysis
- **Documentation Coverage**: Docstring presence and quality
- **Code Structure**: Organization and maintainability
- **Best Practices**: Adherence to Python standards

### **Comprehensive Evaluation** (`eval_runner.py`)
Orchestrates:
- **Multi-dimensional Assessment**: All evaluation types
- **Scoring System**: Weighted performance metrics
- **Grade Assignment**: A-F grading scale
- **Report Generation**: Detailed analysis reports
- **CI/CD Integration**: Automated quality gates

## 🚀 Running Evaluations

### Run All Evaluations
```bash
# Comprehensive evaluation suite
python agent/evals/eval_runner.py

# Individual evaluations
python agent/evals/performance_eval.py
python agent/evals/code_quality_eval.py
```

### Evaluation Outputs
- **JSON Reports**: Detailed metrics and analysis
- **Console Output**: Real-time progress and summaries
- **Grade Assignment**: Overall quality assessment
- **Recommendations**: Improvement suggestions

## 📊 Metrics and Scoring

### Performance Metrics
- **Response Time**: < 1s (Excellent), < 5s (Good), > 5s (Needs Improvement)
- **Success Rate**: > 95% (Excellent), > 90% (Good), < 90% (Needs Improvement)
- **Throughput**: Operations per second benchmarks

### Quality Metrics
- **Complexity**: < 5 (Excellent), < 10 (Good), > 10 (Needs Improvement)
- **Documentation**: > 80% (Excellent), > 60% (Good), < 60% (Needs Improvement)
- **Syntax Validity**: 100% (Required)

### Overall Grading Scale
- **A (90-100%)**: Excellent performance across all metrics
- **B (80-89%)**: Good performance with minor areas for improvement
- **C (70-79%)**: Acceptable performance with notable improvement areas
- **D (60-69%)**: Below expectations, significant improvements needed
- **F (<60%)**: Failing performance, major issues require attention

## 📈 Evaluation Reports

### Report Structure
```json
{
  "timestamp": "2024-06-16T23:00:00Z",
  "duration": 45.2,
  "evaluations": {
    "performance": { /* performance metrics */ },
    "code_quality": { /* quality metrics */ },
    "imports": { /* dependency analysis */ }
  },
  "summary": {
    "performance_score": 0.92,
    "quality_score": 0.85,
    "import_score": 1.0,
    "overall_score": 0.92,
    "grade": "A"
  }
}
```

### Report Files
- `performance_report_[timestamp].json`: Performance benchmarks
- `code_quality_report_[timestamp].json`: Quality assessment
- `comprehensive_evaluation_[timestamp].json`: Complete analysis

## 🔧 Customizing Evaluations

### Adding New Metrics
1. Create evaluation class inheriting from base evaluator
2. Implement metric calculation methods
3. Add to evaluation runner
4. Update scoring algorithms

### Performance Benchmarks
```python
# Add new performance test
test_cases = [
    ("input1",),
    ("input2",),
    # Add more test cases
]

evaluator.evaluate_tool_performance(
    "tool_name", 
    tool_function, 
    test_cases, 
    iterations=10
)
```

### Quality Assessments
```python
# Add new quality metric
metric = CodeQualityMetric(
    name="new_metric",
    value=calculated_value,
    max_value=100,
    description="Description of metric",
    passed=calculated_value >= threshold
)
```

## 🎯 Continuous Improvement

### Tracking Progress
- **Historical Comparison**: Track improvements over time
- **Regression Detection**: Identify performance degradation
- **Benchmark Updates**: Evolve standards as capabilities improve
- **Goal Setting**: Establish improvement targets

### Integration with Development
- **Pre-commit Hooks**: Run evaluations before code commits
- **CI/CD Pipeline**: Automated evaluation in build process
- **Quality Gates**: Prevent deployment of low-quality code
- **Performance Monitoring**: Continuous performance tracking

## 🔍 Evaluation Best Practices

### Regular Evaluation
- Run comprehensive evaluations weekly
- Quick performance checks daily
- Full quality assessment before releases
- Benchmark new features immediately

### Metric Interpretation
- Consider context when interpreting scores
- Look for trends rather than absolute values
- Investigate sudden changes in metrics
- Balance different metric types appropriately

### Improvement Actions
- **Performance Issues**: Profile and optimize bottlenecks
- **Quality Issues**: Refactor and add documentation
- **Reliability Issues**: Add error handling and tests
- **Complexity Issues**: Simplify and modularize code

## 🔗 Integration

### CI/CD Integration
```bash
# In CI pipeline
python agent/evals/eval_runner.py
if [ $? -eq 0 ]; then
    echo "Quality gate passed"
else
    echo "Quality gate failed"
    exit 1
fi
```

### Development Workflow
1. **Code Changes**: Implement new features or fixes
2. **Local Evaluation**: Run relevant evaluations
3. **Quality Check**: Ensure metrics meet standards
4. **Commit**: Submit code with evaluation results
5. **CI Evaluation**: Automated comprehensive assessment
6. **Review**: Human review of evaluation reports

## 📋 Evaluation Checklist

Before releasing new versions:
- [ ] Performance evaluation shows acceptable metrics
- [ ] Code quality meets or exceeds standards
- [ ] All imports and dependencies work correctly
- [ ] Overall grade is B or higher
- [ ] No significant regressions detected
- [ ] Evaluation reports are reviewed and approved

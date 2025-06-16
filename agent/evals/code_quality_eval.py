#!/usr/bin/env python3
"""
Code quality evaluation for Cannister Agent.

This module evaluates the quality of code generated and manipulated by the agent.
"""

import ast
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class CodeQualityMetric:
    """Code quality metric."""
    name: str
    value: float
    max_value: float
    description: str
    passed: bool


class CodeQualityEvaluator:
    """Evaluates code quality metrics."""
    
    def __init__(self):
        """Initialize the evaluator."""
        self.metrics: List[CodeQualityMetric] = []
    
    def analyze_python_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a Python file for quality metrics."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Parse AST
            tree = ast.parse(content)
            
            # Calculate metrics
            metrics = {
                "lines_of_code": len(content.splitlines()),
                "functions": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                "classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                "imports": len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]),
                "complexity": self._calculate_complexity(tree),
                "docstring_coverage": self._calculate_docstring_coverage(tree),
                "syntax_valid": True
            }
            
            return metrics
            
        except SyntaxError:
            return {"syntax_valid": False, "error": "Syntax error in file"}
        except Exception as e:
            return {"syntax_valid": False, "error": str(e)}
    
    def _calculate_complexity(self, tree: ast.AST) -> int:
        """Calculate cyclomatic complexity."""
        complexity = 1  # Base complexity
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
            elif isinstance(node, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    def _calculate_docstring_coverage(self, tree: ast.AST) -> float:
        """Calculate docstring coverage percentage."""
        functions_and_classes = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                functions_and_classes.append(node)
        
        if not functions_and_classes:
            return 1.0  # 100% if no functions/classes
        
        documented = 0
        for node in functions_and_classes:
            if ast.get_docstring(node):
                documented += 1
        
        return documented / len(functions_and_classes)
    
    def evaluate_codebase_quality(self, root_path: str) -> Dict[str, Any]:
        """Evaluate quality of entire codebase."""
        print(f"🔍 Evaluating codebase quality: {root_path}")
        
        root = Path(root_path)
        python_files = list(root.rglob("*.py"))
        
        if not python_files:
            return {"error": "No Python files found"}
        
        total_metrics = {
            "files_analyzed": 0,
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "syntax_errors": 0,
            "avg_complexity": 0,
            "avg_docstring_coverage": 0
        }
        
        complexities = []
        docstring_coverages = []
        
        for py_file in python_files:
            # Skip __pycache__ and other generated files
            if "__pycache__" in str(py_file) or py_file.name.startswith("."):
                continue
            
            metrics = self.analyze_python_file(str(py_file))
            
            if metrics.get("syntax_valid", False):
                total_metrics["files_analyzed"] += 1
                total_metrics["total_lines"] += metrics.get("lines_of_code", 0)
                total_metrics["total_functions"] += metrics.get("functions", 0)
                total_metrics["total_classes"] += metrics.get("classes", 0)
                
                if "complexity" in metrics:
                    complexities.append(metrics["complexity"])
                if "docstring_coverage" in metrics:
                    docstring_coverages.append(metrics["docstring_coverage"])
            else:
                total_metrics["syntax_errors"] += 1
        
        # Calculate averages
        if complexities:
            total_metrics["avg_complexity"] = sum(complexities) / len(complexities)
        if docstring_coverages:
            total_metrics["avg_docstring_coverage"] = sum(docstring_coverages) / len(docstring_coverages)
        
        # Generate quality metrics
        self._generate_quality_metrics(total_metrics)
        
        return total_metrics
    
    def _generate_quality_metrics(self, metrics: Dict[str, Any]):
        """Generate quality assessment metrics."""
        # Complexity metric (lower is better, max reasonable complexity is 10)
        complexity_score = max(0, 10 - metrics.get("avg_complexity", 0)) / 10
        self.metrics.append(CodeQualityMetric(
            name="complexity",
            value=metrics.get("avg_complexity", 0),
            max_value=10,
            description="Average cyclomatic complexity (lower is better)",
            passed=metrics.get("avg_complexity", 0) <= 10
        ))
        
        # Docstring coverage (higher is better)
        docstring_coverage = metrics.get("avg_docstring_coverage", 0)
        self.metrics.append(CodeQualityMetric(
            name="docstring_coverage",
            value=docstring_coverage,
            max_value=1.0,
            description="Docstring coverage percentage",
            passed=docstring_coverage >= 0.7  # 70% threshold
        ))
        
        # Syntax validity
        syntax_error_rate = metrics.get("syntax_errors", 0) / max(1, metrics.get("files_analyzed", 1))
        self.metrics.append(CodeQualityMetric(
            name="syntax_validity",
            value=1.0 - syntax_error_rate,
            max_value=1.0,
            description="Syntax validity rate",
            passed=syntax_error_rate == 0
        ))
    
    def evaluate_ast_merger_quality(self):
        """Evaluate AST merger tool quality."""
        print("🔧 Evaluating AST Merger Quality")
        
        try:
            from agent.tools.code_tools import ast_code_merger_tool
            
            # This would involve creating test cases and evaluating
            # the quality of merged code
            print("✅ AST merger tool available")
            
        except ImportError as e:
            print(f"⚠️ AST merger tool not available: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate quality assessment report."""
        passed_metrics = sum(1 for m in self.metrics if m.passed)
        total_metrics = len(self.metrics)
        
        return {
            "timestamp": time.time(),
            "metrics": [asdict(m) for m in self.metrics],
            "summary": {
                "total_metrics": total_metrics,
                "passed_metrics": passed_metrics,
                "quality_score": passed_metrics / total_metrics if total_metrics > 0 else 0,
                "overall_quality": "High" if passed_metrics / total_metrics >= 0.8 else 
                                 "Medium" if passed_metrics / total_metrics >= 0.6 else "Low"
            }
        }


def main():
    """Run code quality evaluation."""
    print("📊 Cannister Agent Code Quality Evaluation")
    print("=" * 50)
    
    evaluator = CodeQualityEvaluator()
    
    # Evaluate agent codebase
    agent_path = Path(__file__).parent.parent
    metrics = evaluator.evaluate_codebase_quality(str(agent_path))
    
    print(f"\n📈 Codebase Metrics:")
    print(f"   Files analyzed: {metrics.get('files_analyzed', 0)}")
    print(f"   Total lines: {metrics.get('total_lines', 0)}")
    print(f"   Functions: {metrics.get('total_functions', 0)}")
    print(f"   Classes: {metrics.get('total_classes', 0)}")
    print(f"   Avg complexity: {metrics.get('avg_complexity', 0):.2f}")
    print(f"   Docstring coverage: {metrics.get('avg_docstring_coverage', 0):.1%}")
    
    # Evaluate specific tools
    evaluator.evaluate_ast_merger_quality()
    
    # Generate report
    report = evaluator.generate_report()
    
    print(f"\n🎯 Quality Assessment:")
    print(f"   Quality score: {report['summary']['quality_score']:.1%}")
    print(f"   Overall quality: {report['summary']['overall_quality']}")
    
    # Save report
    timestamp = int(time.time())
    filename = f"code_quality_report_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"📄 Report saved to: {filename}")


if __name__ == "__main__":
    main()

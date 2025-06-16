"""
Advanced Code Comprehension Engine - Canister Agent
Copyright (c) 2024 Thant Min Htet. All rights reserved.

Professional SWE-level code understanding and analysis capabilities that match
the sophistication of advanced software engineering agents.

This software is proprietary and confidential. No usage, modification,
or distribution rights are granted without explicit written permission.
"""

import ast
import inspect
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, field
from collections import defaultdict
from google.adk.tools import FunctionTool


@dataclass
class ArchitecturalPattern:
    """Represents an architectural pattern detected in the codebase."""
    name: str
    description: str
    files: List[str]
    confidence: float
    examples: List[str] = field(default_factory=list)
    violations: List[str] = field(default_factory=list)


@dataclass
class CodeQualityMetrics:
    """Comprehensive code quality metrics."""
    cyclomatic_complexity: float
    maintainability_index: float
    technical_debt_ratio: float
    test_coverage_estimate: float
    documentation_coverage: float
    code_duplication_ratio: float
    dependency_coupling: float
    cohesion_score: float


@dataclass
class RefactoringOpportunity:
    """Represents a refactoring opportunity."""
    type: str  # 'extract_method', 'extract_class', 'move_method', etc.
    description: str
    file_path: str
    line_range: Tuple[int, int]
    impact_level: str  # 'low', 'medium', 'high'
    estimated_effort: str  # 'small', 'medium', 'large'
    benefits: List[str]
    risks: List[str]


@dataclass
class DependencyAnalysis:
    """Advanced dependency analysis results."""
    direct_dependencies: Set[str]
    transitive_dependencies: Set[str]
    circular_dependencies: List[List[str]]
    unused_imports: List[str]
    missing_dependencies: List[str]
    dependency_violations: List[str]
    coupling_metrics: Dict[str, float]


class AdvancedCodeComprehension:
    """
    Professional-grade code comprehension engine that provides deep understanding
    of code structure, patterns, dependencies, and architectural relationships.
    """
    
    def __init__(self, indexer=None):
        """Initialize the comprehension engine."""
        self.indexer = indexer
        self.architectural_patterns = {}
        self.quality_metrics = {}
        self.refactoring_opportunities = []
        self.dependency_analysis = {}
        
    def analyze_codebase_architecture(self, root_path: str) -> Dict[str, Any]:
        """
        Perform comprehensive architectural analysis of the codebase.
        
        Args:
            root_path: Root directory of the codebase
            
        Returns:
            Comprehensive architectural analysis report
        """
        root_path = Path(root_path)
        
        analysis = {
            "architectural_patterns": self._detect_architectural_patterns(root_path),
            "design_principles": self._analyze_design_principles(root_path),
            "code_organization": self._analyze_code_organization(root_path),
            "dependency_structure": self._analyze_dependency_structure(root_path),
            "quality_metrics": self._calculate_quality_metrics(root_path),
            "refactoring_opportunities": self._identify_refactoring_opportunities(root_path),
            "technical_debt": self._assess_technical_debt(root_path),
            "maintainability_score": self._calculate_maintainability_score(root_path)
        }
        
        return analysis
    
    def _detect_architectural_patterns(self, root_path: Path) -> List[ArchitecturalPattern]:
        """Detect common architectural patterns in the codebase."""
        patterns = []
        
        # Detect MVC pattern
        mvc_pattern = self._detect_mvc_pattern(root_path)
        if mvc_pattern:
            patterns.append(mvc_pattern)
        
        # Detect Repository pattern
        repo_pattern = self._detect_repository_pattern(root_path)
        if repo_pattern:
            patterns.append(repo_pattern)
        
        # Detect Factory pattern
        factory_pattern = self._detect_factory_pattern(root_path)
        if factory_pattern:
            patterns.append(factory_pattern)
        
        # Detect Observer pattern
        observer_pattern = self._detect_observer_pattern(root_path)
        if observer_pattern:
            patterns.append(observer_pattern)
        
        # Detect Singleton pattern
        singleton_pattern = self._detect_singleton_pattern(root_path)
        if singleton_pattern:
            patterns.append(singleton_pattern)
        
        return patterns
    
    def _detect_mvc_pattern(self, root_path: Path) -> Optional[ArchitecturalPattern]:
        """Detect MVC (Model-View-Controller) pattern."""
        mvc_indicators = {
            'models': ['model', 'models', 'entity', 'entities'],
            'views': ['view', 'views', 'template', 'templates'],
            'controllers': ['controller', 'controllers', 'handler', 'handlers']
        }
        
        found_components = {}
        confidence = 0.0
        
        for py_file in root_path.rglob("*.py"):
            file_name = py_file.stem.lower()
            file_path = str(py_file.relative_to(root_path))
            
            for component, indicators in mvc_indicators.items():
                if any(indicator in file_name or indicator in file_path.lower() 
                       for indicator in indicators):
                    if component not in found_components:
                        found_components[component] = []
                    found_components[component].append(str(py_file))
                    confidence += 0.3
        
        if len(found_components) >= 2:  # At least 2 MVC components found
            return ArchitecturalPattern(
                name="MVC (Model-View-Controller)",
                description="Separation of concerns pattern with models, views, and controllers",
                files=sum(found_components.values(), []),
                confidence=min(confidence, 1.0),
                examples=[f"{comp}: {files[:2]}" for comp, files in found_components.items()]
            )
        
        return None
    
    def _detect_repository_pattern(self, root_path: Path) -> Optional[ArchitecturalPattern]:
        """Detect Repository pattern."""
        repo_files = []
        confidence = 0.0
        
        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for repository pattern indicators
                if re.search(r'class.*Repository.*:', content, re.IGNORECASE):
                    repo_files.append(str(py_file))
                    confidence += 0.4
                
                # Look for CRUD operations
                crud_methods = ['create', 'read', 'update', 'delete', 'find', 'save']
                crud_count = sum(1 for method in crud_methods 
                               if re.search(rf'def.*{method}.*\(', content, re.IGNORECASE))
                
                if crud_count >= 3:
                    if str(py_file) not in repo_files:
                        repo_files.append(str(py_file))
                    confidence += 0.2
                    
            except Exception:
                continue
        
        if repo_files and confidence > 0.3:
            return ArchitecturalPattern(
                name="Repository Pattern",
                description="Data access abstraction pattern",
                files=repo_files,
                confidence=min(confidence, 1.0),
                examples=[f"Repository classes found in {len(repo_files)} files"]
            )
        
        return None
    
    def _detect_factory_pattern(self, root_path: Path) -> Optional[ArchitecturalPattern]:
        """Detect Factory pattern."""
        factory_files = []
        confidence = 0.0
        
        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for factory pattern indicators
                factory_indicators = [
                    r'class.*Factory.*:',
                    r'def.*create.*\(',
                    r'def.*build.*\(',
                    r'def.*make.*\('
                ]
                
                for pattern in factory_indicators:
                    if re.search(pattern, content, re.IGNORECASE):
                        if str(py_file) not in factory_files:
                            factory_files.append(str(py_file))
                        confidence += 0.2
                        
            except Exception:
                continue
        
        if factory_files and confidence > 0.3:
            return ArchitecturalPattern(
                name="Factory Pattern",
                description="Object creation abstraction pattern",
                files=factory_files,
                confidence=min(confidence, 1.0),
                examples=[f"Factory patterns found in {len(factory_files)} files"]
            )
        
        return None
    
    def _detect_observer_pattern(self, root_path: Path) -> Optional[ArchitecturalPattern]:
        """Detect Observer pattern."""
        observer_files = []
        confidence = 0.0
        
        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for observer pattern indicators
                observer_indicators = [
                    r'def.*notify.*\(',
                    r'def.*subscribe.*\(',
                    r'def.*unsubscribe.*\(',
                    r'def.*add_observer.*\(',
                    r'def.*remove_observer.*\(',
                    r'class.*Observer.*:',
                    r'class.*Subject.*:'
                ]
                
                for pattern in observer_indicators:
                    if re.search(pattern, content, re.IGNORECASE):
                        if str(py_file) not in observer_files:
                            observer_files.append(str(py_file))
                        confidence += 0.15
                        
            except Exception:
                continue
        
        if observer_files and confidence > 0.3:
            return ArchitecturalPattern(
                name="Observer Pattern",
                description="Event notification and subscription pattern",
                files=observer_files,
                confidence=min(confidence, 1.0),
                examples=[f"Observer patterns found in {len(observer_files)} files"]
            )
        
        return None
    
    def _detect_singleton_pattern(self, root_path: Path) -> Optional[ArchitecturalPattern]:
        """Detect Singleton pattern."""
        singleton_files = []
        confidence = 0.0
        
        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Look for singleton pattern indicators
                singleton_indicators = [
                    r'def.*__new__.*\(',
                    r'_instance.*=.*None',
                    r'class.*Singleton.*:',
                    r'@.*singleton',
                    r'if.*not.*hasattr.*instance'
                ]
                
                for pattern in singleton_indicators:
                    if re.search(pattern, content, re.IGNORECASE):
                        if str(py_file) not in singleton_files:
                            singleton_files.append(str(py_file))
                        confidence += 0.2
                        
            except Exception:
                continue
        
        if singleton_files and confidence > 0.3:
            return ArchitecturalPattern(
                name="Singleton Pattern",
                description="Single instance creation pattern",
                files=singleton_files,
                confidence=min(confidence, 1.0),
                examples=[f"Singleton patterns found in {len(singleton_files)} files"]
            )
        
        return None

    def _analyze_design_principles(self, root_path: Path) -> Dict[str, Any]:
        """Analyze adherence to SOLID and other design principles."""
        principles = {
            "single_responsibility": self._check_single_responsibility(root_path),
            "dry_principle": self._check_dry_principle(root_path),
            "naming_conventions": self._analyze_naming_conventions(root_path)
        }

        return principles

    def _check_single_responsibility(self, root_path: Path) -> Dict[str, Any]:
        """Check Single Responsibility Principle adherence."""
        violations = []
        score = 1.0

        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        # Count different types of responsibilities
                        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]

                        # Simple heuristic: too many methods might indicate multiple responsibilities
                        if len(methods) > 15:
                            violations.append({
                                "file": str(py_file),
                                "class": node.name,
                                "issue": f"Class has {len(methods)} methods, possibly multiple responsibilities",
                                "line": node.lineno
                            })
                            score -= 0.1

            except Exception:
                continue

        return {
            "score": max(score, 0.0),
            "violations": violations,
            "description": "Classes should have only one reason to change"
        }

    def _check_dry_principle(self, root_path: Path) -> Dict[str, Any]:
        """Check Don't Repeat Yourself principle."""
        code_blocks = defaultdict(list)
        violations = []
        score = 1.0

        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                # Look for similar code blocks (simplified)
                for i in range(len(lines) - 3):
                    block = ''.join(lines[i:i+4]).strip()
                    if len(block) > 50:  # Only consider substantial blocks
                        code_blocks[block].append((str(py_file), i+1))

            except Exception:
                continue

        # Find duplicated blocks
        for block, locations in code_blocks.items():
            if len(locations) > 1:
                violations.append({
                    "code_block": block[:100] + "..." if len(block) > 100 else block,
                    "locations": locations,
                    "duplication_count": len(locations)
                })
                score -= 0.05

        return {
            "score": max(score, 0.0),
            "violations": violations[:10],  # Limit to top 10
            "description": "Avoid code duplication"
        }

    def _analyze_naming_conventions(self, root_path: Path) -> Dict[str, Any]:
        """Analyze naming convention adherence."""
        naming_analysis = {
            "snake_case_files": 0,
            "camel_case_classes": 0,
            "violations": [],
            "score": 1.0
        }

        for py_file in root_path.rglob("*.py"):
            # Check file naming
            file_name = py_file.stem
            if re.match(r'^[a-z][a-z0-9_]*$', file_name):
                naming_analysis["snake_case_files"] += 1
            else:
                naming_analysis["violations"].append({
                    "type": "file",
                    "name": file_name,
                    "file": str(py_file),
                    "issue": "Non-standard file naming"
                })
                naming_analysis["score"] -= 0.05

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                            naming_analysis["camel_case_classes"] += 1
                        else:
                            naming_analysis["violations"].append({
                                "type": "class",
                                "name": node.name,
                                "file": str(py_file),
                                "line": node.lineno,
                                "issue": "Class should use PascalCase"
                            })
                            naming_analysis["score"] -= 0.03

            except Exception:
                continue

        return naming_analysis

    def _analyze_code_organization(self, root_path: Path) -> Dict[str, Any]:
        """Analyze code organization and structure."""
        return {
            "directory_depth": self._calculate_directory_depth(root_path),
            "file_distribution": self._analyze_file_distribution(root_path),
            "module_structure": self._analyze_module_structure(root_path)
        }

    def _calculate_directory_depth(self, root_path: Path) -> int:
        """Calculate maximum directory depth."""
        max_depth = 0
        for item in root_path.rglob("*.py"):
            depth = len(item.relative_to(root_path).parts) - 1
            max_depth = max(max_depth, depth)
        return max_depth

    def _analyze_file_distribution(self, root_path: Path) -> Dict[str, int]:
        """Analyze distribution of files across directories."""
        distribution = defaultdict(int)
        for py_file in root_path.rglob("*.py"):
            parent_dir = py_file.parent.name
            distribution[parent_dir] += 1
        return dict(distribution)

    def _analyze_module_structure(self, root_path: Path) -> Dict[str, Any]:
        """Analyze module structure and organization."""
        modules = {}
        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                module_info = {
                    "classes": len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]),
                    "functions": len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]),
                    "imports": len([n for n in ast.walk(tree) if isinstance(n, (ast.Import, ast.ImportFrom))]),
                    "lines": len(content.splitlines())
                }

                modules[str(py_file.relative_to(root_path))] = module_info

            except Exception:
                continue

        return modules

    def _analyze_dependency_structure(self, root_path: Path) -> DependencyAnalysis:
        """Analyze dependency structure and relationships."""
        direct_deps = set()
        imports_map = defaultdict(set)

        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                file_key = str(py_file.relative_to(root_path))

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            direct_deps.add(alias.name)
                            imports_map[file_key].add(alias.name)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            direct_deps.add(node.module)
                            imports_map[file_key].add(node.module)

            except Exception:
                continue

        # Detect circular dependencies (simplified)
        circular_deps = self._detect_circular_dependencies(imports_map)

        return DependencyAnalysis(
            direct_dependencies=direct_deps,
            transitive_dependencies=set(),  # Would need more complex analysis
            circular_dependencies=circular_deps,
            unused_imports=[],  # Would need usage analysis
            missing_dependencies=[],  # Would need import resolution
            dependency_violations=[],
            coupling_metrics={}
        )

    def _detect_circular_dependencies(self, imports_map: Dict[str, Set[str]]) -> List[List[str]]:
        """Detect circular dependencies between modules."""
        # Simplified circular dependency detection
        circular = []

        for file1, deps1 in imports_map.items():
            for file2, deps2 in imports_map.items():
                if file1 != file2:
                    # Check if they import each other
                    file1_module = Path(file1).stem
                    file2_module = Path(file2).stem

                    if file2_module in deps1 and file1_module in deps2:
                        cycle = [file1, file2]
                        if cycle not in circular and [file2, file1] not in circular:
                            circular.append(cycle)

        return circular

    def _calculate_quality_metrics(self, root_path: Path) -> CodeQualityMetrics:
        """Calculate comprehensive code quality metrics."""
        total_complexity = 0
        total_functions = 0
        total_lines = 0
        documented_functions = 0

        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)
                total_lines += len(content.splitlines())

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1

                        # Calculate cyclomatic complexity (simplified)
                        complexity = self._calculate_cyclomatic_complexity(node)
                        total_complexity += complexity

                        # Check documentation
                        if ast.get_docstring(node):
                            documented_functions += 1

            except Exception:
                continue

        avg_complexity = total_complexity / max(total_functions, 1)
        doc_coverage = documented_functions / max(total_functions, 1)

        return CodeQualityMetrics(
            cyclomatic_complexity=avg_complexity,
            maintainability_index=max(0, 171 - 5.2 * avg_complexity - 0.23 * total_lines/1000),
            technical_debt_ratio=max(0, (avg_complexity - 10) / 10) if avg_complexity > 10 else 0,
            test_coverage_estimate=0.0,  # Would need test analysis
            documentation_coverage=doc_coverage,
            code_duplication_ratio=0.0,  # Would need duplication analysis
            dependency_coupling=0.0,  # Would need coupling analysis
            cohesion_score=0.8  # Placeholder
        )

    def _calculate_cyclomatic_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity for a function."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1

        return complexity

    def _identify_refactoring_opportunities(self, root_path: Path) -> List[RefactoringOpportunity]:
        """Identify refactoring opportunities in the codebase."""
        opportunities = []

        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Check for long functions
                        func_lines = (node.end_lineno or node.lineno) - node.lineno
                        if func_lines > 50:
                            opportunities.append(RefactoringOpportunity(
                                type="extract_method",
                                description=f"Function '{node.name}' is {func_lines} lines long",
                                file_path=str(py_file),
                                line_range=(node.lineno, node.end_lineno or node.lineno),
                                impact_level="medium",
                                estimated_effort="medium",
                                benefits=["Improved readability", "Better testability"],
                                risks=["Potential breaking changes"]
                            ))

                    elif isinstance(node, ast.ClassDef):
                        # Check for large classes
                        methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                        if len(methods) > 20:
                            opportunities.append(RefactoringOpportunity(
                                type="extract_class",
                                description=f"Class '{node.name}' has {len(methods)} methods",
                                file_path=str(py_file),
                                line_range=(node.lineno, node.end_lineno or node.lineno),
                                impact_level="high",
                                estimated_effort="large",
                                benefits=["Better separation of concerns", "Improved maintainability"],
                                risks=["Significant refactoring required"]
                            ))

            except Exception:
                continue

        return opportunities[:10]  # Limit to top 10

    def _assess_technical_debt(self, root_path: Path) -> Dict[str, Any]:
        """Assess technical debt in the codebase."""
        debt_indicators = {
            "todo_comments": 0,
            "fixme_comments": 0,
            "hack_comments": 0,
            "complex_functions": 0,
            "large_files": 0,
            "debt_score": 0.0
        }

        for py_file in root_path.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Count debt indicators in comments
                debt_indicators["todo_comments"] += len(re.findall(r'#.*TODO', content, re.IGNORECASE))
                debt_indicators["fixme_comments"] += len(re.findall(r'#.*FIXME', content, re.IGNORECASE))
                debt_indicators["hack_comments"] += len(re.findall(r'#.*HACK', content, re.IGNORECASE))

                # Check file size
                lines = len(content.splitlines())
                if lines > 500:
                    debt_indicators["large_files"] += 1

                # Check function complexity
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        complexity = self._calculate_cyclomatic_complexity(node)
                        if complexity > 15:
                            debt_indicators["complex_functions"] += 1

            except Exception:
                continue

        # Calculate overall debt score
        total_indicators = sum([
            debt_indicators["todo_comments"],
            debt_indicators["fixme_comments"],
            debt_indicators["hack_comments"],
            debt_indicators["complex_functions"],
            debt_indicators["large_files"]
        ])

        debt_indicators["debt_score"] = min(total_indicators / 10.0, 1.0)

        return debt_indicators

    def _calculate_maintainability_score(self, root_path: Path) -> float:
        """Calculate overall maintainability score."""
        quality_metrics = self._calculate_quality_metrics(root_path)
        design_principles = self._analyze_design_principles(root_path)
        tech_debt = self._assess_technical_debt(root_path)

        # Weighted average of different factors
        maintainability = (
            (1.0 - quality_metrics.technical_debt_ratio) * 0.3 +
            quality_metrics.documentation_coverage * 0.2 +
            design_principles["single_responsibility"]["score"] * 0.2 +
            design_principles["dry_principle"]["score"] * 0.15 +
            design_principles["naming_conventions"]["score"] * 0.15
        )

        return max(0.0, min(1.0, maintainability))


def code_comprehension_tool() -> FunctionTool:
    """
    Create a tool for code comprehension and architectural analysis.
    """

    def analyze_codebase_architecture(
        root_path: str,
        include_patterns: bool = True,
        include_quality: bool = True,
        include_refactoring: bool = True
    ) -> str:
        """
        Perform comprehensive architectural analysis of a codebase with professional SWE-level insights.

        Args:
            root_path: Root directory of the codebase to analyze
            include_patterns: Whether to include architectural pattern detection
            include_quality: Whether to include code quality metrics
            include_refactoring: Whether to include refactoring opportunities

        Returns:
            Comprehensive architectural analysis report
        """
        try:
            comprehension = AdvancedCodeComprehension()
            analysis = comprehension.analyze_codebase_architecture(root_path)

            result_lines = [
                "🏗️  Advanced Codebase Architecture Analysis",
                "=" * 50,
                f"📁 Analyzing: {root_path}",
                ""
            ]

            # Architectural Patterns
            if include_patterns and analysis.get("architectural_patterns"):
                result_lines.extend([
                    "🎯 Architectural Patterns Detected:",
                    "-" * 35
                ])

                for pattern in analysis["architectural_patterns"]:
                    result_lines.extend([
                        f"📐 {pattern.name}",
                        f"   Description: {pattern.description}",
                        f"   Confidence: {pattern.confidence:.2f}",
                        f"   Files: {len(pattern.files)}",
                        f"   Examples: {', '.join(pattern.examples[:2])}",
                        ""
                    ])

            # Design Principles
            if analysis.get("design_principles"):
                result_lines.extend([
                    "⚖️  Design Principles Analysis:",
                    "-" * 30
                ])

                principles = analysis["design_principles"]
                for principle_name, principle_data in principles.items():
                    if isinstance(principle_data, dict) and "score" in principle_data:
                        score = principle_data["score"]
                        emoji = "✅" if score > 0.8 else "⚠️" if score > 0.6 else "❌"
                        result_lines.append(
                            f"{emoji} {principle_name.replace('_', ' ').title()}: {score:.2f}"
                        )

                        if principle_data.get("violations"):
                            violation_count = len(principle_data["violations"])
                            result_lines.append(f"   Violations: {violation_count}")

                result_lines.append("")

            # Code Quality Metrics
            if include_quality and analysis.get("quality_metrics"):
                metrics = analysis["quality_metrics"]
                result_lines.extend([
                    "📊 Code Quality Metrics:",
                    "-" * 25,
                    f"🔄 Cyclomatic Complexity: {metrics.cyclomatic_complexity:.2f}",
                    f"🛠️  Maintainability Index: {metrics.maintainability_index:.2f}",
                    f"📚 Documentation Coverage: {metrics.documentation_coverage:.2%}",
                    f"💸 Technical Debt Ratio: {metrics.technical_debt_ratio:.2%}",
                    f"🔗 Cohesion Score: {metrics.cohesion_score:.2f}",
                    ""
                ])

            # Refactoring Opportunities
            if include_refactoring and analysis.get("refactoring_opportunities"):
                opportunities = analysis["refactoring_opportunities"]
                if opportunities:
                    result_lines.extend([
                        "🔧 Refactoring Opportunities:",
                        "-" * 28
                    ])

                    for opp in opportunities[:5]:  # Show top 5
                        impact_emoji = {"low": "🟢", "medium": "🟡", "high": "🔴"}.get(opp.impact_level, "⚪")
                        result_lines.extend([
                            f"{impact_emoji} {opp.type.replace('_', ' ').title()}",
                            f"   📄 File: {Path(opp.file_path).name}",
                            f"   📝 Description: {opp.description}",
                            f"   ⚡ Impact: {opp.impact_level} | Effort: {opp.estimated_effort}",
                            f"   ✅ Benefits: {', '.join(opp.benefits[:2])}",
                            ""
                        ])

            # Technical Debt Assessment
            if analysis.get("technical_debt"):
                debt = analysis["technical_debt"]
                debt_score = debt.get("debt_score", 0)
                debt_emoji = "🟢" if debt_score < 0.3 else "🟡" if debt_score < 0.7 else "🔴"

                result_lines.extend([
                    "💳 Technical Debt Assessment:",
                    "-" * 30,
                    f"{debt_emoji} Overall Debt Score: {debt_score:.2f}",
                    f"📝 TODO Comments: {debt.get('todo_comments', 0)}",
                    f"🔧 FIXME Comments: {debt.get('fixme_comments', 0)}",
                    f"⚡ Complex Functions: {debt.get('complex_functions', 0)}",
                    f"📄 Large Files: {debt.get('large_files', 0)}",
                    ""
                ])

            # Overall Maintainability Score
            if analysis.get("maintainability_score") is not None:
                score = analysis["maintainability_score"]
                score_emoji = "🟢" if score > 0.8 else "🟡" if score > 0.6 else "🔴"

                result_lines.extend([
                    "🎯 Overall Assessment:",
                    "-" * 20,
                    f"{score_emoji} Maintainability Score: {score:.2f}",
                    ""
                ])

                # Recommendations based on score
                if score < 0.6:
                    result_lines.extend([
                        "💡 Priority Recommendations:",
                        "   • Focus on reducing technical debt",
                        "   • Improve documentation coverage",
                        "   • Address complex functions and large files",
                        "   • Consider architectural refactoring"
                    ])
                elif score < 0.8:
                    result_lines.extend([
                        "💡 Improvement Suggestions:",
                        "   • Continue improving code quality metrics",
                        "   • Address remaining design principle violations",
                        "   • Consider minor refactoring opportunities"
                    ])
                else:
                    result_lines.extend([
                        "🎉 Excellent Codebase!",
                        "   • High maintainability score",
                        "   • Good adherence to design principles",
                        "   • Low technical debt"
                    ])

            return "\n".join(result_lines)

        except Exception as e:
            return f"Error during architectural analysis: {str(e)}"

    return FunctionTool(analyze_codebase_architecture)

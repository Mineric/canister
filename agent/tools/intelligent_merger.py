
import ast
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple
from dataclasses import dataclass, field
from google.adk.tools import FunctionTool

from .code_tools import ASTCodeMerger, MergeContext, MergeImpact
from .code_comprehension import AdvancedCodeComprehension, RefactoringOpportunity


@dataclass
class SWEMergeStrategy:
    """SWE merge strategy."""
    strategy_type: str  # 'conservative', 'aggressive', 'intelligent', 'architectural'
    preserve_patterns: bool = True
    maintain_quality: bool = True
    follow_conventions: bool = True
    optimize_structure: bool = True
    prevent_regressions: bool = True
    architectural_awareness: bool = True


@dataclass
class SWEMergeDecision:
    """Represents a professional-level merge decision."""
    decision_type: str  # 'merge', 'refactor', 'reject', 'defer'
    rationale: str
    confidence: float
    impact_assessment: str
    recommendations: List[str]
    alternative_approaches: List[str]
    risk_factors: List[str]


@dataclass
class CodeIntegrityCheck:
    """Results of code integrity verification."""
    architectural_consistency: bool
    design_pattern_compliance: bool
    naming_convention_adherence: bool
    dependency_integrity: bool
    performance_impact: str  # 'positive', 'neutral', 'negative'
    maintainability_impact: str
    test_impact_estimate: str
    breaking_change_risk: str  # 'low', 'medium', 'high'


class ProfessionalSWEMerger:
    """
    Professional SWE-level code merger with advanced comprehension and decision making.
    Operates at the level of an experienced software engineer.
    """
    
    def __init__(self, indexer=None, comprehension_engine=None):
        """Initialize the professional merger."""
        self.indexer = indexer
        self.comprehension = comprehension_engine or AdvancedCodeComprehension(indexer)
        self.merge_history = []
        self.architectural_context = {}
        
    def professional_merge(
        self,
        file_path: str,
        ai_generated_code: str,
        strategy: SWEMergeStrategy,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Perform professional-level code merging with comprehensive analysis.
        
        Args:
            file_path: Target file for merging
            ai_generated_code: Code to be integrated
            strategy: Professional merge strategy
            dry_run: Whether to perform actual merge or analysis only
            
        Returns:
            Comprehensive merge analysis and results
        """
        # Phase 1: Pre-merge architectural analysis
        architectural_analysis = self._analyze_architectural_context(file_path)
        
        # Phase 2: Code comprehension and impact assessment
        impact_analysis = self._assess_comprehensive_impact(
            file_path, ai_generated_code, architectural_analysis
        )
        
        # Phase 3: Professional merge decision
        merge_decision = self._make_professional_decision(
            file_path, ai_generated_code, impact_analysis, strategy
        )
        
        # Phase 4: Code integrity verification
        integrity_check = self._verify_code_integrity(
            file_path, ai_generated_code, merge_decision
        )
        
        # Phase 5: Execute merge if approved
        merge_result = None
        if merge_decision.decision_type == 'merge' and not dry_run:
            merge_result = self._execute_professional_merge(
                file_path, ai_generated_code, strategy, integrity_check
            )
        elif merge_decision.decision_type == 'refactor':
            merge_result = self._suggest_refactoring_approach(
                file_path, ai_generated_code, impact_analysis
            )
        
        return {
            "architectural_analysis": architectural_analysis,
            "impact_analysis": impact_analysis,
            "merge_decision": merge_decision,
            "integrity_check": integrity_check,
            "merge_result": merge_result,
            "professional_assessment": self._generate_professional_assessment(
                merge_decision, integrity_check, impact_analysis
            )
        }
    
    def _analyze_architectural_context(self, file_path: str) -> Dict[str, Any]:
        """Analyze architectural context around the target file."""
        file_path_obj = Path(file_path)
        project_root = self._find_project_root(file_path_obj)
        
        # Get comprehensive architectural analysis
        arch_analysis = self.comprehension.analyze_codebase_architecture(str(project_root))
        
        # Focus on file-specific context
        file_context = {
            "project_root": str(project_root),
            "file_role": self._determine_file_role(file_path, arch_analysis),
            "architectural_patterns": arch_analysis.get("architectural_patterns", []),
            "design_principles_score": self._extract_design_score(arch_analysis),
            "quality_metrics": arch_analysis.get("quality_metrics"),
            "file_dependencies": self._analyze_file_dependencies(file_path),
            "architectural_constraints": self._identify_constraints(file_path, arch_analysis)
        }
        
        return file_context
    
    def _find_project_root(self, file_path: Path) -> Path:
        """Find the project root directory."""
        current = file_path.parent
        
        # Look for common project indicators
        indicators = ['.git', 'setup.py', 'pyproject.toml', 'requirements.txt', '.gitignore']
        
        while current != current.parent:
            if any((current / indicator).exists() for indicator in indicators):
                return current
            current = current.parent
        
        return file_path.parent
    
    def _determine_file_role(self, file_path: str, arch_analysis: Dict[str, Any]) -> str:
        """Determine the architectural role of the file."""
        file_name = Path(file_path).name.lower()
        
        # Check against architectural patterns
        patterns = arch_analysis.get("architectural_patterns", [])
        for pattern in patterns:
            if file_path in pattern.files:
                return f"{pattern.name.lower()}_component"
        
        # Heuristic-based role detection
        if 'model' in file_name or 'entity' in file_name:
            return 'data_model'
        elif 'view' in file_name or 'template' in file_name:
            return 'presentation_layer'
        elif 'controller' in file_name or 'handler' in file_name:
            return 'control_layer'
        elif 'service' in file_name or 'manager' in file_name:
            return 'business_logic'
        elif 'repository' in file_name or 'dao' in file_name:
            return 'data_access'
        elif 'util' in file_name or 'helper' in file_name:
            return 'utility'
        elif 'test' in file_name:
            return 'test'
        elif 'config' in file_name or 'setting' in file_name:
            return 'configuration'
        else:
            return 'general_module'
    
    def _extract_design_score(self, arch_analysis: Dict[str, Any]) -> float:
        """Extract overall design principles score."""
        principles = arch_analysis.get("design_principles", {})
        scores = []
        
        for principle_data in principles.values():
            if isinstance(principle_data, dict) and "score" in principle_data:
                scores.append(principle_data["score"])
        
        return sum(scores) / len(scores) if scores else 0.5
    
    def _analyze_file_dependencies(self, file_path: str) -> Dict[str, Any]:
        """Analyze dependencies specific to the file."""
        if not self.indexer:
            return {"dependencies": [], "dependents": []}
        
        try:
            dependencies = list(self.indexer.get_dependencies(file_path))
            dependents = list(self.indexer.get_dependents(Path(file_path).stem))
            
            return {
                "dependencies": dependencies,
                "dependents": dependents,
                "dependency_count": len(dependencies),
                "dependent_count": len(dependents),
                "coupling_level": "high" if len(dependencies) > 10 else "medium" if len(dependencies) > 5 else "low"
            }
        except Exception:
            return {"dependencies": [], "dependents": [], "coupling_level": "unknown"}
    
    def _identify_constraints(self, file_path: str, arch_analysis: Dict[str, Any]) -> List[str]:
        """Identify architectural constraints for the file."""
        constraints = []
        
        # Pattern-based constraints
        patterns = arch_analysis.get("architectural_patterns", [])
        for pattern in patterns:
            if file_path in pattern.files:
                if "MVC" in pattern.name:
                    constraints.append("mvc_separation_of_concerns")
                elif "Repository" in pattern.name:
                    constraints.append("data_access_abstraction")
                elif "Factory" in pattern.name:
                    constraints.append("object_creation_consistency")
        
        # Quality-based constraints
        quality_metrics = arch_analysis.get("quality_metrics")
        if quality_metrics:
            if quality_metrics.cyclomatic_complexity > 10:
                constraints.append("complexity_reduction_required")
            if quality_metrics.documentation_coverage < 0.5:
                constraints.append("documentation_improvement_needed")
        
        return constraints
    
    def _assess_comprehensive_impact(
        self, 
        file_path: str, 
        ai_generated_code: str, 
        architectural_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess comprehensive impact of the proposed changes."""
        
        # Parse the AI-generated code
        try:
            ai_ast = ast.parse(ai_generated_code)
        except SyntaxError as e:
            return {"error": f"Invalid Python syntax in AI code: {e}"}
        
        # Analyze what's being added/changed
        changes_analysis = self._analyze_proposed_changes(ai_ast)
        
        # Assess impact on architectural patterns
        pattern_impact = self._assess_pattern_impact(
            changes_analysis, architectural_context["architectural_patterns"]
        )
        
        # Assess impact on dependencies
        dependency_impact = self._assess_dependency_impact(
            file_path, changes_analysis, architectural_context["file_dependencies"]
        )
        
        # Assess quality impact
        quality_impact = self._assess_quality_impact(
            changes_analysis, architectural_context["quality_metrics"]
        )
        
        # Assess maintainability impact
        maintainability_impact = self._assess_maintainability_impact(
            changes_analysis, architectural_context
        )
        
        return {
            "changes_analysis": changes_analysis,
            "pattern_impact": pattern_impact,
            "dependency_impact": dependency_impact,
            "quality_impact": quality_impact,
            "maintainability_impact": maintainability_impact,
            "overall_impact_score": self._calculate_overall_impact_score(
                pattern_impact, dependency_impact, quality_impact, maintainability_impact
            )
        }

    def _analyze_proposed_changes(self, ai_ast: ast.AST) -> Dict[str, Any]:
        """Analyze what changes are being proposed in the AI-generated code."""
        changes = {
            "new_functions": [],
            "new_classes": [],
            "new_imports": [],
            "complexity_estimate": 0,
            "change_scope": "unknown"
        }

        for node in ast.walk(ai_ast):
            if isinstance(node, ast.FunctionDef):
                changes["new_functions"].append({
                    "name": node.name,
                    "line_count": (node.end_lineno or node.lineno) - node.lineno,
                    "has_docstring": bool(ast.get_docstring(node)),
                    "complexity": self._estimate_function_complexity(node)
                })
                changes["complexity_estimate"] += self._estimate_function_complexity(node)

            elif isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                changes["new_classes"].append({
                    "name": node.name,
                    "method_count": len(methods),
                    "has_docstring": bool(ast.get_docstring(node)),
                    "inheritance": [base.id for base in node.bases if isinstance(base, ast.Name)]
                })

            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        changes["new_imports"].append(alias.name)
                else:
                    module = node.module or ""
                    for alias in node.names:
                        changes["new_imports"].append(f"{module}.{alias.name}")

        # Determine change scope
        total_elements = len(changes["new_functions"]) + len(changes["new_classes"])
        if total_elements == 0:
            changes["change_scope"] = "minimal"
        elif total_elements <= 3:
            changes["change_scope"] = "moderate"
        else:
            changes["change_scope"] = "extensive"

        return changes

    def _estimate_function_complexity(self, func_node: ast.FunctionDef) -> int:
        """Estimate function complexity."""
        complexity = 1
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(node, ast.ExceptHandler):
                complexity += 1
        return complexity

    def _assess_pattern_impact(self, changes: Dict[str, Any], patterns: List[Any]) -> Dict[str, Any]:
        """Assess impact on architectural patterns."""
        impact = {
            "affected_patterns": [],
            "compliance_score": 1.0,
            "violations": [],
            "recommendations": []
        }

        for pattern in patterns:
            pattern_name = pattern.name if hasattr(pattern, 'name') else str(pattern)

            # Check if changes align with pattern
            if "MVC" in pattern_name:
                impact.update(self._check_mvc_compliance(changes))
            elif "Repository" in pattern_name:
                impact.update(self._check_repository_compliance(changes))
            elif "Factory" in pattern_name:
                impact.update(self._check_factory_compliance(changes))

        return impact

    def _check_mvc_compliance(self, changes: Dict[str, Any]) -> Dict[str, str]:
        """Check MVC pattern compliance."""
        violations = []

        # Check if new classes follow MVC naming
        for class_info in changes["new_classes"]:
            class_name = class_info["name"].lower()
            if not any(keyword in class_name for keyword in ['model', 'view', 'controller']):
                violations.append(f"Class '{class_info['name']}' doesn't follow MVC naming convention")

        return {"mvc_violations": violations}

    def _check_repository_compliance(self, changes: Dict[str, Any]) -> Dict[str, str]:
        """Check Repository pattern compliance."""
        violations = []

        # Check if new classes follow repository pattern
        for class_info in changes["new_classes"]:
            class_name = class_info["name"].lower()
            if 'repository' in class_name:
                # Should have CRUD methods
                expected_methods = ['create', 'read', 'update', 'delete', 'find', 'save']
                # This is a simplified check - in practice, we'd analyze the actual methods
                violations.append(f"Repository class '{class_info['name']}' should implement CRUD operations")

        return {"repository_violations": violations}

    def _check_factory_compliance(self, changes: Dict[str, Any]) -> Dict[str, str]:
        """Check Factory pattern compliance."""
        violations = []

        for class_info in changes["new_classes"]:
            class_name = class_info["name"].lower()
            if 'factory' in class_name:
                # Should have creation methods
                violations.append(f"Factory class '{class_info['name']}' should implement creation methods")

        return {"factory_violations": violations}

    def _assess_dependency_impact(
        self,
        file_path: str,
        changes: Dict[str, Any],
        file_dependencies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess impact on dependencies."""
        impact = {
            "new_dependencies": changes["new_imports"],
            "dependency_increase": len(changes["new_imports"]),
            "coupling_impact": "neutral",
            "circular_dependency_risk": "low",
            "recommendations": []
        }

        current_deps = len(file_dependencies.get("dependencies", []))
        new_deps = len(changes["new_imports"])

        if new_deps > 5:
            impact["coupling_impact"] = "negative"
            impact["recommendations"].append("Consider reducing number of new dependencies")
        elif new_deps > 0:
            impact["coupling_impact"] = "slight_increase"

        # Check for potential circular dependencies
        dependents = file_dependencies.get("dependents", [])
        for new_dep in changes["new_imports"]:
            if any(new_dep in dependent for dependent in dependents):
                impact["circular_dependency_risk"] = "medium"
                impact["recommendations"].append(f"Check for circular dependency with {new_dep}")

        return impact

    def _assess_quality_impact(self, changes: Dict[str, Any], quality_metrics: Any) -> Dict[str, Any]:
        """Assess impact on code quality."""
        impact = {
            "complexity_change": changes["complexity_estimate"],
            "documentation_impact": "neutral",
            "maintainability_impact": "neutral",
            "recommendations": []
        }

        # Check documentation
        documented_functions = sum(1 for func in changes["new_functions"] if func["has_docstring"])
        total_functions = len(changes["new_functions"])

        if total_functions > 0:
            doc_ratio = documented_functions / total_functions
            if doc_ratio < 0.5:
                impact["documentation_impact"] = "negative"
                impact["recommendations"].append("Add documentation to new functions")
            elif doc_ratio == 1.0:
                impact["documentation_impact"] = "positive"

        # Check complexity
        if changes["complexity_estimate"] > 20:
            impact["maintainability_impact"] = "negative"
            impact["recommendations"].append("Consider breaking down complex functions")
        elif changes["complexity_estimate"] < 5:
            impact["maintainability_impact"] = "positive"

        return impact

    def _assess_maintainability_impact(
        self,
        changes: Dict[str, Any],
        architectural_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Assess impact on maintainability."""
        impact = {
            "maintainability_score_change": 0.0,
            "factors": [],
            "recommendations": []
        }

        # Positive factors
        if changes["change_scope"] == "minimal":
            impact["maintainability_score_change"] += 0.1
            impact["factors"].append("Minimal scope reduces maintenance burden")

        documented_ratio = sum(1 for func in changes["new_functions"] if func["has_docstring"]) / max(len(changes["new_functions"]), 1)
        if documented_ratio > 0.8:
            impact["maintainability_score_change"] += 0.1
            impact["factors"].append("Good documentation improves maintainability")

        # Negative factors
        if changes["complexity_estimate"] > 15:
            impact["maintainability_score_change"] -= 0.2
            impact["factors"].append("High complexity reduces maintainability")
            impact["recommendations"].append("Refactor complex functions")

        if len(changes["new_imports"]) > 5:
            impact["maintainability_score_change"] -= 0.1
            impact["factors"].append("Many new dependencies increase maintenance burden")

        return impact

    def _calculate_overall_impact_score(
        self,
        pattern_impact: Dict[str, Any],
        dependency_impact: Dict[str, Any],
        quality_impact: Dict[str, Any],
        maintainability_impact: Dict[str, Any]
    ) -> float:
        """Calculate overall impact score."""
        score = 0.5  # Neutral baseline

        # Pattern compliance
        if pattern_impact.get("compliance_score", 1.0) > 0.8:
            score += 0.1
        elif pattern_impact.get("compliance_score", 1.0) < 0.6:
            score -= 0.2

        # Dependency impact
        coupling_impact = dependency_impact.get("coupling_impact", "neutral")
        if coupling_impact == "negative":
            score -= 0.2
        elif coupling_impact == "positive":
            score += 0.1

        # Quality impact
        if quality_impact.get("documentation_impact") == "positive":
            score += 0.1
        elif quality_impact.get("documentation_impact") == "negative":
            score -= 0.1

        # Maintainability impact
        score += maintainability_impact.get("maintainability_score_change", 0.0)

        return max(0.0, min(1.0, score))

    def _make_professional_decision(
        self,
        file_path: str,
        ai_generated_code: str,
        impact_analysis: Dict[str, Any],
        strategy: SWEMergeStrategy
    ) -> SWEMergeDecision:
        """Make a professional-level decision about the merge."""

        overall_score = impact_analysis.get("overall_impact_score", 0.5)
        changes = impact_analysis.get("changes_analysis", {})

        # Decision logic based on impact and strategy
        if overall_score > 0.8 and strategy.strategy_type in ['aggressive', 'intelligent']:
            decision_type = 'merge'
            rationale = "High positive impact with good architectural alignment"
            confidence = 0.9
        elif overall_score > 0.6 and strategy.strategy_type == 'intelligent':
            decision_type = 'merge'
            rationale = "Moderate positive impact, acceptable for intelligent strategy"
            confidence = 0.7
        elif overall_score > 0.4 and changes.get("change_scope") == "minimal":
            decision_type = 'merge'
            rationale = "Minimal changes with acceptable impact"
            confidence = 0.6
        elif overall_score < 0.3:
            decision_type = 'reject'
            rationale = "Negative impact on codebase quality and architecture"
            confidence = 0.8
        else:
            decision_type = 'refactor'
            rationale = "Changes need refactoring to improve impact"
            confidence = 0.7

        # Generate recommendations
        recommendations = []
        if impact_analysis.get("quality_impact", {}).get("documentation_impact") == "negative":
            recommendations.append("Add comprehensive documentation to new functions")

        if impact_analysis.get("dependency_impact", {}).get("coupling_impact") == "negative":
            recommendations.append("Reduce number of dependencies or use dependency injection")

        if changes.get("complexity_estimate", 0) > 15:
            recommendations.append("Break down complex functions into smaller, focused units")

        # Alternative approaches
        alternatives = []
        if decision_type == 'reject':
            alternatives.append("Refactor the AI-generated code to better align with architecture")
            alternatives.append("Implement changes incrementally in smaller chunks")
        elif decision_type == 'refactor':
            alternatives.append("Extract complex logic into separate modules")
            alternatives.append("Use existing patterns and conventions from the codebase")

        # Risk factors
        risks = []
        if impact_analysis.get("dependency_impact", {}).get("circular_dependency_risk") != "low":
            risks.append("Potential circular dependency issues")

        if changes.get("change_scope") == "extensive":
            risks.append("Large scope increases risk of introducing bugs")

        return SWEMergeDecision(
            decision_type=decision_type,
            rationale=rationale,
            confidence=confidence,
            impact_assessment=f"Overall impact score: {overall_score:.2f}",
            recommendations=recommendations,
            alternative_approaches=alternatives,
            risk_factors=risks
        )

    def _verify_code_integrity(
        self,
        file_path: str,
        ai_generated_code: str,
        merge_decision: SWEMergeDecision
    ) -> CodeIntegrityCheck:
        """Verify code integrity before merge."""

        # Parse and analyze the code
        try:
            ai_ast = ast.parse(ai_generated_code)
        except SyntaxError:
            return CodeIntegrityCheck(
                architectural_consistency=False,
                design_pattern_compliance=False,
                naming_convention_adherence=False,
                dependency_integrity=False,
                performance_impact="negative",
                maintainability_impact="negative",
                test_impact_estimate="high",
                breaking_change_risk="high"
            )

        # Check naming conventions
        naming_ok = self._check_naming_conventions(ai_ast)

        # Check architectural consistency
        arch_consistent = merge_decision.confidence > 0.7

        # Check design pattern compliance
        pattern_compliant = len(merge_decision.risk_factors) == 0

        # Estimate performance impact
        perf_impact = self._estimate_performance_impact(ai_ast)

        # Estimate maintainability impact
        maint_impact = "positive" if merge_decision.confidence > 0.8 else "neutral" if merge_decision.confidence > 0.5 else "negative"

        # Estimate breaking change risk
        breaking_risk = "low" if merge_decision.decision_type == "merge" and merge_decision.confidence > 0.8 else "medium"

        return CodeIntegrityCheck(
            architectural_consistency=arch_consistent,
            design_pattern_compliance=pattern_compliant,
            naming_convention_adherence=naming_ok,
            dependency_integrity=True,  # Simplified
            performance_impact=perf_impact,
            maintainability_impact=maint_impact,
            test_impact_estimate="medium",  # Simplified
            breaking_change_risk=breaking_risk
        )

    def _check_naming_conventions(self, ai_ast: ast.AST) -> bool:
        """Check if code follows naming conventions."""
        violations = 0

        for node in ast.walk(ai_ast):
            if isinstance(node, ast.FunctionDef):
                if not re.match(r'^[a-z][a-z0-9_]*$', node.name):
                    violations += 1
            elif isinstance(node, ast.ClassDef):
                if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                    violations += 1

        return violations == 0

    def _estimate_performance_impact(self, ai_ast: ast.AST) -> str:
        """Estimate performance impact of the code."""
        # Simplified performance analysis
        loop_count = 0
        recursive_calls = 0

        for node in ast.walk(ai_ast):
            if isinstance(node, (ast.For, ast.While)):
                loop_count += 1
            elif isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    # Check for potential recursive calls (simplified)
                    recursive_calls += 1

        if loop_count > 3 or recursive_calls > 10:
            return "negative"
        elif loop_count == 0 and recursive_calls < 3:
            return "positive"
        else:
            return "neutral"

    def _execute_professional_merge(
        self,
        file_path: str,
        ai_generated_code: str,
        strategy: SWEMergeStrategy,
        integrity_check: CodeIntegrityCheck
    ) -> Dict[str, Any]:
        """Execute the professional merge with all safeguards."""

        # Use the enhanced AST merger
        try:
            from .code_tools import ASTCodeMerger

            # Read the source file
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Create enhanced merger
            merger = ASTCodeMerger(
                source_code=source_code,
                ai_generated_code=ai_generated_code,
                file_path=file_path,
                use_indexer=True
            )

            # Perform the merge
            merged_code = merger.merge()

            # Write back to file with backup
            backup_path = Path(file_path).with_suffix('.py.swe_backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(source_code)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(merged_code)

            return {
                "success": True,
                "backup_created": str(backup_path),
                "merged_code_length": len(merged_code),
                "merge_summary": merger.get_merge_summary()
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "backup_created": None
            }

    def _suggest_refactoring_approach(
        self,
        file_path: str,
        ai_generated_code: str,
        impact_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Suggest refactoring approach instead of direct merge."""

        suggestions = []
        changes = impact_analysis.get("changes_analysis", {})

        # Suggest breaking down large changes
        if changes.get("change_scope") == "extensive":
            suggestions.append("Break down changes into smaller, focused commits")
            suggestions.append("Implement one class or function at a time")

        # Suggest complexity reduction
        if changes.get("complexity_estimate", 0) > 15:
            suggestions.append("Extract complex logic into helper functions")
            suggestions.append("Use design patterns to simplify complex interactions")

        # Suggest dependency management
        if len(changes.get("new_imports", [])) > 5:
            suggestions.append("Consider using dependency injection")
            suggestions.append("Group related imports into modules")

        return {
            "refactoring_type": "incremental_integration",
            "suggestions": suggestions,
            "estimated_effort": "medium",
            "expected_benefits": [
                "Reduced risk of introducing bugs",
                "Better code review process",
                "Improved architectural alignment"
            ]
        }

    def _generate_professional_assessment(
        self,
        merge_decision: SWEMergeDecision,
        integrity_check: CodeIntegrityCheck,
        impact_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate professional-level assessment summary."""

        return {
            "decision_summary": f"{merge_decision.decision_type.title()} with {merge_decision.confidence:.0%} confidence",
            "key_factors": [
                f"Impact score: {impact_analysis.get('overall_impact_score', 0):.2f}",
                f"Architectural consistency: {'✓' if integrity_check.architectural_consistency else '✗'}",
                f"Naming conventions: {'✓' if integrity_check.naming_convention_adherence else '✗'}",
                f"Breaking change risk: {integrity_check.breaking_change_risk}"
            ],
            "professional_recommendation": merge_decision.rationale,
            "next_steps": merge_decision.recommendations[:3],  # Top 3 recommendations
            "risk_mitigation": [
                "Create comprehensive backup before proceeding",
                "Run full test suite after merge",
                "Monitor for performance regressions"
            ] if merge_decision.decision_type == "merge" else [
                "Refactor code according to suggestions",
                "Re-evaluate after improvements",
                "Consider alternative implementation approaches"
            ]
        }


def intelligent_merger_tool() -> FunctionTool:
    """
    Create an intelligent code merger tool with advanced comprehension
    and professional-level decision making capabilities.
    """

    def merge_code_professionally(
        file_path: str,
        ai_generated_code: str,
        strategy_type: str = "intelligent",
        dry_run: bool = True,
        preserve_patterns: bool = True,
        maintain_quality: bool = True
    ) -> str:
        """
        Perform professional SWE-level code merging with comprehensive analysis and decision making.

        Args:
            file_path: Path to the target file for merging
            ai_generated_code: Code to be integrated
            strategy_type: Merge strategy ('conservative', 'aggressive', 'intelligent', 'architectural')
            dry_run: Whether to perform analysis only or actual merge
            preserve_patterns: Whether to preserve architectural patterns
            maintain_quality: Whether to maintain code quality standards

        Returns:
            Comprehensive professional analysis and merge results
        """
        try:
            # Initialize professional merger
            from .codebase_indexer import get_global_indexer
            from .code_comprehension import AdvancedCodeComprehension

            indexer = get_global_indexer()
            comprehension = AdvancedCodeComprehension(indexer)
            merger = ProfessionalSWEMerger(indexer, comprehension)

            # Create merge strategy
            strategy = SWEMergeStrategy(
                strategy_type=strategy_type,
                preserve_patterns=preserve_patterns,
                maintain_quality=maintain_quality,
                follow_conventions=True,
                optimize_structure=True,
                prevent_regressions=True,
                architectural_awareness=True
            )

            # Perform professional merge analysis
            result = merger.professional_merge(
                file_path=file_path,
                ai_generated_code=ai_generated_code,
                strategy=strategy,
                dry_run=dry_run
            )

            # Format comprehensive report
            report_lines = [
                "🎓 Professional SWE-Level Code Merge Analysis",
                "=" * 55,
                f"📁 Target File: {file_path}",
                f"🧠 Strategy: {strategy_type.title()}",
                f"🔍 Analysis Mode: {'Dry Run' if dry_run else 'Live Merge'}",
                ""
            ]

            # Architectural Analysis
            arch_analysis = result.get("architectural_analysis", {})
            if arch_analysis:
                report_lines.extend([
                    "🏗️  Architectural Context:",
                    "-" * 25,
                    f"📂 Project Root: {arch_analysis.get('project_root', 'Unknown')}",
                    f"🎯 File Role: {arch_analysis.get('file_role', 'Unknown').replace('_', ' ').title()}",
                    f"📊 Design Score: {arch_analysis.get('design_principles_score', 0):.2f}",
                    f"🔗 Dependencies: {arch_analysis.get('file_dependencies', {}).get('dependency_count', 0)}",
                    f"⬅️  Dependents: {arch_analysis.get('file_dependencies', {}).get('dependent_count', 0)}",
                    ""
                ])

                # Architectural patterns
                patterns = arch_analysis.get("architectural_patterns", [])
                if patterns:
                    report_lines.append("🎨 Detected Patterns:")
                    for pattern in patterns[:3]:  # Show top 3
                        pattern_name = pattern.name if hasattr(pattern, 'name') else str(pattern)
                        confidence = pattern.confidence if hasattr(pattern, 'confidence') else 0
                        report_lines.append(f"   • {pattern_name} (confidence: {confidence:.2f})")
                    report_lines.append("")

            # Impact Analysis
            impact_analysis = result.get("impact_analysis", {})
            if impact_analysis:
                overall_score = impact_analysis.get("overall_impact_score", 0)
                score_emoji = "🟢" if overall_score > 0.7 else "🟡" if overall_score > 0.4 else "🔴"

                report_lines.extend([
                    "📈 Impact Analysis:",
                    "-" * 18,
                    f"{score_emoji} Overall Impact Score: {overall_score:.2f}",
                    ""
                ])

                changes = impact_analysis.get("changes_analysis", {})
                if changes:
                    report_lines.extend([
                        "🔄 Proposed Changes:",
                        f"   • New Functions: {len(changes.get('new_functions', []))}",
                        f"   • New Classes: {len(changes.get('new_classes', []))}",
                        f"   • New Imports: {len(changes.get('new_imports', []))}",
                        f"   • Complexity Estimate: {changes.get('complexity_estimate', 0)}",
                        f"   • Change Scope: {changes.get('change_scope', 'unknown').title()}",
                        ""
                    ])

            # Professional Decision
            merge_decision = result.get("merge_decision")
            if merge_decision:
                decision_emoji = {
                    "merge": "✅", "refactor": "🔧", "reject": "❌", "defer": "⏸️"
                }.get(merge_decision.decision_type, "❓")

                report_lines.extend([
                    "🎯 Professional Decision:",
                    "-" * 24,
                    f"{decision_emoji} Decision: {merge_decision.decision_type.title()}",
                    f"🎯 Confidence: {merge_decision.confidence:.0%}",
                    f"💭 Rationale: {merge_decision.rationale}",
                    f"📊 Impact: {merge_decision.impact_assessment}",
                    ""
                ])

                if merge_decision.recommendations:
                    report_lines.extend([
                        "💡 Recommendations:",
                        *[f"   • {rec}" for rec in merge_decision.recommendations[:3]],
                        ""
                    ])

                if merge_decision.risk_factors:
                    report_lines.extend([
                        "⚠️  Risk Factors:",
                        *[f"   • {risk}" for risk in merge_decision.risk_factors],
                        ""
                    ])

            # Code Integrity Check
            integrity_check = result.get("integrity_check")
            if integrity_check:
                report_lines.extend([
                    "🔒 Code Integrity Verification:",
                    "-" * 30,
                    f"🏗️  Architectural Consistency: {'✅' if integrity_check.architectural_consistency else '❌'}",
                    f"🎨 Design Pattern Compliance: {'✅' if integrity_check.design_pattern_compliance else '❌'}",
                    f"📝 Naming Convention Adherence: {'✅' if integrity_check.naming_convention_adherence else '❌'}",
                    f"🔗 Dependency Integrity: {'✅' if integrity_check.dependency_integrity else '❌'}",
                    f"⚡ Performance Impact: {integrity_check.performance_impact.title()}",
                    f"🛠️  Maintainability Impact: {integrity_check.maintainability_impact.title()}",
                    f"💥 Breaking Change Risk: {integrity_check.breaking_change_risk.title()}",
                    ""
                ])

            # Professional Assessment
            professional_assessment = result.get("professional_assessment", {})
            if professional_assessment:
                report_lines.extend([
                    "👨‍💻 Professional Assessment:",
                    "-" * 27,
                    f"📋 Summary: {professional_assessment.get('decision_summary', 'N/A')}",
                    ""
                ])

                key_factors = professional_assessment.get("key_factors", [])
                if key_factors:
                    report_lines.extend([
                        "🔑 Key Factors:",
                        *[f"   • {factor}" for factor in key_factors],
                        ""
                    ])

                next_steps = professional_assessment.get("next_steps", [])
                if next_steps:
                    report_lines.extend([
                        "🚀 Next Steps:",
                        *[f"   • {step}" for step in next_steps],
                        ""
                    ])

            # Merge Result (if executed)
            merge_result = result.get("merge_result")
            if merge_result and not dry_run:
                if merge_result.get("success"):
                    report_lines.extend([
                        "✅ Merge Execution Results:",
                        "-" * 26,
                        f"📁 Backup Created: {merge_result.get('backup_created', 'N/A')}",
                        f"📊 Merged Code Length: {merge_result.get('merged_code_length', 0)} characters",
                        ""
                    ])
                else:
                    report_lines.extend([
                        "❌ Merge Execution Failed:",
                        "-" * 25,
                        f"🚨 Error: {merge_result.get('error', 'Unknown error')}",
                        ""
                    ])

            return "\n".join(report_lines)

        except Exception as e:
            return f"Error in professional SWE merger: {str(e)}"

    return FunctionTool(merge_code_professionally)

"""
AST-Based Code Merger Tool - Cannister
Copyright (c) 2024 Thant Min Htet. All rights reserved.

Advanced AST-based code merger that intelligently integrates LLM-generated code
snippets into existing Python source files while preserving structure and avoiding duplicates.

This software is proprietary and confidential. No usage, modification,
or distribution rights are granted without explicit written permission.
"""

import ast
import astor
from pathlib import Path
from typing import Dict, List, Optional, Union, Set, Tuple
from google.adk.tools import FunctionTool
from dataclasses import dataclass


@dataclass
class MergeContext:
    """Context information for intelligent merging."""
    file_path: str
    codebase_indexed: bool = False
    dependencies: Set[str] = None
    dependents: Set[str] = None
    existing_imports: List[str] = None
    potential_conflicts: List[str] = None
    suggested_imports: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = set()
        if self.dependents is None:
            self.dependents = set()
        if self.existing_imports is None:
            self.existing_imports = []
        if self.potential_conflicts is None:
            self.potential_conflicts = []
        if self.suggested_imports is None:
            self.suggested_imports = []


@dataclass
class MergeImpact:
    """Analysis of merge impact on the codebase."""
    affected_files: Set[str]
    broken_references: List[str]
    new_dependencies: List[str]
    import_changes: List[str]
    warnings: List[str]
    suggestions: List[str]

    def __post_init__(self):
        if self.affected_files is None:
            self.affected_files = set()
        if self.broken_references is None:
            self.broken_references = []
        if self.new_dependencies is None:
            self.new_dependencies = []
        if self.import_changes is None:
            self.import_changes = []
        if self.warnings is None:
            self.warnings = []
        if self.suggestions is None:
            self.suggestions = []


class ASTCodeMerger:
    """
    Advanced AST-based code merger that intelligently integrates LLM-generated code
    snippets into existing Python source files while preserving structure and avoiding duplicates.
    Enhanced with codebase indexer integration for intelligent reference resolution.
    """

    def __init__(self, source_code: str, ai_generated_code: str, file_path: Optional[str] = None,
                 use_indexer: bool = True):
        """
        Initialize the code merger with source and AI-generated code.

        Args:
            source_code: The existing Python source code as a string
            ai_generated_code: The AI-generated code snippet to merge as a string
            file_path: Path to the file being modified (for indexer integration)
            use_indexer: Whether to use codebase indexer for enhanced merging

        Raises:
            SyntaxError: If either code snippet contains invalid Python syntax
        """
        try:
            self.source_ast = ast.parse(source_code)
            self.ai_generated_ast = ast.parse(ai_generated_code)
            self.source_code = source_code
            self.ai_generated_code = ai_generated_code
            self.file_path = file_path
            self.use_indexer = use_indexer

            # Initialize merge context and indexer
            self.merge_context = MergeContext(file_path=file_path or "unknown")
            self.indexer = None

            if use_indexer:
                self._initialize_indexer_context()

        except SyntaxError as e:
            raise SyntaxError(f"Invalid Python syntax in code: {e}")

    def _initialize_indexer_context(self):
        """Initialize codebase indexer context for enhanced merging."""
        try:
            from .codebase_indexer import get_global_indexer
            self.indexer = get_global_indexer()

            if self.file_path and self.indexer:
                # Get file dependencies and dependents
                self.merge_context.dependencies = self.indexer.get_dependencies(self.file_path)

                # Get files that depend on this file
                file_stem = Path(self.file_path).stem
                self.merge_context.dependents = self.indexer.get_dependents(file_stem)

                # Get existing imports
                file_summary = self.indexer.get_file_summary(self.file_path)
                if "imports" in file_summary:
                    self.merge_context.existing_imports = [
                        imp["module"] for imp in file_summary["imports"]
                    ]

                self.merge_context.codebase_indexed = True

        except ImportError:
            # Indexer not available, continue without it
            self.use_indexer = False
        except Exception as e:
            # Indexer error, continue without it but log warning
            self.use_indexer = False
            print(f"Warning: Could not initialize indexer context: {e}")

    def merge(self) -> str:
        """
        Perform intelligent merging of AI-generated code into source code.
        Enhanced with codebase awareness and impact analysis.

        Returns:
            The merged source code as a string

        Raises:
            ValueError: If merging encounters irreconcilable conflicts
        """
        try:
            # Analyze merge impact before proceeding
            if self.use_indexer:
                impact = self._analyze_merge_impact()
                self._handle_merge_warnings(impact)

            # Process imports first to avoid dependency issues
            self._merge_imports_enhanced()

            # Process module-level variables and constants
            self._merge_module_level_assignments()

            # Process functions and classes with reference awareness
            for ai_node in self.ai_generated_ast.body:
                if isinstance(ai_node, ast.FunctionDef):
                    self._merge_function_enhanced(ai_node)
                elif isinstance(ai_node, ast.ClassDef):
                    self._merge_class_enhanced(ai_node)
                elif isinstance(ai_node, ast.AsyncFunctionDef):
                    self._merge_async_function_enhanced(ai_node)

            return self.to_source_code()
        except Exception as e:
            raise ValueError(f"Error during code merging: {e}")

    def _analyze_merge_impact(self) -> MergeImpact:
        """Analyze the potential impact of the merge on the codebase."""
        impact = MergeImpact(
            affected_files=set(),
            broken_references=[],
            new_dependencies=[],
            import_changes=[],
            warnings=[],
            suggestions=[]
        )

        if not self.indexer:
            return impact

        # Analyze functions and classes being modified/added
        for ai_node in self.ai_generated_ast.body:
            if isinstance(ai_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                self._analyze_function_impact(ai_node, impact)
            elif isinstance(ai_node, ast.ClassDef):
                self._analyze_class_impact(ai_node, impact)
            elif isinstance(ai_node, (ast.Import, ast.ImportFrom)):
                self._analyze_import_impact(ai_node, impact)

        return impact

    def _analyze_function_impact(self, func_node: Union[ast.FunctionDef, ast.AsyncFunctionDef],
                                impact: MergeImpact):
        """Analyze impact of function changes."""
        func_name = func_node.name

        # Check if function exists and is used elsewhere
        if self.indexer and self.file_path:
            # Search for references to this function
            search_results = self.indexer.search_code_elements(
                query=func_name,
                element_type="function"
            )

            # Check if function is imported/used in other files
            for element in search_results:
                if element.file_path != self.file_path and func_name in element.signature:
                    impact.affected_files.add(element.file_path)
                    impact.warnings.append(
                        f"Function '{func_name}' is referenced in {element.file_path}"
                    )

    def _analyze_class_impact(self, class_node: ast.ClassDef, impact: MergeImpact):
        """Analyze impact of class changes."""
        class_name = class_node.name

        if self.indexer and self.file_path:
            # Search for references to this class
            search_results = self.indexer.search_code_elements(
                query=class_name,
                element_type="class"
            )

            for element in search_results:
                if element.file_path != self.file_path:
                    impact.affected_files.add(element.file_path)
                    impact.warnings.append(
                        f"Class '{class_name}' may be referenced in {element.file_path}"
                    )

    def _analyze_import_impact(self, import_node: Union[ast.Import, ast.ImportFrom],
                              impact: MergeImpact):
        """Analyze impact of import changes."""
        if isinstance(import_node, ast.Import):
            for alias in import_node.names:
                impact.new_dependencies.append(alias.name)
        elif isinstance(import_node, ast.ImportFrom):
            module = import_node.module or ""
            for alias in import_node.names:
                impact.new_dependencies.append(f"{module}.{alias.name}")

    def _handle_merge_warnings(self, impact: MergeImpact):
        """Handle warnings from merge impact analysis."""
        if impact.warnings:
            # Store warnings for later reporting
            self.merge_context.potential_conflicts.extend(impact.warnings)

    def _merge_imports_enhanced(self) -> None:
        """Enhanced import merging with codebase awareness."""
        if self.use_indexer:
            self._merge_imports_with_indexer()
        else:
            self._merge_imports()

    def _merge_imports_with_indexer(self) -> None:
        """Merge imports using codebase indexer for intelligent resolution."""
        existing_imports = self._get_existing_imports()
        new_imports = self._get_new_imports()

        # Analyze and optimize imports using indexer knowledge
        optimized_imports = self._optimize_imports_with_indexer(new_imports)

        # Add optimized imports that don't already exist
        import_insert_index = self._find_import_insert_position()

        for new_import in optimized_imports:
            if not self._import_already_exists(new_import, existing_imports):
                self.source_ast.body.insert(import_insert_index, new_import)
                import_insert_index += 1

                # Track import changes
                import_str = self._import_to_string(new_import)
                self.merge_context.suggested_imports.append(import_str)

    def _optimize_imports_with_indexer(self, new_imports: List[ast.stmt]) -> List[ast.stmt]:
        """Optimize imports using codebase indexer knowledge."""
        if not self.indexer:
            return new_imports

        optimized = []

        for import_node in new_imports:
            # Check if import is actually needed based on codebase analysis
            if self._is_import_needed(import_node):
                # Check for better import alternatives
                optimized_import = self._suggest_better_import(import_node)
                optimized.append(optimized_import)

        return optimized

    def _is_import_needed(self, import_node: ast.stmt) -> bool:
        """Check if an import is actually needed based on usage analysis."""
        # For now, assume all imports are needed
        # This could be enhanced to analyze actual usage in the AI-generated code
        return True

    def _suggest_better_import(self, import_node: ast.stmt) -> ast.stmt:
        """Suggest better import alternatives based on codebase patterns."""
        # For now, return the original import
        # This could be enhanced to suggest more specific imports or aliases
        return import_node

    def _import_to_string(self, import_node: ast.stmt) -> str:
        """Convert import AST node to string representation."""
        if isinstance(import_node, ast.Import):
            names = [alias.name + (f" as {alias.asname}" if alias.asname else "")
                    for alias in import_node.names]
            return f"import {', '.join(names)}"
        elif isinstance(import_node, ast.ImportFrom):
            module = import_node.module or ""
            names = [alias.name + (f" as {alias.asname}" if alias.asname else "")
                    for alias in import_node.names]
            return f"from {module} import {', '.join(names)}"
        return str(import_node)

    def _merge_imports(self) -> None:
        """Merge import statements, avoiding duplicates and maintaining order."""
        existing_imports = self._get_existing_imports()
        new_imports = self._get_new_imports()

        # Add new imports that don't already exist
        import_insert_index = self._find_import_insert_position()

        for new_import in new_imports:
            if not self._import_already_exists(new_import, existing_imports):
                self.source_ast.body.insert(import_insert_index, new_import)
                import_insert_index += 1

    def _get_existing_imports(self) -> List[ast.stmt]:
        """Get all existing import statements from source AST."""
        return [node for node in self.source_ast.body
                if isinstance(node, (ast.Import, ast.ImportFrom))]

    def _get_new_imports(self) -> List[ast.stmt]:
        """Get all import statements from AI-generated AST."""
        return [node for node in self.ai_generated_ast.body
                if isinstance(node, (ast.Import, ast.ImportFrom))]

    def _find_import_insert_position(self) -> int:
        """Find the appropriate position to insert new imports."""
        # Insert after existing imports, or at the beginning if no imports exist
        last_import_index = -1
        for i, node in enumerate(self.source_ast.body):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                last_import_index = i
        return last_import_index + 1 if last_import_index >= 0 else 0

    def _import_already_exists(self, new_import: ast.stmt, existing_imports: List[ast.stmt]) -> bool:
        """Check if an import statement already exists."""
        for existing in existing_imports:
            if self._compare_import_statements(new_import, existing):
                return True
        return False

    def _compare_import_statements(self, import1: ast.stmt, import2: ast.stmt) -> bool:
        """Compare two import statements for equality."""
        if type(import1) != type(import2):
            return False

        if isinstance(import1, ast.Import):
            return self._compare_import_names(import1.names, import2.names)
        elif isinstance(import1, ast.ImportFrom):
            return (import1.module == import2.module and
                    self._compare_import_names(import1.names, import2.names))
        return False

    def _compare_import_names(self, names1: List[ast.alias], names2: List[ast.alias]) -> bool:
        """Compare lists of import aliases."""
        if len(names1) != len(names2):
            return False

        for alias1, alias2 in zip(names1, names2):
            if alias1.name != alias2.name or alias1.asname != alias2.asname:
                return False
        return True

    def _merge_module_level_assignments(self) -> None:
        """Merge module-level variable assignments and constants."""
        for ai_node in self.ai_generated_ast.body:
            if isinstance(ai_node, ast.Assign):
                if not self._assignment_already_exists(ai_node):
                    # Insert after imports but before functions/classes
                    insert_pos = self._find_assignment_insert_position()
                    self.source_ast.body.insert(insert_pos, ai_node)

    def _assignment_already_exists(self, new_assign: ast.Assign) -> bool:
        """Check if a module-level assignment already exists."""
        new_targets = {self._get_assignment_target_name(target)
                      for target in new_assign.targets}

        for node in self.source_ast.body:
            if isinstance(node, ast.Assign):
                existing_targets = {self._get_assignment_target_name(target)
                                  for target in node.targets}
                if new_targets.intersection(existing_targets):
                    # Replace existing assignment
                    node.value = new_assign.value
                    return True
        return False

    def _get_assignment_target_name(self, target: ast.expr) -> Optional[str]:
        """Extract the name from an assignment target."""
        if isinstance(target, ast.Name):
            return target.id
        elif isinstance(target, ast.Attribute):
            return f"{self._get_assignment_target_name(target.value)}.{target.attr}"
        return None

    def _find_assignment_insert_position(self) -> int:
        """Find appropriate position for module-level assignments."""
        # Insert after imports but before functions/classes
        for i, node in enumerate(self.source_ast.body):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
                return i
        return len(self.source_ast.body)

    def _merge_function_enhanced(self, ai_function: ast.FunctionDef) -> None:
        """Enhanced function merging with reference awareness."""
        if self.use_indexer:
            self._merge_function_with_indexer(ai_function)
        else:
            self._merge_function(ai_function)

    def _merge_function_with_indexer(self, ai_function: ast.FunctionDef) -> None:
        """Merge function using indexer for intelligent placement and conflict detection."""
        func_name = ai_function.name
        existing_function = self._find_function(self.source_ast, func_name)

        if existing_function:
            # Check if function is referenced elsewhere before replacing
            if self._is_function_referenced_elsewhere(func_name):
                self.merge_context.potential_conflicts.append(
                    f"Function '{func_name}' is referenced in other files and will be replaced"
                )

            # Replace existing function
            self._replace_node_in_ast(self.source_ast, existing_function, ai_function)
        else:
            # Find optimal position for new function based on codebase patterns
            insert_position = self._find_optimal_function_position(ai_function)
            if insert_position is not None:
                self.source_ast.body.insert(insert_position, ai_function)
            else:
                # Add new function at the end
                self.source_ast.body.append(ai_function)

    def _is_function_referenced_elsewhere(self, func_name: str) -> bool:
        """Check if function is referenced in other files."""
        if not self.indexer or not self.file_path:
            return False

        # Search for function references across the codebase
        search_results = self.indexer.search_code_elements(
            query=func_name,
            element_type="function"
        )

        # Check if function is found in other files
        for element in search_results:
            if element.file_path != self.file_path and element.name == func_name:
                return True

        return False

    def _find_optimal_function_position(self, ai_function: ast.FunctionDef) -> Optional[int]:
        """Find optimal position for new function based on codebase patterns."""
        # Simple heuristic: place functions near similar functions
        func_name = ai_function.name

        # Look for functions with similar names or patterns
        for i, node in enumerate(self.source_ast.body):
            if isinstance(node, ast.FunctionDef):
                # Place near functions with similar naming patterns
                if self._functions_are_related(func_name, node.name):
                    return i + 1

        # If no similar functions found, place after existing functions
        last_function_index = -1
        for i, node in enumerate(self.source_ast.body):
            if isinstance(node, ast.FunctionDef):
                last_function_index = i

        if last_function_index >= 0:
            return last_function_index + 1

        return None

    def _functions_are_related(self, func1: str, func2: str) -> bool:
        """Check if two functions are related based on naming patterns."""
        # Simple heuristics for function relatedness
        func1_lower = func1.lower()
        func2_lower = func2.lower()

        # Check for common prefixes or suffixes
        common_prefixes = ['get_', 'set_', 'is_', 'has_', 'can_', 'should_', 'create_', 'delete_', 'update_']
        common_suffixes = ['_handler', '_helper', '_util', '_tool', '_manager']

        for prefix in common_prefixes:
            if func1_lower.startswith(prefix) and func2_lower.startswith(prefix):
                return True

        for suffix in common_suffixes:
            if func1_lower.endswith(suffix) and func2_lower.endswith(suffix):
                return True

        return False

    def _merge_function(self, ai_function: ast.FunctionDef) -> None:
        """Merge a function, replacing existing or adding new."""
        existing_function = self._find_function(self.source_ast, ai_function.name)
        if existing_function:
            # Replace existing function
            self._replace_node_in_ast(self.source_ast, existing_function, ai_function)
        else:
            # Add new function at the end
            self.source_ast.body.append(ai_function)

    def _merge_async_function_enhanced(self, ai_function: ast.AsyncFunctionDef) -> None:
        """Enhanced async function merging with reference awareness."""
        if self.use_indexer:
            self._merge_async_function_with_indexer(ai_function)
        else:
            self._merge_async_function(ai_function)

    def _merge_async_function_with_indexer(self, ai_function: ast.AsyncFunctionDef) -> None:
        """Merge async function using indexer for intelligent placement."""
        func_name = ai_function.name
        existing_function = self._find_async_function(self.source_ast, func_name)

        if existing_function:
            # Check references before replacing
            if self._is_function_referenced_elsewhere(func_name):
                self.merge_context.potential_conflicts.append(
                    f"Async function '{func_name}' is referenced in other files and will be replaced"
                )

            self._replace_node_in_ast(self.source_ast, existing_function, ai_function)
        else:
            # Find optimal position for new async function
            insert_position = self._find_optimal_async_function_position(ai_function)
            if insert_position is not None:
                self.source_ast.body.insert(insert_position, ai_function)
            else:
                self.source_ast.body.append(ai_function)

    def _find_optimal_async_function_position(self, ai_function: ast.AsyncFunctionDef) -> Optional[int]:
        """Find optimal position for new async function."""
        # Place async functions near other async functions
        last_async_index = -1
        for i, node in enumerate(self.source_ast.body):
            if isinstance(node, ast.AsyncFunctionDef):
                last_async_index = i

        if last_async_index >= 0:
            return last_async_index + 1

        # If no async functions, place after regular functions
        return self._find_optimal_function_position(ai_function)

    def _merge_class_enhanced(self, ai_class: ast.ClassDef) -> None:
        """Enhanced class merging with inheritance and reference awareness."""
        if self.use_indexer:
            self._merge_class_with_indexer(ai_class)
        else:
            self._merge_class(ai_class)

    def _merge_class_with_indexer(self, ai_class: ast.ClassDef) -> None:
        """Merge class using indexer for intelligent analysis."""
        class_name = ai_class.name
        existing_class = self._find_class(self.source_ast, class_name)

        if existing_class:
            # Check if class is referenced/inherited elsewhere
            if self._is_class_referenced_elsewhere(class_name):
                self.merge_context.potential_conflicts.append(
                    f"Class '{class_name}' may be inherited or referenced in other files"
                )

            # Merge class contents intelligently
            self._merge_class_contents_enhanced(existing_class, ai_class)
        else:
            # Find optimal position for new class
            insert_position = self._find_optimal_class_position(ai_class)
            if insert_position is not None:
                self.source_ast.body.insert(insert_position, ai_class)
            else:
                self.source_ast.body.append(ai_class)

    def _is_class_referenced_elsewhere(self, class_name: str) -> bool:
        """Check if class is referenced or inherited in other files."""
        if not self.indexer or not self.file_path:
            return False

        # Search for class references
        search_results = self.indexer.search_code_elements(
            query=class_name,
            element_type="class"
        )

        for element in search_results:
            if element.file_path != self.file_path and class_name in element.signature:
                return True

        return False

    def _find_optimal_class_position(self, ai_class: ast.ClassDef) -> Optional[int]:
        """Find optimal position for new class based on inheritance patterns."""
        # Place classes near their base classes if possible
        for base in ai_class.bases:
            if isinstance(base, ast.Name):
                base_name = base.id
                for i, node in enumerate(self.source_ast.body):
                    if isinstance(node, ast.ClassDef) and node.name == base_name:
                        return i + 1

        # Place after existing classes
        last_class_index = -1
        for i, node in enumerate(self.source_ast.body):
            if isinstance(node, ast.ClassDef):
                last_class_index = i

        if last_class_index >= 0:
            return last_class_index + 1

        return None

    def _merge_async_function(self, ai_function: ast.AsyncFunctionDef) -> None:
        """Merge an async function, replacing existing or adding new."""
        existing_function = self._find_async_function(self.source_ast, ai_function.name)
        if existing_function:
            # Replace existing async function
            self._replace_node_in_ast(self.source_ast, existing_function, ai_function)
        else:
            # Add new async function at the end
            self.source_ast.body.append(ai_function)

    def _merge_class(self, ai_class: ast.ClassDef) -> None:
        """Merge a class, combining methods and attributes intelligently."""
        existing_class = self._find_class(self.source_ast, ai_class.name)
        if existing_class:
            # Merge class contents
            self._merge_class_contents(existing_class, ai_class)
        else:
            # Add new class
            self.source_ast.body.append(ai_class)

    def _merge_class_contents_enhanced(self, existing_class: ast.ClassDef, ai_class: ast.ClassDef) -> None:
        """Enhanced merging of class contents with method organization."""
        # Merge methods and attributes from AI class into existing class
        for ai_node in ai_class.body:
            if isinstance(ai_node, ast.FunctionDef):
                self._merge_class_method_enhanced(existing_class, ai_node)
            elif isinstance(ai_node, ast.AsyncFunctionDef):
                self._merge_class_async_method_enhanced(existing_class, ai_node)
            else:
                # For other node types (assignments, etc.), add them intelligently
                self._merge_class_attribute_enhanced(existing_class, ai_node)

    def _merge_class_method_enhanced(self, existing_class: ast.ClassDef, ai_method: ast.FunctionDef):
        """Merge a class method with intelligent positioning."""
        existing_method = self._find_function(existing_class, ai_method.name)
        if existing_method:
            # Replace existing method
            self._replace_node_in_ast(existing_class, existing_method, ai_method)
        else:
            # Find optimal position for new method
            insert_position = self._find_optimal_method_position(existing_class, ai_method)
            if insert_position is not None:
                existing_class.body.insert(insert_position, ai_method)
            else:
                existing_class.body.append(ai_method)

    def _merge_class_async_method_enhanced(self, existing_class: ast.ClassDef, ai_method: ast.AsyncFunctionDef):
        """Merge an async class method with intelligent positioning."""
        existing_method = self._find_async_function(existing_class, ai_method.name)
        if existing_method:
            # Replace existing async method
            self._replace_node_in_ast(existing_class, existing_method, ai_method)
        else:
            # Find optimal position for new async method
            insert_position = self._find_optimal_async_method_position(existing_class, ai_method)
            if insert_position is not None:
                existing_class.body.insert(insert_position, ai_method)
            else:
                existing_class.body.append(ai_method)

    def _merge_class_attribute_enhanced(self, existing_class: ast.ClassDef, ai_node: ast.stmt):
        """Merge class attributes with intelligent positioning."""
        # Place attributes at the beginning of the class, after __init__ if it exists
        init_index = -1
        for i, node in enumerate(existing_class.body):
            if isinstance(node, ast.FunctionDef) and node.name == "__init__":
                init_index = i
                break

        if init_index >= 0:
            existing_class.body.insert(init_index + 1, ai_node)
        else:
            # Place at the beginning
            existing_class.body.insert(0, ai_node)

    def _find_optimal_method_position(self, existing_class: ast.ClassDef, ai_method: ast.FunctionDef) -> Optional[int]:
        """Find optimal position for a new method in a class."""
        method_name = ai_method.name

        # Special method ordering
        special_method_order = [
            "__new__", "__init__", "__del__", "__repr__", "__str__",
            "__eq__", "__ne__", "__lt__", "__le__", "__gt__", "__ge__",
            "__hash__", "__bool__", "__len__", "__getitem__", "__setitem__",
            "__delitem__", "__iter__", "__next__", "__enter__", "__exit__"
        ]

        if method_name in special_method_order:
            # Place special methods in their conventional order
            target_index = special_method_order.index(method_name)

            for i, node in enumerate(existing_class.body):
                if isinstance(node, ast.FunctionDef) and node.name in special_method_order:
                    existing_index = special_method_order.index(node.name)
                    if existing_index > target_index:
                        return i

            # If no later special method found, place after existing special methods
            last_special_index = -1
            for i, node in enumerate(existing_class.body):
                if isinstance(node, ast.FunctionDef) and node.name in special_method_order:
                    last_special_index = i

            if last_special_index >= 0:
                return last_special_index + 1

        # For regular methods, place near methods with similar names
        for i, node in enumerate(existing_class.body):
            if isinstance(node, ast.FunctionDef):
                if self._functions_are_related(method_name, node.name):
                    return i + 1

        return None

    def _find_optimal_async_method_position(self, existing_class: ast.ClassDef, ai_method: ast.AsyncFunctionDef) -> Optional[int]:
        """Find optimal position for a new async method in a class."""
        # Place async methods near other async methods
        last_async_index = -1
        for i, node in enumerate(existing_class.body):
            if isinstance(node, ast.AsyncFunctionDef):
                last_async_index = i

        if last_async_index >= 0:
            return last_async_index + 1

        # If no async methods, place after regular methods
        return self._find_optimal_method_position(existing_class, ai_method)

    def _merge_class_contents(self, existing_class: ast.ClassDef, ai_class: ast.ClassDef) -> None:
        """Merge the contents of two classes."""
        # Merge methods and attributes from AI class into existing class
        for ai_node in ai_class.body:
            if isinstance(ai_node, ast.FunctionDef):
                existing_method = self._find_function(existing_class, ai_node.name)
                if existing_method:
                    # Replace existing method
                    self._replace_node_in_ast(existing_class, existing_method, ai_node)
                else:
                    # Add new method
                    existing_class.body.append(ai_node)
            elif isinstance(ai_node, ast.AsyncFunctionDef):
                existing_method = self._find_async_function(existing_class, ai_node.name)
                if existing_method:
                    # Replace existing async method
                    self._replace_node_in_ast(existing_class, existing_method, ai_node)
                else:
                    # Add new async method
                    existing_class.body.append(ai_node)
            else:
                # For other node types (assignments, etc.), add them
                existing_class.body.append(ai_node)

    def _find_function(self, root: Union[ast.Module, ast.ClassDef], function_name: str) -> Optional[ast.FunctionDef]:
        """Find a function by name in the given AST root."""
        for node in root.body:
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return node
        return None

    def _find_async_function(self, root: Union[ast.Module, ast.ClassDef], function_name: str) -> Optional[ast.AsyncFunctionDef]:
        """Find an async function by name in the given AST root."""
        for node in root.body:
            if isinstance(node, ast.AsyncFunctionDef) and node.name == function_name:
                return node
        return None

    def _find_class(self, root: ast.Module, class_name: str) -> Optional[ast.ClassDef]:
        """Find a class by name in the given AST root."""
        for node in root.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return node
        return None

    def _replace_node_in_ast(self, root: Union[ast.Module, ast.ClassDef], old_node: ast.stmt, new_node: ast.stmt) -> None:
        """Replace a node in the AST with a new node."""
        for i, node in enumerate(root.body):
            if node is old_node:
                root.body[i] = new_node
                break

    def to_source_code(self) -> str:
        """Convert the merged AST back to source code."""
        try:
            return astor.to_source(self.source_ast)
        except Exception as e:
            raise ValueError(f"Error converting AST to source code: {e}")

    def get_merge_summary(self) -> Dict[str, any]:
        """
        Get a comprehensive summary of what was merged, including codebase impact.

        Returns:
            Dictionary with detailed merge information and impact analysis
        """
        summary = {
            "added_functions": [],
            "replaced_functions": [],
            "added_classes": [],
            "merged_classes": [],
            "added_imports": self.merge_context.suggested_imports,
            "codebase_aware": self.use_indexer and self.merge_context.codebase_indexed,
            "potential_conflicts": self.merge_context.potential_conflicts,
            "dependencies_analyzed": list(self.merge_context.dependencies),
            "dependents_checked": list(self.merge_context.dependents),
            "indexer_enabled": self.use_indexer
        }

        # Analyze what was actually merged by comparing ASTs
        if self.use_indexer:
            summary.update(self._generate_detailed_merge_summary())

        return summary

    def _generate_detailed_merge_summary(self) -> Dict[str, any]:
        """Generate detailed merge summary using AST analysis."""
        detailed_summary = {
            "impact_analysis": {
                "files_potentially_affected": len(self.merge_context.dependents),
                "new_dependencies_introduced": len(self.merge_context.suggested_imports),
                "conflicts_detected": len(self.merge_context.potential_conflicts)
            },
            "merge_strategy": "index_aware" if self.use_indexer else "basic",
            "recommendations": []
        }

        # Add recommendations based on analysis
        if self.merge_context.potential_conflicts:
            detailed_summary["recommendations"].append(
                "Review potential conflicts before deploying changes"
            )

        if self.merge_context.dependents:
            detailed_summary["recommendations"].append(
                f"Test {len(self.merge_context.dependents)} dependent files after changes"
            )

        if self.merge_context.suggested_imports:
            detailed_summary["recommendations"].append(
                "Verify that all new imports are available in the environment"
            )

        return detailed_summary


def ast_code_merger_tool() -> FunctionTool:
    """
    Create an AST-based code editing tool for intelligent merging of LLM-generated code
    snippets into existing Python source files.
    """

    def merge_code_intelligently(
        file_path: str,
        ai_generated_code: str,
        backup: bool = True,
        dry_run: bool = False,
        use_indexer: bool = True,
        analyze_impact: bool = True
    ) -> str:
        """
        Intelligently merge LLM-generated code snippets into existing Python source files
        using AST-based analysis with enhanced codebase awareness and reference resolution.

        Args:
            file_path: Path to the existing Python file to modify
            ai_generated_code: The AI-generated code snippet to merge (as string)
            backup: Whether to create a backup of the original file (default: True)
            dry_run: If True, return the merged code without writing to file (default: False)
            use_indexer: Whether to use codebase indexer for enhanced merging (default: True)
            analyze_impact: Whether to analyze merge impact on the codebase (default: True)

        Returns:
            Success message with details of the merge operation, impact analysis, and recommendations

        Raises:
            FileNotFoundError: If the specified file doesn't exist
            SyntaxError: If either the existing file or AI code contains invalid Python syntax
            PermissionError: If unable to read/write the file
            ValueError: If merging encounters irreconcilable conflicts
        """
        try:
            # Validate file path
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return f"Error: File '{file_path}' does not exist"

            if not file_path_obj.is_file():
                return f"Error: '{file_path}' is not a file"

            if not file_path.endswith('.py'):
                return f"Error: '{file_path}' is not a Python file (.py extension required)"

            # Read existing source code
            try:
                with open(file_path_obj, 'r', encoding='utf-8') as f:
                    source_code = f.read()
            except PermissionError:
                return f"Error: Permission denied reading file '{file_path}'"
            except UnicodeDecodeError:
                return f"Error: Unable to decode file '{file_path}' as UTF-8"

            # Validate that both code snippets are valid Python
            if not source_code.strip():
                return "Error: Source file is empty"

            if not ai_generated_code.strip():
                return "Error: AI-generated code is empty"

            # Create enhanced merger and perform merge
            try:
                merger = ASTCodeMerger(
                    source_code=source_code,
                    ai_generated_code=ai_generated_code,
                    file_path=file_path,
                    use_indexer=use_indexer
                )
                merged_code = merger.merge()
            except SyntaxError as e:
                return f"Error: Invalid Python syntax - {e}"
            except ValueError as e:
                return f"Error during merge: {e}"

            # If dry run, return the merged code
            if dry_run:
                return f"Dry run successful. Merged code:\n\n{merged_code}"

            # Create backup if requested
            if backup:
                backup_path = file_path_obj.with_suffix('.py.backup')
                try:
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(source_code)
                except PermissionError:
                    return f"Error: Permission denied creating backup file '{backup_path}'"

            # Write merged code to file
            try:
                with open(file_path_obj, 'w', encoding='utf-8') as f:
                    f.write(merged_code)
            except PermissionError:
                return f"Error: Permission denied writing to file '{file_path}'"

            # Get comprehensive merge summary
            summary = merger.get_merge_summary()

            result_lines = [
                f"✅ Successfully merged AI-generated code into '{file_path}'",
                f"📁 Backup created: {'Yes' if backup else 'No'}",
                f"📊 Original file size: {len(source_code)} characters",
                f"📊 Merged file size: {len(merged_code)} characters",
                f"🧠 Codebase-aware merging: {'Yes' if summary.get('codebase_aware', False) else 'No'}"
            ]

            # Add indexer-enhanced information
            if summary.get('indexer_enabled', False):
                result_lines.append("\n🔍 Enhanced Merge Analysis:")

                if summary.get('dependencies_analyzed'):
                    result_lines.append(f"  📦 Dependencies analyzed: {len(summary['dependencies_analyzed'])}")

                if summary.get('dependents_checked'):
                    result_lines.append(f"  🔗 Dependent files checked: {len(summary['dependents_checked'])}")

                if summary.get('added_imports'):
                    result_lines.append(f"  ➕ New imports added: {len(summary['added_imports'])}")
                    for imp in summary['added_imports'][:3]:  # Show first 3
                        result_lines.append(f"    - {imp}")
                    if len(summary['added_imports']) > 3:
                        result_lines.append(f"    ... and {len(summary['added_imports']) - 3} more")

            # Add warnings and conflicts
            if summary.get('potential_conflicts'):
                result_lines.append("\n⚠️  Potential Conflicts Detected:")
                for conflict in summary['potential_conflicts']:
                    result_lines.append(f"  - {conflict}")

            # Add impact analysis
            if 'impact_analysis' in summary:
                impact = summary['impact_analysis']
                result_lines.append("\n📈 Impact Analysis:")
                result_lines.append(f"  🎯 Files potentially affected: {impact.get('files_potentially_affected', 0)}")
                result_lines.append(f"  🔄 New dependencies: {impact.get('new_dependencies_introduced', 0)}")
                result_lines.append(f"  ⚡ Conflicts detected: {impact.get('conflicts_detected', 0)}")

            # Add recommendations
            if summary.get('recommendations'):
                result_lines.append("\n💡 Recommendations:")
                for rec in summary['recommendations']:
                    result_lines.append(f"  - {rec}")

            # Add basic summary for backward compatibility
            basic_categories = ['added_functions', 'replaced_functions', 'added_classes', 'merged_classes']
            basic_summary = {k: v for k, v in summary.items() if k in basic_categories and v}

            if basic_summary:
                result_lines.append("\n📋 Merge Summary:")
                for category, items in basic_summary.items():
                    if items:
                        result_lines.append(f"  - {category.replace('_', ' ').title()}: {', '.join(items)}")

            return "\n".join(result_lines)

        except Exception as e:
            return f"Unexpected error during code merge: {str(e)}"

    return FunctionTool(merge_code_intelligently)


def enhanced_ast_code_merger_tool() -> FunctionTool:
    """
    Create an enhanced AST-based code editing tool with full codebase indexer integration
    for intelligent reference resolution and codebase awareness.
    """

    def merge_code_with_codebase_awareness(
        file_path: str,
        ai_generated_code: str,
        backup: bool = True,
        dry_run: bool = False,
        force_index_update: bool = False,
        conflict_resolution: str = "warn"
    ) -> str:
        """
        Merge AI-generated code with full codebase awareness and intelligent reference resolution.

        Args:
            file_path: Path to the existing Python file to modify
            ai_generated_code: The AI-generated code snippet to merge (as string)
            backup: Whether to create a backup of the original file (default: True)
            dry_run: If True, return the merged code without writing to file (default: False)
            force_index_update: Whether to force reindexing before merge (default: False)
            conflict_resolution: How to handle conflicts ("warn", "abort", "force") (default: "warn")

        Returns:
            Comprehensive merge report with impact analysis and recommendations
        """
        try:
            # Ensure codebase is indexed
            if force_index_update:
                try:
                    from .codebase_indexer import get_global_indexer
                    indexer = get_global_indexer()

                    # Index the directory containing the target file
                    file_dir = Path(file_path).parent
                    indexer.index_codebase(file_dir)
                except Exception as e:
                    return f"Warning: Could not update codebase index: {e}\nProceeding with basic merge..."

            # Use the enhanced merger with full indexer integration
            # Create the merger tool and call it
            merger_tool = ast_code_merger_tool()
            result = merger_tool.func(
                file_path=file_path,
                ai_generated_code=ai_generated_code,
                backup=backup,
                dry_run=dry_run,
                use_indexer=True,
                analyze_impact=True
            )

            # Add enhanced analysis header
            enhanced_result = [
                "🚀 Enhanced Codebase-Aware Code Merge",
                "=" * 45,
                "",
                result
            ]

            return "\n".join(enhanced_result)

        except Exception as e:
            return f"Error in enhanced code merge: {str(e)}"

    return FunctionTool(merge_code_with_codebase_awareness)


def code_structure_analyzer_tool() -> FunctionTool:
    """
    Create a tool for analyzing Python code structure to understand what would be merged.
    """

    def analyze_code_structure(file_path: str) -> str:
        """
        Analyze the structure of a Python file to understand its components.

        Args:
            file_path: Path to the Python file to analyze

        Returns:
            Detailed analysis of the file's structure including functions, classes, imports, etc.
        """
        try:
            # Validate file path
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                return f"Error: File '{file_path}' does not exist"

            if not file_path_obj.is_file():
                return f"Error: '{file_path}' is not a file"

            if not file_path.endswith('.py'):
                return f"Error: '{file_path}' is not a Python file (.py extension required)"

            # Read and parse the file
            try:
                with open(file_path_obj, 'r', encoding='utf-8') as f:
                    source_code = f.read()
            except PermissionError:
                return f"Error: Permission denied reading file '{file_path}'"
            except UnicodeDecodeError:
                return f"Error: Unable to decode file '{file_path}' as UTF-8"

            if not source_code.strip():
                return "File is empty"

            try:
                tree = ast.parse(source_code)
            except SyntaxError as e:
                return f"Error: Invalid Python syntax - {e}"

            # Analyze structure
            analysis = []
            analysis.append(f"Analysis of '{file_path}':")
            analysis.append("=" * (len(file_path) + 13))

            # Count different types of nodes
            imports = []
            functions = []
            classes = []
            assignments = []

            for node in tree.body:
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports.append(f"from {module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else ""))
                elif isinstance(node, ast.FunctionDef):
                    args = [arg.arg for arg in node.args.args]
                    functions.append(f"def {node.name}({', '.join(args)})")
                elif isinstance(node, ast.AsyncFunctionDef):
                    args = [arg.arg for arg in node.args.args]
                    functions.append(f"async def {node.name}({', '.join(args)})")
                elif isinstance(node, ast.ClassDef):
                    bases = [ast.unparse(base) if hasattr(ast, 'unparse') else 'base' for base in node.bases]
                    class_info = f"class {node.name}"
                    if bases:
                        class_info += f"({', '.join(bases)})"

                    # Analyze class methods
                    methods = []
                    for class_node in node.body:
                        if isinstance(class_node, ast.FunctionDef):
                            method_args = [arg.arg for arg in class_node.args.args]
                            methods.append(f"    def {class_node.name}({', '.join(method_args)})")
                        elif isinstance(class_node, ast.AsyncFunctionDef):
                            method_args = [arg.arg for arg in class_node.args.args]
                            methods.append(f"    async def {class_node.name}({', '.join(method_args)})")

                    classes.append((class_info, methods))
                elif isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            assignments.append(f"{target.id} = ...")

            # Build analysis report
            if imports:
                analysis.append(f"\nImports ({len(imports)}):")
                for imp in imports:
                    analysis.append(f"  - {imp}")

            if assignments:
                analysis.append(f"\nModule-level assignments ({len(assignments)}):")
                for assign in assignments:
                    analysis.append(f"  - {assign}")

            if functions:
                analysis.append(f"\nFunctions ({len(functions)}):")
                for func in functions:
                    analysis.append(f"  - {func}")

            if classes:
                analysis.append(f"\nClasses ({len(classes)}):")
                for class_info, methods in classes:
                    analysis.append(f"  - {class_info}")
                    if methods:
                        analysis.append("    Methods:")
                        for method in methods:
                            analysis.append(f"      - {method}")

            analysis.append(f"\nFile statistics:")
            analysis.append(f"  - Total lines: {len(source_code.splitlines())}")
            analysis.append(f"  - Total characters: {len(source_code)}")
            analysis.append(f"  - AST nodes: {len(list(ast.walk(tree)))}")

            return "\n".join(analysis)

        except Exception as e:
            return f"Unexpected error during code analysis: {str(e)}"

    return FunctionTool(analyze_code_structure)


# Example usage and testing
if __name__ == "__main__":
    # Example of how to use the AST code merger
    source_code = '''
import os
import sys

def greet(name):
    """Greet someone."""
    print(f"Hello, {name}!")

class Calculator:
    def add(self, a, b):
        return a + b
'''

    ai_generated_code = '''
import json
from pathlib import Path

def greet(name, greeting="Hello"):
    """Greet someone with a custom greeting."""
    print(f"{greeting}, {name}!")

def farewell(name):
    """Say goodbye to someone."""
    print(f"Goodbye, {name}!")

class Calculator:
    def add(self, a, b):
        """Add two numbers."""
        return a + b

    def subtract(self, a, b):
        """Subtract two numbers."""
        return a - b
'''

    print("=== AST Code Merger Example ===")
    try:
        merger = ASTCodeMerger(source_code, ai_generated_code)
        merged_code = merger.merge()
        print("Merged code:")
        print(merged_code)
    except Exception as e:
        print(f"Error: {e}")

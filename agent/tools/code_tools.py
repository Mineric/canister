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
from typing import Dict, List, Optional, Union
from google.adk.tools import FunctionTool


class ASTCodeMerger:
    """
    Advanced AST-based code merger that intelligently integrates LLM-generated code
    snippets into existing Python source files while preserving structure and avoiding duplicates.
    """

    def __init__(self, source_code: str, ai_generated_code: str):
        """
        Initialize the code merger with source and AI-generated code.

        Args:
            source_code: The existing Python source code as a string
            ai_generated_code: The AI-generated code snippet to merge as a string

        Raises:
            SyntaxError: If either code snippet contains invalid Python syntax
        """
        try:
            self.source_ast = ast.parse(source_code)
            self.ai_generated_ast = ast.parse(ai_generated_code)
            self.source_code = source_code
            self.ai_generated_code = ai_generated_code
        except SyntaxError as e:
            raise SyntaxError(f"Invalid Python syntax in code: {e}")

    def merge(self) -> str:
        """
        Perform intelligent merging of AI-generated code into source code.

        Returns:
            The merged source code as a string

        Raises:
            ValueError: If merging encounters irreconcilable conflicts
        """
        try:
            # Process imports first to avoid dependency issues
            self._merge_imports()

            # Process module-level variables and constants
            self._merge_module_level_assignments()

            # Process functions and classes
            for ai_node in self.ai_generated_ast.body:
                if isinstance(ai_node, ast.FunctionDef):
                    self._merge_function(ai_node)
                elif isinstance(ai_node, ast.ClassDef):
                    self._merge_class(ai_node)
                elif isinstance(ai_node, ast.AsyncFunctionDef):
                    self._merge_async_function(ai_node)

            return self.to_source_code()
        except Exception as e:
            raise ValueError(f"Error during code merging: {e}")

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

    def _merge_function(self, ai_function: ast.FunctionDef) -> None:
        """Merge a function, replacing existing or adding new."""
        existing_function = self._find_function(self.source_ast, ai_function.name)
        if existing_function:
            # Replace existing function
            self._replace_node_in_ast(self.source_ast, existing_function, ai_function)
        else:
            # Add new function at the end
            self.source_ast.body.append(ai_function)

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

    def get_merge_summary(self) -> Dict[str, List[str]]:
        """
        Get a summary of what was merged.

        Returns:
            Dictionary with lists of added, replaced, and merged items
        """
        # This would be implemented to track changes during merge
        # For now, return a placeholder
        return {
            "added_functions": [],
            "replaced_functions": [],
            "added_classes": [],
            "merged_classes": [],
            "added_imports": []
        }


def ast_code_merger_tool() -> FunctionTool:
    """
    Create an AST-based code editing tool for intelligent merging of LLM-generated code
    snippets into existing Python source files.
    """

    def merge_code_intelligently(
        file_path: str,
        ai_generated_code: str,
        backup: bool = True,
        dry_run: bool = False
    ) -> str:
        """
        Intelligently merge LLM-generated code snippets into existing Python source files
        using AST-based analysis to avoid duplicates and preserve structure.

        Args:
            file_path: Path to the existing Python file to modify
            ai_generated_code: The AI-generated code snippet to merge (as string)
            backup: Whether to create a backup of the original file (default: True)
            dry_run: If True, return the merged code without writing to file (default: False)

        Returns:
            Success message with details of the merge operation, or the merged code if dry_run=True

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

            # Create merger and perform merge
            try:
                merger = ASTCodeMerger(source_code, ai_generated_code)
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

            # Get merge summary
            summary = merger.get_merge_summary()

            result_lines = [
                f"Successfully merged AI-generated code into '{file_path}'",
                f"Backup created: {'Yes' if backup else 'No'}",
                f"Original file size: {len(source_code)} characters",
                f"Merged file size: {len(merged_code)} characters"
            ]

            # Add summary details if available
            if any(summary.values()):
                result_lines.append("Merge summary:")
                for category, items in summary.items():
                    if items:
                        result_lines.append(f"  - {category.replace('_', ' ').title()}: {', '.join(items)}")

            return "\n".join(result_lines)

        except Exception as e:
            return f"Unexpected error during code merge: {str(e)}"

    return FunctionTool(merge_code_intelligently)


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

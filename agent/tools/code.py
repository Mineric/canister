"""
Code Tools - Canister Agent
Consolidated code analysis, manipulation, and merging operations.
"""

import ast
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from dataclasses import asdict


class CodeTools:
    """Code analysis, manipulation, and merging operations."""
    
    @staticmethod
    def merge(source_file: str, new_code: str, strategy: str = "intelligent", 
             dry_run: bool = True, backup: bool = True) -> str:
        """
        Intelligent code merging with multiple strategies.
        
        Args:
            source_file: Path to the source file to merge into
            new_code: Code to be merged/integrated
            strategy: Merge strategy ('intelligent', 'ast', 'append', 'replace')
            dry_run: Whether to perform actual merge or analysis only
            backup: Whether to create backup before merging
            
        Returns:
            Merge analysis and results
        """
        try:
            source_path = Path(source_file)
            
            # Validate inputs
            if not source_path.exists():
                return f"Error: Source file '{source_file}' does not exist"
            
            if not new_code.strip():
                return "Error: No code provided for merging"
            
            # Read source file
            try:
                source_code = source_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                return f"Error: Cannot read source file '{source_file}' - encoding issue"
            
            # Validate new code syntax
            try:
                ast.parse(new_code)
            except SyntaxError as e:
                return f"Error: Invalid Python syntax in new code - {str(e)}"
            
            # Perform merge based on strategy
            if strategy == "intelligent":
                return CodeTools._intelligent_merge(source_code, new_code, source_path, dry_run, backup)
            elif strategy == "ast":
                return CodeTools._ast_merge(source_code, new_code, source_path, dry_run, backup)
            elif strategy == "append":
                return CodeTools._append_merge(source_code, new_code, source_path, dry_run, backup)
            elif strategy == "replace":
                return CodeTools._replace_merge(source_code, new_code, source_path, dry_run, backup)
            else:
                return f"Error: Unknown merge strategy '{strategy}'. Available: intelligent, ast, append, replace"
                
        except Exception as e:
            return f"Error in code merge: {str(e)}"
    
    @staticmethod
    def _intelligent_merge(source_code: str, new_code: str, source_path: Path, 
                          dry_run: bool, backup: bool) -> str:
        """Intelligent merge using AST analysis and conflict detection."""
        try:
            # Parse both code blocks
            source_ast = ast.parse(source_code)
            new_ast = ast.parse(new_code)
            
            # Analyze existing functions and classes
            existing_elements = {}
            for node in ast.walk(source_ast):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    existing_elements[node.name] = {
                        'type': 'function' if isinstance(node, ast.FunctionDef) else 'class',
                        'line': node.lineno
                    }
            
            # Analyze new code elements
            new_elements = {}
            conflicts = []
            for node in ast.walk(new_ast):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    element_type = 'function' if isinstance(node, ast.FunctionDef) else 'class'
                    new_elements[node.name] = {'type': element_type, 'line': node.lineno}
                    
                    if node.name in existing_elements:
                        conflicts.append(f"{element_type} '{node.name}' already exists at line {existing_elements[node.name]['line']}")
            
            # Generate merge analysis
            analysis = [
                "🧠 Intelligent Merge Analysis:",
                f"Source file: {source_path}",
                f"Strategy: Intelligent AST-based merging",
                f"Mode: {'Dry run' if dry_run else 'Live merge'}",
                "",
                f"📊 Analysis Results:",
                f"  • Existing elements: {len(existing_elements)}",
                f"  • New elements: {len(new_elements)}",
                f"  • Conflicts detected: {len(conflicts)}",
                ""
            ]
            
            if conflicts:
                analysis.extend([
                    "⚠️ Conflicts detected:",
                    *[f"  • {conflict}" for conflict in conflicts],
                    "",
                    "Recommendation: Review conflicts before merging",
                    ""
                ])
            
            if not dry_run and len(conflicts) == 0:
                # Perform actual merge by appending new code
                merged_code = source_code.rstrip() + "\n\n\n# === MERGED CODE ===\n" + new_code
                
                if backup:
                    backup_path = source_path.with_suffix(source_path.suffix + '.backup')
                    backup_path.write_text(source_code)
                    analysis.append(f"✅ Backup created: {backup_path}")
                
                source_path.write_text(merged_code)
                analysis.append(f"✅ Merge completed successfully")
            else:
                analysis.append("ℹ️ Dry run mode - no changes made to file")
            
            return "\n".join(analysis)
            
        except Exception as e:
            return f"Error in intelligent merge: {str(e)}"
    
    @staticmethod
    def _ast_merge(source_code: str, new_code: str, source_path: Path, 
                  dry_run: bool, backup: bool) -> str:
        """AST-based merge with structure preservation."""
        # Simplified AST merge - in a real implementation, this would be more sophisticated
        return CodeTools._append_merge(source_code, new_code, source_path, dry_run, backup)
    
    @staticmethod
    def _append_merge(source_code: str, new_code: str, source_path: Path,
                     dry_run: bool, backup: bool) -> str:
        """Simple append merge strategy."""
        try:
            merged_code = source_code.rstrip() + "\n\n\n# === APPENDED CODE ===\n" + new_code
            
            if not dry_run:
                if backup:
                    backup_path = source_path.with_suffix(source_path.suffix + '.backup')
                    backup_path.write_text(source_code)
                
                source_path.write_text(merged_code)
                return f"✅ Code appended successfully to {source_path}"
            else:
                return f"ℹ️ Dry run: Would append {len(new_code)} characters to {source_path}"
                
        except Exception as e:
            return f"Error in append merge: {str(e)}"
    
    @staticmethod
    def _replace_merge(source_code: str, new_code: str, source_path: Path,
                      dry_run: bool, backup: bool) -> str:
        """Replace merge strategy (overwrites entire file)."""
        try:
            if not dry_run:
                if backup:
                    backup_path = source_path.with_suffix(source_path.suffix + '.backup')
                    backup_path.write_text(source_code)
                
                source_path.write_text(new_code)
                return f"✅ File replaced successfully: {source_path}"
            else:
                return f"ℹ️ Dry run: Would replace entire content of {source_path}"
                
        except Exception as e:
            return f"Error in replace merge: {str(e)}"
    
    @staticmethod
    def analyze_structure(file_path: str, include_metrics: bool = True, 
                         include_dependencies: bool = False) -> str:
        """
        Analyze code structure and patterns.
        
        Args:
            file_path: Path to the Python file to analyze
            include_metrics: Whether to include complexity metrics
            include_dependencies: Whether to analyze import dependencies
            
        Returns:
            Comprehensive code structure analysis
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return f"Error: File '{file_path}' does not exist"
            
            if not path.suffix == '.py':
                return f"Error: File '{file_path}' is not a Python file"
            
            # Read and parse file
            try:
                content = path.read_text(encoding='utf-8')
                tree = ast.parse(content)
            except UnicodeDecodeError:
                return f"Error: Cannot read file '{file_path}' - encoding issue"
            except SyntaxError as e:
                return f"Error: Invalid Python syntax in '{file_path}' - {str(e)}"
            
            # Analyze structure
            analysis = {
                'file_info': {
                    'path': str(path),
                    'size': len(content),
                    'lines': len(content.splitlines())
                },
                'classes': [],
                'functions': [],
                'imports': [],
                'global_variables': []
            }
            
            # Walk AST and collect information
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'line': node.lineno,
                        'methods': [],
                        'decorators': [ast.unparse(d) if hasattr(ast, 'unparse') else str(d) for d in node.decorator_list]
                    }
                    
                    # Find methods
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            class_info['methods'].append(item.name)
                    
                    analysis['classes'].append(class_info)
                
                elif isinstance(node, ast.FunctionDef):
                    # Only top-level functions (not methods)
                    if not any(isinstance(parent, ast.ClassDef) for parent in ast.walk(tree) 
                             if hasattr(parent, 'body') and node in getattr(parent, 'body', [])):
                        func_info = {
                            'name': node.name,
                            'line': node.lineno,
                            'args': len(node.args.args),
                            'decorators': [ast.unparse(d) if hasattr(ast, 'unparse') else str(d) for d in node.decorator_list]
                        }
                        
                        if include_metrics:
                            func_info['complexity'] = CodeTools._calculate_complexity(node)
                        
                        analysis['functions'].append(func_info)
                
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            analysis['imports'].append({
                                'module': alias.name,
                                'alias': alias.asname,
                                'type': 'import'
                            })
                    else:
                        module = node.module or ""
                        for alias in node.names:
                            analysis['imports'].append({
                                'module': f"{module}.{alias.name}" if module else alias.name,
                                'alias': alias.asname,
                                'type': 'from_import'
                            })
            
            # Format results
            result_lines = [
                f"📋 Code Structure Analysis: {file_path}",
                "=" * (len(file_path) + 25),
                "",
                f"📄 File Information:",
                f"  • Size: {analysis['file_info']['size']:,} bytes",
                f"  • Lines: {analysis['file_info']['lines']:,}",
                "",
                f"🏗️ Structure Overview:",
                f"  • Classes: {len(analysis['classes'])}",
                f"  • Functions: {len(analysis['functions'])}",
                f"  • Imports: {len(analysis['imports'])}",
                ""
            ]
            
            # Classes details
            if analysis['classes']:
                result_lines.extend([
                    "🎯 Classes:",
                    *[f"  • {cls['name']} (line {cls['line']}) - {len(cls['methods'])} methods" 
                      for cls in analysis['classes']],
                    ""
                ])
            
            # Functions details
            if analysis['functions']:
                result_lines.extend([
                    "🔧 Functions:",
                    *[f"  • {func['name']} (line {func['line']}) - {func['args']} args" +
                      (f", complexity: {func['complexity']}" if include_metrics and 'complexity' in func else "")
                      for func in analysis['functions']],
                    ""
                ])
            
            # Dependencies
            if include_dependencies and analysis['imports']:
                result_lines.extend([
                    "📦 Dependencies:",
                    *[f"  • {imp['module']}" + (f" as {imp['alias']}" if imp['alias'] else "")
                      for imp in analysis['imports'][:10]],  # Limit to first 10
                    ""
                ])
                
                if len(analysis['imports']) > 10:
                    result_lines.append(f"  ... and {len(analysis['imports']) - 10} more imports")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return f"Error analyzing code structure: {str(e)}"
    
    @staticmethod
    def _calculate_complexity(node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        
        return complexity
    
    @staticmethod
    def index_codebase(root_path: str, exclude_patterns: str = "__pycache__,*.pyc,*.pyo,.git,.venv", 
                      include_patterns: str = "*.py", max_files: int = 1000) -> str:
        """
        Index codebase for analysis and search.
        
        Args:
            root_path: Root directory path to start indexing
            exclude_patterns: Comma-separated patterns to exclude
            include_patterns: Comma-separated patterns to include
            max_files: Maximum number of files to process
            
        Returns:
            Indexing results and statistics
        """
        try:
            root = Path(root_path)
            if not root.exists():
                return f"Error: Root path '{root_path}' does not exist"
            
            if not root.is_dir():
                return f"Error: '{root_path}' is not a directory"
            
            # Parse patterns
            exclude_list = [p.strip() for p in exclude_patterns.split(',') if p.strip()]
            include_list = [p.strip() for p in include_patterns.split(',') if p.strip()]
            
            # Find Python files
            python_files = []
            for pattern in include_list:
                python_files.extend(root.rglob(pattern))
            
            # Filter out excluded patterns
            filtered_files = []
            for file_path in python_files:
                skip_file = False
                for exclude_pattern in exclude_list:
                    if exclude_pattern in str(file_path):
                        skip_file = True
                        break
                if not skip_file:
                    filtered_files.append(file_path)
            
            # Limit file count
            if len(filtered_files) > max_files:
                filtered_files = filtered_files[:max_files]
            
            # Analyze files
            stats = {
                'files_processed': 0,
                'files_with_errors': 0,
                'total_functions': 0,
                'total_classes': 0,
                'total_lines': 0,
                'errors': []
            }
            
            for file_path in filtered_files:
                try:
                    content = file_path.read_text(encoding='utf-8')
                    tree = ast.parse(content)
                    
                    # Count elements
                    functions = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
                    classes = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])
                    lines = len(content.splitlines())
                    
                    stats['total_functions'] += functions
                    stats['total_classes'] += classes
                    stats['total_lines'] += lines
                    stats['files_processed'] += 1
                    
                except Exception as e:
                    stats['files_with_errors'] += 1
                    stats['errors'].append(f"{file_path}: {str(e)}")
            
            # Format results
            result_lines = [
                f"🔍 Codebase Indexing Results",
                f"Root: {root_path}",
                "=" * 50,
                "",
                f"📊 Statistics:",
                f"  • Files found: {len(python_files)}",
                f"  • Files processed: {stats['files_processed']}",
                f"  • Files with errors: {stats['files_with_errors']}",
                f"  • Total functions: {stats['total_functions']}",
                f"  • Total classes: {stats['total_classes']}",
                f"  • Total lines of code: {stats['total_lines']:,}",
                ""
            ]
            
            if stats['errors']:
                result_lines.extend([
                    "⚠️ Errors encountered:",
                    *[f"  • {error}" for error in stats['errors'][:5]],
                    ""
                ])
                if len(stats['errors']) > 5:
                    result_lines.append(f"  ... and {len(stats['errors']) - 5} more errors")
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return f"Error indexing codebase: {str(e)}"
    
    @staticmethod
    def analyze_file(file_path: str) -> str:
        """
        Detailed file analysis with metrics.
        
        Args:
            file_path: Path to the file to analyze
            
        Returns:
            Comprehensive file analysis including structure, dependencies, and metrics
        """
        # This delegates to analyze_structure with full metrics
        return CodeTools.analyze_structure(
            file_path, 
            include_metrics=True, 
            include_dependencies=True
        )
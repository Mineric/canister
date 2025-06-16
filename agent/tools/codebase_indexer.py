"""
Codebase Indexing and Self-Awareness System - Cannister
Copyright (c) 2024 Thant Min Htet. All rights reserved.

Comprehensive codebase indexing and self-awareness system for Google ADK agents.
This module provides deep understanding and navigation capabilities for codebases.

This software is proprietary and confidential. No usage, modification,
or distribution rights are granted without explicit written permission.
"""

import ast
import json
import hashlib
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union
from dataclasses import dataclass, asdict
from google.adk.tools import FunctionTool

# Compatibility for ast.unparse (added in Python 3.9)
if not hasattr(ast, 'unparse'):
    try:
        import astor
        def ast_unparse(node):
            return astor.to_source(node).strip()
        ast.unparse = ast_unparse
    except ImportError:
        def ast_unparse(node):
            # Fallback for very basic cases
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Constant):
                return repr(node.value)
            elif isinstance(node, ast.Attribute):
                return f"{ast_unparse(node.value)}.{node.attr}"
            else:
                return str(type(node).__name__)
        ast.unparse = ast_unparse


@dataclass
class CodeElement:
    """Represents a code element (function, class, method, etc.)."""
    name: str
    type: str  # 'function', 'class', 'method', 'async_function', 'property'
    file_path: str
    line_number: int
    end_line_number: int
    signature: str
    docstring: Optional[str]
    parent_class: Optional[str] = None
    decorators: List[str] = None
    complexity_score: int = 0
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.decorators is None:
            self.decorators = []
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ImportInfo:
    """Represents import information."""
    module: str
    alias: Optional[str]
    from_module: Optional[str]
    file_path: str
    line_number: int
    is_local: bool = False


@dataclass
class FileInfo:
    """Represents file-level information."""
    file_path: str
    size: int
    lines_of_code: int
    last_modified: datetime
    file_hash: str
    encoding: str = 'utf-8'
    syntax_errors: List[str] = None
    
    def __post_init__(self):
        if self.syntax_errors is None:
            self.syntax_errors = []


class CodebaseIndexer:
    """
    Advanced codebase indexer that creates a searchable knowledge base of Python codebases.
    Provides deep understanding of code structure, dependencies, and relationships.
    """
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the codebase indexer.
        
        Args:
            cache_dir: Directory to store cache files (default: .codebase_cache)
        """
        self.cache_dir = Path(cache_dir or ".codebase_cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize SQLite database for structured storage
        self.db_path = self.cache_dir / "codebase_index.db"
        self._init_database()
        
        # In-memory indexes for fast access
        self.code_elements: Dict[str, CodeElement] = {}
        self.imports: List[ImportInfo] = []
        self.files: Dict[str, FileInfo] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_dependency_graph: Dict[str, Set[str]] = {}
        
    def _init_database(self):
        """Initialize SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS code_elements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    type TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    line_number INTEGER,
                    end_line_number INTEGER,
                    signature TEXT,
                    docstring TEXT,
                    parent_class TEXT,
                    decorators TEXT,
                    complexity_score INTEGER DEFAULT 0,
                    dependencies TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(name, type, file_path, line_number)
                );
                
                CREATE TABLE IF NOT EXISTS imports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    module TEXT NOT NULL,
                    alias TEXT,
                    from_module TEXT,
                    file_path TEXT NOT NULL,
                    line_number INTEGER,
                    is_local BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE TABLE IF NOT EXISTS files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT UNIQUE NOT NULL,
                    size INTEGER,
                    lines_of_code INTEGER,
                    last_modified TIMESTAMP,
                    file_hash TEXT,
                    encoding TEXT DEFAULT 'utf-8',
                    syntax_errors TEXT,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_code_elements_name ON code_elements(name);
                CREATE INDEX IF NOT EXISTS idx_code_elements_type ON code_elements(type);
                CREATE INDEX IF NOT EXISTS idx_code_elements_file ON code_elements(file_path);
                CREATE INDEX IF NOT EXISTS idx_imports_module ON imports(module);
                CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path);
            """)
    
    def index_codebase(self, root_path: Union[str, Path], 
                      exclude_patterns: Optional[List[str]] = None,
                      include_patterns: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Index an entire codebase starting from root_path.
        
        Args:
            root_path: Root directory to start indexing
            exclude_patterns: Patterns to exclude (e.g., ['__pycache__', '*.pyc'])
            include_patterns: Patterns to include (default: ['*.py'])
            
        Returns:
            Dictionary with indexing statistics and results
        """
        root_path = Path(root_path)
        if not root_path.exists():
            raise ValueError(f"Root path does not exist: {root_path}")
        
        exclude_patterns = exclude_patterns or [
            '__pycache__', '*.pyc', '*.pyo', '.git', '.svn', 
            'node_modules', '.venv', 'venv', '*.egg-info'
        ]
        include_patterns = include_patterns or ['*.py']
        
        stats = {
            'files_processed': 0,
            'files_with_errors': 0,
            'total_elements': 0,
            'total_imports': 0,
            'start_time': datetime.now(),
            'errors': []
        }
        
        # Find all Python files
        python_files = self._find_python_files(root_path, exclude_patterns, include_patterns)
        
        # Clear existing data for this root path
        self._clear_existing_data(str(root_path))
        
        # Process each file
        for file_path in python_files:
            try:
                self._index_file(file_path)
                stats['files_processed'] += 1
            except Exception as e:
                stats['files_with_errors'] += 1
                stats['errors'].append(f"Error processing {file_path}: {str(e)}")
        
        # Build dependency graphs
        self._build_dependency_graphs()
        
        # Save to database
        self._save_to_database()
        
        stats['end_time'] = datetime.now()
        stats['duration'] = (stats['end_time'] - stats['start_time']).total_seconds()
        stats['total_elements'] = len(self.code_elements)
        stats['total_imports'] = len(self.imports)
        
        return stats

    def _find_python_files(self, root_path: Path, exclude_patterns: List[str],
                          include_patterns: List[str]) -> List[Path]:
        """Find all Python files matching the criteria."""
        python_files = []

        def should_exclude(path: Path) -> bool:
            path_str = str(path)
            for pattern in exclude_patterns:
                if pattern in path_str or path.match(pattern):
                    return True
            return False

        def should_include(path: Path) -> bool:
            for pattern in include_patterns:
                if path.match(pattern):
                    return True
            return False

        for path in root_path.rglob('*'):
            if path.is_file() and should_include(path) and not should_exclude(path):
                python_files.append(path)

        return python_files

    def _clear_existing_data(self, root_path: str):
        """Clear existing data for the given root path."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM code_elements WHERE file_path LIKE ?", (f"{root_path}%",))
            conn.execute("DELETE FROM imports WHERE file_path LIKE ?", (f"{root_path}%",))
            conn.execute("DELETE FROM files WHERE file_path LIKE ?", (f"{root_path}%",))

    def _index_file(self, file_path: Path):
        """Index a single Python file."""
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()

        # Calculate file hash
        file_hash = hashlib.md5(content.encode()).hexdigest()

        # Get file stats
        stat = file_path.stat()
        file_info = FileInfo(
            file_path=str(file_path),
            size=stat.st_size,
            lines_of_code=len(content.splitlines()),
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            file_hash=file_hash
        )

        try:
            # Parse AST
            tree = ast.parse(content, filename=str(file_path))

            # Extract code elements
            self._extract_code_elements(tree, file_path)

            # Extract imports
            self._extract_imports(tree, file_path)

        except SyntaxError as e:
            file_info.syntax_errors.append(f"Syntax error: {e}")

        self.files[str(file_path)] = file_info

    def _extract_code_elements(self, tree: ast.AST, file_path: Path):
        """Extract code elements (functions, classes, methods) from AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._process_function(node, file_path)
            elif isinstance(node, ast.AsyncFunctionDef):
                self._process_async_function(node, file_path)
            elif isinstance(node, ast.ClassDef):
                self._process_class(node, file_path)

    def _process_function(self, node: ast.FunctionDef, file_path: Path, parent_class: str = None):
        """Process a function definition."""
        signature = self._get_function_signature(node)
        docstring = ast.get_docstring(node)
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        element = CodeElement(
            name=node.name,
            type='method' if parent_class else 'function',
            file_path=str(file_path),
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            signature=signature,
            docstring=docstring,
            parent_class=parent_class,
            decorators=decorators,
            complexity_score=self._calculate_complexity(node)
        )

        key = f"{file_path}:{node.name}:{node.lineno}"
        self.code_elements[key] = element

    def _process_async_function(self, node: ast.AsyncFunctionDef, file_path: Path, parent_class: str = None):
        """Process an async function definition."""
        signature = self._get_function_signature(node)
        docstring = ast.get_docstring(node)
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        element = CodeElement(
            name=node.name,
            type='async_method' if parent_class else 'async_function',
            file_path=str(file_path),
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            signature=f"async {signature}",
            docstring=docstring,
            parent_class=parent_class,
            decorators=decorators,
            complexity_score=self._calculate_complexity(node)
        )

        key = f"{file_path}:{node.name}:{node.lineno}"
        self.code_elements[key] = element

    def _process_class(self, node: ast.ClassDef, file_path: Path):
        """Process a class definition."""
        docstring = ast.get_docstring(node)
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        # Process class itself
        element = CodeElement(
            name=node.name,
            type='class',
            file_path=str(file_path),
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            signature=self._get_class_signature(node),
            docstring=docstring,
            decorators=decorators,
            complexity_score=len(node.body)  # Simple complexity measure
        )

        key = f"{file_path}:{node.name}:{node.lineno}"
        self.code_elements[key] = element

        # Process class methods
        for child_node in node.body:
            if isinstance(child_node, ast.FunctionDef):
                self._process_function(child_node, file_path, parent_class=node.name)
            elif isinstance(child_node, ast.AsyncFunctionDef):
                self._process_async_function(child_node, file_path, parent_class=node.name)

    def _extract_imports(self, tree: ast.AST, file_path: Path):
        """Extract import information from AST."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_info = ImportInfo(
                        module=alias.name,
                        alias=alias.asname,
                        from_module=None,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        is_local=self._is_local_import(alias.name, file_path)
                    )
                    self.imports.append(import_info)

            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    import_info = ImportInfo(
                        module=alias.name,
                        alias=alias.asname,
                        from_module=module,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        is_local=self._is_local_import(module, file_path)
                    )
                    self.imports.append(import_info)

    def _get_function_signature(self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]) -> str:
        """Generate function signature string."""
        args = []

        # Regular arguments
        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        # Default arguments
        defaults = node.args.defaults
        if defaults:
            num_defaults = len(defaults)
            for i, default in enumerate(defaults):
                arg_index = len(args) - num_defaults + i
                if arg_index >= 0:
                    args[arg_index] += f" = {ast.unparse(default)}"

        # *args
        if node.args.vararg:
            vararg = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                vararg += f": {ast.unparse(node.args.vararg.annotation)}"
            args.append(vararg)

        # **kwargs
        if node.args.kwarg:
            kwarg = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                kwarg += f": {ast.unparse(node.args.kwarg.annotation)}"
            args.append(kwarg)

        signature = f"{node.name}({', '.join(args)})"

        # Return annotation
        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"

        return signature

    def _get_class_signature(self, node: ast.ClassDef) -> str:
        """Generate class signature string."""
        bases = [ast.unparse(base) for base in node.bases]
        if bases:
            return f"class {node.name}({', '.join(bases)})"
        return f"class {node.name}"

    def _get_decorator_name(self, decorator: ast.expr) -> str:
        """Extract decorator name."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return ast.unparse(decorator)
        elif isinstance(decorator, ast.Call):
            return ast.unparse(decorator.func)
        return ast.unparse(decorator)

    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function/method."""
        complexity = 1  # Base complexity

        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1

        return complexity

    def _is_local_import(self, module_name: str, file_path: Path) -> bool:
        """Determine if an import is local to the project."""
        if not module_name:
            return False

        # Check if it's a relative import
        if module_name.startswith('.'):
            return True

        # Check if the module exists in the project directory
        project_root = file_path.parent
        while project_root.parent != project_root:
            if (project_root / f"{module_name.split('.')[0]}.py").exists():
                return True
            if (project_root / module_name.split('.')[0]).is_dir():
                return True
            project_root = project_root.parent

        return False

    def _build_dependency_graphs(self):
        """Build dependency graphs from import information."""
        self.dependency_graph.clear()
        self.reverse_dependency_graph.clear()

        for import_info in self.imports:
            file_path = import_info.file_path

            if file_path not in self.dependency_graph:
                self.dependency_graph[file_path] = set()

            # Add dependency
            if import_info.from_module:
                dependency = import_info.from_module
            else:
                dependency = import_info.module

            self.dependency_graph[file_path].add(dependency)

            # Build reverse dependency graph
            if dependency not in self.reverse_dependency_graph:
                self.reverse_dependency_graph[dependency] = set()
            self.reverse_dependency_graph[dependency].add(file_path)

    def _save_to_database(self):
        """Save indexed data to SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            # Save code elements
            for element in self.code_elements.values():
                conn.execute("""
                    INSERT OR REPLACE INTO code_elements
                    (name, type, file_path, line_number, end_line_number, signature,
                     docstring, parent_class, decorators, complexity_score, dependencies)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    element.name, element.type, element.file_path, element.line_number,
                    element.end_line_number, element.signature, element.docstring,
                    element.parent_class, json.dumps(element.decorators),
                    element.complexity_score, json.dumps(element.dependencies)
                ))

            # Save imports
            for import_info in self.imports:
                conn.execute("""
                    INSERT OR REPLACE INTO imports
                    (module, alias, from_module, file_path, line_number, is_local)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    import_info.module, import_info.alias, import_info.from_module,
                    import_info.file_path, import_info.line_number, import_info.is_local
                ))

            # Save file information
            for file_info in self.files.values():
                conn.execute("""
                    INSERT OR REPLACE INTO files
                    (file_path, size, lines_of_code, last_modified, file_hash,
                     encoding, syntax_errors)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    file_info.file_path, file_info.size, file_info.lines_of_code,
                    file_info.last_modified, file_info.file_hash, file_info.encoding,
                    json.dumps(file_info.syntax_errors)
                ))

    def search_code_elements(self, query: str, element_type: Optional[str] = None,
                           file_pattern: Optional[str] = None) -> List[CodeElement]:
        """
        Search for code elements matching the query.

        Args:
            query: Search query (name, docstring, or signature)
            element_type: Filter by element type ('function', 'class', 'method', etc.)
            file_pattern: Filter by file path pattern

        Returns:
            List of matching code elements
        """
        results = []

        for element in self.code_elements.values():
            # Type filter
            if element_type and element.type != element_type:
                continue

            # File pattern filter
            if file_pattern and file_pattern not in element.file_path:
                continue

            # Query matching
            if (query.lower() in element.name.lower() or
                (element.docstring and query.lower() in element.docstring.lower()) or
                query.lower() in element.signature.lower()):
                results.append(element)

        return results

    def get_dependencies(self, file_path: str) -> Set[str]:
        """Get dependencies for a specific file."""
        return self.dependency_graph.get(file_path, set())

    def get_dependents(self, module_name: str) -> Set[str]:
        """Get files that depend on a specific module."""
        return self.reverse_dependency_graph.get(module_name, set())

    def get_file_summary(self, file_path: str) -> Dict[str, Any]:
        """Get comprehensive summary of a file."""
        file_info = self.files.get(file_path)
        if not file_info:
            return {"error": f"File not found in index: {file_path}"}

        # Get code elements for this file
        elements = [e for e in self.code_elements.values() if e.file_path == file_path]

        # Categorize elements
        functions = [e for e in elements if e.type in ['function', 'async_function']]
        classes = [e for e in elements if e.type == 'class']
        methods = [e for e in elements if e.type in ['method', 'async_method']]

        # Get imports for this file
        file_imports = [i for i in self.imports if i.file_path == file_path]

        return {
            "file_info": asdict(file_info),
            "statistics": {
                "total_elements": len(elements),
                "functions": len(functions),
                "classes": len(classes),
                "methods": len(methods),
                "imports": len(file_imports),
                "average_complexity": sum(e.complexity_score for e in elements) / len(elements) if elements else 0
            },
            "elements": [asdict(e) for e in elements],
            "imports": [asdict(i) for i in file_imports],
            "dependencies": list(self.get_dependencies(file_path)),
            "dependents": list(self.get_dependents(file_path))
        }


# Global indexer instance for caching
_global_indexer: Optional[CodebaseIndexer] = None


def get_global_indexer() -> CodebaseIndexer:
    """Get or create the global indexer instance."""
    global _global_indexer
    if _global_indexer is None:
        _global_indexer = CodebaseIndexer()
    return _global_indexer


def codebase_indexer_tool() -> FunctionTool:
    """
    Create a tool for indexing and analyzing codebases.
    """

    def index_codebase(
        root_path: str,
        exclude_patterns: str = "__pycache__,*.pyc,*.pyo,.git,.svn,node_modules,.venv,venv,*.egg-info",
        include_patterns: str = "*.py",
        force_reindex: bool = False
    ) -> str:
        """
        Index a codebase to create a searchable knowledge base.

        Args:
            root_path: Root directory path to start indexing
            exclude_patterns: Comma-separated patterns to exclude (default: common patterns)
            include_patterns: Comma-separated patterns to include (default: *.py)
            force_reindex: Whether to force reindexing even if cache exists

        Returns:
            Indexing results and statistics as a formatted string
        """
        try:
            indexer = get_global_indexer()

            # Parse patterns
            exclude_list = [p.strip() for p in exclude_patterns.split(',') if p.strip()]
            include_list = [p.strip() for p in include_patterns.split(',') if p.strip()]

            # Check if we need to reindex
            root_path_obj = Path(root_path)
            if not root_path_obj.exists():
                return f"Error: Root path does not exist: {root_path}"

            # Perform indexing
            stats = indexer.index_codebase(
                root_path=root_path_obj,
                exclude_patterns=exclude_list,
                include_patterns=include_list
            )

            # Format results
            result_lines = [
                f"🔍 Codebase Indexing Complete",
                f"Root Path: {root_path}",
                f"Duration: {stats['duration']:.2f} seconds",
                f"Files Processed: {stats['files_processed']}",
                f"Files with Errors: {stats['files_with_errors']}",
                f"Total Code Elements: {stats['total_elements']}",
                f"Total Imports: {stats['total_imports']}",
            ]

            if stats['errors']:
                result_lines.append(f"\nErrors encountered:")
                for error in stats['errors'][:5]:  # Show first 5 errors
                    result_lines.append(f"  - {error}")
                if len(stats['errors']) > 5:
                    result_lines.append(f"  ... and {len(stats['errors']) - 5} more errors")

            return "\n".join(result_lines)

        except Exception as e:
            return f"Error during codebase indexing: {str(e)}"

    return FunctionTool(index_codebase)


def code_search_tool() -> FunctionTool:
    """
    Create a tool for searching code elements in the indexed codebase.
    """

    def search_code(
        query: str,
        element_type: str = "",
        file_pattern: str = "",
        max_results: int = 20
    ) -> str:
        """
        Search for code elements in the indexed codebase.

        Args:
            query: Search query (searches in names, docstrings, and signatures)
            element_type: Filter by element type (function, class, method, async_function, etc.)
            file_pattern: Filter by file path pattern
            max_results: Maximum number of results to return (default: 20)

        Returns:
            Formatted search results
        """
        try:
            indexer = get_global_indexer()

            # Perform search
            results = indexer.search_code_elements(
                query=query,
                element_type=element_type if element_type else None,
                file_pattern=file_pattern if file_pattern else None
            )

            if not results:
                return f"No code elements found matching query: '{query}'"

            # Limit results
            results = results[:max_results]

            # Format results
            result_lines = [f"🔍 Found {len(results)} code elements matching '{query}':\n"]

            for i, element in enumerate(results, 1):
                result_lines.append(f"{i}. {element.type.upper()}: {element.name}")
                result_lines.append(f"   File: {element.file_path}:{element.line_number}")
                result_lines.append(f"   Signature: {element.signature}")

                if element.parent_class:
                    result_lines.append(f"   Class: {element.parent_class}")

                if element.docstring:
                    # Truncate long docstrings
                    docstring = element.docstring[:100] + "..." if len(element.docstring) > 100 else element.docstring
                    result_lines.append(f"   Doc: {docstring}")

                if element.decorators:
                    result_lines.append(f"   Decorators: {', '.join(element.decorators)}")

                result_lines.append(f"   Complexity: {element.complexity_score}")
                result_lines.append("")  # Empty line between results

            return "\n".join(result_lines)

        except Exception as e:
            return f"Error during code search: {str(e)}"

    return FunctionTool(search_code)


def file_analysis_tool() -> FunctionTool:
    """
    Create a tool for detailed file analysis from the indexed codebase.
    """

    def analyze_file(file_path: str) -> str:
        """
        Get detailed analysis of a specific file from the indexed codebase.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Comprehensive file analysis including structure, dependencies, and metrics
        """
        try:
            indexer = get_global_indexer()

            # Get file summary
            summary = indexer.get_file_summary(file_path)

            if "error" in summary:
                return summary["error"]

            # Format analysis
            result_lines = [
                f"📄 File Analysis: {file_path}",
                "=" * (len(file_path) + 17),
                ""
            ]

            # File information
            file_info = summary["file_info"]
            result_lines.extend([
                "📊 File Information:",
                f"  Size: {file_info['size']} bytes",
                f"  Lines of Code: {file_info['lines_of_code']}",
                f"  Last Modified: {file_info['last_modified']}",
                f"  Encoding: {file_info['encoding']}",
                ""
            ])

            # Statistics
            stats = summary["statistics"]
            result_lines.extend([
                "📈 Code Statistics:",
                f"  Total Elements: {stats['total_elements']}",
                f"  Functions: {stats['functions']}",
                f"  Classes: {stats['classes']}",
                f"  Methods: {stats['methods']}",
                f"  Imports: {stats['imports']}",
                f"  Average Complexity: {stats['average_complexity']:.2f}",
                ""
            ])

            # Dependencies
            if summary["dependencies"]:
                result_lines.extend([
                    "🔗 Dependencies:",
                    *[f"  - {dep}" for dep in summary["dependencies"]],
                    ""
                ])

            # Dependents
            if summary["dependents"]:
                result_lines.extend([
                    "⬅️ Files that depend on this:",
                    *[f"  - {dep}" for dep in summary["dependents"]],
                    ""
                ])

            # Code elements summary
            if summary["elements"]:
                result_lines.extend([
                    "🏗️ Code Elements:",
                    ""
                ])

                # Group by type
                elements_by_type = {}
                for element in summary["elements"]:
                    elem_type = element["type"]
                    if elem_type not in elements_by_type:
                        elements_by_type[elem_type] = []
                    elements_by_type[elem_type].append(element)

                for elem_type, elements in elements_by_type.items():
                    result_lines.append(f"  {elem_type.upper()}S:")
                    for element in elements:
                        result_lines.append(f"    - {element['name']} (line {element['line_number']})")
                        if element['docstring']:
                            doc = element['docstring'][:60] + "..." if len(element['docstring']) > 60 else element['docstring']
                            result_lines.append(f"      {doc}")
                    result_lines.append("")

            return "\n".join(result_lines)

        except Exception as e:
            return f"Error during file analysis: {str(e)}"

    return FunctionTool(analyze_file)


def self_awareness_tool() -> FunctionTool:
    """
    Create a tool for agent self-awareness - understanding its own capabilities and structure.
    """

    def analyze_self(include_tools: bool = True, include_structure: bool = True) -> str:
        """
        Analyze the agent's own codebase to understand its capabilities and structure.

        Args:
            include_tools: Whether to include detailed tool analysis
            include_structure: Whether to include codebase structure analysis

        Returns:
            Comprehensive self-analysis report
        """
        try:
            indexer = get_global_indexer()

            # First, ensure the agent's own codebase is indexed
            import os
            agent_root = Path(__file__).parent.parent  # Go up to agent/ directory

            # Index the agent codebase if not already done
            try:
                stats = indexer.index_codebase(agent_root)
            except Exception as e:
                return f"Error indexing agent codebase: {str(e)}"

            result_lines = [
                "🤖 Agent Self-Awareness Report",
                "=" * 30,
                ""
            ]

            # Basic statistics
            result_lines.extend([
                "📊 Codebase Overview:",
                f"  Root Directory: {agent_root}",
                f"  Files Processed: {stats['files_processed']}",
                f"  Total Code Elements: {stats['total_elements']}",
                f"  Total Imports: {stats['total_imports']}",
                ""
            ])

            if include_tools:
                # Analyze available tools
                tools_info = self._analyze_agent_tools(indexer, str(agent_root))
                result_lines.extend([
                    "🛠️ Available Tools:",
                    *tools_info,
                    ""
                ])

            if include_structure:
                # Analyze codebase structure
                structure_info = self._analyze_codebase_structure(indexer, str(agent_root))
                result_lines.extend([
                    "🏗️ Codebase Structure:",
                    *structure_info,
                    ""
                ])

            # Key capabilities
            capabilities = self._identify_key_capabilities(indexer, str(agent_root))
            result_lines.extend([
                "🎯 Key Capabilities:",
                *capabilities,
                ""
            ])

            return "\n".join(result_lines)

        except Exception as e:
            return f"Error during self-analysis: {str(e)}"

    def _analyze_agent_tools(self, indexer: CodebaseIndexer, agent_root: str) -> List[str]:
        """Analyze available agent tools."""
        tools_info = []

        # Find tool functions (functions that return FunctionTool)
        tool_functions = []
        for element in indexer.code_elements.values():
            if (element.file_path.startswith(agent_root) and
                element.type in ['function'] and
                'tool' in element.name.lower() and
                element.signature and 'FunctionTool' in element.signature):
                tool_functions.append(element)

        if tool_functions:
            tools_info.append(f"  Found {len(tool_functions)} tool functions:")
            for tool in tool_functions:
                file_name = Path(tool.file_path).name
                tools_info.append(f"    - {tool.name} ({file_name})")
                if tool.docstring:
                    doc = tool.docstring.split('\n')[0][:80] + "..." if len(tool.docstring) > 80 else tool.docstring.split('\n')[0]
                    tools_info.append(f"      {doc}")
        else:
            tools_info.append("  No tool functions found")

        return tools_info

    def _analyze_codebase_structure(self, indexer: CodebaseIndexer, agent_root: str) -> List[str]:
        """Analyze the codebase structure."""
        structure_info = []

        # Get all files in the agent codebase
        agent_files = [f for f in indexer.files.keys() if f.startswith(agent_root)]

        if agent_files:
            structure_info.append(f"  Files in codebase: {len(agent_files)}")

            # Organize by directory
            dirs = {}
            for file_path in agent_files:
                dir_path = str(Path(file_path).parent)
                if dir_path not in dirs:
                    dirs[dir_path] = []
                dirs[dir_path].append(Path(file_path).name)

            for dir_path, files in dirs.items():
                rel_dir = Path(dir_path).relative_to(agent_root)
                structure_info.append(f"    {rel_dir}/:")
                for file_name in sorted(files):
                    structure_info.append(f"      - {file_name}")

        return structure_info

    def _identify_key_capabilities(self, indexer: CodebaseIndexer, agent_root: str) -> List[str]:
        """Identify key capabilities based on code analysis."""
        capabilities = []

        # Look for key patterns in function names and docstrings
        capability_keywords = {
            'ast': 'AST-based code analysis and manipulation',
            'merge': 'Code merging and integration',
            'index': 'Codebase indexing and search',
            'analyze': 'Code analysis and inspection',
            'search': 'Code search and retrieval',
            'file': 'File system operations',
            'terminal': 'Terminal command execution',
            'docker': 'Docker container operations',
            'calculator': 'Mathematical calculations',
            'time': 'Date and time operations'
        }

        found_capabilities = set()
        for element in indexer.code_elements.values():
            if element.file_path.startswith(agent_root):
                for keyword, description in capability_keywords.items():
                    if (keyword in element.name.lower() or
                        (element.docstring and keyword in element.docstring.lower())):
                        found_capabilities.add(description)

        if found_capabilities:
            capabilities.extend([f"  - {cap}" for cap in sorted(found_capabilities)])
        else:
            capabilities.append("  - Basic agent functionality")

        return capabilities

    return FunctionTool(analyze_self)

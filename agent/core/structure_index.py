"""
Structure indexing service for the Canister agent.

This module houses the underlying implementation that scans a Python codebase
and persists structural information (code elements, imports, file metadata)
into a SQLite cache. Tool wrappers and other agent components should interact
with this service instead of duplicating indexing logic.
"""

from __future__ import annotations

import ast
import hashlib
import json
import sqlite3
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple, Union

from agent.core.telemetry import get_telemetry

# ---------------------------------------------------------------------------
# Compatibility helpers
# ---------------------------------------------------------------------------

if not hasattr(ast, "unparse"):
    try:
        import astor

        def _ast_unparse(node: ast.AST) -> str:
            return astor.to_source(node).strip()

        ast.unparse = _ast_unparse  # type: ignore[attr-defined]
    except ImportError:

        def _ast_unparse(node: ast.AST) -> str:
            if isinstance(node, ast.Name):
                return node.id
            if isinstance(node, ast.Constant):
                return repr(node.value)
            if isinstance(node, ast.Attribute):
                return f"{_ast_unparse(node.value)}.{node.attr}"
            return str(type(node).__name__)

        ast.unparse = _ast_unparse  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


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
    decorators: Optional[List[str]] = None
    complexity_score: int = 0
    dependencies: Optional[List[str]] = None

    def __post_init__(self) -> None:
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
    level: int = 0


@dataclass
class FileInfo:
    """Represents file-level information."""

    file_path: str
    size: int
    lines_of_code: int
    last_modified: datetime
    file_hash: str
    encoding: str = "utf-8"
    syntax_errors: Optional[List[str]] = None

    def __post_init__(self) -> None:
        if self.syntax_errors is None:
            self.syntax_errors = []


# ---------------------------------------------------------------------------
# Structure index implementation
# ---------------------------------------------------------------------------


class StructureIndex:
    """
    Provides indexing and search capabilities over a Python codebase.

    This class was originally implemented as CodebaseIndexer in
    `agent.tools.codebase_indexer`. It now lives under the core namespace so
    other agent capabilities can reuse it without depending on tool wrappers.
    """

    def __init__(self, cache_dir: Optional[Union[str, Path]] = None) -> None:
        self.cache_dir = Path(cache_dir or ".codebase_cache")
        self.cache_dir.mkdir(exist_ok=True)

        self.db_path = self.cache_dir / "codebase_index.db"
        self._init_database()

        self.code_elements: Dict[str, CodeElement] = {}
        self.imports: List[ImportInfo] = []
        self.files: Dict[str, FileInfo] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}
        self.reverse_dependency_graph: Dict[str, Set[str]] = {}
        self.last_root_path: Optional[Path] = None
        self.module_to_file_map: Dict[str, str] = {}
        self.file_to_module_map: Dict[str, str] = {}
        self._active_code_elements: Dict[str, CodeElement] = self.code_elements
        self._active_imports: List[ImportInfo] = self.imports
        self._active_files: Dict[str, FileInfo] = self.files

    # ------------------------------------------------------------------
    # Index lifecycle
    # ------------------------------------------------------------------

    def index_codebase(
        self,
        root_path: Union[str, Path],
        exclude_patterns: Optional[Iterable[str]] = None,
        include_patterns: Optional[Iterable[str]] = None,
    ) -> Dict[str, Any]:
        """Index an entire codebase starting from root_path."""

        root_path = Path(root_path)
        if not root_path.exists():
            raise ValueError(f"Root path does not exist: {root_path}")

        telemetry = get_telemetry()
        telemetry.log_event(
            "structure_index.index_start",
            root=str(root_path),
        )
        self.last_root_path = root_path.resolve()

        exclude_patterns = list(
            exclude_patterns
            or [
                "__pycache__",
                "*.pyc",
                "*.pyo",
                ".git",
                ".svn",
                "node_modules",
                ".venv",
                "venv",
                "*.egg-info",
            ]
        )
        include_patterns = list(include_patterns or ["*.py"])

        stats: Dict[str, Any] = {
            "files_processed": 0,
            "files_reindexed": 0,
            "files_skipped": 0,
            "files_with_errors": 0,
            "total_elements": 0,
            "total_imports": 0,
            "start_time": datetime.now(),
            "errors": [],
        }

        python_files = self._find_python_files(root_path, exclude_patterns, include_patterns)

        root_resolved = self.last_root_path or root_path.resolve()

        def within_root(path_str: str) -> bool:
            return self._is_within_root(path_str, root_resolved)

        previous_elements_by_file: Dict[str, List[CodeElement]] = {}
        for element in self.code_elements.values():
            if within_root(element.file_path):
                previous_elements_by_file.setdefault(element.file_path, []).append(element)

        previous_imports_by_file: Dict[str, List[ImportInfo]] = {}
        for import_info in self.imports:
            if within_root(import_info.file_path):
                previous_imports_by_file.setdefault(import_info.file_path, []).append(import_info)

        previous_files = {
            path: info for path, info in self.files.items() if within_root(path)
        }

        preserved_code_elements = {
            key: element
            for key, element in self.code_elements.items()
            if not within_root(element.file_path)
        }
        preserved_imports = [
            import_info for import_info in self.imports if not within_root(import_info.file_path)
        ]
        preserved_files = {
            path: info for path, info in self.files.items()
            if not within_root(path)
        }

        new_code_elements: Dict[str, CodeElement] = {}
        new_imports: List[ImportInfo] = []
        new_files: Dict[str, FileInfo] = {}

        self._active_code_elements = new_code_elements
        self._active_imports = new_imports
        self._active_files = new_files

        self._clear_existing_data(str(root_path))

        for file_path in python_files:
            try:
                previous_file = previous_files.get(str(file_path))
                previous_elements = previous_elements_by_file.get(str(file_path))
                previous_imports = previous_imports_by_file.get(str(file_path))
                parsed = self._index_file(
                    file_path,
                    previous_file=previous_file,
                    previous_elements=previous_elements,
                    previous_imports=previous_imports,
                )
                stats["files_processed"] += 1
                if parsed:
                    stats["files_reindexed"] += 1
                else:
                    stats["files_skipped"] += 1
            except Exception as exc:  # pragma: no cover - defensive logging
                stats["files_with_errors"] += 1
                stats["errors"].append(f"Error processing {file_path}: {exc}")

        self.code_elements = {**preserved_code_elements, **new_code_elements}
        self.imports = preserved_imports + new_imports
        self.files = {**preserved_files, **new_files}

        self._active_code_elements = self.code_elements
        self._active_imports = self.imports
        self._active_files = self.files

        self._build_dependency_graphs()
        self._save_to_database()

        stats["end_time"] = datetime.now()
        stats["duration"] = (stats["end_time"] - stats["start_time"]).total_seconds()
        stats["total_elements"] = len(self.code_elements)
        stats["total_imports"] = len(self.imports)

        telemetry.log_event(
            "structure_index.index_complete",
            root=str(root_path),
            duration_seconds=stats["duration"],
            files_processed=stats["files_processed"],
            files_reindexed=stats["files_reindexed"],
            files_skipped=stats["files_skipped"],
            files_with_errors=stats["files_with_errors"],
            total_elements=stats["total_elements"],
            total_imports=stats["total_imports"],
        )
        return stats

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _init_database(self) -> None:
        telemetry = get_telemetry()
        telemetry.log_event("structure_index.database_init", path=str(self.db_path))

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(
                """
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
                """
            )

    def _find_python_files(
        self,
        root_path: Path,
        exclude_patterns: Iterable[str],
        include_patterns: Iterable[str],
    ) -> List[Path]:
        python_files: List[Path] = []

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

        for path in root_path.rglob("*"):
            if path.is_file() and should_include(path) and not should_exclude(path):
                python_files.append(path)

        return python_files

    def _clear_existing_data(self, root_path: str) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM code_elements WHERE file_path LIKE ?", (f"{root_path}%",))
            conn.execute("DELETE FROM imports WHERE file_path LIKE ?", (f"{root_path}%",))
            conn.execute("DELETE FROM files WHERE file_path LIKE ?", (f"{root_path}%",))

    def _index_file(
        self,
        file_path: Path,
        previous_file: Optional[FileInfo] = None,
        previous_elements: Optional[List[CodeElement]] = None,
        previous_imports: Optional[List[ImportInfo]] = None,
    ) -> bool:
        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            content = file_path.read_text(encoding="latin-1")

        file_hash = hashlib.md5(content.encode()).hexdigest()
        stat = file_path.stat()

        file_info = FileInfo(
            file_path=str(file_path),
            size=stat.st_size,
            lines_of_code=len(content.splitlines()),
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            file_hash=file_hash,
        )

        if previous_file and previous_file.file_hash == file_info.file_hash:
            file_info.syntax_errors = list(previous_file.syntax_errors)
            self._active_files[str(file_path)] = file_info
            if previous_elements:
                for element in previous_elements:
                    self._store_code_element(element)
            if previous_imports:
                self._active_imports.extend(previous_imports)
            return False

        try:
            tree = ast.parse(content, filename=str(file_path))
            self._extract_code_elements(tree, file_path)
            self._extract_imports(tree, file_path)
        except SyntaxError as exc:
            file_info.syntax_errors.append(f"Syntax error: {exc}")

        self._active_files[str(file_path)] = file_info
        return True

    def _extract_code_elements(self, tree: ast.AST, file_path: Path) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self._process_function(node, file_path)
            elif isinstance(node, ast.AsyncFunctionDef):
                self._process_async_function(node, file_path)
            elif isinstance(node, ast.ClassDef):
                self._process_class(node, file_path)

    @staticmethod
    def _element_key(file_path: Union[str, Path], name: str, line_number: int) -> str:
        return f"{str(file_path)}:{name}:{line_number}"

    def _store_code_element(self, element: CodeElement) -> None:
        key = self._element_key(element.file_path, element.name, element.line_number)
        self._active_code_elements[key] = element

    def _process_function(
        self,
        node: ast.FunctionDef,
        file_path: Path,
        parent_class: Optional[str] = None,
    ) -> None:
        signature = self._get_function_signature(node)
        docstring = ast.get_docstring(node)
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        element = CodeElement(
            name=node.name,
            type="method" if parent_class else "function",
            file_path=str(file_path),
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            signature=signature,
            docstring=docstring,
            parent_class=parent_class,
            decorators=decorators,
            complexity_score=self._calculate_complexity(node),
        )

        self._store_code_element(element)

    def _process_async_function(
        self,
        node: ast.AsyncFunctionDef,
        file_path: Path,
        parent_class: Optional[str] = None,
    ) -> None:
        signature = self._get_function_signature(node)
        docstring = ast.get_docstring(node)
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        element = CodeElement(
            name=node.name,
            type="async_method" if parent_class else "async_function",
            file_path=str(file_path),
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            signature=f"async {signature}",
            docstring=docstring,
            parent_class=parent_class,
            decorators=decorators,
            complexity_score=self._calculate_complexity(node),
        )

        self._store_code_element(element)

    def _process_class(self, node: ast.ClassDef, file_path: Path) -> None:
        docstring = ast.get_docstring(node)
        decorators = [self._get_decorator_name(d) for d in node.decorator_list]

        element = CodeElement(
            name=node.name,
            type="class",
            file_path=str(file_path),
            line_number=node.lineno,
            end_line_number=node.end_lineno or node.lineno,
            signature=self._get_class_signature(node),
            docstring=docstring,
            decorators=decorators,
            complexity_score=len(node.body),
        )

        self._store_code_element(element)

        for child_node in node.body:
            if isinstance(child_node, ast.FunctionDef):
                self._process_function(child_node, file_path, parent_class=node.name)
            elif isinstance(child_node, ast.AsyncFunctionDef):
                self._process_async_function(child_node, file_path, parent_class=node.name)

    def _extract_imports(self, tree: ast.AST, file_path: Path) -> None:
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_info = ImportInfo(
                        module=alias.name,
                        alias=alias.asname,
                        from_module=None,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        is_local=self._is_local_import(alias.name, file_path),
                        level=0,
                    )
                    self._active_imports.append(import_info)
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                for alias in node.names:
                    import_info = ImportInfo(
                        module=alias.name,
                        alias=alias.asname,
                        from_module=module,
                        file_path=str(file_path),
                        line_number=node.lineno,
                        is_local=self._is_local_import(module, file_path),
                        level=getattr(node, "level", 0) or 0,
                    )
                    self._active_imports.append(import_info)

    def _get_function_signature(
        self, node: Union[ast.FunctionDef, ast.AsyncFunctionDef]
    ) -> str:
        args: List[str] = []

        for arg in node.args.args:
            arg_str = arg.arg
            if arg.annotation:
                arg_str += f": {ast.unparse(arg.annotation)}"
            args.append(arg_str)

        defaults = node.args.defaults
        if defaults:
            num_defaults = len(defaults)
            for i, default in enumerate(defaults):
                arg_index = len(args) - num_defaults + i
                if arg_index >= 0:
                    args[arg_index] += f" = {ast.unparse(default)}"

        if node.args.vararg:
            vararg = f"*{node.args.vararg.arg}"
            if node.args.vararg.annotation:
                vararg += f": {ast.unparse(node.args.vararg.annotation)}"
            args.append(vararg)

        if node.args.kwarg:
            kwarg = f"**{node.args.kwarg.arg}"
            if node.args.kwarg.annotation:
                kwarg += f": {ast.unparse(node.args.kwarg.annotation)}"
            args.append(kwarg)

        signature = f"{node.name}({', '.join(args)})"

        if node.returns:
            signature += f" -> {ast.unparse(node.returns)}"

        return signature

    def _get_class_signature(self, node: ast.ClassDef) -> str:
        bases = [ast.unparse(base) for base in node.bases]
        if bases:
            return f"class {node.name}({', '.join(bases)})"
        return f"class {node.name}"

    @staticmethod
    def _get_decorator_name(decorator: ast.expr) -> str:
        if isinstance(decorator, ast.Name):
            return decorator.id
        if isinstance(decorator, ast.Attribute):
            return ast.unparse(decorator)
        if isinstance(decorator, ast.Call):
            return ast.unparse(decorator.func)
        return ast.unparse(decorator)

    @staticmethod
    def _calculate_complexity(node: ast.AST) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.And, ast.Or)):
                complexity += 1
        return complexity

    def _is_local_import(self, module_name: str, file_path: Path) -> bool:
        if not module_name:
            return False

        if module_name.startswith("."):
            return True

        project_root = file_path.parent
        while project_root.parent != project_root:
            if (project_root / f"{module_name.split('.')[0]}.py").exists():
                return True
            if (project_root / module_name.split(".")[0]).is_dir():
                return True
            project_root = project_root.parent

        return False

    @staticmethod
    def _is_within_root(path_str: str, root: Path) -> bool:
        try:
            Path(path_str).resolve().relative_to(root.resolve())
            return True
        except ValueError:
            return False

    def _build_module_maps(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        module_to_file: Dict[str, str] = {}
        file_to_module: Dict[str, str] = {}

        root = self.last_root_path
        if not root:
            return module_to_file, file_to_module

        root = root.resolve()
        for file_path_str in self.files.keys():
            path_obj = Path(file_path_str).resolve()
            try:
                rel = path_obj.relative_to(root)
            except ValueError:
                continue

            if path_obj.suffix != ".py":
                continue

            module_parts = list(rel.with_suffix("").parts)
            is_package_init = bool(module_parts and module_parts[-1] == "__init__")
            if is_package_init:
                base_parts = module_parts[:-1]
            else:
                base_parts = module_parts

            if not base_parts:
                module_name = root.name
            else:
                module_name = ".".join(base_parts)

            module_to_file[module_name] = str(path_obj)
            file_to_module[str(path_obj)] = module_name

            if is_package_init:
                module_to_file[".".join(module_parts)] = str(path_obj)

        return module_to_file, file_to_module

    def _normalize_dependencies(
        self,
        import_info: ImportInfo,
        module_to_file: Dict[str, str],
        file_to_module: Dict[str, str],
    ) -> Set[str]:
        candidates: Set[str] = set()
        module = (import_info.module or "").strip()
        from_module = (import_info.from_module or "").strip()
        level = import_info.level or 0

        if module and not from_module:
            candidates.add(module)

        if from_module:
            candidates.add(from_module)
            if module and module != "*":
                candidates.add(f"{from_module}.{module}")

        if module and module != "*" and from_module:
            candidates.add(module)

        file_module = file_to_module.get(import_info.file_path)
        if level:
            if file_module:
                base_parts = file_module.split(".")
                if level <= len(base_parts):
                    base_parts = base_parts[:-level]
                else:
                    base_parts = []
                relative_parts = module.split(".") if module else []
                combined_parts = [part for part in base_parts + relative_parts if part]
                if combined_parts:
                    candidates.add(".".join(combined_parts))
                elif base_parts:
                    candidates.add(".".join(base_parts))
            elif module:
                candidates.add(module.lstrip("."))

        if not candidates and module:
            candidates.add(module)
        if not candidates and from_module:
            candidates.add(from_module)

        normalized: Set[str] = set()
        fallback: Set[str] = set()
        for candidate in candidates:
            candidate = candidate.lstrip(".")
            if not candidate:
                continue
            resolved = self._resolve_module_to_file(candidate, module_to_file)
            if resolved:
                normalized.add(resolved)
            else:
                fallback.add(candidate)

        if normalized:
            return normalized
        return fallback or {"external"}

    @staticmethod
    def _resolve_module_to_file(
        module_name: str,
        module_to_file: Dict[str, str],
    ) -> Optional[str]:
        if module_name in module_to_file:
            return module_to_file[module_name]

        parts = module_name.split(".")
        while len(parts) > 1:
            parts = parts[:-1]
            candidate = ".".join(parts)
            if candidate in module_to_file:
                return module_to_file[candidate]
        return None

    def _build_dependency_graphs(self) -> None:
        self.dependency_graph.clear()
        self.reverse_dependency_graph.clear()
        module_to_file, file_to_module = self._build_module_maps()
        self.module_to_file_map = module_to_file
        self.file_to_module_map = file_to_module

        for import_info in self.imports:
            file_path = import_info.file_path
            self.dependency_graph.setdefault(file_path, set())

            normalized_dependencies = self._normalize_dependencies(
                import_info, module_to_file, file_to_module
            )

            for dependency in normalized_dependencies:
                self.dependency_graph[file_path].add(dependency)
                self.reverse_dependency_graph.setdefault(dependency, set()).add(file_path)

    def _save_to_database(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            for element in self.code_elements.values():
                conn.execute(
                    """
                    INSERT OR REPLACE INTO code_elements
                    (name, type, file_path, line_number, end_line_number, signature,
                     docstring, parent_class, decorators, complexity_score, dependencies)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        element.name,
                        element.type,
                        element.file_path,
                        element.line_number,
                        element.end_line_number,
                        element.signature,
                        element.docstring,
                        element.parent_class,
                        json.dumps(element.decorators),
                        element.complexity_score,
                        json.dumps(element.dependencies),
                    ),
                )

            for import_info in self.imports:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO imports
                    (module, alias, from_module, file_path, line_number, is_local)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        import_info.module,
                        import_info.alias,
                        import_info.from_module,
                        import_info.file_path,
                        import_info.line_number,
                        import_info.is_local,
                    ),
                )

            for file_info in self.files.values():
                conn.execute(
                    """
                    INSERT OR REPLACE INTO files
                    (file_path, size, lines_of_code, last_modified, file_hash,
                     encoding, syntax_errors)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        file_info.file_path,
                        file_info.size,
                        file_info.lines_of_code,
                        file_info.last_modified,
                        file_info.file_hash,
                        file_info.encoding,
                        json.dumps(file_info.syntax_errors),
                    ),
                )

    # ------------------------------------------------------------------
    # Public query APIs
    # ------------------------------------------------------------------

    def search_code_elements(
        self,
        query: str,
        element_type: Optional[str] = None,
        file_pattern: Optional[str] = None,
    ) -> List[CodeElement]:
        results: List[CodeElement] = []
        for element in self.code_elements.values():
            if element_type and element.type != element_type:
                continue
            if file_pattern and file_pattern not in element.file_path:
                continue
            if query.lower() in element.name.lower() or (
                element.docstring and query.lower() in element.docstring.lower()
            ):
                results.append(element)
                continue
            if query.lower() in element.signature.lower():
                results.append(element)
        return results

    def get_dependencies(self, file_path: str) -> Set[str]:
        return self.dependency_graph.get(file_path, set())

    def get_dependents(self, target: str) -> Set[str]:
        dependents = set(self.reverse_dependency_graph.get(target, set()))

        module_name = self.file_to_module_map.get(target)
        if module_name:
            dependents.update(self.reverse_dependency_graph.get(module_name, set()))
        else:
            file_path = self.module_to_file_map.get(target)
            if file_path:
                dependents.update(self.reverse_dependency_graph.get(file_path, set()))

        return dependents

    def get_file_summary(self, file_path: str) -> Dict[str, Any]:
        file_info = self.files.get(file_path)
        if not file_info:
            return {"error": f"File not found in index: {file_path}"}

        elements = [e for e in self.code_elements.values() if e.file_path == file_path]

        functions = [e for e in elements if e.type in ["function", "async_function"]]
        classes = [e for e in elements if e.type == "class"]
        methods = [e for e in elements if e.type in ["method", "async_method"]]

        file_imports = [imp for imp in self.imports if imp.file_path == file_path]

        return {
            "file_info": asdict(file_info),
            "statistics": {
                "total_elements": len(elements),
                "functions": len(functions),
                "classes": len(classes),
                "methods": len(methods),
                "imports": len(file_imports),
                "average_complexity": (
                    sum(e.complexity_score for e in elements) / len(elements)
                    if elements
                    else 0
                ),
            },
            "elements": [asdict(e) for e in elements],
            "imports": [asdict(i) for i in file_imports],
            "dependencies": list(self.get_dependencies(file_path)),
            "dependents": list(self.get_dependents(file_path)),
        }


# ---------------------------------------------------------------------------
# Global accessor
# ---------------------------------------------------------------------------

_global_structure_index: Optional[StructureIndex] = None


def get_structure_index(cache_dir: Optional[Union[str, Path]] = None) -> StructureIndex:
    """Return the shared StructureIndex instance (creating it if needed)."""
    global _global_structure_index
    if _global_structure_index is None:
        _global_structure_index = StructureIndex(cache_dir=cache_dir)
    elif cache_dir and Path(cache_dir) != _global_structure_index.cache_dir:
        _global_structure_index = StructureIndex(cache_dir=cache_dir)
    return _global_structure_index


# For backwards compatibility with existing imports.
CodebaseIndexer = StructureIndex

__all__ = [
    "CodeElement",
    "ImportInfo",
    "FileInfo",
    "StructureIndex",
    "CodebaseIndexer",
    "get_structure_index",
]

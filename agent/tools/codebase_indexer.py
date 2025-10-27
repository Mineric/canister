"""
Tool wrappers for the core structure index service.

These functions expose Google ADK FunctionTools that delegate to the shared
StructureIndex implementation located under ``agent.core.structure_index``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional

from google.adk.tools import FunctionTool

from agent.core.structure_index import (
    CodebaseIndexer,
    get_structure_index,
)

__all__ = [
    "CodebaseIndexer",
    "codebase_indexer_tool",
    "code_search_tool",
    "file_analysis_tool",
    "self_awareness_tool",
    "get_global_indexer",
]


def get_global_indexer() -> CodebaseIndexer:
    """
    Return the shared structure index instance.

    This preserves the historical name used throughout the codebase while
    delegating to the new core implementation.
    """
    return get_structure_index()


def codebase_indexer_tool() -> FunctionTool:
    """
    Create a tool for indexing and analyzing codebases.
    """

    def index_codebase(
        root_path: str,
        exclude_patterns: str = "__pycache__,*.pyc,*.pyo,.git,.svn,node_modules,.venv,venv,*.egg-info",
        include_patterns: str = "*.py",
        force_reindex: bool = False,  # Included for backwards compatibility
    ) -> str:
        try:
            indexer = get_global_indexer()

            exclude_list = [p.strip() for p in exclude_patterns.split(",") if p.strip()]
            include_list = [p.strip() for p in include_patterns.split(",") if p.strip()]

            root_path_obj = Path(root_path)
            if not root_path_obj.exists():
                return f"Error: Root path does not exist: {root_path}"

            stats = indexer.index_codebase(
                root_path=root_path_obj,
                exclude_patterns=exclude_list,
                include_patterns=include_list,
            )

            result_lines = [
                "🔍 Codebase Indexing Complete",
                f"Root Path: {root_path}",
                f"Duration: {stats['duration']:.2f} seconds",
                f"Files Processed: {stats['files_processed']}",
                f"Files Reindexed: {stats.get('files_reindexed', 0)}",
                f"Files Skipped (cached): {stats.get('files_skipped', 0)}",
                f"Files with Errors: {stats['files_with_errors']}",
                f"Total Code Elements: {stats['total_elements']}",
                f"Total Imports: {stats['total_imports']}",
            ]

            if stats["errors"]:
                result_lines.append("\nErrors encountered:")
                for error in stats["errors"][:5]:
                    result_lines.append(f"  - {error}")
                if len(stats["errors"]) > 5:
                    result_lines.append(f"  ... and {len(stats['errors']) - 5} more errors")

            return "\n".join(result_lines)

        except Exception as exc:
            return f"Error during codebase indexing: {exc}"

    return FunctionTool(index_codebase)


def code_search_tool() -> FunctionTool:
    """
    Create a tool for searching code elements in the indexed codebase.
    """

    def search_code(
        query: str,
        element_type: str = "",
        file_pattern: str = "",
        max_results: int = 20,
    ) -> str:
        try:
            indexer = get_global_indexer()
            results = indexer.search_code_elements(
                query=query,
                element_type=element_type or None,
                file_pattern=file_pattern or None,
            )

            if not results:
                return f"No code elements found matching query: '{query}'"

            results = results[:max_results]

            result_lines = [f"🔍 Found {len(results)} code elements matching '{query}':\n"]

            for i, element in enumerate(results, 1):
                result_lines.append(f"{i}. {element.type.upper()}: {element.name}")
                result_lines.append(f"   File: {element.file_path}:{element.line_number}")
                result_lines.append(f"   Signature: {element.signature}")

                if element.parent_class:
                    result_lines.append(f"   Class: {element.parent_class}")

                if element.docstring:
                    docstring = (
                        element.docstring[:100] + "..."
                        if len(element.docstring) > 100
                        else element.docstring
                    )
                    result_lines.append(f"   Doc: {docstring}")

                if element.decorators:
                    result_lines.append(f"   Decorators: {', '.join(element.decorators)}")

                result_lines.append(f"   Complexity: {element.complexity_score}")
                result_lines.append("")

            return "\n".join(result_lines)

        except Exception as exc:
            return f"Error during code search: {exc}"

    return FunctionTool(search_code)


def file_analysis_tool() -> FunctionTool:
    """
    Create a tool for detailed file analysis from the indexed codebase.
    """

    def analyze_file(file_path: str) -> str:
        try:
            indexer = get_global_indexer()
            summary = indexer.get_file_summary(file_path)

            if "error" in summary:
                return summary["error"]

            result_lines: List[str] = [
                f"📄 File Analysis: {file_path}",
                "=" * (len(file_path) + 17),
                "",
            ]

            file_info: Any = summary["file_info"]
            result_lines.extend(
                [
                    "📊 File Information:",
                    f"  Size: {file_info['size']} bytes",
                    f"  Lines of Code: {file_info['lines_of_code']}",
                    f"  Last Modified: {file_info['last_modified']}",
                    f"  Encoding: {file_info['encoding']}",
                    "",
                ]
            )

            stats: Any = summary["statistics"]
            result_lines.extend(
                [
                    "📈 Code Statistics:",
                    f"  Total Elements: {stats['total_elements']}",
                    f"  Functions: {stats['functions']}",
                    f"  Classes: {stats['classes']}",
                    f"  Methods: {stats['methods']}",
                    f"  Imports: {stats['imports']}",
                    f"  Average Complexity: {stats['average_complexity']:.2f}",
                    "",
                ]
            )

            if summary["dependencies"]:
                result_lines.extend(
                    ["🔗 Dependencies:", *[f"  - {dep}" for dep in summary["dependencies"]], ""]
                )

            if summary["dependents"]:
                result_lines.extend(
                    [
                        "⬅️ Files that depend on this:",
                        *[f"  - {dep}" for dep in summary["dependents"]],
                        "",
                    ]
                )

            if summary["elements"]:
                result_lines.extend(["🏗️ Code Elements:", ""])
                elements_by_type: dict[str, List[Any]] = {}
                for element in summary["elements"]:
                    elements_by_type.setdefault(element["type"], []).append(element)

                for elem_type, elements in elements_by_type.items():
                    result_lines.append(f"  {elem_type.upper()}S:")
                    for element in elements:
                        result_lines.append(
                            f"    - {element['name']} (line {element['line_number']})"
                        )
                        if element.get("docstring"):
                            doc = (
                                element["docstring"][:60] + "..."
                                if len(element["docstring"]) > 60
                                else element["docstring"]
                            )
                            result_lines.append(f"      {doc}")
                    result_lines.append("")

            return "\n".join(result_lines)

        except Exception as exc:
            return f"Error during file analysis: {exc}"

    return FunctionTool(analyze_file)


def self_awareness_tool() -> FunctionTool:
    """
    Create a tool for agent self-awareness - understanding its own capabilities and structure.
    """

    def analyze_self(include_tools: bool = True, include_structure: bool = True) -> str:
        try:
            indexer = get_global_indexer()
            agent_root = Path(__file__).parent.parent  # agent/ directory

            try:
                stats = indexer.index_codebase(agent_root)
            except Exception as exc:
                return f"Error indexing agent codebase: {exc}"

            result_lines: List[str] = [
                "🤖 Agent Self-Awareness Report",
                "=" * 30,
                "",
                "📊 Codebase Overview:",
                f"  Root Directory: {agent_root}",
                f"  Files Processed: {stats['files_processed']}",
                f"  Total Code Elements: {stats['total_elements']}",
                f"  Total Imports: {stats['total_imports']}",
                "",
            ]

            if include_tools:
                tools_info = _analyze_agent_tools(indexer, str(agent_root))
                result_lines.extend(["🛠️ Available Tools:", *tools_info, ""])

            if include_structure:
                structure_info = _analyze_codebase_structure(indexer, str(agent_root))
                result_lines.extend(["🏗️ Codebase Structure:", *structure_info, ""])

            capabilities = _identify_key_capabilities(indexer, str(agent_root))
            result_lines.extend(["🎯 Key Capabilities:", *capabilities, ""])

            return "\n".join(result_lines)

        except Exception as exc:
            return f"Error during self-analysis: {exc}"

    return FunctionTool(analyze_self)


def _analyze_agent_tools(indexer: CodebaseIndexer, agent_root: str) -> List[str]:
    tools_info: List[str] = []
    tool_functions = []

    for element in indexer.code_elements.values():
        if (
            element.file_path.startswith(agent_root)
            and element.type in ["function"]
            and element.signature
            and "FunctionTool" in element.signature
            and "tool" in element.name.lower()
        ):
            tool_functions.append(element)

    if tool_functions:
        tools_info.append(f"  Found {len(tool_functions)} tool functions:")
        for tool in tool_functions:
            file_name = Path(tool.file_path).name
            tools_info.append(f"    - {tool.name} ({file_name})")
            if tool.docstring:
                doc = tool.docstring.split("\n")[0]
                if len(doc) > 80:
                    doc = doc[:80] + "..."
                tools_info.append(f"      {doc}")
    else:
        tools_info.append("  No tool functions found")

    return tools_info


def _analyze_codebase_structure(indexer: CodebaseIndexer, agent_root: str) -> List[str]:
    structure_info: List[str] = []
    agent_files = [f for f in indexer.files.keys() if f.startswith(agent_root)]

    if agent_files:
        structure_info.append(f"  Files in codebase: {len(agent_files)}")
        dirs: dict[str, List[str]] = {}
        for file_path in agent_files:
            dir_path = str(Path(file_path).parent)
            dirs.setdefault(dir_path, []).append(Path(file_path).name)

        for dir_path, files in dirs.items():
            rel_dir = Path(dir_path).relative_to(agent_root)
            structure_info.append(f"    {rel_dir}/:")
            for file_name in sorted(files):
                structure_info.append(f"      - {file_name}")

    return structure_info


def _identify_key_capabilities(indexer: CodebaseIndexer, agent_root: str) -> List[str]:
    capabilities: List[str] = []
    capability_keywords = {
        "ast": "AST-based code analysis and manipulation",
        "merge": "Code merging and integration",
        "index": "Codebase indexing and search",
        "analyze": "Code analysis and inspection",
        "search": "Code search and retrieval",
        "file": "File system operations",
        "terminal": "Terminal command execution",
        "docker": "Docker container operations",
        "calculator": "Mathematical calculations",
        "time": "Date and time operations",
    }

    found_capabilities = set()
    for element in indexer.code_elements.values():
        if element.file_path.startswith(agent_root):
            for keyword, description in capability_keywords.items():
                if keyword in element.name.lower():
                    found_capabilities.add(description)
                    continue
                if element.docstring and keyword in element.docstring.lower():
                    found_capabilities.add(description)

    if found_capabilities:
        capabilities.extend([f"  - {cap}" for cap in sorted(found_capabilities)])
    else:
        capabilities.append("  - Basic agent functionality")

    return capabilities

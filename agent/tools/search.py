"""
Search Tools - Canister Agent
Unified search across code, memory, and documentation.
"""

import re
import ast
from pathlib import Path
from typing import Dict, Any, List, Optional, Union


class SearchTools:
    """Unified search across code, memory, and documentation."""
    
    @staticmethod
    def code(query: str, search_type: str = "hybrid", root_path: str = ".", 
            file_pattern: str = "*.py", max_results: int = 20) -> str:
        """
        Search code elements with semantic + keyword.
        
        Args:
            query: Search query (function names, class names, or content)
            search_type: Type of search ('keyword', 'pattern', 'hybrid')
            root_path: Root directory to search in
            file_pattern: File pattern to match (e.g., '*.py')
            max_results: Maximum number of results to return
            
        Returns:
            Formatted search results
        """
        try:
            root = Path(root_path)
            if not root.exists():
                return f"Error: Root path '{root_path}' does not exist"
            
            # Find matching files
            files = list(root.rglob(file_pattern))
            if not files:
                return f"No files matching pattern '{file_pattern}' found in '{root_path}'"
            
            results = []
            
            # Search through files
            for file_path in files:
                try:
                    # Skip non-text files and common excludes
                    if any(exclude in str(file_path) for exclude in ['__pycache__', '.git', '.venv']):
                        continue
                    
                    content = file_path.read_text(encoding='utf-8')
                    
                    # Perform different types of searches
                    if search_type in ['keyword', 'hybrid']:
                        keyword_matches = SearchTools._keyword_search(query, content, file_path)
                        results.extend(keyword_matches)
                    
                    if search_type in ['pattern', 'hybrid']:
                        pattern_matches = SearchTools._pattern_search(query, content, file_path)
                        results.extend(pattern_matches)
                    
                except (UnicodeDecodeError, PermissionError):
                    continue  # Skip files that can't be read
                except Exception:
                    continue  # Skip files with other issues
            
            # Sort and limit results
            results.sort(key=lambda x: x.get('relevance', 0), reverse=True)
            results = results[:max_results]
            
            if not results:
                return f"No results found for query: '{query}'"
            
            # Format results
            result_lines = [
                f"🔍 Code Search Results for '{query}'",
                f"Search Type: {search_type} | Found: {len(results)} results",
                "=" * 60,
                ""
            ]
            
            for i, result in enumerate(results, 1):
                result_lines.extend([
                    f"{i}. {result['type'].upper()}: {result['name']}",
                    f"   📁 {result['file']}:{result['line']}",
                    f"   📝 {result['context'][:100]}{'...' if len(result['context']) > 100 else ''}",
                    ""
                ])
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return f"Error in code search: {str(e)}"
    
    @staticmethod
    def _keyword_search(query: str, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Perform keyword-based search."""
        results = []
        query_lower = query.lower()
        lines = content.split('\n')
        
        # Simple keyword matching in content
        for line_num, line in enumerate(lines, 1):
            if query_lower in line.lower():
                results.append({
                    'type': 'keyword_match',
                    'name': query,
                    'file': str(file_path),
                    'line': line_num,
                    'context': line.strip(),
                    'relevance': 0.5
                })
        
        # AST-based search for function and class names
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and query_lower in node.name.lower():
                    results.append({
                        'type': 'function',
                        'name': node.name,
                        'file': str(file_path),
                        'line': node.lineno,
                        'context': f"def {node.name}(...)",
                        'relevance': 0.8
                    })
                elif isinstance(node, ast.ClassDef) and query_lower in node.name.lower():
                    results.append({
                        'type': 'class',
                        'name': node.name,
                        'file': str(file_path),
                        'line': node.lineno,
                        'context': f"class {node.name}",
                        'relevance': 0.8
                    })
        except SyntaxError:
            pass  # Skip files with syntax errors
        
        return results
    
    @staticmethod
    def _pattern_search(query: str, content: str, file_path: Path) -> List[Dict[str, Any]]:
        """Perform pattern-based search using regex."""
        results = []
        
        try:
            # Use query as regex pattern
            pattern = re.compile(query, re.IGNORECASE)
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                matches = pattern.finditer(line)
                for match in matches:
                    results.append({
                        'type': 'pattern_match',
                        'name': match.group(),
                        'file': str(file_path),
                        'line': line_num,
                        'context': line.strip(),
                        'relevance': 0.6
                    })
        
        except re.error:
            # If query is not a valid regex, skip pattern search
            pass
        
        return results
    
    @staticmethod
    def memory(query: str, search_type: str = "keyword", context_types: str = "all",
              max_results: int = 10, session_id: str = "current") -> str:
        """
        Search memory with context awareness.
        
        Args:
            query: Search query for memory content
            search_type: Type of search ('keyword', 'semantic', 'hybrid')
            context_types: Types of context to search ('all', 'conversation', 'code', etc.)
            max_results: Maximum number of results
            session_id: Session ID to search within
            
        Returns:
            Formatted memory search results
        """
        # Note: This is a placeholder implementation
        # In the real system, this would integrate with the MemoryEngine
        
        try:
            # Simulate memory search results
            if search_type == "semantic":
                return f"🧠 Semantic Memory Search for '{query}' (Feature not yet implemented)\n" \
                       f"This will be implemented when vector capabilities are added.\n" \
                       f"Current mode: {search_type} | Context: {context_types}"
            
            # Basic keyword-based memory search simulation
            result_lines = [
                f"🧠 Memory Search Results for '{query}'",
                f"Search Type: {search_type} | Context: {context_types}",
                f"Session: {session_id}",
                "=" * 50,
                "",
                "ℹ️ Memory search integration pending:",
                "  • Will integrate with MemoryEngine when implemented",
                "  • Will support semantic search with vector capabilities",
                f"  • Current query: '{query}' in {context_types} context",
                ""
            ]
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return f"Error in memory search: {str(e)}"
    
    @staticmethod
    def similarity(item: str, item_type: str = "auto", threshold: float = 0.7,
                  max_results: int = 10, include_score: bool = True) -> str:
        """
        Find similar items (code, memory, docs).
        
        Args:
            item: The item to find similarities for (code snippet, text, etc.)
            item_type: Type of item ('code', 'text', 'auto')
            threshold: Similarity threshold (0.0 to 1.0)
            max_results: Maximum number of similar items to return
            include_score: Whether to include similarity scores
            
        Returns:
            Formatted similarity search results
        """
        try:
            # Detect item type if auto
            if item_type == "auto":
                if SearchTools._looks_like_code(item):
                    item_type = "code"
                else:
                    item_type = "text"
            
            result_lines = [
                f"🎯 Similarity Search Results",
                f"Query: {item[:50]}{'...' if len(item) > 50 else ''}",
                f"Type: {item_type} | Threshold: {threshold}",
                "=" * 50,
                "",
                "ℹ️ Similarity search will be enhanced with vector capabilities:",
                "  • Semantic similarity using embeddings",
                "  • Code structure similarity analysis", 
                "  • Cross-modal similarity (code ↔ text)",
                "",
                f"Current basic analysis:",
                f"  • Item length: {len(item)} characters",
                f"  • Detected type: {item_type}",
                f"  • Would search for items with >{threshold} similarity",
                ""
            ]
            
            if item_type == "code":
                result_lines.extend([
                    "🔍 Code Analysis:",
                    f"  • Contains function definitions: {'Yes' if 'def ' in item else 'No'}",
                    f"  • Contains class definitions: {'Yes' if 'class ' in item else 'No'}",
                    f"  • Contains imports: {'Yes' if 'import ' in item else 'No'}",
                    ""
                ])
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return f"Error in similarity search: {str(e)}"
    
    @staticmethod
    def _looks_like_code(text: str) -> bool:
        """Heuristic to determine if text looks like code."""
        code_indicators = [
            'def ', 'class ', 'import ', 'from ', 'return ', 'if __name__',
            '    ', '\t', '):',  # indentation and colons
        ]
        
        text_lower = text.lower()
        code_score = sum(1 for indicator in code_indicators if indicator in text_lower)
        
        # If multiple code indicators are present, likely code
        return code_score >= 2
    
    @staticmethod
    def context(session_id: str = "current", max_tokens: int = 8000, 
               context_types: str = "all", format_style: str = "summary") -> str:
        """
        Get contextual information for session.
        
        Args:
            session_id: Session ID to get context for
            max_tokens: Maximum tokens for context
            context_types: Types of context to include
            format_style: How to format the context ('summary', 'detailed', 'timeline')
            
        Returns:
            Formatted contextual information
        """
        try:
            result_lines = [
                f"📋 Context Summary",
                f"Session: {session_id} | Max Tokens: {max_tokens}",
                f"Types: {context_types} | Format: {format_style}",
                "=" * 40,
                "",
                "ℹ️ Context retrieval integration pending:",
                "  • Will integrate with MemoryEngine for session context",
                "  • Will include conversation history",
                "  • Will include relevant code context", 
                "  • Will use semantic search for context discovery",
                "",
                f"Current session info:",
                f"  • Session ID: {session_id}",
                f"  • Context budget: {max_tokens} tokens",
                f"  • Format preference: {format_style}",
                f"  • Context types: {context_types}",
                ""
            ]
            
            if format_style == "timeline":
                result_lines.extend([
                    "🕒 Timeline format will include:",
                    "  • Chronological order of interactions",
                    "  • Code changes and decisions",
                    "  • Key insights and learnings",
                    ""
                ])
            elif format_style == "detailed":
                result_lines.extend([
                    "📝 Detailed format will include:",
                    "  • Full conversation context",
                    "  • Complete code snippets",
                    "  • Detailed analysis results",
                    ""
                ])
            else:  # summary
                result_lines.extend([
                    "📊 Summary format will include:",
                    "  • Key points and decisions",
                    "  • Important code elements",
                    "  • Relevant insights only",
                    ""
                ])
            
            return "\n".join(result_lines)
            
        except Exception as e:
            return f"Error getting context: {str(e)}"
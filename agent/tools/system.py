"""
System Tools - Canister Agent
Consolidated system-level operations: files, processes, time, calculations.
"""

import os
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class SystemTools:
    """System-level operations: files, processes, time, calculations."""
    
    @staticmethod
    def filesystem(operation: str, path: str = ".", content: str = "", 
                  encoding: str = "utf-8", **kwargs) -> str:
        """
        Unified file system operations.
        
        Args:
            operation: Operation to perform ('read', 'write', 'append', 'list', 'exists', 'mkdir', 'getcwd')
            path: File or directory path (default: current directory)
            content: Content for write/append operations
            encoding: File encoding (default: utf-8)
            **kwargs: Additional operation-specific parameters
            
        Returns:
            Operation result or error message
        """
        try:
            path_obj = Path(path).resolve()
            
            if operation == "read":
                if not path_obj.exists():
                    return f"Error: File '{path}' does not exist"
                if not path_obj.is_file():
                    return f"Error: '{path}' is not a file"
                
                try:
                    content = path_obj.read_text(encoding=encoding)
                    # Limit output for very large files
                    if len(content) > 10000:
                        return f"File content (first 10000 characters):\n{content[:10000]}\n\n... (file truncated, total size: {len(content)} characters)"
                    return f"File content:\n{content}"
                except UnicodeDecodeError:
                    return f"Error: Cannot decode file '{path}' with encoding '{encoding}'"
                except PermissionError:
                    return f"Error: Permission denied reading file '{path}'"
                    
            elif operation == "write":
                if not content:
                    return "Error: No content provided for write operation"
                try:
                    path_obj.parent.mkdir(parents=True, exist_ok=True)
                    path_obj.write_text(content, encoding=encoding)
                    return f"Successfully wrote {len(content)} characters to '{path}'"
                except PermissionError:
                    return f"Error: Permission denied writing to file '{path}'"
                    
            elif operation == "append":
                if not content:
                    return "Error: No content provided for append operation"
                try:
                    path_obj.parent.mkdir(parents=True, exist_ok=True)
                    with open(path_obj, 'a', encoding=encoding) as f:
                        f.write(content)
                    return f"Successfully appended {len(content)} characters to '{path}'"
                except PermissionError:
                    return f"Error: Permission denied appending to file '{path}'"
                    
            elif operation == "list":
                if not path_obj.exists():
                    return f"Error: Path '{path}' does not exist"
                if not path_obj.is_dir():
                    return f"Error: Path '{path}' is not a directory"
                    
                try:
                    items = []
                    for item in sorted(path_obj.iterdir()):
                        item_type = "DIR" if item.is_dir() else "FILE"
                        size = ""
                        if item.is_file():
                            try:
                                size = f" ({item.stat().st_size} bytes)"
                            except (OSError, PermissionError):
                                size = " (size unknown)"
                        items.append(f"[{item_type}] {item.name}{size}")
                    
                    if not items:
                        return f"Directory '{path}' is empty"
                    return f"Contents of '{path}':\n" + "\n".join(items)
                except PermissionError:
                    return f"Error: Permission denied accessing '{path}'"
                    
            elif operation == "exists":
                return f"Path '{path}' {'exists' if path_obj.exists() else 'does not exist'}"
                
            elif operation == "mkdir":
                try:
                    path_obj.mkdir(parents=True, exist_ok=True)
                    return f"Successfully created directory '{path}'"
                except PermissionError:
                    return f"Error: Permission denied creating directory '{path}'"
                    
            elif operation == "getcwd":
                return f"Current working directory: {os.getcwd()}"
                
            else:
                return f"Error: Invalid operation '{operation}'. Available: read, write, append, list, exists, mkdir, getcwd"
                
        except Exception as e:
            return f"Error in filesystem operation: {str(e)}"
    
    @staticmethod
    def process(command: str, timeout: int = 30, cwd: str = "", 
               sandbox: bool = False, language: str = "python") -> str:
        """
        Execute system commands safely with optional sandboxing.
        
        Args:
            command: Command to execute or code to run in sandbox
            timeout: Maximum execution time in seconds (default: 30)
            cwd: Working directory for command execution
            sandbox: Whether to run in Docker sandbox
            language: Language for sandbox execution (default: python)
            
        Returns:
            Command output, error messages, and exit code
        """
        if sandbox:
            return SystemTools._run_in_sandbox(command, language, timeout)
        
        # Security: Block potentially dangerous commands
        dangerous_commands = [
            'rm -rf', 'del /f', 'format', 'fdisk', 'mkfs', 'dd if=', 'sudo rm',
            'shutdown', 'reboot', 'halt', 'poweroff', 'init 0', 'init 6',
            '> /dev/', 'chmod 777', 'chown root', 'passwd', 'su -', 'sudo su'
        ]
        
        command_lower = command.lower().strip()
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                return f"Error: Command blocked for security reasons. Dangerous pattern detected: '{dangerous}'"
        
        # Block access to sensitive system files
        if any(pattern in command_lower for pattern in ['/etc/passwd', '/etc/shadow', 'registry', 'system32']):
            return "Error: Command blocked for security reasons. Access to sensitive system files not allowed."
        
        try:
            # Set working directory
            working_dir = None
            if cwd:
                cwd_path = Path(cwd)
                if not cwd_path.exists():
                    return f"Error: Working directory '{cwd}' does not exist"
                if not cwd_path.is_dir():
                    return f"Error: '{cwd}' is not a directory"
                working_dir = cwd
            
            # Execute the command
            process = subprocess.Popen(
                command, shell=True, cwd=working_dir,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
                
                result_parts = []
                if stdout.strip():
                    result_parts.append(f"Stdout: {stdout.strip()}")
                if stderr.strip():
                    result_parts.append(f"Stderr: {stderr.strip()}")
                result_parts.append(f"Exit Code: {exit_code}")
                
                return "Command executed.\n" + "\n".join(result_parts)
                
            except subprocess.TimeoutExpired:
                process.kill()
                return "Error: Command execution time exceeded timeout limit"
                
        except Exception as e:
            return f"Error executing command: {str(e)}"
    
    @staticmethod 
    def _run_in_sandbox(code: str, language: str, timeout: int) -> str:
        """Execute code in a Docker-based sandbox environment."""
        container_name = f"sandbox_{uuid.uuid4()}"
        temp_dir = Path("sandbox_tmp")
        temp_dir.mkdir(exist_ok=True)
        
        # Determine file extension and Docker image
        if language == "python":
            code_file = temp_dir / "temp_code.py"
            docker_image = "python:3.9-slim"
            run_command = ["python", "/sandbox/temp_code.py"]
        else:
            return f"Error: Unsupported sandbox language: {language}"
        
        try:
            # Write code to temporary file
            code_file.write_text(code)
            
            # Docker command
            docker_command = [
                "docker", "run", "--rm", "--name", container_name,
                "-v", f"{temp_dir.absolute()}:/sandbox",
                docker_image, *run_command
            ]
            
            # Execute in Docker
            result = subprocess.run(
                docker_command, capture_output=True, text=True, timeout=timeout
            )
            
            if result.returncode != 0:
                return f"Sandbox execution failed:\n{result.stderr.strip()}"
            
            return f"Sandbox execution successful:\n{result.stdout.strip()}"
            
        except subprocess.TimeoutExpired:
            return "Error: Sandbox execution timed out"
        except FileNotFoundError:
            return "Error: Docker not found. Install Docker to use sandbox execution."
        except Exception as e:
            return f"Error in sandbox execution: {str(e)}"
        finally:
            # Cleanup
            try:
                if code_file.exists():
                    code_file.unlink()
                if temp_dir.exists() and not any(temp_dir.iterdir()):
                    temp_dir.rmdir()
            except Exception:
                pass  # Best effort cleanup
    
    @staticmethod
    def calculate(expression: str) -> str:
        """
        Safe mathematical calculations.
        
        Args:
            expression: Mathematical expression or operation string
            
        Returns:
            Calculation result or error message
        """
        try:
            # Check if it's a simple operation format: "operation a b"
            parts = expression.strip().split()
            if len(parts) == 3:
                operation, a_str, b_str = parts
                try:
                    a, b = float(a_str), float(b_str)
                    
                    operations = {
                        "add": lambda x, y: x + y,
                        "subtract": lambda x, y: x - y,
                        "multiply": lambda x, y: x * y,
                        "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
                    }
                    
                    if operation.lower() in operations:
                        result = operations[operation.lower()](a, b)
                        return str(result)
                except ValueError:
                    pass  # Fall through to expression evaluation
            
            # Safe evaluation of mathematical expressions
            # Only allow safe mathematical operations
            allowed_chars = set('0123456789+-*/().,% ')
            if not all(c in allowed_chars for c in expression):
                return "Error: Expression contains invalid characters. Only numbers and basic operators (+, -, *, /, %, parentheses) are allowed."
            
            # Replace some common mathematical functions
            safe_expression = expression.replace('^', '**')  # Power operator
            
            try:
                result = eval(safe_expression, {"__builtins__": {}}, {})
                return str(result)
            except ZeroDivisionError:
                return "Error: Division by zero"
            except Exception as e:
                return f"Error: Invalid mathematical expression - {str(e)}"
                
        except Exception as e:
            return f"Error in calculation: {str(e)}"
    
    @staticmethod
    def analyze_text(text: str) -> str:
        """
        Text analysis and statistics.
        
        Args:
            text: Text to analyze
            
        Returns:
            Formatted text analysis results
        """
        try:
            if not text.strip():
                return "Error: No text provided for analysis"
            
            # Basic text statistics
            characters = len(text)
            characters_no_spaces = len(text.replace(' ', ''))
            words = text.split()
            word_count = len(words)
            
            # Sentence count (rough estimation)
            sentence_endings = ['.', '!', '?']
            sentences = [s.strip() for s in text.split('.') + text.split('!') + text.split('?')]
            sentence_count = len([s for s in sentences if s.strip()])
            
            # Average word length
            avg_word_length = round(sum(len(word.strip('.,!?;:')) for word in words) / word_count, 2) if words else 0
            
            # Additional metrics
            paragraphs = len([p for p in text.split('\n\n') if p.strip()])
            lines = len(text.split('\n'))
            
            # Most common words (simple analysis)
            word_freq = {}
            for word in words:
                clean_word = word.lower().strip('.,!?;:"()[]{}')
                if len(clean_word) > 2:  # Skip very short words
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
            
            most_common = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
            
            analysis = f"""Text Analysis Results:
📊 Basic Statistics:
  • Characters: {characters:,} (excluding spaces: {characters_no_spaces:,})
  • Words: {word_count:,}
  • Sentences: {sentence_count:,}
  • Paragraphs: {paragraphs:,}
  • Lines: {lines:,}
  • Average word length: {avg_word_length} characters

📈 Readability Metrics:
  • Words per sentence: {round(word_count / sentence_count, 1) if sentence_count > 0 else 0}
  • Characters per word: {round(characters / word_count, 1) if word_count > 0 else 0}"""

            if most_common:
                analysis += f"\n\n🔤 Most Common Words:\n"
                for word, count in most_common:
                    analysis += f"  • {word}: {count} times\n"
            
            return analysis.strip()
            
        except Exception as e:
            return f"Error in text analysis: {str(e)}"
    
    @staticmethod
    def get_time(format_string: str = "%Y-%m-%d %H:%M:%S", timezone: str = "") -> str:
        """
        Get current time in specified format.
        
        Args:
            format_string: Time format string (default: "%Y-%m-%d %H:%M:%S")
            timezone: Timezone (not implemented yet, uses local time)
            
        Returns:
            Formatted current time
        """
        try:
            current_time = datetime.now()
            
            # Common format shortcuts
            format_shortcuts = {
                "iso": "%Y-%m-%dT%H:%M:%S",
                "date": "%Y-%m-%d", 
                "time": "%H:%M:%S",
                "datetime": "%Y-%m-%d %H:%M:%S",
                "us": "%m/%d/%Y %I:%M:%S %p",
                "eu": "%d/%m/%Y %H:%M:%S"
            }
            
            if format_string.lower() in format_shortcuts:
                format_string = format_shortcuts[format_string.lower()]
            
            formatted_time = current_time.strftime(format_string)
            
            if timezone:
                return f"{formatted_time} (Note: Timezone conversion not yet implemented, showing local time)"
            
            return formatted_time
            
        except ValueError as e:
            return f"Error: Invalid time format string - {str(e)}"
        except Exception as e:
            return f"Error getting time: {str(e)}"
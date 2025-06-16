from datetime import datetime
import os
import subprocess
from pathlib import Path
from google.adk.tools import FunctionTool

def get_current_time_tool() -> FunctionTool:
    """Create a tool that gets the current date and time."""

    def get_current_time() -> str:
        """Get the current date and time."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return FunctionTool(get_current_time)


def calculator_tool() -> FunctionTool:
    """Create a calculator tool for basic mathematical operations."""

    def calculator(operation: str, a: float, b: float) -> str:
        """Perform basic mathematical operations (add, subtract, multiply, divide)."""
        operations = {
            "add": lambda x, y: x + y,
            "subtract": lambda x, y: x - y,
            "multiply": lambda x, y: x * y,
            "divide": lambda x, y: x / y if y != 0 else "Error: Division by zero"
        }

        if operation.lower() in operations:
            result = operations[operation.lower()](a, b)
            return str(result)
        else:
            return "Error: Invalid operation. Use: add, subtract, multiply, or divide"

    return FunctionTool(calculator)


def text_analyzer_tool() -> FunctionTool:
    """Create a tool that analyzes text and returns basic statistics."""

    def text_analyzer(text: str) -> str:
        """Analyze text and return statistics (character count, word count, sentence count, average word length)."""
        words = text.split()
        sentences = text.split('.')

        stats = {
            "character_count": len(text),
            "word_count": len(words),
            "sentence_count": len([s for s in sentences if s.strip()]),
            "average_word_length": round(sum(len(word) for word in words) / len(words), 2) if words else 0,
        }

        return f"Text Analysis:\n- Characters: {stats['character_count']}\n- Words: {stats['word_count']}\n- Sentences: {stats['sentence_count']}\n- Average word length: {stats['average_word_length']}"

    return FunctionTool(text_analyzer)


def directory_operations_tool() -> FunctionTool:
    """Create a tool for directory operations (get current directory and list files)."""

    def directory_operations(operation: str, path: str = ".") -> str:
        """
        Perform directory operations.

        Args:
            operation: The operation to perform ('getcwd', 'listdir')
            path: The directory path (default: current directory)

        Returns:
            String containing the operation result or error message
        """
        try:
            if operation.lower() == "getcwd":
                current_dir = os.getcwd()
                return f"Current working directory: {current_dir}"

            elif operation.lower() == "listdir":
                # Convert to Path object for better handling
                dir_path = Path(path).resolve()

                if not dir_path.exists():
                    return f"Error: Path '{path}' does not exist"

                if not dir_path.is_dir():
                    return f"Error: Path '{path}' is not a directory"

                try:
                    items = []
                    for item in sorted(dir_path.iterdir()):
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

                    result = f"Contents of '{path}':\n" + "\n".join(items)
                    return result

                except PermissionError:
                    return f"Error: Permission denied accessing '{path}'"
                except Exception as e:
                    return f"Error listing directory '{path}': {str(e)}"

            else:
                return "Error: Invalid operation. Use 'getcwd' to get current directory or 'listdir' to list directory contents"

        except Exception as e:
            return f"Error in directory operation: {str(e)}"

    return FunctionTool(directory_operations)


def file_management_tool() -> FunctionTool:
    """Create a tool for file management operations (read, write, update files)."""

    def file_management(operation: str, file_path: str, content: str = "", encoding: str = "utf-8") -> str:
        """
        Perform file management operations.

        Args:
            operation: The operation to perform ('read', 'write', 'append')
            file_path: The path to the file
            content: Content to write/append (for write/append operations)
            encoding: File encoding (default: utf-8)

        Returns:
            String containing the operation result or error message
        """
        try:
            file_path_obj = Path(file_path)

            if operation.lower() == "read":
                if not file_path_obj.exists():
                    return f"Error: File '{file_path}' does not exist"

                if not file_path_obj.is_file():
                    return f"Error: '{file_path}' is not a file"

                try:
                    with open(file_path_obj, 'r', encoding=encoding) as f:
                        file_content = f.read()

                    # Limit output size for very large files
                    if len(file_content) > 10000:
                        return f"File content (first 10000 characters):\n{file_content[:10000]}\n\n... (file truncated, total size: {len(file_content)} characters)"
                    else:
                        return f"File content:\n{file_content}"

                except UnicodeDecodeError:
                    return f"Error: Cannot decode file '{file_path}' with encoding '{encoding}'. File may be binary or use different encoding."
                except PermissionError:
                    return f"Error: Permission denied reading file '{file_path}'"
                except Exception as e:
                    return f"Error reading file '{file_path}': {str(e)}"

            elif operation.lower() == "write":
                if not content:
                    return "Error: No content provided for write operation"

                try:
                    # Create parent directories if they don't exist
                    file_path_obj.parent.mkdir(parents=True, exist_ok=True)

                    with open(file_path_obj, 'w', encoding=encoding) as f:
                        f.write(content)

                    return f"Successfully wrote {len(content)} characters to '{file_path}'"

                except PermissionError:
                    return f"Error: Permission denied writing to file '{file_path}'"
                except Exception as e:
                    return f"Error writing to file '{file_path}': {str(e)}"

            elif operation.lower() == "append":
                if not content:
                    return "Error: No content provided for append operation"

                try:
                    # Create parent directories if they don't exist
                    file_path_obj.parent.mkdir(parents=True, exist_ok=True)

                    with open(file_path_obj, 'a', encoding=encoding) as f:
                        f.write(content)

                    return f"Successfully appended {len(content)} characters to '{file_path}'"

                except PermissionError:
                    return f"Error: Permission denied appending to file '{file_path}'"
                except Exception as e:
                    return f"Error appending to file '{file_path}': {str(e)}"

            else:
                return "Error: Invalid operation. Use 'read' to read file, 'write' to write new content, or 'append' to add content"

        except Exception as e:
            return f"Error in file management operation: {str(e)}"

    return FunctionTool(file_management)


def terminal_command_tool() -> FunctionTool:
    """Create a tool for safe terminal command execution."""

    def terminal_command(command: str, timeout: int = 30, working_directory: str = "") -> str:
        """
        Execute terminal/shell commands safely.

        Args:
            command: The command to execute
            timeout: Maximum execution time in seconds (default: 30)
            working_directory: Working directory for command execution (default: current directory)

        Returns:
            String containing command output, error messages, and exit code
        """
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

        # Additional security: Block commands that try to access sensitive system files
        if any(pattern in command_lower for pattern in ['/etc/passwd', '/etc/shadow', 'registry', 'system32']):
            return "Error: Command blocked for security reasons. Access to sensitive system files not allowed."

        try:
            # Set working directory
            cwd = None
            if working_directory:
                cwd_path = Path(working_directory)
                if not cwd_path.exists():
                    return f"Error: Working directory '{working_directory}' does not exist"
                if not cwd_path.is_dir():
                    return f"Error: '{working_directory}' is not a directory"
                cwd = working_directory

            # Execute the command
            process = subprocess.Popen(
                command, shell=True, cwd=cwd,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                universal_newlines=True
            )
            try:
                stdout, stderr = process.communicate(timeout=timeout)
                exit_code = process.returncode
                result = (f"Command executed.\nStdout: {stdout}\nStderr: {stderr}" +
                          f"\nExit Code: {exit_code}")
                return result

            except subprocess.TimeoutExpired:
                process.kill()
                return "Error: Command execution time exceeded timeout limit"

        except Exception as e:
            return f"Error executing terminal command: {str(e)}"

    return FunctionTool(terminal_command)



def docker_sandbox_tool() -> FunctionTool:
    """Create a tool that runs code inside a Docker container for sandbox execution."""

    def run_code_in_sandbox(code: str, language: str = "python") -> dict:
        """Execute provided code in a Docker-based sandbox environment."""
        import uuid
        import subprocess
        import os

        # Generate a unique container name to avoid collisions
        container_name = f"sandbox_{uuid.uuid4()}"
        temp_dir = "sandbox_tmp"
        os.makedirs(temp_dir, exist_ok=True)
        code_file = f"{temp_dir}/temp_code.py"
        
        # Write the code to a temporary file
        with open(code_file, "w") as file:
            file.write(code)

        try:
            # Define the base Docker command according to chosen language
            if language == "python":
                docker_image = "python:3.9-slim"
                run_command = ["python", "/sandbox/temp_code.py"]
            else:
                return {"error": f"Unsupported language: {language}"}
            
            docker_command = [
                "docker", "run", "--rm", "--name", container_name,
                "-v", f"{os.getcwd()}/{temp_dir}:/sandbox",
                docker_image, *run_command
            ]

            # Execute the Docker command and handle the output
            result = subprocess.run(docker_command, capture_output=True, text=True, timeout=30)
            
            # Process result
            if result.returncode != 0:
                return {"error": result.stderr.strip()}
            
            return {"output": result.stdout.strip()}
        except subprocess.TimeoutExpired:
            return {"error": "Execution timed out"}
        finally:
            # Clean up the temporary files
            os.remove(code_file)
            os.rmdir(temp_dir)

    return FunctionTool(run_code_in_sandbox)

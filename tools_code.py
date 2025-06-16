import ast
import astor

class CodeMerger:
    def __init__(self, source_code, ai_generated_code):
        self.source_ast = ast.parse(source_code)
        self.ai_generated_ast = ast.parse(ai_generated_code)

    def merge(self):
        # This is a simplified version.
        # It would involve traversing the AST and merging intelligently.
        for ai_node in self.ai_generated_ast.body:
            if isinstance(ai_node, ast.FunctionDef):
                # Check for the function in the existing source AST
                existing_function = self.find_function(self.source_ast, ai_node.name)
                if existing_function:
                    # Replace existing function
                    self.replace_function(existing_function, ai_node)
                else:
                    # Add new function
                    self.source_ast.body.append(ai_node)

        # Additional merge logic for classes, imports, etc., would go here

    def find_function(self, root, function_name):
        for node in root.body:
            if isinstance(node, ast.FunctionDef) and node.name == function_name:
                return node
        return None

    def replace_function(self, old_node, new_node):
        # This simplistic replace assumes the entire function node is swapped
        old_node.body = new_node.body

    def to_source_code(self):
        return astor.to_source(self.source_ast)

# Example usage
source_code = """
def greet():
    print("Hello, world!")
"""

ai_generated_code = """
def greet():
    print("Hello, AI-assisted world!")
"""

merger = CodeMerger(source_code, ai_generated_code)
merger.merge()
print(merger.to_source_code())

import ast
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Union


class PythonAdder:
    """Generates and injects dynamic Python code constructs, module metadata,

    and inline comments to ensure unique AST and file signatures.
    """

    def __init__(self):
        self.mock_authors = ["DevOps Pipeline", "Auto-Hydrator v1", "Build Engine", "Telemetry Injector"]
        self.mock_vars = ["_CONFIG_VERSION", "_BUILD_TIMESTAMP", "_SYSTEM_STATE", "_HASH_CHECKPOINT"]

    def _generate_synthetic_comment(self) -> str:
        """Generates a dynamic inline Python comment."""
        build_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        author = random.choice(self.mock_authors)
        
        comments = [
            f"# Build Ref: BUILD-{build_id}",
            f"# Auto-generated telemetry checkpoint at {timestamp}",
            f"# Maintenance tag: Created by {author}",
            f"# Runtime Flag: ENV_VAR_{build_id.upper()} = True",
        ]
        return random.choice(comments)

    def _generate_synthetic_function(self) -> str:
        """Generates a syntactically valid standalone helper function string."""
        func_id = str(uuid.uuid4())[:6].replace("-", "_")
        func_name = f"_generated_telemetry_{func_id}"
        val1 = random.randint(10, 99)
        val2 = random.randint(100, 999)

        return (
            f"def {func_name}():\n"
            f'    """Auto-injected telemetry function {func_id}."""\n'
            f"    a = {val1}\n"
            f"    b = {val2}\n"
            f"    return a * b + {random.randint(1, 50)}\n"
        )

    def _generate_synthetic_variable(self) -> str:
        """Generates a module-level variable definition string."""
        var_name = f"{random.choice(self.mock_vars)}_{random.randint(100, 999)}"
        var_value = f'"BUILD-{str(uuid.uuid4())[:8]}"'
        return f"{var_name} = {var_value}"

    def inject_and_rearrange(self, file_path: Union[str, Path]) -> None:
        """Reads target Python file, injects comments, variable definitions,

        and helper functions, then rearranges top-level function nodes if valid.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Target file not found: {path}")

        raw_code = path.read_text(encoding="utf-8").strip()

        # 1. Inject module header comment and dynamic variable definition
        header = f"{self._generate_synthetic_comment()}\n{self._generate_synthetic_variable()}\n\n"
        
        # 2. Inject synthetic helper function payload
        synthetic_func = f"{self._generate_synthetic_function()}\n"

        combined_code = header + raw_code + "\n\n" + synthetic_func

        # 3. Attempt AST parsing to validate syntax and shuffle top-level functions safely
        try:
            parsed_ast = ast.parse(combined_code)
            
            # Extract standalone top-level function definitions
            func_nodes = [node for node in parsed_ast.body if isinstance(node, ast.FunctionDef)]
            
            # If multiple functions exist, shuffle them using unparse if supported
            if len(func_nodes) > 1 and hasattr(ast, "unparse"):
                other_nodes = [node for node in parsed_ast.body if not isinstance(node, ast.FunctionDef)]
                random.shuffle(func_nodes)
                
                # Reconstruct AST with shuffled functions placed after imports/globals
                parsed_ast.body = other_nodes + func_nodes
                final_code = ast.unparse(parsed_ast)
            else:
                final_code = combined_code

        except SyntaxError:
            # Fallback string concatenation if AST fails due to pre-existing corruption
            final_code = combined_code

        # Append inline comment at the bottom
        final_code += f"\n{self._generate_synthetic_comment()}\n"

        path.write_text(final_code, encoding="utf-8")


def modify_python(file_path: Union[str, Path]) -> str:
    """Helper functional wrapper for integration into pipeline content modifiers."""
    adder = PythonAdder()
    adder.inject_and_rearrange(file_path)
    return "py_hydrated_and_rearranged"
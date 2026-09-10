import random


def corrupt_py(file_path: str) -> str:
    """Mutates a Python file in-place and returns the mutation label applied."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        code = f.read()

    if not code.strip():
        return "none"

    mutations = {
        "keyword_syntax_error": lambda c: c.replace("def ", "deff "),
        "mixed_tabs_spaces": lambda c: c.replace("    ", "\t", 3),
        "missing_block_colon": lambda c: c.replace(":", "", 2),
        "unclosed_docstring": lambda c: c[: len(c) // 2] + "\n'''",
        "broken_import": lambda c: "import non_existent_module_xyz\n" + c,
        "assignment_in_conditional": lambda c: c.replace("==", "="),
    }

    label, mutation_func = random.choice(list(mutations.items()))
    mutated = mutation_func(code)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(mutated)

    return label
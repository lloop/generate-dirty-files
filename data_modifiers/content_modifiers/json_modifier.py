import random


def corrupt_json(file_path: str) -> str:
    """Mutates a JSON file in-place and returns the mutation label applied."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()

    if not content.strip():
        return "none"

    mutations = {
        "trailing_comma": lambda j: j.rstrip().rstrip("}") + ",",
        "invalid_syntax": lambda j: j.replace(":", "=>"),
        "stripped_braces": lambda j: j.strip("{}"),
        "unclosed_string": lambda j: j.replace('"', "", 1),
    }

    label, mutation_func = random.choice(list(mutations.items()))
    mutated = mutation_func(content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(mutated)

    return label
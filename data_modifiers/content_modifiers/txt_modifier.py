import random


def corrupt_txt(file_path: str) -> str:
    """Mutates a plain text file in-place and returns the mutation label applied."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    if not text.strip():
        return "none"

    mutations = {
        "all_caps": lambda t: t.upper(),
        "extra_spacing": lambda t: t.replace(" ", "  "),
        "garbage_eof": lambda t: t + "\n[CORRUPTED_EOF]",
        "truncated_text": lambda t: t[: len(t) // 2],
    }

    label, mutation_func = random.choice(list(mutations.items()))
    mutated = mutation_func(text)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(mutated)

    return label
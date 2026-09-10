import random


def corrupt_html(file_path: str) -> str:
    """Mutates an HTML file in-place and returns the mutation label applied."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        html = f.read()

    if not html.strip():
        return "none"

    mutations = {
        "unclosed_closing_tag": lambda h: h.replace("</html>", ""),
        "truncated_body": lambda h: h.replace("<body>", "<body><!-- truncated -->"),
        "broken_brackets": lambda h: h.replace("<", "</"),
        "missing_doctype": lambda h: h.replace("<!DOCTYPE html>", ""),
    }

    label, mutation_func = random.choice(list(mutations.items()))
    mutated = mutation_func(html)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(mutated)

    return label
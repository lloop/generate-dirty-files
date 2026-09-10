import random


def corrupt_xml(file_path: str) -> str:
    """Mutates an XML file in-place and returns the mutation label applied."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        xml = f.read()

    if not xml.strip():
        return "none"

    mutations = {
        "broken_header": lambda x: x.replace("<?xml", "<?xml_broken"),
        "premature_eof": lambda x: x[: len(x) // 2],
        "injected_unclosed_tag": lambda x: x.replace(">", "><broken_tag>", 1),
    }

    label, mutation_func = random.choice(list(mutations.items()))
    mutated = mutation_func(xml)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(mutated)

    return label
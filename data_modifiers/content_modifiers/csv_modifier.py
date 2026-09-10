import random


def corrupt_csv(file_path: str) -> str:
    """Mutates a CSV file in-place by introducing common CSV errors."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    if not lines:
        return "none"


    mutations = {
        "dropped_header": lambda l: l[1:] if len(l) > 1 else l,
        "swapped_delimiter": lambda l: [line.replace(",", ";") for line in l],
        "malformed_row": lambda l: (
            l[:-1] + [l[-1].rstrip("\n") + "\n", "unmatched,row,data,extra\n"]
            if l
            else ["unmatched,row,data,extra\n"]
        ),
    }

    # Pick a random label and run its associated function
    label, mutation_func = random.choice(list(mutations.items()))
    mutated_lines = mutation_func(lines)

    with open(file_path, "w", encoding="utf-8") as f:
        f.writelines(mutated_lines)

    return label
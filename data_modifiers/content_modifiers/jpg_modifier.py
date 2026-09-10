import random


def corrupt_jpg(file_path: str) -> str:
    """Mutates a JPEG binary file in-place and returns the mutation label applied."""
    with open(file_path, "rb") as f:
        data = bytearray(f.read())

    if len(data) < 10:
        return "none"

    def _flip_bytes(b: bytearray) -> bytearray:
        for _ in range(min(5, len(b) - 4)):
            idx = random.randint(4, len(b) - 1)
            b[idx] = random.randint(0, 255)
        return b

    mutations = {
        "flipped_bytes": _flip_bytes,
        "truncated_binary": lambda b: b[: len(b) // 2],
    }

    label, mutation_func = random.choice(list(mutations.items()))
    mutated_data = mutation_func(data)

    with open(file_path, "wb") as f:
        f.write(mutated_data)

    return label
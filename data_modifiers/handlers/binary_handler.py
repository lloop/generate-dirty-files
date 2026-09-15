import random
from .base import BaseFormatHandler


class BinaryHandler(BaseFormatHandler):

    def add_unique_entropy(self, content: str | bytes, token: str) -> bytes:
        raw_bytes = content.encode("utf-8") if isinstance(content, str) else content
        entropy_bytes = token.encode("utf-8")
        return raw_bytes + b"\x00_build_uid:" + entropy_bytes

    def corrupt_structure(
        self, content: str | bytes, mutation_type: str = "auto"
    ) -> tuple[bytes, str]:
        raw_bytes = content.encode("utf-8") if isinstance(content, str) else content
        mutations = {
            "flipped_bytes": lambda d: self._flip_random_byte(d),
            "truncated_binary": lambda d: d[: max(10, len(d) // 2)],
            "zero_byte": lambda d: b"",
        }

        if mutation_type == "auto":
            label = random.choice(list(mutations.keys()))
            staged_data = mutations[label](raw_bytes)
        else:
            label = "none"
            staged_data = raw_bytes

        return staged_data, label

    def _flip_random_byte(self, data: bytes) -> bytes:
        if len(data) < 10:
            return data
        byte_arr = bytearray(data)
        idx = random.randint(len(byte_arr) // 2, len(byte_arr) - 1)
        byte_arr[idx] ^= 0xFF
        return bytes(byte_arr)
import random
from .base import BaseFormatHandler


class FallbackHandler(BaseFormatHandler):

    def add_unique_entropy(self, content: str | bytes, token: str) -> str:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        return f"# build_id: {token}\n" + text

    def corrupt_structure(
        self, content: str | bytes, mutation_type: str = "auto"
    ) -> tuple[str, str]:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        mutations = ["truncated_text", "zero_byte"]

        label = random.choice(mutations) if mutation_type == "auto" else "none"

        if label == "zero_byte":
            return "", label
        elif label == "truncated_text":
            cut_point = max(10, len(text) // 2)
            return text[:cut_point], label

        return text, label
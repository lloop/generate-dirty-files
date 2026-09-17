import json
import random
from .base import BaseFormatHandler


class JSONHandler(BaseFormatHandler):

    def add_unique_entropy(self, content: str | bytes, token: str) -> str:
        text = content.decode("utf-8", errors="surrogateescape") if isinstance(content, bytes) else content
        return text + f"\n// build_id: {token}\n"

    def corrupt_structure(
        self, content: str | bytes, mutation_type: str = "auto"
    ) -> tuple[str, str]:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        mutations = ["unclosed_string", "missing_comma", "zero_byte"]

        label = random.choice(mutations) if mutation_type == "auto" else "none"

        if label == "zero_byte":
            return "", label
        elif label == "unclosed_string":
            return text[:-5], label
        elif label == "missing_comma":
            return text.replace(",", "", 1), label

        return text, label
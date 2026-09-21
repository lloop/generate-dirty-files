import random

from .base import BaseFormatHandler


class HTMLHandler(BaseFormatHandler):

    def add_unique_entropy(
        self,
        content: str | bytes,
        token: str,
        corruption_label: str = "none",
    ) -> str:
        text = (
            content.decode("utf-8", errors="surrogateescape")
            if isinstance(content, bytes)
            else content
        )

        return text + f"\n<!-- build_id: {token} -->\n"

    def corrupt_structure(
        self, content: str | bytes, mutation_type: str = "auto"
    ) -> tuple[str, str]:
        text = (
            content.decode("utf-8", errors="surrogateescape")
            if isinstance(content, bytes)
            else content
        )

        mutations = ["truncated_text", "zero_byte"]

        label = random.choice(mutations) if mutation_type == "auto" else mutation_type

        token_start = text.find("<!-- build_id:")
        token_end = -1

        if token_start != -1:
            token_end = text.find("-->", token_start)

            if token_end != -1:
                token_end += 3

        if label == "zero_byte":
            return "", label

        elif label == "truncated_text":
            cut_point = max(10, len(text) // 2)

            if token_start != -1 and cut_point >= token_start:
                cut_point = max(10, token_start - 1)

            return text[:cut_point], label

        return text, label
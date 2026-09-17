import random
from .base import BaseFormatHandler


class XMLHandler(BaseFormatHandler):

    def add_unique_entropy(self, content: str | bytes, token: str) -> str:
        text = content.decode("utf-8", errors="surrogateescape") if isinstance(content, bytes) else content
        return text + f"\n<!-- meta_uid: {token} -->\n"

    def corrupt_structure(
        self, content: str | bytes, mutation_type: str = "auto"
    ) -> tuple[str, str]:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        mutations = ["premature_eof", "unclosed_tag", "zero_byte"]

        label = random.choice(mutations) if mutation_type == "auto" else "none"

        if label == "zero_byte":
            return "", label
        elif label == "premature_eof":
            cut_point = max(10, len(text) // 2)
            return text[:cut_point], label
        elif label == "unclosed_tag":
            return text.replace("</", "<"), label

        return text, label
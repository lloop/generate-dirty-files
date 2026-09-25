import random
from .base import BaseFormatHandler


class FallbackHandler(BaseFormatHandler):

    def add_unique_entropy(
        self,
        content: str | bytes,
        token: str,
    ) -> str:

        text = (
            content.decode("utf-8", errors="surrogateescape")
            if isinstance(content, bytes)
            else content
        )

        return (
            f"# DEBUG_START:{token}\n"
            f"# DEBUG_END\n"
            + text
        )
        
    def corrupt_structure(
        self, content: str | bytes, corruption_type: str = "auto"
    ) -> tuple[str, str]:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        corruptions = ["zero_byte"]

        label = random.choice(corruptions) if corruption_type == "auto" else "none"

        if label == "zero_byte":
            return "", label

        return text, label
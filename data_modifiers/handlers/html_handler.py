import random

from .base import BaseFormatHandler


class HTMLHandler(BaseFormatHandler):

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

        debug_block = (
            f"<!-- DEBUG_START:{token} -->\n"
            f"<!-- DEBUG_END -->\n"
        )

        return debug_block + text

    def corrupt_structure(
        self, content: str | bytes, corruption_type: str = "auto"
    ) -> tuple[str, str]:
        text = (
            content.decode("utf-8", errors="surrogateescape")
            if isinstance(content, bytes)
            else content
        )

        corruptions = ["zero_byte"]

        label = random.choice(corruptions) if corruption_type == "auto" else corruption_type

        debug_start = text.find("<!-- DEBUG_START:")
        debug_end = text.find("<!-- DEBUG_END -->", debug_start)

        if debug_start != -1 and debug_end != -1:
            debug_end += len("<!-- DEBUG_END -->")
        else:
            debug_start = -1
            debug_end = -1

        if label == "zero_byte":
            return "", label

        return text, label
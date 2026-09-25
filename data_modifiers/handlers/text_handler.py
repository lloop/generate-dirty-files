from .base import BaseFormatHandler


class TextHandler(BaseFormatHandler):

    def add_unique_entropy(
        self,
        content: str | bytes,
        token: str,
    ) -> str | bytes:

        text = (
            content.decode("utf-8", errors="surrogateescape")
            if isinstance(content, bytes)
            else content
        )

        return (
            f"DEBUG_START:{token}\n"
            f"DEBUG_END\n"
            + text
        )

    def corrupt_structure(
        self,
        content: str | bytes,
        corruption_type: str = "auto",
    ) -> tuple[str | bytes, str]:
        return content, "none"
from .base import BaseFormatHandler
import random


class PythonHandler(BaseFormatHandler):

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
            f"# DEBUG_START:{token}\n"
            f"# DEBUG_END\n"
            + text
        )

    def corrupt_structure(
        self,
        content: str | bytes,
        corruption_type: str = "auto",
    ) -> tuple[str | bytes, str]:

        text = (
            content.decode("utf-8", errors="surrogateescape")
            if isinstance(content, bytes)
            else content
        )

        corruptions = [
            "missing_colon",
            "unclosed_bracket",
            "zero_byte",
        ]

        label = (
            random.choice(corruptions)
            if corruption_type == "auto"
            else corruption_type
        )

        debug_start = text.find("# DEBUG_START:")
        debug_end = text.find("# DEBUG_END", debug_start)

        if debug_start != -1 and debug_end != -1:
            debug_end = text.find("\n", debug_end)
            if debug_end == -1:
                debug_end = len(text)
        else:
            debug_start = -1
            debug_end = -1

        if label == "zero_byte":
            return "", label

        # Only mutate content after the protected debug block.
        mutable_start = debug_end if debug_end != -1 else 0
        mutable_text = text[mutable_start:]

        if label == "missing_colon":
            lines = mutable_text.splitlines(keepends=True)

            for i, line in enumerate(lines):
                stripped = line.strip()

                if (
                    stripped.startswith(("if ", "elif ", "else", "for ", "while ",
                                         "def ", "class ", "try", "except",
                                         "finally", "with ", "match ", "case "))
                    and stripped.endswith(":")
                ):
                    lines[i] = line.replace(":", "", 1)
                    return (
                        text[:mutable_start] + "".join(lines),
                        label,
                    )

            return text, "none"

        elif label == "unclosed_bracket":
            pairs = {
                "(": ")",
                "[": "]",
                "{": "}",
            }

            for opening, closing in pairs.items():
                position = mutable_text.find(opening)

                if position != -1:
                    closing_position = mutable_text.find(
                        closing,
                        position + 1,
                    )

                    if closing_position != -1:
                        absolute_position = mutable_start + closing_position

                        return (
                            text[:absolute_position]
                            + text[absolute_position + 1:],
                            label,
                        )

            return text, "none"

        return text, label
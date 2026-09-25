import random
import xml.etree.ElementTree as ET
from .base import BaseFormatHandler


class XMLHandler(BaseFormatHandler):

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

        if text.lstrip().startswith("<?xml"):
            declaration_end = text.find("?>")

            if declaration_end != -1:
                insertion_point = declaration_end + 2
                return (
                    text[:insertion_point]
                    + "\n"
                    + debug_block
                    + text[insertion_point:]
                )

        return debug_block + text

    def corrupt_structure(
        self, content: str | bytes, corruption_type: str = "auto"
    ) -> tuple[str, str]:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        corruptions = ["premature_eof", "unclosed_tag", "zero_byte"]

        label = random.choice(corruptions) if corruption_type == "auto" else corruption_type

        # Locate the protected debug region.
        debug_start = text.find("<!-- DEBUG_START:")
        debug_end = text.find("<!-- DEBUG_END -->", debug_start)

        if debug_start != -1 and debug_end != -1:
            debug_end += len("<!-- DEBUG_END -->")
        else:
            debug_start = -1
            debug_end = -1

        if label == "zero_byte":
            return "", label

        elif label == "premature_eof":
            cut_point = max(10, len(text) // 2)

            # Do not truncate through the protected debug region.
            if debug_end != -1 and cut_point <= debug_end:
                if debug_end < len(text) - 1:
                    cut_point = random.randint(
                        debug_end + 1,
                        len(text) - 1,
                    )
                else:
                    return text, "none"

            return text[:cut_point], label

        elif label == "unclosed_tag":
            mutable_start = debug_end if debug_end != -1 else 0

            closing_tag = text.find("</", mutable_start)

            if closing_tag != -1:
                return (
                    text[:closing_tag]
                    + text[closing_tag:].replace("</", "<", 1),
                    label,
                )

            return text, "none"

        return text, label
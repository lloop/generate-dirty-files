import ast
import json
import random
import re
from .base import BaseFormatHandler


def sanitize_json_string(text: str) -> str:
    """Normalizes raw non-compliant JSON (single quotes, trailing commas)."""
    try:
        json.loads(text, strict=False)
        return text
    except json.JSONDecodeError:
        pass

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, (dict, list)):
            return json.dumps(parsed, indent=2)
    except (ValueError, SyntaxError):
        pass

    # Convert single-quoted keys/values to double quotes
    sanitized = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", r'"\1"', text)
    # Strip trailing commas inside dicts/lists
    sanitized = re.sub(r",\s*([}\]])", r"\1", sanitized)
    return sanitized


class JSONHandler(BaseFormatHandler):

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
        text = sanitize_json_string(text)

        try:
            data = json.loads(text, strict=False)

            if isinstance(data, dict):
                data["_build_id"] = token
            elif isinstance(data, list):
                data.append({"_build_id": token})

            return json.dumps(data, indent=2)

        except json.JSONDecodeError:
            return text
        
    def corrupt_structure(
        self, content: str | bytes, corruption_type: str = "auto"
    ) -> tuple[str, str]:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        corruptions = ["unclosed_string", "missing_comma", "zero_byte"]

        label = random.choice(corruptions) if corruption_type == "auto" else corruption_type

        token_start = text.find('"_build_id"')
        token_end = -1

        if token_start != -1:
            token_end = text.find("\n", token_start)

            if token_end == -1:
                token_end = len(text)

        if label == "zero_byte":
            return "", label

        elif label == "unclosed_string":
            if token_end != -1:
                # Preserve _build_id, remove the closing JSON structure.
                return text[:token_end], label

            cut_point = max(1, len(text) - 5)
            return text[:cut_point], label

        elif label == "missing_comma":
            # Remove a comma from the actual JSON content, never from
            # the protected _build_id field.
            mutable_end = token_start if token_start != -1 else len(text)
            before = text[:mutable_end]

            comma_position = before.rfind(",")

            if comma_position != -1:
                return (
                    text[:comma_position] + text[comma_position + 1:],
                    label,
                )

            return text, "none"

        return text, label
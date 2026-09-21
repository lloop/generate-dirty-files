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
        corruption_label: str = "none",
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
            last_brace = text.rfind("}")

            if last_brace != -1:
                entropy = f', "_build_id": "{token}"'
                return text[:last_brace] + entropy + text[last_brace:]

            return text

    def corrupt_structure(
        self, content: str | bytes, mutation_type: str = "auto"
    ) -> tuple[str, str]:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        mutations = ["unclosed_string", "missing_comma", "zero_byte"]

        label = random.choice(mutations) if mutation_type == "auto" else "none"

        token_start = text.find('"_build_id"')
        token_end = -1

        if token_start != -1:
            token_end = text.find("\n", token_start)

            if token_end == -1:
                token_end = len(text)

        if label == "zero_byte":
            return "", label
        elif label == "unclosed_string":
            cut_point = max(1, len(text) - 5)

            if token_start != -1 and token_start <= cut_point < token_end:
                cut_point = max(1, token_start - 1)

            return text[:cut_point], label
        elif label == "missing_comma":
            if token_start != -1:
                protected_start = token_start
                protected_end = token_end

                before = text[:protected_start]
                protected = text[protected_start:protected_end]
                after = text[protected_end:]

                after = after.replace(",", "", 1)

                return before + protected + after, label

            return text.replace(",", "", 1), label

        return text, label
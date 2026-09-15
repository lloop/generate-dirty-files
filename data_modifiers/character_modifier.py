import random

class CharacterModifier:
    def corrupt_character_encoding(self, content: str) -> tuple[str, str]:
        """
        Introduces character encoding artifacts or corrupts string encoding.
        """
        if not isinstance(content, str) or not content:
            return content, "none"

        corruptions = [
            self._corrupt_mojibake,
            self._corrupt_null_bytes,
            self._corrupt_replacement_chars,
        ]
        chosen_func = random.choice(corruptions)
        return chosen_func(content)

    def _corrupt_mojibake(self, content: str) -> tuple[str, str]:
        try:
            # Simulate double-encoding artifact (UTF-8 bytes read as Windows-1252)
            corrupted = content.encode("utf-8").decode("cp1252", errors="replace")
            return corrupted, "mojibake"
        except Exception:
            return content, "none"

    def _corrupt_null_bytes(self, content: str) -> tuple[str, str]:
        pos = random.randint(0, len(content) - 1)
        corrupted = content[:pos] + "\x00" + content[pos:]
        return corrupted, "null_byte_injection"

    def _corrupt_replacement_chars(self, content: str) -> tuple[str, str]:
        # Replace random characters with the Unicode replacement character
        num_replacements = random.randint(1, min(5, max(1, len(content) // 20)))
        content_list = list(content)
        for _ in range(num_replacements):
            idx = random.randint(0, len(content_list) - 1)
            content_list[idx] = "\ufffd"
        return "".join(content_list), "unicode_replacement_char"
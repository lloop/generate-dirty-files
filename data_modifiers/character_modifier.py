import random

class CharacterModifier:
    
    def corrupt_character_encoding(self, content: str) -> tuple[str, list[str]]:
        if not isinstance(content, str) or not content:
            return content, []

        corruptions = [
            self._corrupt_mojibake,
            self._corrupt_null_bytes,
            self._corrupt_replacement_chars,
        ]

        random.shuffle(corruptions)

        for corruption in corruptions:
            corrupted, label = corruption(content)

            if label != "none" and corrupted != content:
                return corrupted, [label]

        return content, []

    def _corrupt_mojibake(self, content: str) -> tuple[str, str]:
        try:
            corrupted = (
                content
                .encode("utf-8")
                .decode("cp1252", errors="replace")
            )

            if corrupted == content:
                return content, "none"

            return corrupted, "mojibake"

        except Exception:
            return content, "none"

    def _corrupt_null_bytes(self, content: str) -> tuple[str, str]:
        pos = random.randint(0, len(content) - 1)
        corrupted = content[:pos] + "\x00" + content[pos:]
        return corrupted, "null_byte_injection"

    def _corrupt_replacement_chars(self, content: str) -> tuple[str, str]:
        marker = "CHARACTER_CORRUPTION_ZONE:"

        start = content.find(marker)

        if start == -1:
            return content, "none"

        start += len(marker)

        end = content.find("\n", start)

        if end == -1:
            end = len(content)

        zone = content[start:end]

        safe_indices = [
            i for i, char in enumerate(zone)
            if char.isalnum()
        ]

        if not safe_indices:
            return content, "none"

        num_replacements = random.randint(
            1,
            min(5, len(safe_indices))
        )

        zone_list = list(zone)

        for _ in range(num_replacements):
            idx = random.choice(safe_indices)
            zone_list[idx] = "\ufffd"

        corrupted = (
            content[:start]
            + "".join(zone_list)
            + content[end:]
        )

        return corrupted, "unicode_replacement_char"
    
    # Temp. Injecting multiple corruptions to test the lists
    def apply_test_corruptions(
        self,
        content: str,
    ) -> tuple[str, list[str]]:
        content, label_1 = self._corrupt_null_bytes(content)
        content, label_2 = self._corrupt_replacement_chars(content)

        return content, [label_1, label_2]
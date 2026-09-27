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
        content, target, quote = self._get_corruption_target(content)

        if not target:
            return content, "none"

        try:
            corrupted = (
                target
                .encode("utf-8")
                .decode("cp1252", errors="replace")
            )

            if corrupted == target:
                return content, "none"

            marker = "CHARACTER_CORRUPTION_ZONE:"
            start = content.find(marker)
            value_start = start + len(marker)

            while content[value_start].isspace():
                value_start += 1

            value_start += 1

            value_end = content.find(quote, value_start)

            corrupted_content = (
                content[:value_start]
                + corrupted
                + content[value_end:]
            )

            return corrupted_content, "mojibake"

        except Exception:
            return content, "none"
        
    def _corrupt_null_bytes(self, content: str) -> tuple[str, str]:
        content, target, quote = self._get_corruption_target(content)

        if not target:
            return content, "none"

        pos = random.randint(0, len(target))

        corrupted_target = (
            target[:pos]
            + "\x00"
            + target[pos:]
        )

        marker = "CHARACTER_CORRUPTION_ZONE:"
        start = content.find(marker)
        value_start = start + len(marker)

        while content[value_start].isspace():
            value_start += 1

        value_start += 1

        value_end = content.find(quote, value_start)

        corrupted_content = (
            content[:value_start]
            + corrupted_target
            + content[value_end:]
        )

        return corrupted_content, "null_byte_injection"

    def _corrupt_replacement_chars(self, content: str) -> tuple[str, str]:
        content, target, quote = self._get_corruption_target(content)

        if not target:
            return content, "none"

        safe_indices = [
            i for i, char in enumerate(target)
            if char.isalnum()
        ]

        if not safe_indices:
            return content, "none"

        num_replacements = random.randint(
            1,
            min(5, len(safe_indices))
        )

        selected_indices = random.sample(
            safe_indices,
            num_replacements
        )

        target_list = list(target)

        for idx in selected_indices:
            target_list[idx] = "\ufffd"

        corrupted_target = "".join(target_list)

        marker = "CHARACTER_CORRUPTION_ZONE:"
        start = content.find(marker)
        value_start = start + len(marker)

        while content[value_start].isspace():
            value_start += 1

        value_start += 1

        value_end = content.find(quote, value_start)

        corrupted_content = (
            content[:value_start]
            + corrupted_target
            + content[value_end:]
        )

        return corrupted_content, "unicode_replacement_char"

    def _get_corruption_target(
        self,
        content: str,
    ) -> tuple[str, str, str]:
        marker = "CHARACTER_CORRUPTION_ZONE:"

        start = content.find(marker)

        if start == -1:
            return content, "", ""

        value_start = start + len(marker)

        # Find the first quote after the marker.
        while value_start < len(content) and content[value_start].isspace():
            value_start += 1

        if value_start >= len(content):
            return content, "", ""

        quote = content[value_start]

        if quote not in ('"', "'"):
            return content, "", ""

        value_start += 1

        # Find the closing quote.
        value_end = content.find(quote, value_start)

        if value_end == -1:
            return content, "", ""

        target = content[value_start:value_end]

        return content, target, quote
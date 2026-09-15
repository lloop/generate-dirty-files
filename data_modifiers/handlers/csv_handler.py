import random
from .base import BaseFormatHandler


class CSVHandler(BaseFormatHandler):

    def add_unique_entropy(self, content: str | bytes, token: str) -> str:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        header = lines[0] if lines else "id,timestamp,data,status"
        body = lines[1:] if len(lines) > 1 else []

        body.append(f"rec_{token[:4]},{token[:6]},active_data,OK")
        transformed = [header] + body
        transformed.append(f"# build_id,{token}")
        return "\n".join(transformed) + "\n"

    def corrupt_structure(
        self, content: str | bytes, mutation_type: str = "auto"
    ) -> tuple[str, str]:
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if not lines:
            return text, "none"

        header = lines[0]
        body = lines[1:]

        mutations = {
            "dropped_header": lambda h, b: b,
            "swapped_delimiter": lambda h, b: [
                line.replace(",", ";") for line in ([h] + b)
            ],
            "malformed_row": lambda h, b: [h] + b + ["unmatched,row,extra"],
            "zero_byte": lambda h, b: [],
        }

        label = (
            random.choice(list(mutations.keys()))
            if mutation_type == "auto"
            else "none"
        )

        if label == "none":
            return text, label

        transformed = mutations[label](header, body)
        return "\n".join(transformed) + ("\n" if transformed else ""), label
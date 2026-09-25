import random
from .base import BaseFormatHandler
import csv
import io

class CSVHandler(BaseFormatHandler):

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

        rows = list(csv.reader(io.StringIO(text)))

        if not rows:
            return text

        rows[0].append("_build_id")

        for row in rows[1:]:
            row.append(token)

        output = io.StringIO()
        writer = csv.writer(output, lineterminator="\n")
        writer.writerows(rows)

        return output.getvalue()

    def corrupt_structure(
        self, content: str | bytes, corruption_type: str = "auto"
    ) -> tuple[str, str]:
        '''Applies format-specific structural corruptions
        
        Corruption types:
        dropped_header
        malformed_row
        zero_byte
        
        Need to dev out more, for example malformed quoting, 
        inconsistent structure, truncated content, or invalid CSV syntax.
        '''
        text = content.decode("utf-8") if isinstance(content, bytes) else content
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        if not lines:
            return text, "none"

        header = lines[0]
        body = lines[1:]

        corruptions = {
            "dropped_header": lambda h, b: ["_build_id"] + b,
            "malformed_row": lambda h, b: [h] + b + ["unmatched,row,extra"],
            "zero_byte": lambda h, b: [],
        }

        label = (
            random.choice(list(corruptions.keys()))
            if corruption_type == "auto"
            else corruption_type
        )

        if label == "none":
            return text, label

        transformed = corruptions[label](header, body)
        return "\n".join(transformed) + ("\n" if transformed else ""), label
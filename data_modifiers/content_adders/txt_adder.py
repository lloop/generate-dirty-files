import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Union


class TXTAdder:
    """Generates and injects dynamic text blocks, timestamp headers, and

    rearranges paragraph sections to ensure unique file variance.
    """

    def __init__(self):
        self.mock_categories = ["AUDIT_LOG", "SYSTEM_DIAGNOSTIC", "USER_NOTES", "REPORT_SUMMARY"]
        self.mock_sentences = [
            "The system completed the scheduled operation without encountering standard errors.",
            "Pipeline telemetry indicates normal load variance across all evaluated nodes.",
            "Verification protocols confirmed data integrity checks were executed successfully.",
            "Automated background processing generated secondary log outputs for review.",
            "Resource allocation parameters remained within baseline performance thresholds.",
            "Notice: Diagnostic traces were logged to the central monitoring server."
        ]

    def _generate_synthetic_header(self) -> str:
        """Generates a dynamic timestamped header block."""
        build_id = str(uuid.uuid4())[:8]
        category = random.choice(self.mock_categories)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        return (
            f"=== {category} HEADER ===\n"
            f"Timestamp: {timestamp}\n"
            f"Trace ID: TRACE-{build_id}\n"
            f"----------------------------------------"
        )

    def _generate_synthetic_paragraph(self) -> str:
        """Generates a random paragraph constructed from mock sentences."""
        num_sentences = random.randint(2, 4)
        chosen_sentences = random.sample(self.mock_sentences, k=min(num_sentences, len(self.mock_sentences)))
        return " ".join(chosen_sentences)

    def inject_and_rearrange(self, file_path: Union[str, Path]) -> None:
        """Reads target TXT file, injects dynamic headers and synthetic text blocks,

        shuffles existing paragraph sections, and writes back to disk.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Target file not found: {path}")

        raw_text = path.read_text(encoding="utf-8").strip()

        # 1. Split existing content into paragraph blocks
        paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]

        # 2. Generate new dynamic content
        new_header = self._generate_synthetic_header()
        new_paragraph = self._generate_synthetic_paragraph()

        # Add the newly generated paragraph into the block collection
        paragraphs.append(new_paragraph)

        # 3. Shuffle paragraph order if multiple exist to vary layout structure
        if len(paragraphs) > 1:
            random.shuffle(paragraphs)

        # 4. Assemble final document (Header at top, followed by rearranged paragraphs)
        final_paragraphs = [new_header] + paragraphs
        final_text = "\n\n".join(final_paragraphs) + "\n"

        path.write_text(final_text, encoding="utf-8")


def modify_txt(file_path: Union[str, Path]) -> str:
    """Helper functional wrapper for integration into pipeline content modifiers."""
    adder = TXTAdder()
    adder.inject_and_rearrange(file_path)
    return "txt_hydrated_and_rearranged"
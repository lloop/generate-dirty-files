from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class FileRecord:
    """Schema object holding the full lifecycle state and manifest metadata of a synthetic file."""

    # Identity & Path State
    unique_token: str
    original_filename: str
    original_extension: str
    output_filename: str = ""
    output_extension: str = ""

    # Content Payload State
    content: str | bytes = ""
    is_binary: bool = False

    # Mutation Labels (Provenance Tracking)
    structural_mutation: str = "none"
    character_mutation: str = "none"
    extension_scrambled: bool = False
    is_duplicate: bool = False

    # Computed Metadata
    sha256_hash: str = field(init=False, default="")
    byte_size: int = field(init=False, default=0)

    def finalize_content(self, final_content: str | bytes) -> None:
        """Updates the payload and recomputes exact hashes/sizes right before disk write."""
        self.content = final_content

        if isinstance(final_content, str):
            raw_bytes = final_content.encode("utf-8", errors="surrogateescape")
        else:
            raw_bytes = final_content

        self.byte_size = len(raw_bytes)
        self.sha256_hash = hashlib.sha256(raw_bytes).hexdigest()

    def to_manifest_dict(self) -> dict:
        """Exports the schema state for the final dataset JSON manifest."""
        return {
            "unique_token": self.unique_token,
            "original_filename": self.original_filename,
            "output_filename": self.output_filename,
            "original_extension": self.original_extension,
            "output_extension": self.output_extension,
            "extension_mismatch": self.extension_scrambled,
            "is_duplicate": self.is_duplicate,
            "mutations": {
                "structural": self.structural_mutation,
                "character_encoding": self.character_mutation,
            },
            "file_size_bytes": self.byte_size,
            "sha256": self.sha256_hash,
        }
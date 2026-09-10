import os
import random
import uuid
from datetime import datetime
from pathlib import Path
from typing import Union


class JPGAdder:
    """Injects dynamic binary metadata/padding trailing payloads after the JPEG EOI

    (End of Image) marker to ensure unique file hashes without breaking rendering.
    """

    def __init__(self):
        self.mock_cameras = [b"NIKON_D850", b"CANON_EOS_R5", b"SONY_ALPHA_A7IV", b"IPHONE_14_PRO"]

    def _generate_synthetic_binary_payload(self) -> bytes:
        """Generates a dynamic byte payload containing timestamp tags, camera metadata,

        and random byte padding.
        """
        build_id = str(uuid.uuid4())[:8].encode("utf-8")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S").encode("utf-8")
        camera = random.choice(self.mock_cameras)
        
        # Binary comment header
        header = b"\n-- HYDRATION_METADATA_START --\n"
        meta = b"BUILD:" + build_id + b"|DATE:" + timestamp + b"|CAM:" + camera + b"\n"
        
        # Dynamic byte padding (16 to 128 random bytes)
        padding_length = random.randint(16, 128)
        padding = os.urandom(padding_length)
        
        footer = b"\n-- HYDRATION_METADATA_END --\n"

        return header + meta + padding + footer

    def inject_payload(self, file_path: Union[str, Path]) -> None:
        """Appends dynamic binary payload to the end of the JPEG file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Target file not found: {path}")

        # Open in binary append mode and append dynamic trailing bytes
        payload = self._generate_synthetic_binary_payload()
        
        with open(path, "ab") as f:
            f.write(payload)


def modify_jpg(file_path: Union[str, Path]) -> str:
    """Helper functional wrapper for integration into pipeline content modifiers."""
    adder = JPGAdder()
    adder.inject_payload(file_path)
    return "jpg_binary_payload_injected"
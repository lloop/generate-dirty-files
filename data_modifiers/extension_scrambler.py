# data_modifiers/extension_scrambler.py
import random
from pathlib import Path


def scramble_extension(file_path: Path, extensions: list) -> Path:
    """Returns a new Path object with a scrambled extension prior to file creation."""
    current_ext = file_path.suffix.lower()
    possible_exts = [e for e in extensions if e != current_ext]
    new_ext = random.choice(possible_exts)
    
    # print(f"    [!] Scrambled extension: {current_ext} -> {new_ext}")

    return file_path.with_suffix(new_ext)
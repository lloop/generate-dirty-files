# data_modifiers/extension_scrambler.py
import random
from pathlib import Path

WRONG_EXTENSIONS = [".xml", ".txt", ".csv", ".json", ".dat", ".html", ".jpg", ".png"]

def scramble_extension(file_path: Path) -> Path:
    """Returns a new Path object with a scrambled extension prior to file creation."""
    current_ext = file_path.suffix.lower()
    possible_exts = [e for e in WRONG_EXTENSIONS if e != current_ext]
    new_ext = random.choice(possible_exts)
    
    # print(f"    [!] Scrambled extension: {current_ext} -> {new_ext}")

    return file_path.with_suffix(new_ext)
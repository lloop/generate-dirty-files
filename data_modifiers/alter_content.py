import os
import random

from .content_modifiers.csv_modifier import corrupt_csv
from .content_modifiers.html_modifier import corrupt_html
from .content_modifiers.jpg_modifier import corrupt_jpg
from .content_modifiers.json_modifier import corrupt_json
from .content_modifiers.py_modifier import corrupt_py
from .content_modifiers.txt_modifier import corrupt_txt
from .content_modifiers.xml_modifier import corrupt_xml

PERCENT_CORRUPTED = 0.4

# Registry mapping extensions to their respective handlers
MODIFIER_MAP = {
    ".txt": corrupt_txt,
    ".csv": corrupt_csv,
    ".html": corrupt_html,
    ".json": corrupt_json,
    ".xml": corrupt_xml,
    ".jpg": corrupt_jpg,
    ".py": corrupt_py,
}


def alter_content(file_path: str) -> str:
    """Entry point for content alterations. Routes file paths to extension handlers."""
    if random.random() >= PERCENT_CORRUPTED:
        return "none"

    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    modifier_func = MODIFIER_MAP.get(ext)
    if modifier_func:
        mod_type = modifier_func(file_path)
        
        print(f"    [*] Altered the content of .{ext} file '{file_path}' (Mod Type: {mod_type})")
        
        return mod_type
    
    return "none"
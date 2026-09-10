from pathlib import Path
import shutil
from config import OUT_DIRECTORY, AMOUNT_OF_FILES
from data_modifiers.generate_title import generate_title

# Create the output directory. delete previous output if it exists
files = Path(OUT_DIRECTORY)
if files.exists():
    shutil.rmtree(OUT_DIRECTORY)
files.mkdir()


for i in range(1, AMOUNT_OF_FILES + 1):
    finished_name = generate_title()
    file_path = files / f"{finished_name}"
    file_path.write_text(f"This is dirty file {i}")

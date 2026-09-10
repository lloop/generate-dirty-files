import random
from modifiers.capitals import capitalized, cap_first
from modifiers.mistakes import mistake_punctuation

MODIFIERS = [capitalized, cap_first] 
PERCENT_ADDED = 0.8
PERCENT_MISTAKEN_PUNCTUATION = 0.03
PERCENT_MODIFIED = 0.4
# FILE_EXTENSIONS = [".txt", ".csv", ".jpg", ".pdf", "html", ".docx", ".xlsx", ".pptx", ".json", ".xml"]
FILE_EXTENSIONS = [".txt", ".csv", ".jpg", ".html", ".json", ".xml"]
FILE_NAMES = [
    "invoice",
    "photo",
    "report",
    "notes",
    "data",
    "presentation",
    "budget",
    "meeting",
    "contract",
    "receipt",
    "project",
    "backup",
]

ADDED = [
    "_final",
    "_old",
    "_new",
    "_copy",
    "_backup",
    "_draft",
]

def generate_title():
    """Generate a random file title with random modifications and mistakes."""
    # Generate a random file name
    name = random.choice(FILE_NAMES)
    if random.random() < PERCENT_ADDED:
        added = random.choice(ADDED)
        full_name = f"{name}{added}"
        print(f"    [!] Introduced name addition ({PERCENT_ADDED*100}% hit): {name} -> {full_name}")        
    else:
        full_name = name
    
    # Apply a random modifier
    if random.random() < PERCENT_MODIFIED:
        modifier = random.choice(MODIFIERS)
        pre_name = full_name
        full_name = modifier(full_name)
        print(f"    [!] Introduced random modifier ({PERCENT_MODIFIED*100}% hit): {pre_name} -> {full_name}")        
        
    # Add a random mistake punctuation
    if random.random() < PERCENT_MISTAKEN_PUNCTUATION:
        mistaken = mistake_punctuation(full_name)
        print(f"    [!] Introduced mistaken punctuation ({PERCENT_MISTAKEN_PUNCTUATION*100}% hit): {full_name} -> {mistaken}")
        finished_name = mistaken
    else:
        finished_name = full_name
            
    # Write the file
    extension = random.choice(FILE_EXTENSIONS)
    file_name = f"{finished_name}{extension}"
    
    return file_name

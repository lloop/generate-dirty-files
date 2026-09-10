import random

PERCENT_ADDED = 0.8
PERCENT_MISTAKEN_PUNCTUATION = 0.03
PERCENT_MODIFIED = 0.4
# FILE_EXTENSIONS = [".txt", ".csv", ".jpg", ".pdf", "html", ".docx", ".xlsx", ".pptx", ".json", ".xml"]
FILE_EXTENSIONS = [".txt", ".csv", ".jpg", ".html", ".json", ".xml"]
MISTAKES = ["_", "-", "."]
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
    "proposal",
    "agenda",
    "timesheet",
    "schedule",
    "inventory",
    "statement",
    "memo",
    "roster",
    "summary",
    "audit",
    "brief",
    "log",
]

ADDED = [
    "_final",
    "_old",
    "_new",
    "_copy",
    "_backup",
    "_draft",
]


def cap_first(str):
    return str.capitalize()

def capitalized(str):
    return str.upper()

MODIFIERS = [capitalized, cap_first] 


def generate_title(available_extensions: list = None) -> str:
    """Generate a random file title with random modifications and mistakes."""
    
    # Use discovered template extensions if passed, otherwise fall back to default list
    extensions = available_extensions or FILE_EXTENSIONS
    
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
    ext = random.choice(extensions)
    file_name = f"{finished_name}{ext}"
    
    return file_name


def mistake_punctuation(word: str) -> str:
    """Add a random mistake punctuation to the word."""

    mistake = random.choice(MISTAKES)
    
    # Pick a random insertion index (0 to length of string inclusive)
    insert_pos = random.randint(0, len(word))

    # Splice the character into the string
    return word[:insert_pos] + mistake + word[insert_pos:]


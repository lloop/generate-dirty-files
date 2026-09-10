import random

MISTAKES = ["_", "-", "."]

def mistake_punctuation(word: str) -> str:
    """Add a random mistake punctuation to the word."""

    mistake = random.choice(MISTAKES)
    
    # Pick a random insertion index (0 to length of string inclusive)
    insert_pos = random.randint(0, len(word))

    # Splice the character into the string
    return word[:insert_pos] + mistake + word[insert_pos:]
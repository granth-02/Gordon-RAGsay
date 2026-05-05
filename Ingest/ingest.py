from pathlib import Path
import re


recipies = Path("Data/Recipies")
recipies_files = list(recipies.glob("*.txt"))

def parse_metadata(text: str) -> dict:
    metadata = {}
    matches = {
        "name": r"Name:\s*(.+)",
        "cuisine": r"Cuisine:\s*(.+)",
        "prep_time": r"Prep Time:\s*(.+)",
        "cook_time": r"Cook Time:\s*(.+)",
        "spice_level": r"Spice Level:\s*(\d+)",
        "savoury": r"Savoury Level:\s*(\d+)",
        "salt": r"Salt Level:\s*(\d+)",
        "sweetness": r"Sweetness Level:\s*(\d+)",
        "umami": r"Umami Level:\s*(\d+)",
    }

    for key, pattern in matches.items():
        pattern = re.search(pattern, text, re.IGNORECASE)
        if pattern:
            metadata[key] = pattern.group(1)
    
    for key in ["spice_level", "savoury", "salt", "sweetness", "umami"]:
        if key in metadata:
            metadata[key] = int(metadata[key])
    
    ingredients_match = re.search(r"Ingredients:(.*?)Procedure:", text, re.DOTALL)
    if ingredients_match:
        ingredients = ingredients_match.group(1).lower()
        metadata["has_paneer"] = "paneer" in ingredients
        metadata["has_chicken"] = "chicken" in ingredients
        metadata["has_eggs"] = "eggs" in ingredients

    return metadata

def chunk_sections(text: str) -> dict:
    def get_chunk(start, end=None):
        if end:
            pattern = rf"{start}(.*?){end}"
        else:
            pattern = rf"{start}(.*)"
        match = re.search(pattern, text, re.DOTALL)
        return match.group(1).strip() if match else ""
    
    metadata_chunk = text.split("Ingredients:")[0].strip()
    ingredients_chunk = get_chunk("Ingredients:", "Procedure:")
    procedure_chunk = get_chunk("Procedure:", "My Notes:")
    notes_chunk = get_chunk("My Notes:", "Alternatives:")
    alternatives_chunk = get_chunk("Alternatives:")

    return {
        "metadata_chunk": metadata_chunk,
        "ingredients_chunk": ingredients_chunk,
        "procedure_chunk": procedure_chunk,
        "notes_chunk": notes_chunk,
        "alternatives_chunk": alternatives_chunk,
    }

def chunk_sentances(text: str) -> list:
    return [line.strip() for line in text.split('\n') if line.strip() if line.strip() and not line.strip().endswith(':')]

for file in recipies_files:
    text = file.read_text(encoding='utf-8')
    par = chunk_sentances(text)
    print(par)
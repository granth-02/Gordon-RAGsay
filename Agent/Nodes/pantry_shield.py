import json
from pathlib import Path
from Agent.state import AgentState

ROOT = Path(__file__).parent.parent.parent
RELATIONSHIPS_PATH = ROOT / "Data" / "recipe_relationships.json"

with open(RELATIONSHIPS_PATH, "r") as f:
    relationships = json.load(f)

def extract_recipe_ingredients(recipe_text: str) -> list:
    lines = recipe_text.split("\n")
    capturing = False
    ingredients = []
    for line in lines:
        line = line.strip()
        if line.lower().startswith("ingredients:") or line.lower().startswith("ingrediants:"):
            capturing = True
            continue
        if capturing:
            if line.lower().startswith("procedure:"):
                break
            if line:
                ingredients.append(line.lower())
    return ingredients

def find_alternative(missing: str) -> str:
    for cluster, data in relationships["ingredient_clusters"].items():
        if missing.lower() in cluster.lower():
            return f"Consider using an alternative from your personal substitutions"
    return ""

def pantry_shield_node(state: AgentState) -> AgentState:
    retrieved = state.get("retrieved_recipes", [])
    pantry = state.get("pantry")

    if not pantry or not retrieved:
        return state

    pantry_items = [
        item["name"].lower()
        for item in pantry.get("ingredients", [])
    ]

    top_recipe = retrieved[0] if retrieved else ""
    recipe_ingredients = extract_recipe_ingredients(top_recipe)

    missing = []
    for ingredient in recipe_ingredients:
        ingredient_clean = ingredient.strip("- ").split(" ")[0]
        if not any(ingredient_clean in pantry_item for pantry_item in pantry_items):
            alternative = find_alternative(ingredient_clean)
            missing.append({
                "ingredient": ingredient_clean,
                "alternative": alternative
            })

    return {**state, "missing_ingredients": missing}
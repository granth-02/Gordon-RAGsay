import json
from pathlib import Path
from Agent.state import AgentState

ROOT = Path(__file__).parent.parent.parent
RELATIONSHIPS_PATH = ROOT / "Data" / "recipe_relationships.json"

with open(RELATIONSHIPS_PATH, "r") as f:
    relationships = json.load(f)

dna = relationships["dna_rules"]

DNA_CONTEXT = f"""
always: {', '.join(dna['always'])}
never: {', '.join(dna['never'])}
spice: {dna['spice_philosophy']}
health: {dna['health_philosophy']}
"""

def expand_query(query: str) -> str:
    return f"{query}. Cooking preferences: {DNA_CONTEXT}"

def query_expansion_node(state: AgentState) -> AgentState:
    query = state.get("query", "")
    dish_tags = state.get("dish_tags")

    if dish_tags:
        expanded = f"{dish_tags.get('dish_name', '')} {dish_tags.get('cuisine', '')} style. {DNA_CONTEXT}"
    else:
        expanded = expand_query(query)

    return {**state, "query": expanded}
import requests
import json
from config import call_llm
from Agent.state import AgentState

NORMAL_PROMPT = """You are a recipe ranking assistant with deep knowledge of the user's cooking preferences.

User query: {query}

User DNA:
- Always doubles garlic, cooks it dark brown
- Spice level 4-5/5 for all savoury dishes
- Prefers whole wheat over all purpose flour
- Uses yogurt instead of cream/mayo
- Always adds more vegetables than recipe calls for
- Never uses milk chocolate
- Finishes every savoury dish with lemon juice

Available pantry: {pantry}

Here are {count} candidate recipes. Rank them from most to least suitable based on:
1. How well they match the user's DNA and preferences
2. How many pantry ingredients they already have
3. How relevant they are to the query

Recipes:
{recipes}

Return ONLY a JSON array of indices in ranked order (most suitable first), no explanation:
[0, 2, 1]"""

GORDON_PROMPT = """You are ranking recipes like Gordon Ramsay would — brutal and uncompromising.

User query: {query}

User DNA:
- Always doubles garlic, cooks it dark brown
- Spice level 4-5/5 for all savoury dishes
- Prefers whole wheat over all purpose flour
- Uses yogurt instead of cream/mayo
- Always adds more vegetables than recipe calls for
- Never uses milk chocolate
- Finishes every savoury dish with lemon juice

Available pantry: {pantry}

Here are {count} candidate recipes. Rank them by what will actually produce something worth eating.
Don't waste my time with recipes missing half the ingredients or that violate the user's DNA.

Recipes:
{recipes}

Return ONLY a JSON array of indices in ranked order (most suitable first), no explanation:
[0, 2, 1]"""

def reranker_node(state: AgentState) -> AgentState:
    retrieved = state.get("retrieved_recipes", [])
    query = state.get("query", "")
    pantry = state.get("pantry")
    persona = state.get("persona", "normal")

    if not retrieved or len(retrieved) <= 1:
        return state

    pantry_str = ""
    if pantry:
        ingredients = [item["name"] for item in pantry.get("ingredients", [])]
        pantry_str = ", ".join(ingredients)

    recipes_str = ""
    for i, recipe in enumerate(retrieved):
        recipes_str += f"\n[{i}] {recipe[:300]}...\n"

    template = GORDON_PROMPT if persona == "gordon" else NORMAL_PROMPT
    prompt = template.format(
        query=query,
        pantry=pantry_str or "not provided",
        count=len(retrieved),
        recipes=recipes_str
    )

    raw = call_llm(prompt)

    try:
        raw = raw.replace("```json", "").replace("```", "").strip()
        start = raw.find("[")
        end = raw.rfind("]") + 1
        ranked_indices = json.loads(raw[start:end])
        reranked = [retrieved[i] for i in ranked_indices if i < len(retrieved)]
        return {**state, "retrieved_recipes": reranked}
    except Exception:
        return state
from Agent.state import AgentState
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def hde_node(state: AgentState) -> AgentState:
    expanded_query = state.get("query", "")
    pantry = state.get("pantry")
    dish_tags = state.get("dish_tags")

    pantry_context = ""
    if pantry:
        ingredients = [
            item["name"]
            for item in pantry.get("ingredients", [])
        ]
        pantry_context = f"Available pantry ingredients: {', '.join(ingredients)}"

    dish_context = ""
    if dish_tags:
        dish_context = f"""
Dish Name: {dish_tags.get('dish_name', '')}
Cuisine: {dish_tags.get('cuisine', '')}
Meal Type: {dish_tags.get('meal_type', '')}
"""

    hypothetical_document = f"""
This is a personalised recipe request.

{expanded_query}

{dish_context}

{pantry_context}

The ideal recipe should:
- follow the user's cooking style
- maximise pantry ingredient usage
- avoid unnecessary ingredients
- maintain flavour depth
- resemble previous recipes cooked by the user
"""

    embedding = model.encode(hypothetical_document).tolist()

    return {
        **state,
        "hde_document": hypothetical_document,
        "query_embedding": embedding
    }
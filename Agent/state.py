from typing import TypedDict, Optional

class AgentState(TypedDict):
    query: str
    image: Optional[str]
    image_type: Optional[str]
    pantry: Optional[dict]
    dish_tags: Optional[dict]
    retrieved_recipes: Optional[list[str]]
    missing_ingredients: Optional[list]
    missing_prices: Optional[dict]
    memory_context: Optional[str]
    route: Optional[str]
    response: Optional[str]
    retrieval_scores: Optional[list]
    persona: Optional[str]
    chunk_mode: Optional[str]
    chat_history: Optional[list]
import json
from pathlib import Path
from Agent.state import AgentState
from config import call_llm

ROOT = Path(__file__).parent.parent.parent
RELATIONSHIPS_PATH = ROOT / "Data" / "recipe_relationships.json"

with open(RELATIONSHIPS_PATH, "r") as f:
    relationships = json.load(f)

dna = relationships["dna_rules"]

SYSTEM = """You are Gordon RAGsay, a personal recipe assistant.
Be direct and concise. Never start with greetings like "Hey Granth" or "Oh Granth".
Answer exactly what was asked. Nothing more."""

GORDON_SYSTEM = """You are Gordon RAGsay channeling Gordon Ramsay.
Brutal, direct, censored cuss words (f**k, s**t). Use "idiot sandwich" when warranted.
Never start with greetings. Answer exactly what was asked."""

COOKING_STYLE = """Granth's style (inspiration only, not rules):
garlic dark brown, spice 4-5/5, whole wheat preferred, yogurt over cream, extra veg, lemon finish"""

CONVERSATIONAL = [
    "what is", "what's", "how much", "how many", "why", "is it", "does it",
    "tell me", "explain", "umami", "spice level", "how long", "what are",
    "can i", "should i", "thanks", "ok", "okay", "got it", "cool", "nice"
]

PRICE_WORDS = ["price", "cost", "how much", "woolworths", "buy", "afford"]

def is_conversational(query: str, history: list) -> bool:
    q = query.lower()
    return len(history) > 0 and len(q.split()) < 12 and any(kw in q for kw in CONVERSATIONAL)

def is_price_query(query: str) -> bool:
    return any(kw in query.lower() for kw in PRICE_WORDS)

def build_prompt(state: AgentState) -> str:
    query = state.get("query", "")
    retrieved = state.get("retrieved_recipes", [])
    memory = state.get("memory_context", "")
    missing = state.get("missing_ingredients", [])
    prices = state.get("missing_prices", {})
    pantry = state.get("pantry")
    persona = state.get("persona", "normal")
    history = state.get("chat_history", [])
    route = state.get("route", "")

    system = GORDON_SYSTEM if persona == "gordon" else SYSTEM

    # history — last 3 turns stripped of footers
    history_str = ""
    if history:
        for turn in history[-3:]:
            if isinstance(turn, (list, tuple)) and len(turn) == 2:
                h, a = turn
                clean = str(a).split("---")[0].strip()[:250]
                history_str += f"User: {h}\nAssistant: {clean}\n\n"

    # pantry
    pantry_str = ""
    pantry_items = []
    if pantry:
        pantry_items = [item["name"] for item in pantry.get("ingredients", [])]
        pantry_str = f"Pantry: {', '.join(pantry_items)}"

    # memory
    memory_str = f"Memory: {memory}" if memory else ""

    # missing + prices — only when price is asked
    missing_str = ""
    if missing:
        if is_price_query(query) and prices:
            lines = []
            for item in missing:
                ing = item.get("ingredient", "")
                if ing in prices and prices[ing].get("price"):
                    p = prices[ing]
                    lines.append(f"- {ing}: ${p['price']} / {p.get('unit','')}")
                elif item.get("alternative"):
                    lines.append(f"- {ing}: substitute with {item['alternative']}")
            if lines:
                missing_str = "Woolworths prices:\n" + "\n".join(lines)
        elif not is_price_query(query):
            names = [m["ingredient"] for m in missing[:3]]
            if names:
                missing_str = f"Missing from pantry: {', '.join(names)}"

    # recipe — clean injection
    recipe_str = ""
    if retrieved and route == "existing":
        # only show the recipe, nothing else
        recipe_str = f"PERSONAL RECIPE:\n{retrieved[0]}"
    elif retrieved and route != "existing":
        recipe_str = f"Style reference:\n{retrieved[0][:400]}"

    # instruction — tightly controlled
    if is_price_query(query) and not pantry:
        # direct price query with no pantry context
        instruction = """Fetch and show the Woolworths price from the data provided.
If no price data available, say so clearly in one sentence.
Do not suggest recipes unless asked."""
    elif is_conversational(query, history):
        instruction = "Answer in 1-3 sentences. No recipe format."
    elif route == "existing" and pantry_items:
        instruction = f"""Show the personal recipe above.
Then check: which ingredients does the user NOT have from: {', '.join(pantry_items)}
List only what's missing. Do not generate a new recipe — just show theirs with a missing ingredients note."""
    elif route == "existing":
        instruction = "Show the personal recipe above exactly. Answer any specific question about it briefly."
    elif pantry_items:
        instruction = f"""Suggest a recipe using ONLY these ingredients: {', '.join(pantry_items)}
Do not add ingredients not in this list.
Format: Recipe name, ingredients (from list only), simple steps, done."""
    else:
        instruction = f"""Suggest a recipe inspired by Granth's style.
{COOKING_STYLE}
Format:
**Recipe:** name
**Time:** X mins
**Spice:** X/5
**Ingredients:** list
**Method:** steps
**Notes:** one line"""

    prompt = f"""{system}

{history_str}User: {query}

{pantry_str}
{memory_str}
{missing_str}
{recipe_str}

{instruction}"""

    return prompt

def synthesiser_node(state: AgentState) -> AgentState:
    prompt = build_prompt(state)
    response = call_llm(prompt)
    return {**state, "response": response}
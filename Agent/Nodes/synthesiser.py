import json
from pathlib import Path
from Agent.state import AgentState
from config import call_llm

ROOT = Path(__file__).parent.parent.parent
RELATIONSHIPS_PATH = ROOT / "Data" / "recipe_relationships.json"
GLOSSARY_PATH = ROOT / "Data" / "glossary.json"

with open(RELATIONSHIPS_PATH, "r") as f:
    relationships = json.load(f)

with open(GLOSSARY_PATH, "r") as f:
    glossary = json.load(f)

dna = relationships["dna_rules"]

DNA_RULES = f"""
Granth's cooking DNA — use as inspiration, not strict rules:
- Generally likes garlic and cooks it dark brown
- Prefers spice level 4-5/5 for savoury dishes
- Likes whole wheat over all-purpose flour where possible
- Prefers yogurt over cream/mayo for lighter dishes
- Loves adding extra vegetables
- Never uses milk chocolate in desserts
- Usually finishes savoury dishes with lemon juice
- Health conscious — lower calories, higher protein where possible"""

NORMAL_PERSONA = f"""You are Gordon RAGsay, a warm and knowledgeable personal recipe assistant for Granth.
You are encouraging, conversational, and helpful.
You know Granth's cooking style and use it as inspiration when suggesting recipes.
You can have normal conversations, answer questions, and help with anything food related.
When Granth wants to learn something new or try a different style, support that fully.

{DNA_RULES}"""

GORDON_PERSONA = f"""You are Gordon RAGsay channeling Gordon Ramsay's brutal honesty.
Harsh, blunt, use censored cuss words like f**k, s**t, d**n.
Use "idiot sandwich" when appropriate. Zero sugar coating.
Despite harshness you genuinely care about Granth's cooking.
You can still have normal conversations — just with brutal honesty.

{DNA_RULES}"""

CONVERSATIONAL_KEYWORDS = ["what is", "what's", "how much", "why", "is it",
                            "does it", "tell me", "explain", "umami", "spice level",
                            "how long", "what are", "can i", "should i", "what do",
                            "how do", "thanks", "ok", "okay", "got it", "cool"]

def is_conversational(query: str, history: list) -> bool:
    query_lower = query.lower()
    word_count = len(query.split())
    has_history = len(history) > 0
    is_short = word_count < 12
    has_conv_kw = any(kw in query_lower for kw in CONVERSATIONAL_KEYWORDS)
    return has_history and is_short and has_conv_kw

def get_system_prompt(persona: str) -> str:
    return GORDON_PERSONA if persona == "gordon" else NORMAL_PERSONA

def build_prompt(state: AgentState) -> str:
    query = state.get("query", "")
    retrieved = state.get("retrieved_recipes", [])
    memory = state.get("memory_context", "")
    missing = state.get("missing_ingredients", [])
    prices = state.get("missing_prices", {})
    pantry = state.get("pantry")
    persona = state.get("persona", "normal")
    chat_history = state.get("chat_history", [])
    route = state.get("route", "")

    system = get_system_prompt(persona)

    # last 4 turns of conversation
    history_str = ""
    if chat_history:
        history_str = "Previous conversation:\n"
        for turn in chat_history[-4:]:
            if isinstance(turn, (list, tuple)) and len(turn) == 2:
                human, assistant = turn
                clean_assistant = str(assistant).split("---")[0].strip()
                history_str += f"User: {human}\nAssistant: {clean_assistant[:400]}\n\n"

    pantry_str = ""
    if pantry:
        items = [item["name"] for item in pantry.get("ingredients", [])]
        pantry_str = f"Current pantry: {', '.join(items)}"

    memory_str = f"Memory: {memory}" if memory else ""

    missing_str = ""
    if missing:
        missing_lines = []
        for item in missing:
            line = f"- {item['ingredient']}"
            if item.get("alternative"):
                line += f" (sub: {item['alternative']})"
            elif item["ingredient"] in (prices or {}):
                p = prices[item["ingredient"]]
                if p.get("price"):
                    line += f" (Woolworths: ${p['price']} / {p.get('unit','')})"
            missing_lines.append(line)
        missing_str = "Missing ingredients:\n" + "\n".join(missing_lines)

    # recipe context — inspiration not restriction
    recipes_str = ""
    if retrieved and route == "existing":
        recipes_str = f"""Granth has a personal recipe that matches this request.
Show it to him and offer to adapt it if needed.

GRANTH'S PERSONAL RECIPE:
{retrieved[0]}"""
    elif retrieved:
        recipes_str = "Similar recipes from Granth's collection for inspiration:\n"
        for i, recipe in enumerate(retrieved[:2]):
            recipes_str += f"\n--- {i+1} ---\n{recipe[:600]}\n"

    # dynamic instruction
    if is_conversational(query, chat_history):
        instruction = "Answer conversationally in 1-4 sentences. Do not generate a full recipe unless asked."
    elif route == "existing":
        instruction = "Show Granth his personal recipe. Offer to adapt it. Keep it concise."
    else:
        instruction = """Generate a recipe inspired by Granth's cooking style.
You don't need to follow his DNA strictly — if he wants to try something new, support that.
Format:
**Recipe Name:**
**Cuisine:**
**Cook Time:**
**Spice Level:**

**Ingredients:**

**Procedure:**

**Notes:**"""

    prompt = f"""{system}

{history_str}
---
User: {query}

{pantry_str}
{memory_str}
{missing_str}
{recipes_str}

{instruction}"""

    return prompt

def synthesiser_node(state: AgentState) -> AgentState:
    prompt = build_prompt(state)
    response = call_llm(prompt)
    return {**state, "response": response}
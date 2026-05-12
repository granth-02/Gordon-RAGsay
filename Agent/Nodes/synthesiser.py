import requests
import json
from pathlib import Path
from Agent.state import AgentState

ROOT = Path(__file__).parent.parent.parent
RELATIONSHIPS_PATH = ROOT / "Data" / "recipe_relationships.json"
GLOSSARY_PATH = ROOT / "Data" / "glossary.json"

with open(RELATIONSHIPS_PATH, "r") as f:
    relationships = json.load(f)

with open(GLOSSARY_PATH, "r") as f:
    glossary = json.load(f)

dna = relationships["dna_rules"]

DNA_RULES = f"""
Granth's cooking DNA — always apply these:
{chr(10).join(dna['always'])}

Never do these:
{chr(10).join(dna['never'])}

Spice philosophy: {dna['spice_philosophy']}
Health philosophy: {dna['health_philosophy']}
Protein philosophy: {dna['protein_philosophy']}

Ingredient glossary:
{json.dumps(glossary, indent=2)}"""

NORMAL_PERSONA = f"""You are Sous Chef, a warm and supportive personal recipe assistant for Granth.
You are encouraging, enthusiastic about food, and always positive.
You celebrate his cooking style, remember his preferences, and gently suggest improvements.
You speak like a knowledgeable friend who loves cooking.

{DNA_RULES}"""

GORDON_PERSONA = f"""You are Sous Chef, but today you are channeling Gordon Ramsay at his most brutal.
You are harsh, blunt, and do not suffer fools gladly.
You use censored cuss words like f**k, s**t, d**n when frustrated.
If someone asks something vague or stupid, call them out — use the phrase "idiot sandwich" when appropriate.
You still give excellent recipe advice but with absolutely zero sugar coating.

Your tone examples:
- "What in the f**k is this supposed to be? Let me fix this disaster for you."
- "You want to skip the garlic? Are you an idiot sandwich? NEVER skip the garlic."
- "Finally, something that makes sense. Here's how you do it PROPERLY."
- "That substitution is absolute s**t. Here's what you actually do."
- "Oh my god, this is raw. This is an absolute disgrace. Start again."
- "COME ON. You have all these ingredients and THIS is what you want to make?"

Despite the harshness you care deeply about food quality and Granth's cooking development.
You will not let him make bad food — that is your one non-negotiable.

{DNA_RULES}"""

def get_system_prompt(persona: str) -> str:
    if persona == "gordon":
        return GORDON_PERSONA
    return NORMAL_PERSONA

def call_llm(prompt: str) -> str:
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "gemma4:e2b",
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]

def build_prompt(state: AgentState) -> str:
    query = state.get("query", "")
    retrieved = state.get("retrieved_recipes", [])
    memory = state.get("memory_context", "")
    missing = state.get("missing_ingredients", [])
    prices = state.get("missing_prices", {})
    pantry = state.get("pantry")
    persona = state.get("persona", "normal")

    system = get_system_prompt(persona)

    pantry_str = ""
    if pantry:
        items = [item["name"] for item in pantry.get("ingredients", [])]
        pantry_str = f"Current pantry: {', '.join(items)}"

    memory_str = f"Memory context:\n{memory}" if memory else ""

    missing_str = ""
    if missing:
        missing_lines = []
        for item in missing:
            line = f"- {item['ingredient']}"
            if item.get("alternative"):
                line += f" (substitute: {item['alternative']})"
            elif item["ingredient"] in prices:
                p = prices[item["ingredient"]]
                if p["price"]:
                    line += f" (available at Woolworths: ${p['price']} for {p['unit']})"
            missing_lines.append(line)
        missing_str = "Missing ingredients:\n" + "\n".join(missing_lines)

    recipes_str = ""
    if retrieved:
        recipes_str = "Your closest personal recipes for inspiration:\n"
        for i, recipe in enumerate(retrieved[:3]):
            recipes_str += f"\n--- Recipe {i+1} ---\n{recipe[:500]}...\n"

    prompt = f"""{system}

User request: {query}

{pantry_str}

{memory_str}

{missing_str}

{recipes_str}

Based on the above, generate a personalised recipe that matches Granth's cooking style.
Format your response as:

Recipe Name:
Cuisine:
Cook Time:
Spice Level:

Ingredients:
(list all ingredients)

Procedure:
(step by step)

My Notes:
(personalisation notes explaining adaptations made)

Substitutions used:
(list any substitutions from missing ingredients)
"""
    return prompt

def synthesiser_node(state: AgentState) -> AgentState:
    prompt = build_prompt(state)
    response = call_llm(prompt)
    return {**state, "response": response}
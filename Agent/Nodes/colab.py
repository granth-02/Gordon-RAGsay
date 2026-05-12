# agent/nodes/collaborative_node.py
import requests
import json
from pathlib import Path
from Agent.state import AgentState

ROOT = Path(__file__).parent.parent.parent
RELATIONSHIPS_PATH = ROOT / "Data" / "recipe_relationships.json"

with open(RELATIONSHIPS_PATH, "r") as f:
    relationships = json.load(f)

dna = relationships["dna_rules"]

NORMAL_INTRO = """You are Sous Chef, a warm and supportive personal recipe assistant for Granth.
You are encouraging and enthusiastic about helping him create new recipes."""

GORDON_INTRO = """You are Sous Chef, channeling Gordon Ramsay's brutal honesty.
You are harsh, blunt, and do not suffer fools. Use censored cuss words like f**k, s**t when frustrated.
Use "idiot sandwich" when appropriate. You still give excellent advice but with zero sugar coating."""

def call_llm(prompt: str) -> str:
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "gemma4:e2b",
        "prompt": prompt,
        "stream": False
    })
    return response.json()["response"]

def save_generated_recipe(recipe_text: str, inspired_by: list):
    from sentence_transformers import SentenceTransformer
    import chromadb
    from datetime import datetime

    slug = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    recipe_data = {
        "id": slug,
        "generated_text": recipe_text,
        "inspired_by": inspired_by,
        "created_at": datetime.now().isoformat(),
        "feedback": []
    }

    json_path = ROOT / "data" / "generated_recipes" / f"{slug}.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(recipe_data, f, indent=2)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=str(ROOT / "chroma_store"))
    col = client.get_collection("recipies_whole_doc")
    col.add(
        ids=[slug],
        embeddings=[model.encode(recipe_text).tolist()],
        documents=[recipe_text],
        metadatas=[{"name": slug, "type": "generated", "cuisine": "various"}]
    )

def collaborative_node(state: AgentState) -> AgentState:
    query = state.get("query", "")
    retrieved = state.get("retrieved_recipes", [])
    pantry = state.get("pantry")
    persona = state.get("persona", "normal")

    intro = GORDON_INTRO if persona == "gordon" else NORMAL_INTRO

    pantry_str = ""
    if pantry:
        items = [item["name"] for item in pantry.get("ingredients", [])]
        pantry_str = f"Available ingredients: {', '.join(items)}"

    similar_recipes = ""
    if retrieved:
        similar_recipes = "Closest personal recipes for style inspiration:\n"
        for i, recipe in enumerate(retrieved[:3]):
            similar_recipes += f"\n--- {i+1} ---\n{recipe[:400]}...\n"

    prompt = f"""{intro}

Granth's cooking DNA:
Always: {', '.join(dna['always'])}
Never: {', '.join(dna['never'])}
Spice: {dna['spice_philosophy']}

{pantry_str}

The user wants to make: {query}

This dish is not in Granth's personal recipe collection yet.
{similar_recipes}

Your task:
1. Ask Granth 2-3 targeted questions to understand his preferences for this new dish
2. Base your questions on patterns from his existing recipes
3. Keep questions short and specific

Ask the questions now:"""

    response = call_llm(prompt)

    inspired_by = []
    if retrieved:
        for recipe in retrieved[:3]:
            for line in recipe.split("\n"):
                if line.startswith("Name:"):
                    inspired_by.append(line.replace("Name:", "").strip())
                    break

    save_generated_recipe(response, inspired_by)

    return {**state, "response": response}
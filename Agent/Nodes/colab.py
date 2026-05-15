import json
from pathlib import Path
from Agent.state import AgentState
from config import call_llm
from sentence_transformers import SentenceTransformer
import chromadb
from datetime import datetime

ROOT = Path(__file__).parent.parent.parent

def save_generated_recipe(recipe_text: str, recipe_name: str, inspired_by: list):
    slug = f"generated_{recipe_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    recipe_data = {
        "id": slug,
        "name": recipe_name,
        "generated_text": recipe_text,
        "inspired_by": inspired_by,
        "created_at": datetime.now().isoformat(),
        "feedback": []
    }
    json_path = ROOT / "Data" / "generated_recipes" / f"{slug}.json"
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w") as f:
        json.dump(recipe_data, f, indent=2)

    model = SentenceTransformer("all-MiniLM-L6-v2")
    client = chromadb.PersistentClient(path=str(ROOT / "chroma_store"))
    col = client.get_or_create_collection("recipies_generated")
    col.add(
        ids=[slug],
        embeddings=[model.encode(recipe_text).tolist()],
        documents=[recipe_text],
        metadatas=[{
            "name": recipe_name,
            "type": "generated",
            "cuisine": "various",
            "slug": slug
        }]
    )

def collaborative_node(state: AgentState) -> AgentState:
    query = state.get("query", "")
    retrieved = state.get("retrieved_recipes", [])
    pantry = state.get("pantry")
    persona = state.get("persona", "normal")
    history = state.get("chat_history", [])

    persona_str = "Be direct like Gordon Ramsay, no fluff." if persona == "gordon" else "Be helpful and concise."

    pantry_str = ""
    pantry_items = []
    if pantry:
        pantry_items = [item["name"] for item in pantry.get("ingredients", [])]
        pantry_str = f"Available ingredients: {', '.join(pantry_items)}"

    inspiration_str = ""
    inspired_by = []
    if retrieved:
        inspiration_str = "Inspiration from Granth's personal recipes:\n"
        for r in retrieved[:2]:
            # extract recipe name for inspired_by
            for line in r.split("\n"):
                if line.strip().startswith("Name:"):
                    inspired_by.append(line.replace("Name:", "").strip())
                    break
            inspiration_str += f"\n{r[:500]}\n"

    # history context
    history_str = ""
    if history:
        for turn in history[-2:]:
            if isinstance(turn, (list, tuple)) and len(turn) == 2:
                h, a = turn
                clean = str(a).split("---")[0].strip()[:200]
                history_str += f"User: {h}\nAssistant: {clean}\n"

    prompt = f"""You are Gordon RAGsay, Granth's personal recipe assistant. {persona_str}

{history_str}
User request: {query}

{pantry_str}

{inspiration_str}

Generate a NEW recipe that:
1. Uses ONLY the available ingredients listed above
2. Takes inspiration from Granth's personal recipes above for style, technique and flavour
3. Feels like something Granth would cook — his spice levels, his techniques
4. Do NOT add ingredients not in the available list
5. Be concise

Format:
**Recipe:** [name]
**Cuisine:** [type]
**Time:** [cook time]
**Spice:** [X/5]

**Ingredients:** (from available list only)

**Method:** (inspired by Granth's techniques)

**Inspired by:** {', '.join(inspired_by) if inspired_by else 'Granth style'}"""

    response = call_llm(prompt)

    recipe_name = query
    for line in response.split("\n"):
        if "**Recipe:**" in line:
            recipe_name = line.replace("**Recipe:**", "").strip()
            break

    if "**Ingredients:**" in response:
        save_generated_recipe(response, recipe_name, inspired_by)

    return {**state, "response": response}
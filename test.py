from Ingest.ingest import parse_metadata, chunk_sections, chunk_sentences
from Agent.Nodes.router import router
from Agent.Nodes.vision_node import extract_pantry, extract_dish_tags
from Agent.state import AgentState
import chromadb
from sentence_transformers import SentenceTransformer
from pathlib import Path

ROOT = Path(__file__).parent
CHROMA_PATH = str(ROOT / "chroma_store")

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=CHROMA_PATH)

# ── Test 1: retrieval working ──
print("── Test 1: Retrieval ──")
col = client.get_collection("recipies_whole_doc")
embedding = model.encode("spicy indian dinner").tolist()
results = col.query(query_embeddings=[embedding], n_results=3)
for meta in results["metadatas"][0]:
    print(f"  {meta['name']}")

# ── Test 2: router text query ──
print("\n── Test 2: Router (text) ──")
state: AgentState = {
    "query": "I want something spicy for dinner",
    "image": None,
    "image_type": None,
    "pantry": None,
    "dish_tags": None,
    "retrieved_recipes": [],
    "missing_ingredients": None,
    "missing_prices": None,
    "memory_context": None,
    "route": None,
    "response": None
}
result = router(state)
print(f"  Route: {result['route']}")
print(f"  Top recipe: {result['retrieved_recipes'][0][:80]}...")

# ── Test 3: router with image ──
print("\n── Test 3: Router (image) ──")
state_img: AgentState = {
    **state,
    "query": "I have these ingredients what can I make",
    "image": "pantry.jpg"
}
result_img = router(state_img)
print(f"  Route: {result_img['route']}")
print(f"  Image type: {result_img['image_type']}")
print("\n── Test 4: Vision (pantry) ──")
pantry_result = extract_pantry("pantry.jpg")
print(f"  Extracted: {pantry_result}")

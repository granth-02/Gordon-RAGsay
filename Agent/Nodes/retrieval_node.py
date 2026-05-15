from Agent.state import AgentState
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
CHROMA_PATH = str(ROOT / "chroma_store")

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=CHROMA_PATH)

COLLECTIONS = {
    "whole": "recipies_whole_doc",
    "sections": "recipies_sections",
    "sentences": "recipies_sentences"
}

def retrieval_node(state: AgentState) -> AgentState:
    query = state.get("query", "")
    chunk_mode = state.get("chunk_mode", "whole")
    pantry = state.get("pantry")
    dish_tags = state.get("dish_tags")
    route = state.get("route", "")

    existing = state.get("retrieved_recipes", [])
    if existing:
        return state

    if pantry and route == "collaborative":
        items = [item["name"] for item in pantry.get("ingredients", [])]
        retrieval_query = f"recipe using {' '.join(items)}"
    elif dish_tags:
        retrieval_query = f"{dish_tags.get('dish_name', '')} {dish_tags.get('cuisine', '')}"
    else:
        retrieval_query = query

    collection_name = COLLECTIONS.get(chunk_mode, "recipies_whole_doc")
    collection = client.get_collection(collection_name)

    embedding = model.encode(retrieval_query).tolist()
    results = collection.query(
        query_embeddings=[embedding],
        n_results=3,
        include=["documents", "metadatas", "distances"]
    )

    retrieved_docs = results["documents"][0]
    distances = results["distances"][0]
    similarity_scores = [round(1 / (1 + d), 3) for d in distances]

    return {
        **state,
        "retrieved_recipes": retrieved_docs,
        "retrieval_scores": similarity_scores,
        "chunk_mode": chunk_mode
    }
from Agent.state import AgentState
from sentence_transformers import SentenceTransformer
import chromadb
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent
chroma_path = str(ROOT / 'chroma_store')
sim_threshold = 0.6

model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path=chroma_path)
col_whole = client.get_collection("recipies_whole_doc")

pantry_keywords = ["have", "i got", "what can i make", "ingredients", "fridge", "pantry", "using these", "i have"]
dish_keywords = ["recreate", "make this", "what is this", "same as", "like this", "this dish", "saw this", "eaten this"]

def check_image_type(query: str) -> str:
    query_lower = query.lower()
    if any(key_words in query_lower for key_words in pantry_keywords):
        return "pantry"
    if any(key_words in query_lower for key_words in dish_keywords):
        return "dish"

def check_sim(query: str) -> tuple[float, list]:
    embedding = model.encode(query).tolist()
    results = col_whole.query(query_embeddings=[embedding], n_results=3, include=["documents", "metadatas", "distances"])
    top_dist = results["distances"][0][0]

    similarity = 1/(1 + top_dist)
    documents = results["documents"][0]

    return similarity, documents

def router(state: AgentState) -> AgentState:
    image = state.get("image")
    query = state.get("query", "")

    if image:
        image_type = check_image_type(query)
        if image_type == "pantry":
            return {**state, "route": "pantry_image", "image_type": "pantry"}
        else:
            return {**state, "route": "image_query", "image_type": "dish"}
    
    similarity, documents = check_sim(query)

    if similarity >= sim_threshold:
        return {**state, "route": "existing", "retrieved_recipes": documents}
    else:
        return {**state, "route": "collaborative", "retrieved_recipes": documents}
    
    

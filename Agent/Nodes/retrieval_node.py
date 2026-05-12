from Agent.state import AgentState
import chromadb
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent

CHROMA_PATH = str(ROOT / "chroma_store")

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    "recipies_whole_doc"
)

def retrieval_node(state: AgentState) -> AgentState:
    query_embedding = state.get(
        "query_embedding"
    )

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    retrieved_docs = results["documents"][0]

    distances = results["distances"][0]

    similarity_scores = [
        round(1 / (1 + d), 3)
        for d in distances
    ]

    return {
        **state,
        "retrieved_recipes": retrieved_docs,
        "retrieval_scores": similarity_scores
    }
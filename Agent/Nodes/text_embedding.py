from Agent.state import AgentState
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

def text_embedding_node(state: AgentState) -> AgentState:
    hde_document = state.get(
        "hde_document",
        ""
    )

    embedding = model.encode(
        hde_document
    ).tolist()

    return {
        **state,
        "query_embedding": embedding
    }
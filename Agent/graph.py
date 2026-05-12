from langgraph.graph import StateGraph, END
from Agent.state import AgentState
from Agent.Nodes.router import router
from Agent.Nodes.vision_node import vision_node
from Agent.Nodes.query_expansion import query_expansion_node
from Agent.Nodes.hde import hde_node
from Agent.Nodes.retrieval_node import retrieval_node
from Agent.Nodes.reranker import reranker_node
from Agent.Nodes.memory_node import memory_node
from Agent.Nodes.pantry_shield import pantry_shield_node
from Agent.Nodes.woolies import woolworths_node
from Agent.Nodes.synthesiser import synthesiser_node
from Agent.Nodes.colab import collaborative_node

def route_after_router(state: AgentState) -> str:
    return state["route"]

def route_after_reranker(state: AgentState) -> str:
    if state["route"] == "collaborative":
        return "collaborative"
    return "memory"

graph = StateGraph(AgentState)

graph.add_node("router", router)
graph.add_node("vision", vision_node)
graph.add_node("query_expansion", query_expansion_node)
graph.add_node("hde", hde_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("reranker", reranker_node)
graph.add_node("memory", memory_node)
graph.add_node("pantry_shield", pantry_shield_node)
graph.add_node("woolworths", woolworths_node)
graph.add_node("synthesiser", synthesiser_node)
graph.add_node("collaborative", collaborative_node)

graph.set_entry_point("router")

graph.add_conditional_edges("router", route_after_router, {
    "pantry_image": "vision",
    "image_query": "vision",
    "existing": "query_expansion",
    "collaborative": "query_expansion"
})

graph.add_edge("vision", "query_expansion")
graph.add_edge("query_expansion", "hde")
graph.add_edge("hde", "retrieval")
graph.add_edge("retrieval", "reranker")

graph.add_conditional_edges("reranker", route_after_reranker, {
    "collaborative": "collaborative",
    "memory": "memory"
})

graph.add_edge("memory", "pantry_shield")
graph.add_edge("pantry_shield", "woolworths")
graph.add_edge("woolworths", "synthesiser")
graph.add_edge("synthesiser", END)
graph.add_edge("collaborative", END)

app = graph.compile()
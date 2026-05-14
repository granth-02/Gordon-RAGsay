from langgraph.graph import StateGraph, END
from Agent.state import AgentState
from Agent.Nodes.router import router, check_sim
from Agent.Nodes.vision_node import vision_node
from Agent.Nodes.retrieval_node import retrieval_node
from Agent.Nodes.memory_node import memory_node
from Agent.Nodes.pantry_shield import pantry_shield_node
from Agent.Nodes.woolies import woolworths_node
from Agent.Nodes.synthesiser import synthesiser_node
from Agent.Nodes.colab import collaborative_node

def vision_router_node(state: AgentState) -> AgentState:
    image_type = state.get("image_type")

    if image_type == "pantry":
        return {**state, "route": "existing"}

    dish_tags = state.get("dish_tags")
    if dish_tags:
        query = f"{dish_tags.get('dish_name', '')} {dish_tags.get('cuisine', '')}"
        similarity, docs = check_sim(query)
        if similarity >= 0.5:
            return {**state, "route": "existing", "retrieved_recipes": docs}

    return {**state, "route": "collaborative"}

def route_after_router(state: AgentState) -> str:
    return state["route"]

def route_after_retrieval(state: AgentState) -> str:
    if state.get("route") == "collaborative":
        return "collaborative"
    return "memory"

graph = StateGraph(AgentState)

graph.add_node("router", router)
graph.add_node("vision", vision_node)
graph.add_node("vision_router", vision_router_node)
graph.add_node("retrieval", retrieval_node)
graph.add_node("memory", memory_node)
graph.add_node("pantry_shield", pantry_shield_node)
graph.add_node("woolworths", woolworths_node)
graph.add_node("synthesiser", synthesiser_node)
graph.add_node("collaborative", collaborative_node)

graph.set_entry_point("router")

graph.add_conditional_edges("router", route_after_router, {
    "pantry_image": "vision",
    "image_query": "vision",
    "existing": "retrieval",
    "collaborative": "retrieval"
})

graph.add_edge("vision", "vision_router")
graph.add_edge("vision_router", "retrieval")

graph.add_conditional_edges("retrieval", route_after_retrieval, {
    "collaborative": "collaborative",
    "memory": "memory"
})

graph.add_edge("memory", "pantry_shield")
graph.add_edge("pantry_shield", "woolworths")
graph.add_edge("woolworths", "synthesiser")
graph.add_edge("synthesiser", END)
graph.add_edge("collaborative", END)

app = graph.compile()
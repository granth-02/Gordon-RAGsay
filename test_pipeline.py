# test_full_pipeline.py
from Agent.graph import app
from Agent.state import AgentState
from Agent.Nodes.memory_node import save_feedback, get_memory_context

print("── Test 1: Full pipeline — text query normal mode ──")
state: AgentState = {
    "query": "I want something spicy for dinner tonight",
    "image": None,
    "image_type": None,
    "pantry": None,
    "dish_tags": None,
    "retrieved_recipes": [],
    "missing_ingredients": None,
    "missing_prices": None,
    "memory_context": None,
    "route": None,
    "response": None,
    "hde_document": None,
    "query_embedding": None,
    "retrieval_scores": None,
    "persona": "normal"
}
result = app.invoke(state)
print(f"  Route taken: {result['route']}")
print(f"  Response preview: {result['response'][:200]}...")

print("\n── Test 2: Full pipeline — gordon mode ──")
state_gordon: AgentState = {**state, "persona": "gordon"}
result_gordon = app.invoke(state_gordon)
print(f"  Response preview: {result_gordon['response'][:200]}...")

print("\n── Test 3: Full pipeline — with pantry image ──")
state_pantry: AgentState = {
    **state,
    "query": "I have these ingredients what can I make",
    "image": "pantry.jpg",
    "image_type": None,
}
result_pantry = app.invoke(state_pantry)
print(f"  Route taken: {result_pantry['route']}")
print(f"  Pantry extracted: {result_pantry['pantry']}")
print(f"  Response preview: {result_pantry['response'][:200]}...")

print("\n── Test 4: Memory feedback ──")
save_feedback("Dal Tadka", 4, "too salty reduce salt next time")
context = get_memory_context(["Dal Tadka"])
print(f"  Memory context: {context}")

print("\n── Test 5: Memory injected in pipeline ──")
state_memory: AgentState = {**state, "query": "make me dal tadka"}
result_memory = app.invoke(state_memory)
print(f"  Memory context in state: {result_memory['memory_context']}")
print(f"  Response preview: {result_memory['response'][:200]}...")

print("\n── Test 6: Collaborative route ──")
state_collab: AgentState = {
    **state,
    "query": "I want to make beef wellington",
    "persona": "gordon"
}
result_collab = app.invoke(state_collab)
print(f"  Route taken: {result_collab['route']}")
print(f"  Response preview: {result_collab['response'][:200]}...")
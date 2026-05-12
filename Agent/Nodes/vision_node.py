import requests
import base64
import json
from Agent.state import AgentState

PANTRY_PROMPT = """You are a kitchen inventory assistant. Analyse this image of a pantry or ingredients.

For every visible food item extract:
- name: the specific product name (e.g. "basmati rice" not just "rice")
- type: the category (e.g. "grain", "vegetable", "dairy", "spice", "protein", "condiment")

Return ONLY valid JSON in exactly this format, no explanation:
{
  "ingredients": [
    {"name": "basmati rice", "type": "grain"},
    {"name": "garlic", "type": "vegetable"}
  ]
}
Do not wrap the JSON in code fences or markdown. Output raw JSON only.
If you cannot identify an item clearly, skip it."""

DISH_PROMPT = """You are a food recognition assistant. Analyse this image of a dish.

Extract the following information:
- dish_name: what the dish appears to be (e.g. "pasta carbonara", "chicken curry")
- cuisine: cuisine type (e.g. "Italian", "Indian", "Thai", "Mexican")
- meal_type: most likely meal time ("breakfast", "lunch", "dinner", "snack", "dessert")
- has_meat: true or false based on visible meat
- has_paneer: true or false based on visible paneer/cottage cheese
- main_ingredients: list of 3-5 key visible ingredients

Return ONLY valid JSON in exactly this format, no explanation:
{
  "dish_name": "pasta carbonara",
  "cuisine": "Italian",
  "meal_type": "dinner",
  "has_meat": false,
  "has_paneer": false,
  "main_ingredients": ["pasta", "egg", "parmesan"]
}
Do not wrap the JSON in code fences or markdown. Output raw JSON only."""

def call_vision(image_path: str, prompt: str) -> str:
    with open(image_path, "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')
    
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "gemma4:e2b",
        "prompt": prompt,
        "images": [image_data],
        "stream": False
    })

    return response.json()['response']

def extract_pantry(image_path: str) -> dict:
    raw = call_vision(image_path, PANTRY_PROMPT)
    print(f"Raw response: {raw}") 
    try:
        start = raw.find("{")
        end = raw.rfind("}") + 1
        return json.loads(raw[start:end])
    except Exception as e:
        print(f"Parse error: {e}")
        return{"ingredients": []}
    
def extract_dish_tags(image_path: str) -> dict:
    raw = call_vision(image_path, DISH_PROMPT)
    print(f"Raw response: {raw}") 
    try:
        start = raw.find("{")
        end = raw.find("}") + 1
        return json.loads(raw[start:end])
    except Exception:
        return{}

def vision_node(state: AgentState) -> AgentState:
    image = state.get("image")
    image_type = state.get("image_type")

    if not image:
        return state

    if image_type == "pantry":
        pantry = extract_pantry(image)
        return {**state, "pantry": pantry}
    else:
        dish_tags = extract_dish_tags(image)
        return {**state, "dish_tags": dish_tags}
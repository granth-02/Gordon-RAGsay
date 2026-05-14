import gradio as gr
import json
import shutil
import time
from pathlib import Path
from Agent.graph import app
from Agent.state import AgentState
from Agent.Nodes.memory_node import save_feedback

ROOT = Path(__file__).parent
UPLOAD_DIR = ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

last_call_time = 0
MIN_INTERVAL = 2  # seconds between calls — RPM protection

def run_agent(message, history, image, persona):
    global last_call_time
    
    # RPM protection
    elapsed = time.time() - last_call_time
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
    last_call_time = time.time()

    image_path = None
    image_type = None

    if image is not None:
        image_path = str(UPLOAD_DIR / "uploaded_image.jpg")
        shutil.copy(image, image_path)
        pantry_keywords = ["have", "i got", "what can i make", "ingredients",
                          "fridge", "pantry", "using these", "i have"]
        if any(kw in message.lower() for kw in pantry_keywords):
            image_type = "pantry"
        else:
            image_type = "dish"

    state: AgentState = {
        "query": message,
        "image": image_path,
        "image_type": image_type,
        "pantry": None,
        "dish_tags": None,
        "retrieved_recipes": [],
        "missing_ingredients": None,
        "missing_prices": None,
        "memory_context": None,
        "route": None,
        "response": None,
        "retrieval_scores": None,
        "persona": "gordon" if persona == "Gordon Ramsay" else "normal",
        "chunk_mode": None,
        "chat_history": history
    }

    result = app.invoke(state)

    response = result.get("response", "No response generated")
    route = result.get("route", "unknown")
    chunk_used = result.get("chunk_mode", "whole")
    scores = result.get("retrieval_scores", [])
    missing = result.get("missing_ingredients", [])
    prices = result.get("missing_prices", {})

    chunk_labels = {
        "whole": "Whole Document",
        "sections": "Section Chunks",
        "sentences": "Sentence Chunks"
    }

    info_lines = [
        f"Route: {route}",
        f"Chunk mode: {chunk_labels.get(chunk_used, chunk_used)}",
    ]
    if scores:
        info_lines.append(f"Retrieval scores: {[round(s,3) for s in scores[:3]]}")
    if missing:
        missing_names = [m["ingredient"] for m in missing[:5]]
        info_lines.append(f"Missing: {', '.join(missing_names)}")
    if prices:
        price_lines = [f"{k}: ${v['price']}" for k, v in list(prices.items())[:3] if v.get("price")]
        if price_lines:
            info_lines.append(f"Woolworths: {', '.join(price_lines)}")

    info = "\n".join(info_lines)
    full_response = f"{response}\n\n---\n*{info}*"

    return full_response


def save_user_feedback(recipe_name, rating, comment):
    if not recipe_name.strip():
        return "Please enter the recipe name."
    save_feedback(recipe_name.strip(), int(rating), comment)
    return f"Saved — {recipe_name} rated {int(rating)}/5 ⭐"


with gr.Blocks(title="Gordon RAGsay 🍳") as demo:
    gr.Markdown("""
    # 🍳 Gordon RAGsay
    ### Your Personalised Recipe Agent
    *Powered by Gemini + your personal recipe DNA*
    """)

    with gr.Row():
        persona_toggle = gr.Radio(
            choices=["Normal Chef", "Gordon Ramsay"],
            value="Normal Chef",
            label="Chef Persona",
            scale=1
        )
        image_input = gr.Image(
            label="Upload pantry or dish photo (optional)",
            type="filepath",
            scale=2
        )

    gr.ChatInterface(
    fn=run_agent,
    additional_inputs=[image_input, persona_toggle],
    chatbot=gr.Chatbot(height=520),
    textbox=gr.Textbox(
        placeholder="Ask me anything — what to cook, recreate a dish, check your pantry...",
        scale=7
    ),
    submit_btn="🍴 Cook it up!",
)

    gr.Markdown("---")
    gr.Markdown("### 📝 Rate a recipe")
    gr.Markdown("*Rate recipes to help the agent remember your preferences.*")

    with gr.Row():
        feedback_recipe = gr.Textbox(label="Recipe name", scale=2)
        feedback_rating = gr.Slider(minimum=1, maximum=5, step=1, value=3,
                                    label="Rating ⭐", scale=1)

    feedback_comment = gr.Textbox(
        label="Comments",
        placeholder="e.g. too salty, loved the spice level..."
    )
    feedback_btn = gr.Button("💾 Save Feedback")
    feedback_status = gr.Textbox(label="Status", interactive=False)

    feedback_btn.click(
        fn=save_user_feedback,
        inputs=[feedback_recipe, feedback_rating, feedback_comment],
        outputs=[feedback_status]
    )

if __name__ == "__main__":
    demo.launch(share=False)
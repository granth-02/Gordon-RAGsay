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
MIN_INTERVAL = 2

def process_image(image):
    if image is None:
        return None, "No image uploaded"
    image_path = str(UPLOAD_DIR / "uploaded_image.jpg")
    shutil.copy(image, image_path)
    return image_path, "✅ Image stored for this conversation"

def run_agent(message, history, persona, stored_image_path):
    global last_call_time
    elapsed = time.time() - last_call_time
    if elapsed < MIN_INTERVAL:
        time.sleep(MIN_INTERVAL - elapsed)
    last_call_time = time.time()

    image_path = stored_image_path
    image_type = None

    if image_path:
        pantry_keywords = ["have", "i got", "what can i make", "using these",
                          "i have", "fridge", "pantry", "ingredients"]
        image_type = "pantry" if any(kw in message.lower() for kw in pantry_keywords) else "dish"

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

    info_parts = [
        f"Route: {route}",
        f"Chunks: {chunk_labels.get(chunk_used, chunk_used)}"
    ]
    if scores:
        info_parts.append(f"Scores: {[round(s,3) for s in scores[:3]]}")
    if missing:
        info_parts.append(f"Missing: {', '.join([m['ingredient'] for m in missing[:4]])}")
    if prices:
        pl = [f"{k}: ${v['price']}" for k, v in list(prices.items())[:3] if v.get("price")]
        if pl:
            info_parts.append(f"Woolworths: {', '.join(pl)}")

    footer = " | ".join(info_parts)
    return f"{response}\n\n---\n*{footer}*"

def save_user_feedback(recipe_name, rating, comment):
    if not recipe_name.strip():
        return "Please enter the recipe name."
    save_feedback(recipe_name.strip(), int(rating), comment)
    return f"Saved — '{recipe_name}' rated {int(rating)}/5 ⭐"

with gr.Blocks(title="Gordon RAGsay 🍳") as demo:
    gr.Markdown("""
    # 🍳 Gordon RAGsay
    *Your personalised recipe agent — powered by Gemini + your personal recipe DNA*
    """)

    stored_image = gr.State(value=None)

    with gr.Row():
        persona_toggle = gr.Radio(
            choices=["Normal Chef", "Gordon Ramsay"],
            value="Normal Chef",
            label="Persona",
            scale=1
        )
        with gr.Column(scale=2):
            image_input = gr.Image(
                label="Upload pantry or dish photo (stored for whole conversation)",
                type="filepath"
            )
            with gr.Row():
                upload_btn = gr.Button("📸 Store Image", size="sm", variant="primary")
                clear_img_btn = gr.Button("🗑️ Clear Image", size="sm")
            image_status = gr.Textbox(
                value="No image uploaded",
                interactive=False,
                show_label=False,
                lines=1
            )

    upload_btn.click(
        fn=process_image,
        inputs=[image_input],
        outputs=[stored_image, image_status]
    )

    clear_img_btn.click(
        fn=lambda: (None, None, "Image cleared"),
        outputs=[stored_image, image_input, image_status]
    )

    gr.ChatInterface(
        fn=run_agent,
        additional_inputs=[persona_toggle, stored_image],
        chatbot=gr.Chatbot(height=500),
        textbox=gr.Textbox(
            placeholder="What do you want to cook? Ask me anything...",
            scale=7
        ),
        submit_btn="🍴 Cook it up!",
    )

    gr.Markdown("---")
    gr.Markdown("### 📝 Rate a recipe")

    with gr.Row():
        feedback_recipe = gr.Textbox(label="Recipe name", scale=2)
        feedback_rating = gr.Slider(minimum=1, maximum=5, step=1,
                                    value=3, label="Rating ⭐", scale=1)
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
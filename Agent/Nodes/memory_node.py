import sqlite3
from pathlib import Path
from Agent.state import AgentState

ROOT = Path(__file__).parent.parent.parent
DB_PATH = str(ROOT / "Memory" / "feedback.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_name TEXT,
            rating INTEGER,
            comment TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def get_memory_context(recipe_names: list) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    context_lines = []
    for name in recipe_names:
        cursor.execute(
            "SELECT rating, comment FROM feedback WHERE recipe_name=? ORDER BY timestamp DESC LIMIT 1",
            (name,)
        )
        row = cursor.fetchone()
        if row:
            rating, comment = row
            context_lines.append(
                f"Last time you made {name} you rated it {rating}/5 and said: '{comment}'"
            )
    conn.close()
    return "\n".join(context_lines) if context_lines else ""

def save_feedback(recipe_name: str, rating: int, comment: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (recipe_name, rating, comment) VALUES (?, ?, ?)",
        (recipe_name, rating, comment)
    )
    conn.commit()
    conn.close()

def memory_node(state: AgentState) -> AgentState:
    retrieved = state.get("retrieved_recipes", [])
    recipe_names = []
    for recipe_text in retrieved:
        lines = recipe_text.split("\n")
        for line in lines:
            if line.startswith("Name: "):
                recipe_names.append(line.replace("Name: ", "").strip())
                break
    memory_context = get_memory_context(recipe_names)
    return {**state, "memory_context": memory_context}

init_db()
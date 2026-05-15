import subprocess
import sys

def install(packages):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)

print("── Gordon RAGsay Setup ──\n")

# Embeddings and vector store
install(['sentence-transformers', 'chromadb'])

# Agent orchestration
install(['langgraph'])

# Gemini API (new SDK)
install(['google-genai'])

# Utilities
install(['requests', 'pillow'])

# Evaluation
install(['tabulate'])

# UI
install(['gradio'])

print("\n── All dependencies installed ──")
print("\nNext steps:")
print("  1. Add your Gemini API key to config.py")
print("  2. Run: python -m Ingest.ingest")
print("  3. Run: python app.py")
print("  4. Open: http://localhost:7860")
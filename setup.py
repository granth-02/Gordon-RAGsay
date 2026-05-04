import subprocess
import sys

def install(packages):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)

# Embeddings
install(['sentence-transformers', 'chromadb'])

# Agent Orchestration
install(['langgraph'])

# API Handling
install(["python-dotenv", "requests", "beautifulsoup4",])

# Evaluation
install(["google-generativeai", "rouge-score", "numpy", "pandas",])

print("All Dependancies installed")

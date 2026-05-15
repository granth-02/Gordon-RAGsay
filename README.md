# Gordon RAGsay 🍳
### A Personalised Multimodal Recipe Agent
*Powered by Gemini + 47 personal recipes + your cooking DNA*

---

## Requirements

- Python 3.11+
- Gemini API key — free tier at https://aistudio.google.com
- Internet connection (for Gemini API and Woolworths price fetching)

---

## Installation

### 1. Clone the repository
```bash
git clone <repo-url>
cd "Gordon RAGsay"
```

### 2. Run the setup script
```bash
python setup.py
```

### 3. Add your Gemini API key
Open `config.py` and replace:
```python
client = genai.Client(api_key="YOUR_GEMINI_API_KEY")
```

### 4. Ingest recipes into ChromaDB
```bash
python -m Ingest.ingest
```
This builds three vector collections from the 47 personal recipe TXT files.
Only needs to be run once.

### 5. Launch the app
```bash
python app.py
```
Open `http://localhost:7860` in your browser.

---

## Usage

- Type any cooking question in the chat
- Upload a pantry photo to get recipe suggestions from what you have
- Upload a dish photo to recreate it in your personal style
- Toggle between **Normal Chef** and **Gordon Ramsay** persona
- Rate recipes using the feedback form — ratings are remembered across sessions

---

## Running the Evaluation

```bash
# Add test images first
mkdir eval/test_images
# Copy pantry.jpg and pasta.jpg into eval/test_images/

# Run chunking ablation across all 4 conditions
python -m eval.run_eval

# Run LLM judge scoring
python -m eval.llm_judge

# Run baseline comparison
python -m eval.baseline_comparison

# Compare agent vs baseline
python -m eval.baseline_comparison compare
```

Results cache to `eval/results/` — re-running metrics does not consume API quota.

---

## Project Structure

```
Gordon RAGsay/
├── Data/
│   ├── Recipies/              # 47 personal recipe TXT files
│   ├── recipe_relationships.json
│   ├── glossary.json
│   └── generated_recipes/
├── chroma_store/              # Vector DB (auto-created by ingest)
├── memory/
│   └── feedback.db            # SQLite feedback store
├── Agent/
│   ├── state.py
│   ├── graph.py
│   └── Nodes/
│       ├── router.py
│       ├── vision_node.py
│       ├── retrieval_node.py
│       ├── memory_node.py
│       ├── pantry_shield.py
│       ├── woolies.py
│       ├── synthesiser.py
│       └── colab.py
├── Ingest/
│   └── ingest.py
├── eval/
│   ├── test_queries.py
│   ├── metrics.py
│   ├── run_eval.py
│   ├── llm_judge.py
│   └── baseline_comparison.py
├── app.py
├── config.py
├── setup.py
└── requirements.txt
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `google-genai` | Gemini API — LLM and vision |
| `sentence-transformers` | Local embeddings (all-MiniLM-L6-v2) |
| `chromadb` | Vector database |
| `langgraph` | Agent orchestration |
| `gradio` | Web UI |
| `requests` | Woolworths API calls |
| `pillow` | Image processing |
| `numpy` / `pandas` / `tabulate` | Evaluation metrics |
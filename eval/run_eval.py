import sys
import os
import json
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from eval.test_queries import TEST_QUERIES
from eval.metrics import (
    recall_at_k, mrr, keyword_match_score,
    dna_compliance_score, chunk_mode_accuracy, measure_latency
)
from Agent.graph import app
from Agent.state import AgentState

RESULTS_DIR = ROOT / "eval" / "results"
RESULTS_DIR.mkdir(exist_ok=True)
CACHE_FILE = RESULTS_DIR / "raw_results.json"

CHUNK_MODES = ["whole", "sections", "sentences", "dynamic"]

def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)

def run_query(query_dict: dict, chunk_mode: str) -> dict:
    query = query_dict["query"]
    image_path = query_dict.get("image_path")

    image_type = None
    if image_path:
        pantry_keywords = ["have", "i got", "what can i make", "ingredients",
                          "fridge", "pantry", "using these", "i have", "with these"]
        image_type = "pantry" if any(kw in query.lower() for kw in pantry_keywords) else "dish"

    state: AgentState = {
        "query": query,
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
        "persona": "normal",
        "chunk_mode": None if chunk_mode == "dynamic" else chunk_mode,
        "chat_history": []
    }

    result, latency = measure_latency(app.invoke, state)

    return {
        "response": result.get("response", ""),
        "route": result.get("route", ""),
        "chunk_mode_used": result.get("chunk_mode", "whole"),
        "retrieval_scores": result.get("retrieval_scores", []),
        "retrieved_recipes": result.get("retrieved_recipes", []),
        "latency": latency
    }

def extract_recipe_names(retrieved: list) -> list:
    names = []
    for recipe_text in retrieved:
        for line in recipe_text.split("\n"):
            if line.strip().startswith("Name:"):
                names.append(line.replace("Name:", "").strip())
                break
    return names

def run_evaluation():
    cache = load_cache()
    all_results = {}

    print("\n── Gordon RAGsay Evaluation ──\n")

    for chunk_mode in CHUNK_MODES:
        print(f"\nRunning condition: {chunk_mode.upper()}")
        mode_results = []

        for q in TEST_QUERIES:
            cache_key = f"{q['id']}_{chunk_mode}"

            if cache_key in cache:
                print(f"  [cached] {q['id']} — {q['family']}")
                result_data = cache[cache_key]
            else:
                print(f"  [running] {q['id']} — {q['family']} — {q['query'][:50]}...")
                try:
                    result_data = run_query(q, chunk_mode)
                    cache[cache_key] = result_data
                    save_cache(cache)
                    time.sleep(2)  # RPM protection
                except Exception as e:
                    print(f"  ERROR: {e}")
                    result_data = {
                        "response": "", "route": "error",
                        "chunk_mode_used": chunk_mode,
                        "retrieval_scores": [], "retrieved_recipes": [],
                        "latency": 0
                    }

            # compute metrics
            retrieved_names = extract_recipe_names(result_data.get("retrieved_recipes", []))
            response = result_data.get("response", "")
            
            r_at_k = recall_at_k(retrieved_names, q.get("expected_recipe"), k=3)
            mrr_score = mrr(retrieved_names, q.get("expected_recipe"))
            kw_score = keyword_match_score(response, q.get("ground_truth_keywords", []))
            dna_score = dna_compliance_score(response)
            chunk_acc = chunk_mode_accuracy(
                result_data.get("chunk_mode_used", ""), 
                q.get("expected_chunk_mode", "")
            )

            mode_results.append({
                "id": q["id"],
                "family": q["family"],
                "recall_at_3": r_at_k,
                "mrr": mrr_score,
                "keyword_match": kw_score,
                "dna_compliance": dna_score,
                "chunk_accuracy": chunk_acc,
                "latency": result_data.get("latency", 0),
                "chunk_mode_used": result_data.get("chunk_mode_used", "")
            })

        all_results[chunk_mode] = mode_results

    # print summary table
    print_summary(all_results)
    
    # save full results
    with open(RESULTS_DIR / "eval_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\nResults saved to eval/results/eval_results.json")

def print_summary(all_results: dict):
    try:
        from tabulate import tabulate
    except ImportError:
        print("Install tabulate: pip install tabulate")
        return

    metrics = ["recall_at_3", "mrr", "keyword_match", "dna_compliance", 
               "chunk_accuracy", "latency"]
    labels = ["Recall@3", "MRR", "Keyword Match", "DNA Compliance", 
              "Chunk Accuracy", "Avg Latency(s)"]

    print("\n── Overall Results ──")
    table = []
    for metric, label in zip(metrics, labels):
        row = [label]
        for mode in CHUNK_MODES:
            results = all_results.get(mode, [])
            if results:
                avg = round(sum(r.get(metric, 0) for r in results) / len(results), 3)
                row.append(avg)
            else:
                row.append("N/A")
        table.append(row)

    print(tabulate(table, 
                  headers=["Metric"] + [m.upper() for m in CHUNK_MODES],
                  tablefmt="grid"))

    # breakdown by family
    print("\n── Recall@3 by Query Family ──")
    families = ["factual", "cross_modal", "analytical", "conversational"]
    family_table = []
    for family in families:
        row = [family.replace("_", " ").title()]
        for mode in CHUNK_MODES:
            results = [r for r in all_results.get(mode, []) if r["family"] == family]
            if results:
                avg = round(sum(r["recall_at_3"] for r in results) / len(results), 3)
                row.append(avg)
            else:
                row.append("N/A")
        family_table.append(row)

    print(tabulate(family_table,
                  headers=["Family"] + [m.upper() for m in CHUNK_MODES],
                  tablefmt="grid"))

if __name__ == "__main__":
    run_evaluation()
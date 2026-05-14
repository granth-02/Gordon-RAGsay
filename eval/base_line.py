import sys
import json
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from config import call_llm
from eval.metrics import keyword_match_score, dna_compliance_score
from eval.test_queries import TEST_QUERIES

RESULTS_DIR = ROOT / "eval" / "results"
BASELINE_FILE = RESULTS_DIR / "baseline_results.json"

def run_baseline():
    baseline = {}
    print("\n── Running Baseline (Plain Gemini, no RAG) ──\n")

    for q in TEST_QUERIES:
        if q.get("image_path"):
            print(f"  [skip] {q['id']} — image query, baseline is text only")
            continue

        print(f"  Running: {q['id']} — {q['query'][:50]}...")
        
        # plain Gemini — no system prompt, no DNA, no retrieved recipes
        prompt = f"User: {q['query']}\n\nPlease help with this cooking question."
        
        try:
            response = call_llm(prompt)
            baseline[q["id"]] = {
                "query": q["query"],
                "family": q["family"],
                "response": response,
                "expected_recipe": q.get("expected_recipe"),
                "keywords": q.get("ground_truth_keywords", [])
            }
            time.sleep(2)
        except Exception as e:
            print(f"  ERROR: {e}")

    with open(BASELINE_FILE, "w") as f:
        json.dump(baseline, f, indent=2)

    print(f"\nBaseline saved to eval/results/baseline_results.json")

def compare():
    if not BASELINE_FILE.exists():
        print("Run baseline first.")
        return

    agent_file = RESULTS_DIR / "raw_results.json"
    if not agent_file.exists():
        print("Run run_eval.py first.")
        return

    with open(BASELINE_FILE) as f:
        baseline = json.load(f)
    with open(agent_file) as f:
        agent_cache = json.load(f)

    print("\n── Baseline vs Agent (Dynamic) ──\n")
    
    rows = []
    agent_wins = 0
    baseline_wins = 0

    for qid, b_data in baseline.items():
        agent_key = f"{qid}_dynamic"
        if agent_key not in agent_cache:
            continue

        a_data = agent_cache[agent_key]
        keywords = b_data.get("keywords", [])

        b_kw = keyword_match_score(b_data["response"], keywords)
        a_kw = keyword_match_score(a_data["response"], keywords)
        b_dna = dna_compliance_score(b_data["response"])
        a_dna = dna_compliance_score(a_data["response"])

        winner = "AGENT" if (a_kw + a_dna) > (b_kw + b_dna) else "BASELINE"
        if winner == "AGENT":
            agent_wins += 1
        else:
            baseline_wins += 1

        rows.append([
            qid, b_data["family"][:8],
            round(b_kw, 2), round(a_kw, 2),
            round(b_dna, 2), round(a_dna, 2),
            winner
        ])

    try:
        from tabulate import tabulate
        print(tabulate(rows,
            headers=["ID", "Family", "Base KW", "Agent KW", 
                    "Base DNA", "Agent DNA", "Winner"],
            tablefmt="grid"))
    except ImportError:
        for row in rows:
            print(row)

    total = agent_wins + baseline_wins
    print(f"\nAgent wins: {agent_wins}/{total} ({round(agent_wins/total*100)}%)")
    print(f"Baseline wins: {baseline_wins}/{total} ({round(baseline_wins/total*100)}%)")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        compare()
    else:
        run_baseline()
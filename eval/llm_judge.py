import sys
import json
import time
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from config import call_llm

RESULTS_DIR = ROOT / "eval" / "results"
JUDGE_FILE = RESULTS_DIR / "judge_scores.json"

JUDGE_PROMPT = """You are evaluating a personalised recipe assistant response.

Query: {query}
Expected recipe: {expected}
Response: {response}

Score the response on these criteria (1-5 each):
- relevance: does it address the query directly
- accuracy: is the recipe information correct and plausible
- personalisation: does it feel personalised (garlic, spice levels, yogurt, etc)
- groundedness: is it grounded in actual recipe knowledge or hallucinated
- conciseness: is it appropriately concise without padding

Return ONLY valid JSON:
{{
  "relevance": 0,
  "accuracy": 0,
  "personalisation": 0,
  "groundedness": 0,
  "conciseness": 0,
  "overall": 0,
  "reasoning": "one sentence"
}}"""

def judge_response(query: str, response: str, expected_recipe: str) -> dict:
    prompt = JUDGE_PROMPT.format(
        query=query,
        expected=expected_recipe or "any relevant recipe",
        response=response[:1000]
    )
    try:
        raw = call_llm(prompt)
        raw = raw.replace("```json", "").replace("```", "").strip()
        start = raw.find("{")
        end = raw.rfind("}") + 1
        scores = json.loads(raw[start:end])
        scores["overall"] = round(sum([
            scores.get("relevance", 3),
            scores.get("accuracy", 3),
            scores.get("personalisation", 3),
            scores.get("groundedness", 3),
            scores.get("conciseness", 3)
        ]) / 5, 2)
        return scores
    except Exception:
        return {
            "relevance": 3, "accuracy": 3, "personalisation": 3,
            "groundedness": 3, "conciseness": 3, "overall": 3,
            "reasoning": "parse error — default scores"
        }

def run_llm_judge():
    cache_file = RESULTS_DIR / "raw_results.json"
    if not cache_file.exists():
        print("No raw_results.json found. Run run_eval.py first.")
        return

    with open(cache_file) as f:
        cache = json.load(f)

    from eval.test_queries import TEST_QUERIES
    query_map = {q["id"]: q for q in TEST_QUERIES}

    judge_scores = {}
    print("\n── LLM Judge Evaluation ──\n")

    for cache_key, result_data in cache.items():
        query_id = cache_key.rsplit("_", 1)[0]
        condition = cache_key.rsplit("_", 1)[1]
        
        if query_id not in query_map:
            continue

        q = query_map[query_id]
        response = result_data.get("response", "")

        if not response:
            continue

        print(f"  Judging: {cache_key}")
        scores = judge_response(q["query"], response, q.get("expected_recipe"))
        judge_scores[cache_key] = {
            "query_id": query_id,
            "condition": condition,
            "family": q["family"],
            "scores": scores
        }
        time.sleep(2)

    with open(JUDGE_FILE, "w") as f:
        json.dump(judge_scores, f, indent=2)

    print("\n── Judge Scores by Condition ──")
    for condition in ["whole", "sections", "sentences", "dynamic"]:
        cond_scores = [v["scores"] for v in judge_scores.values() 
                      if v["condition"] == condition]
        if cond_scores:
            avg_overall = round(sum(s["overall"] for s in cond_scores) / len(cond_scores), 2)
            avg_personal = round(sum(s["personalisation"] for s in cond_scores) / len(cond_scores), 2)
            print(f"  {condition.upper()}: overall={avg_overall}/5 | personalisation={avg_personal}/5")

    print(f"\nJudge scores saved to eval/results/judge_scores.json")

if __name__ == "__main__":
    run_llm_judge()
import time
import re

def recall_at_k(retrieved_names: list, expected_name: str, k: int = 3) -> float:
    if not expected_name or not retrieved_names:
        return 0.0
    top_k = retrieved_names[:k]
    expected_lower = expected_name.lower()
    for name in top_k:
        if expected_lower in str(name).lower() or str(name).lower() in expected_lower:
            return 1.0
    return 0.0

def mrr(retrieved_names: list, expected_name: str) -> float:
    if not expected_name or not retrieved_names:
        return 0.0
    expected_lower = expected_name.lower()
    for i, name in enumerate(retrieved_names):
        if expected_lower in str(name).lower() or str(name).lower() in expected_lower:
            return 1.0 / (i + 1)
    return 0.0

def keyword_match_score(response: str, keywords: list) -> float:
    if not keywords or not response:
        return 0.0
    response_lower = response.lower()
    matched = sum(1 for kw in keywords if kw.lower() in response_lower)
    return round(matched / len(keywords), 3)

def dna_compliance_score(response: str) -> float:
    if not response:
        return 0.0
    r = response.lower()
    score = 0.0
    checks = [
        ("garlic", 0.1),
        ("lemon", 0.1),
        ("whole wheat", 0.1),
        ("yogurt", 0.1),
        ("vegetable", 0.1),
        ("spice", 0.1),
        ("protein", 0.1),
        ("healthy", 0.05),
        ("fresh", 0.05),
        ("olive oil", 0.1),
    ]
    for keyword, weight in checks:
        if keyword in r:
            score += weight
    # penalise milk chocolate
    if "milk chocolate" in r:
        score -= 0.1
    return round(min(max(score, 0.0), 1.0), 3)

def ingredient_utilisation_rate(response: str, pantry_items: list) -> float:
    if not pantry_items or not response:
        return 0.0
    response_lower = response.lower()
    # find ingredients section in response
    ingredients_section = response_lower
    if "ingredients:" in response_lower:
        start = response_lower.find("ingredients:")
        end = response_lower.find("method:", start)
        if end == -1:
            end = response_lower.find("procedure:", start)
        if end != -1:
            ingredients_section = response_lower[start:end]

    pantry_lower = [item.lower() for item in pantry_items]
    found = sum(1 for item in pantry_lower if item in ingredients_section)
    total_words = len([w for w in ingredients_section.split("\n") 
                      if w.strip() and not w.strip().startswith("**")])
    
    if total_words == 0:
        return 0.0
    return round(found / max(total_words, len(pantry_lower)), 3)

def chunk_mode_accuracy(predicted: str, expected: str) -> float:
    if not expected:
        return 1.0  # no expectation — always correct
    return 1.0 if predicted == expected else 0.0

def measure_latency(func, *args, **kwargs):
    start = time.time()
    result = func(*args, **kwargs)
    latency = round(time.time() - start, 3)
    return result, latency
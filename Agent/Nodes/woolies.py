import requests
from Agent.state import AgentState

WOOLIES_URL = "https://www.woolworths.com.au/apis/ui/Search/products"
PRICE_WORDS = ["price", "cost", "how much", "woolworths", "buy", "afford"]

def is_price_query(query: str) -> bool:
    return any(kw in query.lower() for kw in PRICE_WORDS)

def get_price(ingredient: str) -> dict:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        params = {"searchTerm": ingredient, "pageSize": 3, "pageNumber": 1}
        r = requests.get(WOOLIES_URL, params=params, headers=headers, timeout=5)
        products = r.json()["Products"][0]["Products"]
        return {
            "name": products[0]["Name"],
            "price": products[0]["Price"],
            "unit": products[0]["PackageSize"]
        }
    except Exception:
        return {"name": ingredient, "price": None, "unit": None}

def woolworths_node(state: AgentState) -> AgentState:
    query = state.get("query", "")

    if not is_price_query(query):
        return state

    missing = state.get("missing_ingredients", [])
    prices = {}

    if missing:
        # fetch prices for missing ingredients
        for item in missing:
            ing = item.get("ingredient", "")
            if ing and not item.get("alternative"):
                prices[ing] = get_price(ing)
    else:
        # no missing list — extract ingredient from query directly
        # e.g. "fetch price of chicken breast"
        words = query.lower()
        skip = ["price", "cost", "fetch", "get", "me", "the", "of", "at",
                "woolworths", "how", "much", "is", "a", "can", "you", "please"]
        ingredient = " ".join([w for w in words.split() if w not in skip]).strip()
        if ingredient:
            prices[ingredient] = get_price(ingredient)

    return {**state, "missing_prices": prices}
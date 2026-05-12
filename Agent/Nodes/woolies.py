import requests
from Agent.state import AgentState

WOOLIES_URL = "https://www.woolworths.com.au/apis/ui/Search/products"

def get_price(ingredient: str) -> dict:
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        params = {"searchTerm": ingredient, "pageSize": 3, "pageNumber": 1}
        response = requests.get(WOOLIES_URL, params=params, headers=headers, timeout=5)
        products = response.json()["Products"][0]["Products"]
        return {
            "name": products[0]["Name"],
            "price": products[0]["Price"],
            "unit": products[0]["PackageSize"]
        }
    except Exception:
        return {"name": ingredient, "price": None, "unit": None}

def woolworths_node(state: AgentState) -> AgentState:
    missing = state.get("missing_ingredients", [])
    if not missing:
        return state

    prices = {}
    for item in missing:
        ingredient = item["ingredient"]
        if not item.get("alternative"):
            price_info = get_price(ingredient)
            prices[ingredient] = price_info

    return {**state, "missing_prices": prices}
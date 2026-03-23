import requests
import os
from dotenv import load_dotenv

load_dotenv()

ITAD_API_KEY = os.getenv("ITAD_API_KEY")

# ITAD numeric shop IDs
PLATFORM_SHOPS = {
    "ps":    [183, 184],  # PSN PS4=183, PS5=184
    "steam": [61],        # Steam
    "xbox":  [185, 186],  # Xbox One=185, Xbox Series X=186
}

PLATFORM_LABELS = {
    "ps":    "PlayStation",
    "steam": "Steam",
    "xbox":  "Xbox",
}


def _searchGame(game_title: str) -> str | None:
    """Search ITAD for a game and return its ITAD ID."""
    try:
        url = "https://api.isthereanydeal.com/games/search/v1"
        params = {
            "key":   ITAD_API_KEY,
            "title": game_title,
            "limit": 1,
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return None

        return data[0].get("id")

    except Exception as e:
        print(f"[ERROR] ITAD search failed for '{game_title}': {e}")
        return None


def _getGamePrice(game_id: str, shops: list[int]) -> dict | None:
    try:
        url = "https://api.isthereanydeal.com/games/prices/v3"
        params = {
            "key":     ITAD_API_KEY,
            "country": "US",
        }
        resp = requests.post(url, params=params, json=[game_id], timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return None

        game_data = data[0]
        deals = game_data.get("deals", [])

        print(f"[DEBUG] Game ID {game_id} has {len(deals)} deals, looking for shops {shops}")
        for deal in deals:
            shop_id = deal.get("shop", {}).get("id")
            cut     = deal.get("price", {}).get("cut", 0)
            print(f"[DEBUG] Shop ID: {shop_id}, cut: {cut}")
            if shop_id in shops and cut > 0:
                regular   = deal.get("regular", {}).get("amount", 0)
                sale      = deal.get("price", {}).get("amount", 0)
                url_buy   = deal.get("url", "")
                shop_name = deal.get("shop", {}).get("name", str(shop_id))
                return {
                    "sale_price":    f"${sale:.2f}",
                    "regular_price": f"${regular:.2f}",
                    "discount":      str(cut),
                    "url":           url_buy,
                    "shop":          shop_name,
                }
        return None
    except Exception as e:
        print(f"[ERROR] ITAD price fetch failed for game ID '{game_id}': {e}")
        return None

def fetchDealsForWishlist(wishlist: list[str], platforms: list[str]) -> list[dict]:
    """
    Search ITAD for each wishlist game on each platform.
    Returns only games that are currently on sale.
    """
    matched = []
    supported = [p for p in platforms if p in PLATFORM_SHOPS]

    if not supported or not wishlist:
        return []

    for platform in supported:
        shops = PLATFORM_SHOPS[platform]
        print(f"[→] Checking {PLATFORM_LABELS[platform]} for {len(wishlist)} games...")

        for game in wishlist:
            game_id = _searchGame(game)
            if not game_id:
                print(f"[✗] Not found on ITAD: {game}")
                continue

            deal = _getGamePrice(game_id, shops)
            if deal:
                matched.append({
                    "name":           game,
                    "sale_price":     deal["sale_price"],
                    "regular_price":  deal["regular_price"],
                    "discount":       deal["discount"],
                    "url":            deal["url"],
                    "platform":       platform,
                    "platform_label": PLATFORM_LABELS[platform],
                    "shop":           deal["shop"],
                })
                print(f"[✓] On sale: {game} on {deal['shop']} — {deal['sale_price']} ({deal['discount']}% OFF)")
            else:
                print(f"[✗] Not on sale: {game} on {PLATFORM_LABELS[platform]}")

    print(f"[✓] Total matches found: {len(matched)}")
    return matched


#def _searchPSGame(game_title: str) -> dict | None:
    """Search PlayStation Store directly for a game and check if on sale."""
    try:
        query = game_title.replace(" ", "%20")
        url = f"https://store.playstation.com/en-us/search/{query}"
        
        # Use Sony's internal search API
        api_url = "https://web.np.playstation.com/api/graphql/v1/op"
        params = {
            "operationName": "getSearchResults",
            "variables": json.dumps({
                "searchTerm": game_title,
                "pageSize": 1,
                "pageOffset": 0,
                "countryCode": "US",
                "languageCode": "en"
            }),
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "x-psn-correlation-id": "search"
        }
        resp = requests.get(api_url, params=params, headers=headers, timeout=10)
        data = resp.json()
        # parse price and discount from response
        ...
    except Exception as e:
        print(f"[ERROR] PS search failed for '{game_title}': {e}")
        return None

# ── Backwards compatibility ────────────────────────────────────────────────────

def fetchDealsForPlatforms(platforms: list[str]) -> list[dict]:
    """Legacy function — no longer used, use fetchDealsForWishlist instead."""
    print("[WARN] fetchDealsForPlatforms called — use fetchDealsForWishlist instead.")
    return []


def fetchPsDeals() -> list[dict]:
    """Legacy function — no longer used."""
    return []


def filterWishlistDeals(deals: list[dict], wishlist: list[str]) -> list[dict]:
    """Legacy filter — returns deals as-is since fetchDealsForWishlist already filters."""
    return deals
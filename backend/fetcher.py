import requests
import os
from dotenv import load_dotenv

load_dotenv()

ITAD_API_KEY = os.getenv("ITAD_API_KEY", "YOUR_ITAD_API_KEY_HERE")

PLATFORM_SHOPS = {
    "ps":    ["ps5", "ps4"],
    "steam": ["steam"],
    "xbox":  ["xboxone", "xbox360"],
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


def _getGamePrice(game_id: str, shops: list[str]) -> dict | None:
    """Get current price for a game on specific shops, returns deal if on sale."""
    try:
        url = "https://api.isthereanydeal.com/games/prices/v3"
        params = {
            "key":     ITAD_API_KEY,
            "country": "US",
        }
        body = [game_id]
        resp = requests.post(url, params=params, json=body, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if not data:
            return None

        game_data = data[0]
        deals = game_data.get("deals", [])

        # Filter to only deals from our target shops
        for deal in deals:
            shop_id = deal.get("shop", {}).get("id", "")
            if shop_id in shops and deal.get("price", {}).get("cut", 0) > 0:
                regular = deal.get("regular", {}).get("amount", 0)
                sale    = deal.get("price", {}).get("amount", 0)
                cut     = deal.get("price", {}).get("cut", 0)
                url_buy = deal.get("url", "")
                shop_name = deal.get("shop", {}).get("name", shop_id)

                return {
                    "sale_price":     f"${sale:.2f}",
                    "regular_price":  f"${regular:.2f}",
                    "discount":       str(cut),
                    "url":            url_buy,
                    "shop":           shop_name,
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
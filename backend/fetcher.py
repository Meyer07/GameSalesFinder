import requests
import os
from dotenv import load_dotenv

load_dotenv()

ITAD_API_KEY = os.getenv("ITAD_API_KEY")

PLATFORM_LABELS = {
    "ps":    "PlayStation",
    "steam": "Steam",
    "xbox":  "Xbox",
}


# ── Steam via ITAD ─────────────────────────────────────────

def _searchSteamGame(game_title: str) -> str | None:
    """Search ITAD for a game and return its ITAD ID."""
    try:
        resp = requests.get(
            "https://api.isthereanydeal.com/games/search/v1",
            params={"key": ITAD_API_KEY, "title": game_title, "limit": 1},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        return data[0].get("id") if data else None
    except Exception as e:
        print(f"[ERROR] ITAD search failed for '{game_title}': {e}")
        return None


def _getSteamPrice(game_id: str) -> dict | None:
    """Get current Steam price for a game from ITAD."""
    try:
        resp = requests.post(
            "https://api.isthereanydeal.com/games/prices/v3",
            params={"key": ITAD_API_KEY, "country": "US"},
            json=[game_id],
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            return None

        for deal in data[0].get("deals", []):
            shop_id = deal.get("shop", {}).get("id")
            cut     = deal.get("price", {}).get("cut", 0)
            if shop_id == 61 and cut > 0:  # 61 = Steam
                return {
                    "sale_price":    f"${deal['price']['amount']:.2f}",
                    "regular_price": f"${deal['regular']['amount']:.2f}",
                    "discount":      str(cut),
                    "url":           deal.get("url", ""),
                    "shop":          "Steam",
                }
        return None
    except Exception as e:
        print(f"[ERROR] ITAD price fetch failed for '{game_id}': {e}")
        return None


def _fetchSteamDeals(wishlist: list[str]) -> list[dict]:
    """Check Steam deals for wishlist games via ITAD."""
    matched = []
    print(f"[→] Checking Steam for {len(wishlist)} games via ITAD...")
    for game in wishlist:
        game_id = _searchSteamGame(game)
        if not game_id:
            print(f"[✗] Not found on ITAD: {game}")
            continue
        deal = _getSteamPrice(game_id)
        if deal:
            matched.append({
                "name":           game,
                "sale_price":     deal["sale_price"],
                "regular_price":  deal["regular_price"],
                "discount":       deal["discount"],
                "url":            deal["url"],
                "platform":       "steam",
                "platform_label": "Steam",
            })
            print(f"[✓] On sale: {game} on Steam — {deal['sale_price']} ({deal['discount']}% OFF)")
        else:
            print(f"[✗] Not on sale: {game} on Steam")
    return matched


# ── PS / Xbox via database ─────────────────────────────────

def _fetchDatabaseDeals(wishlist: list[str], platform: str) -> list[dict]:
    """Check PS or Xbox deals for wishlist games from our database."""
    from database import SessionLocal
    import models

    matched = []
    label   = PLATFORM_LABELS.get(platform, platform)
    print(f"[→] Checking {label} for {len(wishlist)} games via database...")

    db = SessionLocal()
    try:
        for game in wishlist:
            deal = db.query(models.StoreDeal).filter(
                models.StoreDeal.platform   == platform,
                models.StoreDeal.game_title.ilike(f"%{game}%")
            ).first()

            if deal:
                matched.append({
                    "name":           deal.game_title,
                    "sale_price":     deal.sale_price,
                    "regular_price":  deal.regular_price,
                    "discount":       deal.discount,
                    "url":            deal.url or "",
                    "platform":       platform,
                    "platform_label": label,
                    "sale_end_date":  deal.sale_end_date or "",
                })
                print(f"[✓] On sale: {deal.game_title} on {label} — {deal.sale_price} ({deal.discount}% OFF)")
            else:
                print(f"[✗] Not on sale: {game} on {label}")
    finally:
        db.close()

    return matched


# ── Main entry point ───────────────────────────────────────

def fetchDealsForWishlist(wishlist: list[str], platforms: list[str]) -> list[dict]:
    """
    Fetch deals for wishlist games across platforms.
    - Steam: uses ITAD API
    - PS / Xbox: queries our own database
    """
    matched = []

    for platform in platforms:
        if platform == "steam":
            matched.extend(_fetchSteamDeals(wishlist))
        elif platform in ("ps", "xbox"):
            matched.extend(_fetchDatabaseDeals(wishlist, platform))
        else:
            print(f"[WARN] Unknown platform: {platform}")

    print(f"[✓] Total matches found: {len(matched)}")
    return matched


# ── Backwards compatibility ────────────────────────────────

def fetchDealsForPlatforms(platforms: list[str]) -> list[dict]:
    print("[WARN] fetchDealsForPlatforms is deprecated — use fetchDealsForWishlist.")
    return []

def fetchPsDeals() -> list[dict]:
    return []

def filterWishlistDeals(deals: list[dict], wishlist: list[str]) -> list[dict]:
    return deals
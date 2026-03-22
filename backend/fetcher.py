import time
from playwright.sync_api import sync_playwright

PLATFORM_FILTERS = {
    "ps":    "ps4,ps5",
    "steam": "steam",
    "xbox":  "xbox-one,xbox-series-x",
}

PLATFORM_LABELS = {
    "ps":    "PlayStation",
    "steam": "Steam",
    "xbox":  "Xbox",
}


def _searchGame(page, game_title: str, platform_key: str) -> dict | None:
    """Search DekuDeals for a specific game on a specific platform and check if it's on sale."""
    try:
        platform_filter = PLATFORM_FILTERS[platform_key]
        query = game_title.replace(" ", "+")
        url = f"https://www.dekudeals.com/search?q={query}&filter[platform]={platform_filter}&filter[discount]=discounted"

        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000)

        result = page.evaluate("""
            () => {
                // Try list view first
                const firstItem = document.querySelector('.col.d-block');
                if (firstItem) {
                    const titleEl    = firstItem.querySelector('a.main-link h6');
                    const linkEl     = firstItem.querySelector('a.main-link');
                    const priceEl    = firstItem.querySelector('strong');
                    const originalEl = firstItem.querySelector('s.text-muted');
                    const discountEl = firstItem.querySelector('span.badge-danger');
                    if (titleEl && priceEl) {
                        return {
                            name:     titleEl.innerText.trim(),
                            url:      linkEl ? linkEl.href : '',
                            price:    priceEl.innerText.trim(),
                            original: originalEl ? originalEl.innerText.trim() : 'N/A',
                            discount: discountEl ? discountEl.innerText.trim().replace('%','').replace('-','') : '?'
                        };
                    }
                }
                return null;
            }
        """)

        if result:
            return {
                "name":           result["name"],
                "sale_price":     result["price"],
                "regular_price":  result["original"],
                "discount":       result["discount"],
                "url":            result["url"],
                "platform":       platform_key,
                "platform_label": PLATFORM_LABELS[platform_key],
            }
        return None

    except Exception as e:
        print(f"[ERROR] Search failed for '{game_title}' on {platform_key}: {e}")
        return None


def fetchDealsForWishlist(wishlist: list[str], platforms: list[str]) -> list[dict]:
    """
    Search DekuDeals for each wishlist game on each platform.
    Returns only games that are currently on sale.
    """
    matched = []
    supported = [p for p in platforms if p in PLATFORM_FILTERS]

    if not supported or not wishlist:
        return []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        try:
            for platform in supported:
                print(f"[→] Searching {PLATFORM_LABELS[platform]} for {len(wishlist)} games...")
                for game in wishlist:
                    result = _searchGame(page, game, platform)
                    if result:
                        # Verify the result name loosely matches the search query
                        if game.lower()[:6] in result["name"].lower():
                            matched.append(result)
                            print(f"[✓] Match: {result['name']} on {PLATFORM_LABELS[platform]} — {result['sale_price']} ({result['discount']}% OFF)")
                        else:
                            print(f"[~] Skipped unrelated result for '{game}': got '{result['name']}'")
                    else:
                        print(f"[✗] Not on sale: {game} on {PLATFORM_LABELS[platform]}")
        finally:
            browser.close()

    print(f"[✓] Total matches found: {len(matched)}")
    return matched


# ── Backwards compatibility ────────────────────────────────────────────────────

def fetchDealsForPlatforms(platforms: list[str]) -> list[dict]:
    """
    Legacy function — returns empty since we now search per-game.
    Use fetchDealsForWishlist() instead.
    """
    print("[WARN] fetchDealsForPlatforms called — use fetchDealsForWishlist instead.")
    return []


def fetchPsDeals() -> list[dict]:
    """Backwards-compatible — returns empty, use fetchDealsForWishlist."""
    return []


def filterWishlistDeals(deals: list[dict], wishlist: list[str]) -> list[dict]:
    """Legacy filter — returns deals as-is since fetchDealsForWishlist already filters."""
    return deals
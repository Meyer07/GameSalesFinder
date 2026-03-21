import time
from playwright.sync_api import sync_playwright

MAX_DEALS = 200

PLATFORM_URLS = {
    "ps":    "https://www.dekudeals.com/ps-deals",
    "steam": "https://www.dekudeals.com/steam-deals",
    "xbox":  "https://www.dekudeals.com/xbox-deals",
}

PLATFORM_LABELS = {
    "ps":    "PlayStation",
    "steam": "Steam",
    "xbox":  "Xbox",
}


def _scrapeDeals(page, url: str, platform_key: str) -> list[dict]:
    """Scrape deals from a DekuDeals page using Playwright."""
    try:
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(5000)

        deals_data = page.evaluate("""
            () => {
                const results = [];
                document.querySelectorAll('.col.d-block').forEach(card => {
                    const titleEl    = card.querySelector('a.main-link h6');
                    const linkEl     = card.querySelector('a.main-link');
                    const priceEl    = card.querySelector('strong');
                    const originalEl = card.querySelector('s.text-muted');
                    const discountEl = card.querySelector('span.badge-danger');
                    if (titleEl && priceEl) {
                        results.push({
                            name:     titleEl.innerText.trim(),
                            url:      linkEl ? linkEl.href : '',
                            price:    priceEl.innerText.trim(),
                            original: originalEl ? originalEl.innerText.trim() : 'N/A',
                            discount: discountEl ? discountEl.innerText.trim().replace('%','').replace('-','') : '?'
                        });
                    }
                });
                return results;
            }
        """)

        deals = [{
            "name":           d["name"],
            "sale_price":     d["price"],
            "regular_price":  d["original"],
            "discount":       d["discount"],
            "url":            d["url"],
            "platform":       platform_key,
            "platform_label": PLATFORM_LABELS[platform_key],
        } for d in deals_data[:MAX_DEALS]]

        print(f"[✓] Fetched {len(deals)} {PLATFORM_LABELS[platform_key]} deals.")
        return deals

    except Exception as e:
        print(f"[ERROR] Failed to fetch {platform_key} deals: {e}")
        return []


def fetchDealsForPlatforms(platforms: list[str]) -> list[dict]:
    """Fetch deals for a list of platform keys e.g. ['ps', 'steam', 'xbox']"""
    all_deals = []

    # Filter out any unsupported platforms
    supported = [p for p in platforms if p in PLATFORM_URLS]

    if not supported:
        print("[WARN] No supported platforms in list.")
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
                deals = _scrapeDeals(page, PLATFORM_URLS[platform], platform)
                all_deals.extend(deals)
        finally:
            browser.close()

    print(f"[✓] Total deals fetched across all platforms: {len(all_deals)}")
    return all_deals


def fetchPsDeals() -> list[dict]:
    """Backwards-compatible single-platform fetch for PlayStation."""
    return fetchDealsForPlatforms(["ps"])


def filterWishlistDeals(deals: list[dict], wishlist: list[str]) -> list[dict]:
    """Returns only deals that match games in the wishlist."""
    matched = []
    for game in wishlist:
        match = next(
            (d for d in deals if game.lower() in d["name"].lower()),
            None
        )
        if match:
            matched.append(match)
    return matched
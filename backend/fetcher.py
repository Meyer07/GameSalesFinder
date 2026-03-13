import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

MAX_DEALS = 100

PLATFORM_URLS = {
    "ps":     "https://www.dekudeals.com/ps-deals",
    "steam":  "https://www.dekudeals.com/steam-deals",
    "switch": "https://www.dekudeals.com/eshop-sales",
    "xbox":   "https://www.dekudeals.com/xbox-deals",
}

PLATFORM_LABELS = {
    "ps":     "PlayStation",
    "steam":  "Steam",
    "switch": "Nintendo Switch",
    "switch2":  "Nintendo Switch 2",
    "xbox":   "Xbox",
}


def _makeDriver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def _scrapeDeals(driver, url: str, platform_key: str) -> list[dict]:
    """Scrape deals from a single DekuDeals page."""
    try:
        driver.get(url)
        time.sleep(8)

        deals_data = driver.execute_script("""
            const cards = document.querySelectorAll('.col.d-block');
            const results = [];
            cards.forEach(card => {
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
        """)

        deals = [{
            "name":          d["name"],
            "sale_price":    d["price"],
            "regular_price": d["original"],
            "discount":      d["discount"],
            "url":           d["url"],
            "platform":      platform_key,
            "platform_label": PLATFORM_LABELS[platform_key],
        } for d in deals_data[:MAX_DEALS]]

        print(f"[✓] Fetched {len(deals)} {PLATFORM_LABELS[platform_key]} deals.")
        return deals

    except Exception as e:
        print(f"[ERROR] Failed to fetch {platform_key} deals: {e}")
        return []


def fetchDealsForPlatforms(platforms: list[str]) -> list[dict]:
    """Fetch deals for a list of platform keys e.g. ['ps', 'steam']"""
    all_deals = []
    driver = _makeDriver()
    try:
        for platform in platforms:
            url = PLATFORM_URLS.get(platform)
            if not url:
                print(f"[WARN] Unknown platform: {platform}")
                continue
            deals = _scrapeDeals(driver, url, platform)
            all_deals.extend(deals)
    finally:
        driver.quit()

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
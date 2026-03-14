import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

MAX_DEALS = 200

PLATFORM_URLS = {
    "ps":    "https://www.dekudeals.com/ps-deals",
    "steam": "https://www.dekudeals.com/steam-deals",
    "xbox":  "https://www.dekudeals.com/xbox-deals",
}

PLATFORM_LABELS = {
    "ps":     "PlayStation",
    "steam":  "Steam",
    "switch": "Nintendo Switch",
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
    """Scrape deals from a DekuDeals page — handles both page layouts."""
    try:
        driver.get(url)
        time.sleep(8)

        deals_data = driver.execute_script("""
            const results = [];

            // Layout 1: PS/Steam/Xbox — .col.d-block
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

            // Layout 2: Switch/eShop — .col.cell
            document.querySelectorAll('.col.cell').forEach(card => {
                const titleEl    = card.querySelector('div.h6.name');
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


def _fetchSwitchDeals() -> list[dict]:
    """Fetch Switch deals directly from Nintendo's eShop API — no Selenium needed."""
    all_deals = []
    offset    = 0
    count     = 200

    try:
        while True:
            url  = f"https://ec.nintendo.com/api/US/en/search/sales?count={count}&offset={offset}"
            resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=15)
            resp.raise_for_status()
            data = resp.json()

            contents = data.get("contents", [])
            if not contents:
                break

            for item in contents:
                price_info = item.get("price", {})
                regular    = price_info.get("regular_price", {})
                discount   = price_info.get("discount_price", {})

                if not discount:
                    continue

                regular_amount  = regular.get("raw_value", "N/A")
                discount_amount = discount.get("raw_value", "N/A")

                try:
                    pct = round((1 - float(discount_amount) / float(regular_amount)) * 100)
                except Exception:
                    pct = "?"

                all_deals.append({
                    "name":           item.get("formal_name", "Unknown"),
                    "sale_price":     f"${discount_amount}",
                    "regular_price":  f"${regular_amount}",
                    "discount":       str(pct),
                    "url":            f"https://www.nintendo.com/us/store/products/{item.get('id', '')}",
                    "platform":       "switch",
                    "platform_label": "Nintendo Switch",
                })

            if len(contents) < count:
                break
            offset += count

        print(f"[✓] Fetched {len(all_deals)} Nintendo Switch deals from eShop API.")
        return all_deals[:MAX_DEALS]

    except Exception as e:
        print(f"[ERROR] Nintendo eShop API failed: {e}")
        return []


def fetchDealsForPlatforms(platforms: list[str]) -> list[dict]:
    """Fetch deals for a list of platform keys e.g. ['ps', 'steam', 'switch']"""
    all_deals          = []
    selenium_platforms = [p for p in platforms if p != "switch"]

    # Switch uses Nintendo eShop API directly — no Selenium, no bot detection
    if "switch" in platforms:
        all_deals.extend(_fetchSwitchDeals())

    # PS, Steam, Xbox use Selenium to scrape DekuDeals
    if selenium_platforms:
        driver = _makeDriver()
        try:
            for platform in selenium_platforms:
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
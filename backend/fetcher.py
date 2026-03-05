import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

MAX_DEALS = 100


def fetchPsDeals() -> list[dict]:
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://www.dekudeals.com/ps-deals")
        time.sleep(8)

        # Use JavaScript to extract all deal data at once from the rendered page
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
            "platforms":     ["PS"],
            "sale_end_date": "",
        } for d in deals_data[:MAX_DEALS]]

        print(f"[✓] Fetched {len(deals)} deals from DekuDeals.")
        return deals

    except Exception as e:
        print(f"Error fetching deals: {e}")
        return []

    finally:
        driver.quit()


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
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routes import users, wishlist
from scheduler import startScheduler

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="PS Deals Notifier", version="1.0.0")

# CORS — allow React frontend to communicate with the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://game-sales-finder.vercel.app",
        "https://game-sales-finder-git-main-meyer07s-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(users.router)
app.include_router(wishlist.router)


models.Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"message": "PS Deals Notifier API is running"}


@app.on_event("startup")
def startup():
    startScheduler()
    print("[✓] Background scheduler started.")


# ── Test Endpoints (remove before deploying to production) ────────────────────

@app.get("/test-notify")
def test_notify():
    """
    Runs the full notification job for all users using their saved platform preferences.
    Visit: http://localhost:8000/test-notify
    """
    from fetcher import fetchDealsForPlatforms, filterWishlistDeals
    from notifications import sendEmail, sendPushover
    from database import SessionLocal

    db = SessionLocal()
    results = []

    try:
        active_users = db.query(models.User).filter(models.User.is_active == True).all()
        platform_cache: dict[str, list] = {}

        for user in active_users:
            wishlist_titles = [item.game_title for item in user.wishlist]
            if not wishlist_titles:
                results.append({"user": user.email, "status": "skipped — no wishlist"})
                continue

            platforms = [p.strip() for p in (user.platforms or "ps").split(",")]
            cache_key = ",".join(sorted(platforms))

            if cache_key not in platform_cache:
                platform_cache[cache_key] = fetchDealsForPlatforms(platforms)

            deals = platform_cache[cache_key]
            matched = filterWishlistDeals(deals, wishlist_titles)

            if not matched:
                results.append({"user": user.email, "status": "no matches", "platforms": platforms})
                continue

            notify_email = user.notification_email or user.email
            sendEmail(notify_email, matched)
            if user.pushover_key:
                sendPushover(user.pushover_key, matched)

            results.append({
                "user":      user.email,
                "platforms": platforms,
                "matches":   [f"{d['name']} ({d.get('platform_label','')}) — {d['sale_price']} ({d['discount']}% OFF)" for d in matched],
                "status":    "notified"
            })
    finally:
        db.close()

    return {"results": results}


@app.get("/test-deals")
def test_deals(platform: str = "ps"):
    """
    Fetch deals for a specific platform and return them.
    Usage:
      http://localhost:8000/test-deals           → PlayStation (default)
      http://localhost:8000/test-deals?platform=steam
      http://localhost:8000/test-deals?platform=switch
      http://localhost:8000/test-deals?platform=xbox
      http://localhost:8000/test-deals?platform=ps,steam  → multiple platforms
    """
    from fetcher import fetchDealsForPlatforms

    platforms = [p.strip() for p in platform.split(",")]
    deals = fetchDealsForPlatforms(platforms)
    return {
        "platforms": platforms,
        "count":     len(deals),
        "deals":     deals
    }


@app.get("/test-match")
def test_match(platform: str = "ps"):
    """
    Fetch deals for a platform and check which wishlist games match for each user.
    Useful for debugging before sending notifications.
    Usage:
      http://localhost:8000/test-match
      http://localhost:8000/test-match?platform=steam
      http://localhost:8000/test-match?platform=ps,steam,switch,xbox
    """
    from fetcher import fetchDealsForPlatforms, filterWishlistDeals
    from database import SessionLocal

    db = SessionLocal()
    results = []

    try:
        platforms = [p.strip() for p in platform.split(",")]
        deals = fetchDealsForPlatforms(platforms)

        active_users = db.query(models.User).filter(models.User.is_active == True).all()
        for user in active_users:
            wishlist_titles = [item.game_title for item in user.wishlist]
            matched = filterWishlistDeals(deals, wishlist_titles)
            results.append({
                "user":      user.email,
                "platforms": platforms,
                "wishlist":  wishlist_titles,
                "matches":   [f"{d['name']} ({d.get('platform_label','')}) — {d['sale_price']} ({d['discount']}% OFF)" for d in matched],
            })
    finally:
        db.close()

    return {
        "platforms":    platforms,
        "total_deals":  len(deals),
        "user_results": results
    }

@app.get("/test-switch-html")
def test_switch_html():
    import time
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.chrome.options import Options
    from webdriver_manager.chrome import ChromeDriverManager

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("https://www.dekudeals.com/eshop-sales")
    time.sleep(8)

    result = driver.execute_script("""
        return {
            col_dblock: document.querySelectorAll('.col.d-block').length,
            col_cell: document.querySelectorAll('.col.cell').length,
            main_link: document.querySelectorAll('a.main-link').length,
            h6_name: document.querySelectorAll('div.h6.name').length,
            body_snippet: document.body.innerHTML.substring(0, 2000)
        }
    """)
    driver.quit()
    return result

@app.get("/health")
async def health_check():
    return {"status": "awake"}
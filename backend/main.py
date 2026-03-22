from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routes import users, wishlist
import threading
import os

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Game Sales Notifier", version="1.0.0")

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


@app.get("/")
def root():
    return {"message": "Game Sales Notifier API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Helper ────────────────────────────────────────────────────────────────────

def _runNotifyForPlatform(platform_key: str):
    """Search wishlist games for one platform and notify users with matches."""
    from fetcher import fetchDealsForWishlist
    from notifications import sendPushover
    from database import SessionLocal

    db = SessionLocal()
    results = []

    try:
        active_users = db.query(models.User).filter(models.User.is_active == True).all()

        for user in active_users:
            # Only process users who have this platform selected
            user_platforms = [p.strip() for p in (user.platforms or "ps").split(",")]
            if platform_key not in user_platforms:
                continue

            wishlist_titles = [item.game_title for item in user.wishlist]
            if not wishlist_titles:
                results.append({"user": user.email, "status": "skipped — no wishlist"})
                continue

            # Search DekuDeals for each wishlist game on this platform
            matched = fetchDealsForWishlist(wishlist_titles, [platform_key])

            if not matched:
                results.append({"user": user.email, "status": "no matches"})
                continue

            if user.pushover_key:
                sendPushover(user.pushover_key, matched)

            results.append({
                "user":    user.email,
                "matches": [f"{d['name']} — {d['sale_price']} ({d['discount']}% OFF)" for d in matched],
                "status":  "notified via pushover"
            })

    finally:
        db.close()

    return {
        "platform": platform_key,
        "results":  results
    }


def _runInBackground(platform_key: str):
    """Run notify job in background thread so endpoint returns immediately."""
    thread = threading.Thread(target=_runNotifyForPlatform, args=(platform_key,), daemon=True)
    thread.start()


# ── Per-Platform Notify Endpoints ─────────────────────────────────────────────
# Point cron-job.org at each of these at staggered times:
#   9:00am → /notify-ps
#   9:15am → /notify-steam
#   9:30am → /notify-xbox

@app.get("/notify-ps")
def notify_ps():
    _runInBackground("ps")
    return {"status": "PS notify job started"}


@app.get("/notify-steam")
def notify_steam():
    _runInBackground("steam")
    return {"status": "Steam notify job started"}


@app.get("/notify-xbox")
def notify_xbox():
    _runInBackground("xbox")
    return {"status": "Xbox notify job started"}


# ── Debug endpoint ────────────────────────────────────────────────────────────

@app.get("/debug-wishlist")
def debug_wishlist(platform: str = "ps"):
    """
    Check what games would match for each user on a given platform.
    Usage:
      /debug-wishlist?platform=ps
      /debug-wishlist?platform=steam
      /debug-wishlist?platform=xbox
    """
    from fetcher import fetchDealsForWishlist
    from database import SessionLocal

    db = SessionLocal()
    results = []

    try:
        active_users = db.query(models.User).filter(models.User.is_active == True).all()
        for user in active_users:
            user_platforms = [p.strip() for p in (user.platforms or "ps").split(",")]
            if platform not in user_platforms:
                continue
            wishlist_titles = [item.game_title for item in user.wishlist]
            matched = fetchDealsForWishlist(wishlist_titles, [platform])
            results.append({
                "user":     user.email,
                "wishlist": wishlist_titles,
                "matched":  [d["name"] for d in matched],
            })
    finally:
        db.close()

    return {"platform": platform, "results": results}

@app.get("/debug-itad")
def debug_itad(game: str = "Red Dead Redemption 2"):
    import requests
    import os
    
    api_key = os.getenv("ITAD_API_KEY")
    
    # Step 1: Search for game
    search_resp = requests.get(
        "https://api.isthereanydeal.com/games/search/v1",
        params={"key": api_key, "title": game, "limit": 1},
        timeout=10
    )
    search_data = search_resp.json()
    
    if not search_data:
        return {"error": "Game not found", "game": game}
    
    game_id = search_data[0].get("id")
    
    # Step 2: Get prices
    price_resp = requests.post(
        "https://api.isthereanydeal.com/games/prices/v3",
        params={"key": api_key, "country": "US"},
        json=[game_id],
        timeout=10
    )
    
    return {
        "game": game,
        "game_id": game_id,
        "raw_price_response": price_resp.json()
    }
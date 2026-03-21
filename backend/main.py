from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routes import users, wishlist
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
    """Fetch deals for one platform and notify users who have it selected."""
    from fetcher import fetchDealsForPlatforms, filterWishlistDeals
    from notifications import sendEmail, sendPushover
    from database import SessionLocal

    db = SessionLocal()
    results = []

    try:
        deals = fetchDealsForPlatforms([platform_key])
        if not deals:
            return {"platform": platform_key, "status": "no deals fetched", "results": []}

        active_users = db.query(models.User).filter(models.User.is_active == True).all()

        for user in active_users:
            # Only notify users who have this platform selected
            user_platforms = [p.strip() for p in (user.platforms or "ps").split(",")]
            if platform_key not in user_platforms:
                continue

            wishlist_titles = [item.game_title for item in user.wishlist]
            if not wishlist_titles:
                results.append({"user": user.email, "status": "skipped — no wishlist"})
                continue

            matched = filterWishlistDeals(deals, wishlist_titles)
            if not matched:
                results.append({"user": user.email, "status": "no matches"})
                continue

            notify_email = user.notification_email or user.email
            sendEmail(notify_email, matched)
            if user.pushover_key:
                sendPushover(user.pushover_key, matched)

            results.append({
                "user":    user.email,
                "matches": [f"{d['name']} — {d['sale_price']} ({d['discount']}% OFF)" for d in matched],
                "status":  "notified"
            })

    finally:
        db.close()

    return {
        "platform": platform_key,
        "deals_found": len(deals),
        "results": results
    }


# ── Per-Platform Notify Endpoints ─────────────────────────────────────────────
# Point cron-job.org at each of these at staggered times:
#   9:00am → /notify-ps
#   9:05am → /notify-steam
#   9:10am → /notify-xbox

@app.get("/notify-ps")
def notify_ps():
    return _runNotifyForPlatform("ps")


@app.get("/notify-steam")
def notify_steam():
    return _runNotifyForPlatform("steam")


@app.get("/notify-xbox")
def notify_xbox():
    return _runNotifyForPlatform("xbox")


# ── Combined notify (for local testing only) ──────────────────────────────────

@app.get("/test-notify")
def test_notify():
    """Run all platforms at once — for local testing only, too slow for production."""
    ps    = _runNotifyForPlatform("ps")
    steam = _runNotifyForPlatform("steam")
    xbox  = _runNotifyForPlatform("xbox")
    return {"ps": ps, "steam": steam, "xbox": xbox}

@app.get("/debug-playwright")
def debug_playwright():
    import subprocess
    result = subprocess.getoutput("find /opt/render/project/src/.playwright -name 'chrome*' 2>/dev/null")
    return {"playwright_path": result}
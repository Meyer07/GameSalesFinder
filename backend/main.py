from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
from routes import users, wishlist, deals
import threading

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Game Sales Notifier", version="2.0.0",redirect_slashes=False)

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

app.include_router(users.router)
app.include_router(wishlist.router)
app.include_router(deals.router)


@app.get("/")
def root():
    return {"message": "Game Sales Notifier API is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


# ── Notify helpers ─────────────────────────────────────────

def _runNotifyForPlatform(platform_key: str):
    from fetcher import fetchDealsForWishlist
    from notifications import sendPushover
    from database import SessionLocal

    db = SessionLocal()
    results = []

    try:
        active_users = db.query(models.User).filter(models.User.is_active == True).all()

        for user in active_users:
            user_platforms = [p.strip() for p in (user.platforms or "ps").split(",")]
            if platform_key not in user_platforms:
                continue

            wishlist_titles = [item.game_title for item in user.wishlist]
            if not wishlist_titles:
                results.append({"user": user.email, "status": "skipped — no wishlist"})
                continue

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

    return {"platform": platform_key, "results": results}


def _runInBackground(platform_key: str):
    thread = threading.Thread(target=_runNotifyForPlatform, args=(platform_key,), daemon=True)
    thread.start()


# ── Notify endpoints ───────────────────────────────────────

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


# ── Debug endpoints ────────────────────────────────────────

@app.get("/debug-wishlist")
def debug_wishlist(platform: str = "ps"):
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
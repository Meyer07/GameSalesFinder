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
    allow_origins=["http://localhost:5173", "https://your-app.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(users.router)
app.include_router(wishlist.router)


@app.get("/")
def root():
    return {"message": "PS Deals Notifier API is running"}


@app.on_event("startup")
def startup():
    startScheduler()
    print("[✓] Background scheduler started.")


@app.get("/test-notify")
def test_notify():
    from fetcher import fetchPsDeals, filterWishlistDeals
    from notifications import sendEmail, sendPushover
    from database import SessionLocal
    import models

    db = SessionLocal()
    users = db.query(models.User).filter(models.User.is_active == True).all()
    deals = fetchPsDeals()

    for user in users:
        wishlist = [item.game_title for item in user.wishlist]
        if not wishlist or not deals:
            continue
        matched = filterWishlistDeals(deals, wishlist)
        if matched:
            notify_email = user.notification_email or user.email
            sendEmail(notify_email, matched)
            if user.pushover_key:
                sendPushover(user.pushover_key, matched)

    db.close()
    return {"message": f"Notified {len(users)} users"}

@app.get("/test-deals")
def test_deals():
    from fetcher import fetchPsDeals
    return fetchPsDeals()
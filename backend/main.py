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
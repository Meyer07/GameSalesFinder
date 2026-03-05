"""
scheduler.py — Runs the daily deals job for every user in the database.
Each user gets notified only about their own wishlist games that are on sale.
"""

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session
from database import SessionLocal
from fetcher import fetchPsDeals, filterWishlistDeals
from notifications import sendEmail, sendPushover
import models


def runDailyDealsJob():
    print("[scheduler] Running daily deals job...")
    db: Session = SessionLocal()

    try:
        deals = fetchPsDeals()
        if not deals:
            print("[scheduler] No deals fetched, aborting.")
            return

        users = db.query(models.User).filter(models.User.is_active == True).all()
        print(f"[scheduler] Processing {len(users)} users...")

        for user in users:
            wishlist = [item.game_title for item in user.wishlist]
            if not wishlist:
                print(f"[scheduler] No wishlist for {user.email}, skipping.")
                continue

            matched_deals = filterWishlistDeals(deals, wishlist)
            if not matched_deals:
                print(f"[scheduler] No wishlist matches for {user.email}.")
                continue

            print(f"[scheduler] {len(matched_deals)} match(es) for {user.email}.")

            # Use notification_email if set, otherwise fall back to login email
            notify_email = user.notification_email or user.email
            sendEmail(notify_email, matched_deals)

            if user.pushover_key:
                sendPushover(user.pushover_key, matched_deals)

    finally:
        db.close()


def startScheduler():
    """Start as a background scheduler (used inside FastAPI on startup)."""
    scheduler = BackgroundScheduler()
    scheduler.add_job(runDailyDealsJob, "cron", hour=9, minute=0)
    scheduler.start()
    return scheduler


if __name__ == "__main__":
    """Run standalone as a blocking scheduler."""
    print("[scheduler] Starting standalone scheduler, runs daily at 9am...")
    scheduler = BlockingScheduler()
    scheduler.add_job(runDailyDealsJob, "cron", hour=9, minute=0)
    scheduler.start()
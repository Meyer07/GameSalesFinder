# 🎮 PS Deals Notifier

A full-stack web app that lets multiple users sign up, manage their own game wishlists on the platform of their choice, and recieve Pushover notifications when their games go on sale.

## Stack
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy
- **Frontend**: React + Vite
- **Notifications**: Pushover (push)
- **Deals Source**: ITAD API + STORE_DEALS Database 
- **Hosting**: Render (backend) + Supabase (database) + Vercel (frontend) — all free
- **Automation**: Cron-job.org(to keep the render instance awake)

---

## Local Development Setup

### 1. Backend

```bash
cd backend
pip3 install -r requirements.txt

# Copy env file and fill in your values
cp .env.example .env

# Run the API
uvicorn main:app --reload
```

API will be running at: http://localhost:8000
API docs at: http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend will be running at: http://localhost:5173

### 3. Database (PostgreSQL)

Install PostgreSQL locally or use Supabase for a free hosted database.

```bash
# Option A — local database
createdb psdeals

# Update DATABASE_URL in backend/.env:
DATABASE_URL=postgresql://localhost/psdeals
```

```bash
# Option B — use your Supabase connection string directly in .env:
DATABASE_URL=postgresql://postgres:[PASSWORD]@db.xxxx.supabase.co:5432/postgres
```

Tables are created automatically when the backend starts.

---

## Deployment (Free Stack)

All three services have free tiers. Total cost: **$0/month**.

> ⚠️ Render's free tier spins down after 15 minutes of inactivity, this is solved with cron-job.org sending a request to a health end point in the render deployment to keep it awake every 10 minutes 

---

## How It Works

1. Users sign up with their email and optional Pushover key
2. They add games to their wishlist via the dashboard
3. Every day at 9am, the scheduler fetches all PS deals from DekuDeals
4. For each user, it checks if any wishlist games are on sale
5. If matches are found, it sends a personalized email + Pushover notification

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/signup` | Create account |
| POST | `/auth/login` | Login, get JWT token |
| GET | `/auth/me` | Get current user |
| PUT | `/auth/me` | Update Pushover key / password |
| GET | `/wishlist/` | Get user's wishlist |
| POST | `/wishlist/` | Add game to wishlist |
| DELETE | `/wishlist/{id}` | Remove game from wishlist |
# 🎮 PS Deals Notifier

A full-stack web app that lets multiple users sign up, manage their own PS game wishlists, and receive personalized email + Pushover notifications when their games go on sale.

## Stack
- **Backend**: FastAPI + PostgreSQL + SQLAlchemy
- **Frontend**: React + Vite
- **Notifications**: Roadrunner SMTP (email) + Pushover (push)
- **Deals Source**: DekuDeals (Selenium scraper)
- **Hosting**: Render (backend) + Supabase (database) + Vercel (frontend) — all free

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

> ⚠️ Render's free tier spins down after 15 minutes of inactivity. The first request after a period of no use takes ~30 seconds to wake up. This is fine for a scheduled deals notifier.

---

### Step 1 — Database → Supabase (Free PostgreSQL)

1. Sign up at [supabase.com](https://supabase.com)
2. Click **New Project**, give it a name (e.g. `psdeals`)
3. Set a strong database password and save it somewhere safe
4. Once created, go to **Settings → Database**
5. Copy the **Connection String** under "URI" — it looks like:
   ```
   postgresql://postgres:[PASSWORD]@db.xxxx.supabase.co:5432/postgres
   ```
6. Save this — you'll need it for the backend env vars

---

### Step 2 — Backend → Render (Free Web Service)

1. Sign up at [render.com](https://render.com)
2. Click **New → Web Service**
3. Connect your GitHub repo
4. Set the following:
   - **Root Directory**: `backend`
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Under **Environment Variables**, add all variables from `.env.example`:

   | Key | Value |
   |---|---|
   | `DATABASE_URL` | Your Supabase connection string from Step 1 |
   | `SECRET_KEY` | A long random string (e.g. run `openssl rand -hex 32` in terminal) |
   | `ROADRUNNER_EMAIL` | Your Roadrunner email |
   | `ROADRUNNER_PASSWORD` | Your Roadrunner password |
   | `PUSHOVER_API_TOKEN` | Your Pushover app token |

6. Click **Deploy** — Render will build and launch your API
7. Copy your Render URL (e.g. `https://psdeals-api.onrender.com`) — you'll need it for the frontend

---

### Step 3 — Frontend → Vercel (Free)

1. Sign up at [vercel.com](https://vercel.com)
2. Click **Add New → Project**
3. Import your GitHub repo
4. Set **Root Directory** to `frontend`
5. Under **Environment Variables**, add:
   ```
   VITE_API_URL=https://psdeals-api.onrender.com
   ```
   (Use your actual Render URL from Step 2)
6. Click **Deploy**
7. Vercel will give you a live URL like `https://psdeals.vercel.app`

---

### Step 4 — Update CORS

Once deployed, open `backend/main.py` and add your Vercel URL to the allowed origins:

```python
allow_origins=[
    "http://localhost:5173",
    "https://psdeals.vercel.app",   # ← add your real Vercel URL
],
```

Commit and push — Render will auto-redeploy.

---

## Environment Variables

| Variable | Description |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret (make this long and random) |
| `ROADRUNNER_EMAIL` | Your Roadrunner email address |
| `ROADRUNNER_PASSWORD` | Your Roadrunner password |
| `PUSHOVER_API_TOKEN` | Your Pushover app token (from pushover.net) |

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
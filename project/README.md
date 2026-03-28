# AI Temp Mail Agent

A full-stack app that generates disposable email addresses, fetches inbox messages, and auto-extracts OTPs — all stored in PostgreSQL.

---

## Project Structure

```
project/
├── backend/
│   ├── main.py                 # FastAPI app + routes
│   ├── config.py               # DB config + env vars
│   ├── schema.sql              # Manual DB setup (optional)
│   ├── requirements.txt
│   ├── .env.example
│   ├── db/
│   │   ├── connection.py       # psycopg2 connection + init_db()
│   │   └── models.py           # insert/fetch functions
│   └── services/
│       ├── email_service.py    # mail.tm API integration
│       └── otp_service.py      # regex OTP extraction
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── script.js               # ← update API_BASE before deploying
├── render.yaml                 # Render deployment config
└── netlify.toml                # Netlify deployment config
```

---

## Local Development

### 1. Prerequisites
- Python 3.10+
- PostgreSQL running locally
- Node not required (vanilla JS frontend)

### 2. Database Setup
```sql
-- In psql:
CREATE DATABASE tempmail_db;
```
Tables are created automatically on first startup via `init_db()`.

### 3. Backend Setup
```bash
cd backend
cp .env.example .env
# Edit .env with your local DB credentials

pip install -r requirements.txt
uvicorn main:app --reload
# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### 4. Frontend Setup
```bash
# No build step needed — pure HTML/CSS/JS
# Open frontend/index.html directly in browser
# OR serve with:
cd frontend
python -m http.server 3000
# Visit http://localhost:3000
```

> **Important:** In `frontend/script.js`, the `API_BASE` auto-detects localhost vs production.

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/health` | Health check |
| POST | `/create-email` | Generate new temp email |
| GET  | `/get-messages?email=<addr>` | Fetch & sync inbox |
| GET  | `/get-otp?email=<addr>` | Get latest extracted OTP |

### Example Responses

**POST /create-email**
```json
{
  "success": true,
  "email": "abcd1234@indimail.org",
  "created_at": "2024-01-15 10:30:00"
}
```

**GET /get-messages?email=abcd1234@indimail.org**
```json
{
  "success": true,
  "count": 1,
  "messages": [
    {
      "id": 1,
      "sender": "noreply@service.com",
      "subject": "Your verification code is 847291",
      "body": "Use code 847291 to verify your account.",
      "received_at": "2024-01-15 10:32:00"
    }
  ]
}
```

**GET /get-otp?email=abcd1234@indimail.org**
```json
{
  "success": true,
  "otp": "847291",
  "type": "numeric_6",
  "created_at": "2024-01-15 10:32:05"
}
```

---

## Deployment (Free Tier)

### Step 1 — Push to GitHub
```bash
git init
git add .
git commit -m "initial commit"
git remote add origin https://github.com/YOUR/repo.git
git push -u origin main
```

### Step 2 — Deploy Backend + DB on Render

1. Go to [render.com](https://render.com) → New → **Blueprint**
2. Connect your GitHub repo
3. Render reads `render.yaml` automatically and creates:
   - A **Web Service** (FastAPI backend)
   - A **PostgreSQL database** (free tier)
4. After deploy, copy your backend URL: `https://tempmail-backend.onrender.com`

**Manual alternative (without Blueprint):**
- New → Web Service → connect repo → set Root Dir: `backend`
- Build: `pip install -r requirements.txt`
- Start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add env vars from `.env.example` (use Render's "Connect to DB" for DB vars)

### Step 3 — Update Frontend API URL
Edit `frontend/script.js` line ~6:
```js
: 'https://YOUR-RENDER-APP.onrender.com'  // ← paste your Render URL here
```
Commit and push.

### Step 4 — Deploy Frontend on Netlify

1. Go to [netlify.com](https://netlify.com) → New Site → Import from Git
2. Connect your repo
3. Set **Base directory**: `frontend`
4. Set **Publish directory**: `frontend`
5. Build command: *(leave empty)*
6. Deploy

### Step 5 — Update CORS on Render
In Render dashboard → your web service → Environment:
```
CORS_ORIGINS = https://YOUR-APP.netlify.app
```

---

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_PORT` | PostgreSQL port | `5432` |
| `DB_NAME` | Database name | `tempmail_db` |
| `DB_USER` | DB username | `postgres` |
| `DB_PASSWORD` | DB password | — |
| `CORS_ORIGINS` | Allowed frontend origins (comma-sep) | `*` |

---

## OTP Detection Patterns

| Type | Pattern | Example |
|------|---------|---------|
| `numeric_6` | 6-digit number | `847291` |
| `numeric_4` | 4-digit number | `4821` |
| `numeric_8` | 8-digit number | `84729123` |
| `alphanum` | 6-10 char alphanumeric | `AB4K9Z` |
| `verify_link` | Verification URL | `https://...verify?token=...` |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `connection refused` on DB | Check PostgreSQL is running, credentials in `.env` |
| `CORS error` in browser | Add your Netlify URL to `CORS_ORIGINS` in Render |
| mail.tm returns 429 | Rate limited — wait 30s and retry |
| No OTP found | Refresh inbox first, then fetch OTP |
| Render app sleeping | Free tier spins down after 15min — first request is slow |

# ⬡ TempMail Agent

### AI-powered disposable email with automatic OTP extraction

[![Live Demo](https://img.shields.io/badge/🌐_Live_Demo-tempmail--agent.netlify.app-7c6af7?style=for-the-badge)](https://tempmail-agent.netlify.app/)
[![Backend](https://img.shields.io/badge/⚡_Backend-Render-00c7b7?style=for-the-badge)](https://tempmail-backend-y1y6.onrender.com/docs)
[![License](https://img.shields.io/badge/📄_License-MIT-3ecfb2?style=for-the-badge)](#)

**Generate → Receive → Extract. Done.**

No sign-up. No trace. No cost.


[🚀 Try it Live](https://tempmail-agent.netlify.app/) · [📖 API Docs](https://tempmail-backend-y1y6.onrender.com/docs) · [🐛 Report Bug](https://github.com/sujalsharma21/tempmail-agent/issues) · [✨ Request Feature](https://github.com/sujalsharma21/tempmail-agent/issues)

---

## 📸 Preview

> **Page 1 — Generate** a disposable email instantly
>
> **Page 2 — Inbox** syncs real emails from mail.tm in real time
>
> **Page 3 — OTP** auto-extracted from email body using regex AI

---

## ✨ What It Does

| Feature | Description |
|---|---|
| 📧 **Generate Email** | Creates a real disposable inbox via mail.tm API |
| 📥 **Fetch Inbox** | Pulls and syncs live emails into PostgreSQL |
| 🔐 **Extract OTP** | Auto-detects 4/6/8-digit codes & verification links |
| 🗄️ **Stores Everything** | Full email + message + OTP history in the cloud |
| 📱 **Responsive UI** | Works on mobile, tablet, and desktop |
| ⚡ **Zero Setup** | No account needed to use the app |

---

## 🌐 Live Demo

```
🔗 https://tempmail-agent.netlify.app/
```

> ⚠️ **Note:** First load may take 30-50 seconds — the free backend wakes up from sleep on first request. After that it's fast!

---

## 🛠️ Tech Stack

```
┌─────────────────────────────────────────────────────┐
│                    FRONTEND                         │
│         HTML + CSS + Vanilla JavaScript             │
│              Hosted on Netlify (free)               │
└────────────────────┬────────────────────────────────┘
                     │ HTTP/REST
┌────────────────────▼────────────────────────────────┐
│                    BACKEND                          │
│              Python 3.11 + FastAPI                  │
│              Hosted on Render (free)                │
└────────────────────┬────────────────────────────────┘
                     │ psycopg2
┌────────────────────▼────────────────────────────────┐
│                   DATABASE                          │
│                 PostgreSQL 15                       │
│              Hosted on Render (free)                │
└─────────────────────────────────────────────────────┘
                     │ HTTP
┌────────────────────▼────────────────────────────────┐
│                 EMAIL API                           │
│           mail.tm (free, no key needed)             │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
tempmail-agent/
└── project/
    ├── backend/
    │   ├── main.py              # FastAPI app + all routes
    │   ├── config.py            # Environment config
    │   ├── requirements.txt     # Python dependencies
    │   ├── .python-version      # Forces Python 3.11
    │   ├── schema.sql           # DB schema reference
    │   ├── db/
    │   │   ├── connection.py    # psycopg2 connection + init_db()
    │   │   └── models.py        # All DB insert/fetch functions
    │   └── services/
    │       ├── email_service.py # mail.tm API integration
    │       └── otp_service.py   # Regex OTP extraction engine
    └── frontend/
        ├── index.html           # Single page app
        ├── style.css            # Dark terminal aesthetic
        └── script.js            # All frontend logic
```

---

## 🔌 API Reference

Base URL: `https://tempmail-backend-y1y6.onrender.com`

### `POST /create-email`
Generates a new disposable email and stores it in DB.

```json
{
  "success": true,
  "email": "abcd1234@indimail.org",
  "created_at": "2024-01-15 10:30:00"
}
```

### `GET /get-messages?email=<address>`
Fetches and syncs inbox messages for the given email.

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

### `GET /get-otp?email=<address>`
Returns the most recently extracted OTP.

```json
{
  "success": true,
  "otp": "847291",
  "type": "numeric_6",
  "created_at": "2024-01-15 10:32:05"
}
```

### `GET /health`
```json
{"status": "ok"}
```

---

## 🔐 OTP Detection Patterns

| Type | Pattern | Example |
|---|---|---|
| `numeric_6` | 6-digit number | `847291` |
| `numeric_4` | 4-digit number | `4821` |
| `numeric_8` | 8-digit number | `84729123` |
| `alphanum` | 6-10 char alphanumeric | `AB4K9Z` |
| `verify_link` | Verification URL | `https://app.com/verify?token=...` |

---

## 🗄️ Database Schema

```sql
-- Stores generated email accounts
emails (id, email, password, token, created_at)

-- Stores fetched inbox messages
messages (id, email_id → emails, sender, subject, body, received_at)

-- Stores extracted OTPs
otps (id, message_id → messages, otp, otp_type, created_at)
```

---

## 🚀 Run Locally

**Requirements:** Python 3.11+, PostgreSQL

```bash
# 1. Clone the repo
git clone https://github.com/sujalsharma21/tempmail-agent.git
cd tempmail-agent/project/backend

# 2. Create database
psql -U postgres -c "CREATE DATABASE tempmail_db;"

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup environment
cp .env.example .env
# Edit .env → add your DB password

# 5. Start backend
python -m uvicorn main:app --reload
# → http://localhost:8000
# → http://localhost:8000/docs

# 6. Start frontend (new terminal)
cd ../frontend
python -m http.server 3000
# → http://localhost:3000
```

---

## ☁️ Deploy Your Own (100% Free)

| Service | Purpose | Cost |
|---|---|---|
| [Render](https://render.com) | Backend + PostgreSQL | Free |
| [Netlify](https://netlify.com) | Frontend | Free forever |
| [mail.tm](https://mail.tm) | Email API | Free, no key needed |

**Steps:**
1. Fork this repo
2. Deploy backend on Render → set environment variables
3. Update `API_BASE` in `frontend/script.js` with your Render URL
4. Deploy frontend on Netlify → set base dir to `project/frontend`
5. Update `CORS_ORIGINS` on Render with your Netlify URL

---

## ⚙️ Environment Variables

```env
DB_HOST=your-render-db-internal-host
DB_PORT=5432
DB_NAME=tempmail_db
DB_USER=your-db-user
DB_PASSWORD=your-db-password
CORS_ORIGINS=https://your-app.netlify.app
```

---

## 🗺️ Roadmap

- [x] Generate disposable email
- [x] Fetch inbox messages
- [x] Auto-extract OTP
- [x] PostgreSQL storage
- [x] Deploy to cloud (free)
- [ ] Auto-refresh inbox every 10 seconds
- [ ] Copy OTP with one click
- [ ] Multiple email management
- [ ] Email expiry countdown timer
- [ ] Mobile app using same API

---

## 👨‍💻 Author

**Sujal Sharma**

[![GitHub](https://img.shields.io/badge/GitHub-sujalsharma21-181717?style=flat&logo=github)](https://github.com/sujalsharma21)

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

**Built with 🖤 using Python, FastAPI, and vanilla JS**

⭐ **Star this repo if you found it useful!**

[🚀 Try the Live Demo](https://tempmail-agent.netlify.app/)

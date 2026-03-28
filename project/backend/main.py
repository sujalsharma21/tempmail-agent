import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from config import CORS_ORIGINS
from db.connection import init_db
from services.email_service import create_temp_email, fetch_inbox
from services.otp_service import extract_and_store_otps, get_latest_otp

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initialising database...")
    init_db()
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="AI Temp Mail Agent",
    version="1.0.0",
    description="Generate temp emails, fetch inbox, extract OTPs automatically.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tempmail-agent.netlify.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Health ──────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok"}


# ── Email ───────────────────────────────────────────────────────────────────

@app.post("/create-email")
async def create_email():
    """Generate a new temporary email address and store in DB."""
    try:
        record = create_temp_email()
        return {
            "success": True,
            "email": record["email"],
            "created_at": str(record["created_at"]),
        }
    except Exception as e:
        logger.error(f"/create-email error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Messages ─────────────────────────────────────────────────────────────────

@app.get("/get-messages")
async def get_messages(email: str = Query(..., description="Temp email address")):
    """Fetch and sync inbox messages for a given email."""
    try:
        messages = fetch_inbox(email)
        # Trigger OTP extraction whenever messages are refreshed
        try:
            extract_and_store_otps(email)
        except Exception:
            pass  # OTP extraction is best-effort

        serialised = []
        for m in messages:
            serialised.append({
                "id": m["id"],
                "sender": m["sender"],
                "subject": m["subject"],
                "body": m["body"],
                "received_at": str(m["received_at"]),
            })
        return {"success": True, "count": len(serialised), "messages": serialised}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"/get-messages error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── OTP ──────────────────────────────────────────────────────────────────────

@app.get("/get-otp")
async def get_otp(email: str = Query(..., description="Temp email address")):
    """Return the most recent extracted OTP for a given email."""
    try:
        otp_record = get_latest_otp(email)
        if not otp_record:
            return {"success": False, "message": "No OTP found yet. Try refreshing the inbox first."}
        return {
            "success": True,
            "otp": otp_record["otp"],
            "type": otp_record["otp_type"],
            "created_at": str(otp_record["created_at"]),
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"/get-otp error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ── Exception handler ────────────────────────────────────────────────────────

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

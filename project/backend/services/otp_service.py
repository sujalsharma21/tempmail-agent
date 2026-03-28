import re
import logging
from db.models import insert_otp, get_messages_by_email_id, get_latest_otp_for_email, get_email_by_address

logger = logging.getLogger(__name__)

# ── Regex patterns ─────────────────────────────────────────────────────────

PATTERNS = {
    "numeric_6":   re.compile(r"\b(\d{6})\b"),
    "numeric_4":   re.compile(r"\b(\d{4})\b"),
    "numeric_8":   re.compile(r"\b(\d{8})\b"),
    "alphanum":    re.compile(r"\b([A-Z0-9]{6,10})\b"),
    "verify_link": re.compile(r'https?://[^\s"<>]+(?:verify|confirm|activate|token)[^\s"<>]*', re.IGNORECASE),
}


def extract_otp(text: str) -> dict:
    """
    Extract OTP or verification link from text.
    Returns {'otp': str, 'type': str} or empty dict.
    """
    # Prioritize 6-digit OTPs (most common)
    for label, pattern in PATTERNS.items():
        match = pattern.search(text)
        if match:
            return {"otp": match.group(0), "type": label}
    return {}


def extract_and_store_otps(email_address: str) -> list[dict]:
    """
    For all messages of an email, extract OTPs and store in DB.
    Returns list of OTP records.
    """
    record = get_email_by_address(email_address)
    if not record:
        raise ValueError(f"Email {email_address} not in DB")

    messages = get_messages_by_email_id(record["id"])
    results = []

    for msg in messages:
        body = msg.get("body") or ""
        subject = msg.get("subject") or ""
        combined = f"{subject} {body}"

        extracted = extract_otp(combined)
        if extracted:
            saved = insert_otp(
                message_id=msg["id"],
                otp=extracted["otp"],
                otp_type=extracted["type"],
            )
            results.append({**saved, "message_subject": subject})

    return results


def get_latest_otp(email_address: str) -> dict | None:
    record = get_email_by_address(email_address)
    if not record:
        raise ValueError(f"Email {email_address} not in DB")
    return get_latest_otp_for_email(record["id"])

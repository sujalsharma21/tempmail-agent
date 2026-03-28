import random
import string
import requests
import logging
from config import MAILTM_BASE_URL
from db.models import insert_email, get_email_by_address, insert_message, get_messages_by_email_id

logger = logging.getLogger(__name__)


def _random_string(length=10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))


def _get_domain() -> str:
    """Fetch a valid mail.tm domain."""
    resp = requests.get(f"{MAILTM_BASE_URL}/domains", timeout=10)
    resp.raise_for_status()
    domains = resp.json().get("hydra:member", [])
    if not domains:
        raise ValueError("No domains available from mail.tm")
    return domains[0]["domain"]


def create_temp_email() -> dict:
    """
    Creates a new mail.tm account and stores it in DB.
    Returns email record dict.
    """
    domain = _get_domain()
    username = _random_string(10)
    email = f"{username}@{domain}"
    password = _random_string(16)

    # Register account
    resp = requests.post(
        f"{MAILTM_BASE_URL}/accounts",
        json={"address": email, "password": password},
        timeout=10,
    )
    resp.raise_for_status()

    # Get auth token
    token_resp = requests.post(
        f"{MAILTM_BASE_URL}/token",
        json={"address": email, "password": password},
        timeout=10,
    )
    token_resp.raise_for_status()
    token = token_resp.json().get("token", "")

    record = insert_email(email, password, token)
    logger.info(f"Created temp email: {email}")
    return record


def fetch_inbox(email_address: str) -> list[dict]:
    """
    Fetches messages from mail.tm for the given address and syncs to DB.
    Returns list of message dicts.
    """
    record = get_email_by_address(email_address)
    if not record:
        raise ValueError(f"Email {email_address} not found in DB")

    token = record["token"]
    email_id = record["id"]

    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{MAILTM_BASE_URL}/messages", headers=headers, timeout=10)
    resp.raise_for_status()

    raw_messages = resp.json().get("hydra:member", [])
    stored = []

    for msg in raw_messages:
        msg_id = msg.get("id", "")
        # Fetch full message body
        detail_resp = requests.get(
            f"{MAILTM_BASE_URL}/messages/{msg_id}",
            headers=headers,
            timeout=10,
        )
        if detail_resp.status_code != 200:
            continue

        detail = detail_resp.json()
        sender = detail.get("from", {}).get("address", "unknown")
        subject = detail.get("subject", "(no subject)")
        body = detail.get("text", detail.get("html", ""))

        saved = insert_message(email_id, msg_id, sender, subject, body)
        if saved:
            stored.append(saved)

    # Return all messages from DB (includes previously fetched)
    return get_messages_by_email_id(email_id)

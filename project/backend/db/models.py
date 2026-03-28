from db.connection import get_db


# ── Emails ─────────────────────────────────────────────────────────────────

def insert_email(email: str, password: str, token: str) -> dict:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO emails (email, password, token)
                VALUES (%s, %s, %s)
                ON CONFLICT (email) DO UPDATE SET token = EXCLUDED.token
                RETURNING *
                """,
                (email, password, token),
            )
            return dict(cur.fetchone())


def get_email_by_address(email: str) -> dict | None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM emails WHERE email = %s", (email,))
            row = cur.fetchone()
            return dict(row) if row else None


def get_all_emails() -> list[dict]:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM emails ORDER BY created_at DESC")
            return [dict(r) for r in cur.fetchall()]


# ── Messages ────────────────────────────────────────────────────────────────

def insert_message(email_id: int, mail_tm_id: str, sender: str, subject: str, body: str) -> dict:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO messages (email_id, mail_tm_id, sender, subject, body)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING *
                """,
                (email_id, mail_tm_id, sender, subject, body),
            )
            row = cur.fetchone()
            return dict(row) if row else {}


def get_messages_by_email_id(email_id: int) -> list[dict]:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM messages WHERE email_id = %s ORDER BY received_at DESC",
                (email_id,),
            )
            return [dict(r) for r in cur.fetchall()]


# ── OTPs ────────────────────────────────────────────────────────────────────

def insert_otp(message_id: int, otp: str, otp_type: str = "numeric") -> dict:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO otps (message_id, otp, otp_type) VALUES (%s, %s, %s) RETURNING *",
                (message_id, otp, otp_type),
            )
            return dict(cur.fetchone())


def get_otps_by_message_id(message_id: int) -> list[dict]:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT * FROM otps WHERE message_id = %s ORDER BY created_at DESC",
                (message_id,),
            )
            return [dict(r) for r in cur.fetchall()]


def get_latest_otp_for_email(email_id: int) -> dict | None:
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT o.* FROM otps o
                JOIN messages m ON o.message_id = m.id
                WHERE m.email_id = %s
                ORDER BY o.created_at DESC
                LIMIT 1
                """,
                (email_id,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

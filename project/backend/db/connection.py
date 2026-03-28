import psycopg2
import psycopg2.extras
import logging
from contextlib import contextmanager
from config import DB_CONFIG

logger = logging.getLogger(__name__)


def get_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=psycopg2.extras.RealDictCursor)


@contextmanager
def get_db():
    conn = None
    try:
        conn = get_connection()
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        logger.error(f"DB error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_db():
    """Create tables if they don't exist."""
    sql = """
    CREATE TABLE IF NOT EXISTS emails (
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        token TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS messages (
        id SERIAL PRIMARY KEY,
        email_id INTEGER REFERENCES emails(id) ON DELETE CASCADE,
        mail_tm_id TEXT,
        sender TEXT,
        subject TEXT,
        body TEXT,
        received_at TIMESTAMP DEFAULT NOW()
    );

    CREATE TABLE IF NOT EXISTS otps (
        id SERIAL PRIMARY KEY,
        message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
        otp TEXT,
        otp_type TEXT DEFAULT 'numeric',
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
    logger.info("Database initialized.")

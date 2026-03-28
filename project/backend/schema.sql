-- AI Temp Mail Agent — PostgreSQL Schema
-- Run this manually or let init_db() handle it on startup

CREATE TABLE IF NOT EXISTS emails (
    id         SERIAL PRIMARY KEY,
    email      TEXT NOT NULL UNIQUE,
    password   TEXT NOT NULL,
    token      TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS messages (
    id          SERIAL PRIMARY KEY,
    email_id    INTEGER REFERENCES emails(id) ON DELETE CASCADE,
    mail_tm_id  TEXT,
    sender      TEXT,
    subject     TEXT,
    body        TEXT,
    received_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS otps (
    id         SERIAL PRIMARY KEY,
    message_id INTEGER REFERENCES messages(id) ON DELETE CASCADE,
    otp        TEXT,
    otp_type   TEXT DEFAULT 'numeric',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_messages_email_id ON messages(email_id);
CREATE INDEX IF NOT EXISTS idx_otps_message_id   ON otps(message_id);

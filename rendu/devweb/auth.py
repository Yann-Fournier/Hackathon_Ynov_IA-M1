"""
Magic-link email authentication for the Streamlit chat app, plus
per-user conversation history storage.

No passwords, no JWT: a login is just a single-use, time-limited token
emailed to the user. Once verified, the email address becomes the key
used to load/save that user's conversation history (data/history.json).

Storage is plain JSON files under data/ (gitignored) - enough for a
hackathon demo, not meant to survive concurrent writers at scale.
"""

from __future__ import annotations

import json
import logging
import os
import secrets
import smtplib
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent / "data"
USERS_FILE = DATA_DIR / "users.json"
TOKENS_FILE = DATA_DIR / "tokens.json"
HISTORY_FILE = DATA_DIR / "history.json"

TOKEN_TTL_MINUTES = 15


@dataclass
class MailSettings:
    smtp_host: str = os.environ.get("SMTP_HOST", "smtp-relay.brevo.com")
    smtp_port: int = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user: str = os.environ.get("SMTP_USER", "")
    smtp_password: str = os.environ.get("SMTP_PASSWORD", "")
    mail_from: str = os.environ.get("MAIL_FROM", "techcorp@example.com")
    mail_enabled: bool = os.environ.get("MAIL_ENABLED", "false").lower() == "true"
    frontend_url: str = os.environ.get("FRONTEND_URL", "http://localhost:8501")


settings = MailSettings()


def _load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_json(path: Path, data: dict) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _send_mail(to: str, subject: str, html: str) -> None:
    if not settings.mail_enabled:
        logger.info("Mail disabled - would send '%s' to %s", subject, to)
        return

    message = MIMEMultipart("alternative")
    message["From"] = settings.mail_from
    message["To"] = to
    message["Subject"] = subject
    message.attach(MIMEText(html, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as smtp:
        smtp.starttls()
        smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)
    logger.info("Sent '%s' to %s", subject, to)


def request_magic_link(email: str) -> str:
    """Create a login token for `email` and email it. Returns the magic
    link (so the caller can display it directly when MAIL_ENABLED=false)."""
    email = email.strip().lower()

    users = _load_json(USERS_FILE)
    if email not in users:
        users[email] = {"created_at": datetime.now(timezone.utc).isoformat()}
        _save_json(USERS_FILE, users)

    token = secrets.token_urlsafe(32)
    tokens = _load_json(TOKENS_FILE)
    tokens[token] = {
        "email": email,
        "expires_at": (datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MINUTES)).isoformat(),
        "used": False,
    }
    _save_json(TOKENS_FILE, tokens)

    link = f"{settings.frontend_url}/?token={token}"
    html = f"""
    <h2>Votre lien de connexion TechCorp AI</h2>
    <p>Cliquez sur le lien ci-dessous pour vous connecter. Il expire dans {TOKEN_TTL_MINUTES} minutes.</p>
    <p><a href="{link}">Se connecter</a></p>
    <p>Ou copiez : {link}</p>
    """
    _send_mail(to=email, subject="Votre lien de connexion", html=html)
    return link


def verify_token(token: str) -> str | None:
    """Validate a token (not used, not expired). Returns the email on
    success and marks the token as used, or None if invalid."""
    tokens = _load_json(TOKENS_FILE)
    entry = tokens.get(token)
    if not entry or entry["used"]:
        return None

    expires_at = datetime.fromisoformat(entry["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        return None

    entry["used"] = True
    _save_json(TOKENS_FILE, tokens)
    return entry["email"]


def load_history(email: str) -> list[dict]:
    history = _load_json(HISTORY_FILE)
    return history.get(email, [])


def save_history(email: str, messages: list[dict]) -> None:
    history = _load_json(HISTORY_FILE)
    history[email] = messages
    _save_json(HISTORY_FILE, history)

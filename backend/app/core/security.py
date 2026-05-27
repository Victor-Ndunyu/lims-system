import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.session import UserSession
from app.models.user import User


def hash_password(password: str) -> str:
    """Hash password using bcrypt directly (avoids passlib compatibility issues)."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')


def verify_password(password: str, password_hash: str) -> bool:
    """Verify password using bcrypt directly (avoids passlib compatibility issues)."""
    password_bytes = password.encode('utf-8')
    hash_bytes = password_hash.encode('utf-8')
    try:
        return bcrypt.checkpw(password_bytes, hash_bytes)
    except ValueError:
        return False


def create_session_token() -> str:
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_user_session(db: Session, user: User, device_info: str | None = None) -> tuple[str, UserSession]:
    token = create_session_token()
    token_hash = hash_session_token(token)
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    session = UserSession(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
        device_info=device_info,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return token, session


def get_user_session_by_token(db: Session, token: str) -> UserSession | None:
    token_hash = hash_session_token(token)
    return db.query(UserSession).filter(UserSession.token_hash == token_hash).first()


def revoke_user_session(db: Session, session: UserSession) -> None:
    db.delete(session)
    db.commit()

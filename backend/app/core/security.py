import uuid
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings
from app.core.exceptions import TokenExpiredError, TokenInvalidError


def hash_token(token: str) -> str:
    return bcrypt.hashpw(token.encode(), bcrypt.gensalt(rounds=10)).decode()


def verify_token(token: str, hashed: str) -> bool:
    return bcrypt.checkpw(token.encode(), hashed.encode())


def create_access_token(user_id: uuid.UUID, device_id: uuid.UUID) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "did": str(device_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.AUTH.JWT_EXPIRY_MINUTES),
        "jti": str(uuid.uuid4()),
    }
    return jwt.encode(payload, settings.AUTH.JWT_SECRET, algorithm=settings.AUTH.JWT_ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.AUTH.JWT_SECRET,
            algorithms=[settings.AUTH.JWT_ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise TokenInvalidError()


def create_refresh_token() -> str:
    return str(uuid.uuid4())

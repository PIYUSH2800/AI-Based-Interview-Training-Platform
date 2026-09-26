import os
import secrets
import logging
from datetime import datetime, timezone, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("auth")

# ---------------------------------------------------------------------------
# Secret key — MUST be set via environment variable.
# Never fall back to a hardcoded default in any environment.
# ---------------------------------------------------------------------------
_KNOWN_INSECURE_DEFAULT = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

SECRET_KEY: str = os.getenv("SECRET_KEY", "")

if not SECRET_KEY or SECRET_KEY == _KNOWN_INSECURE_DEFAULT:
    _env = os.getenv("ENVIRONMENT", "development").lower()
    if _env in ("production", "staging"):
        # Hard-fail in production/staging: a missing or default key is a critical
        # security misconfiguration.
        raise RuntimeError(
            "CRITICAL: SECRET_KEY is not set or uses the insecure default value. "
            "Set a strong, unique SECRET_KEY environment variable before starting the server."
        )
    else:
        # Development/test: generate a random key for this session and warn loudly.
        SECRET_KEY = secrets.token_hex(32)
        logger.warning(
            "WARNING: SECRET_KEY is not configured. A random key has been generated for "
            "this session only. All existing JWT tokens are now invalid. "
            "Set SECRET_KEY in your .env file to persist sessions across restarts."
        )

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

import bcrypt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        p_bytes = plain_password.encode("utf-8")[:72]
        h_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(p_bytes, h_bytes)
    except Exception:
        return False


def get_password_hash(password: str) -> str:
    p_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(p_bytes, salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

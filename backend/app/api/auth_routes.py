import secrets
import hashlib
import time
from collections import defaultdict
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.auth.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from app.services.email_service import email_service

router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"]
)

# ---------------------------------------------------------------------------
# In-memory sliding-window rate limiter for password reset requests
# ---------------------------------------------------------------------------
_reset_request_history = defaultdict(list)
_RATE_LIMIT_WINDOW_SECONDS = 600  # 10 minutes
_RATE_LIMIT_MAX_REQUESTS = 5      # 5 requests per window

def check_reset_rate_limit(key: str) -> bool:
    now = time.time()
    timestamps = _reset_request_history[key]
    _reset_request_history[key] = [t for t in timestamps if now - t < _RATE_LIMIT_WINDOW_SECONDS]
    if len(_reset_request_history[key]) >= _RATE_LIMIT_MAX_REQUESTS:
        return False
    _reset_request_history[key].append(now)
    return True

def clear_reset_rate_limits():
    """Testing helper to clear rate limit dictionary."""
    _reset_request_history.clear()


@router.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        education=user.education,
        experience_level=user.experience_level
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Also create an empty profile for the user
    db_profile = models.Profile(user_id=db_user.id)
    db.add(db_profile)
    db.commit()
    
    return db_user

@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/forgot-password", response_model=schemas.ForgotPasswordResponse)
def forgot_password(
    req: schemas.ForgotPasswordRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    normalized_email = req.email.strip().lower()
    client_ip = request.client.host if request.client else "unknown"
    rate_key = f"{client_ip}:{normalized_email}"

    if not check_reset_rate_limit(rate_key):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many password reset requests. Please wait a few minutes before trying again."
        )

    generic_message = "If an account exists with this email, a password reset link has been sent."

    # Look up user case-insensitively
    user = db.query(models.User).filter(func.lower(models.User.email) == normalized_email).first()
    if user:
        # Generate cryptographically secure random token (256-bit entropy)
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()

        now_utc = datetime.now(timezone.utc)
        expires_at = now_utc + timedelta(minutes=20)

        # Invalidate previous unused reset tokens for this user
        db.query(models.PasswordResetToken).filter(
            models.PasswordResetToken.user_id == user.id,
            models.PasswordResetToken.used_at.is_(None)
        ).update({"used_at": now_utc}, synchronize_session=False)

        # Store only hashed token in database
        new_token_record = models.PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
            created_at=now_utc
        )
        db.add(new_token_record)
        db.commit()

        # Send password reset email via service
        email_service.send_password_reset_email(user.email, raw_token)

    return {"message": generic_message}


@router.post("/reset-password", response_model=schemas.ResetPasswordResponse)
def reset_password(
    req: schemas.ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    if len(req.new_password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long."
        )

    # Hash incoming token to match stored hash
    token_hash = hashlib.sha256(req.token.strip().encode("utf-8")).hexdigest()

    token_record = db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.token_hash == token_hash
    ).first()

    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token."
        )

    if token_record.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset token has already been used."
        )

    now_utc = datetime.now(timezone.utc)
    record_exp = token_record.expires_at
    if record_exp.tzinfo is None:
        record_exp = record_exp.replace(tzinfo=timezone.utc)

    if now_utc > record_exp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired."
        )

    user = db.query(models.User).filter(models.User.id == token_record.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account associated with this token no longer exists."
        )

    # Update password using existing bcrypt hashing
    user.password_hash = get_password_hash(req.new_password)
    user.password_changed_at = now_utc

    # Consume token
    token_record.used_at = now_utc

    # Invalidate all other pending tokens for this user
    db.query(models.PasswordResetToken).filter(
        models.PasswordResetToken.user_id == user.id,
        models.PasswordResetToken.id != token_record.id,
        models.PasswordResetToken.used_at.is_(None)
    ).update({"used_at": now_utc}, synchronize_session=False)

    db.commit()

    return {"message": "Password has been successfully reset. You can now log in with your new password."}

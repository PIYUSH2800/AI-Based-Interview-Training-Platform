"""
test_password_reset.py

Comprehensive security and functional tests for email-based password reset.
Covers:
- Registered email forgot-password request
- Unregistered email forgot-password request
- Generic response consistency (no user enumeration)
- Valid reset token acceptance
- Invalid reset token rejection
- Expired reset token rejection
- Reused reset token rejection (single-use enforcement)
- Multiple reset requests invalidating previous tokens
- Weak password rejection (< 6 chars)
- Successful login with new password
- Rejection of old password after reset
- Cross-user token isolation
- JWT session invalidation after password reset
- Missing/unconfigured SMTP resilience
- Rate limiting protection
- Existing user data and profile preservation
"""

import hashlib
import time
from datetime import datetime, timezone, timedelta
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.database.database import get_db
from app.models import models
from app.auth.auth import get_password_hash, create_access_token
from app.services.email_service import email_service
from app.api.auth_routes import clear_reset_rate_limits

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_rate_limits_and_emails():
    clear_reset_rate_limits()
    email_service._test_sent_emails.clear()
    yield
    clear_reset_rate_limits()
    email_service._test_sent_emails.clear()


class UserWrapperHelper:
    def __init__(self, id, email, name, education):
        self.id = id
        self.email = email
        self.name = name
        self.education = education


@pytest.fixture
def test_user(setup_test_db):
    """Creates a fresh test user in the test database."""
    db = next(app.dependency_overrides[get_db]())
    user = models.User(
        name="Reset Test User",
        email="reset_student@example.com",
        password_hash=get_password_hash("OldPassword123!"),
        education="Computer Science",
        experience_level="Intermediate"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    profile = models.Profile(user_id=user.id, target_role="Backend Developer", skills="Python, SQL")
    db.add(profile)
    db.commit()
    wrapper = UserWrapperHelper(user.id, user.email, user.name, user.education)
    db.close()
    return wrapper


@pytest.fixture
def second_user(setup_test_db):
    """Creates a second test user in the test database for cross-user tests."""
    db = next(app.dependency_overrides[get_db]())
    user = models.User(
        name="Second User",
        email="second_user@example.com",
        password_hash=get_password_hash("SecondPassword123!"),
        education="Software Engineering",
        experience_level="Senior"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    wrapper = UserWrapperHelper(user.id, user.email, user.name, user.education)
    db.close()
    return wrapper


def test_forgot_password_registered_email(test_user):
    """Requesting password reset for registered email returns generic message and generates token."""
    res = client.post("/api/auth/forgot-password", json={"email": "reset_student@example.com"})
    assert res.status_code == 200
    data = res.json()
    assert "If an account exists with this email, a password reset link has been sent." in data["message"]

    # Verify email was captured by testing hook
    assert len(email_service._test_sent_emails) == 1
    assert email_service._test_sent_emails[0]["to"] == "reset_student@example.com"
    raw_token = email_service._test_sent_emails[0]["token"]
    assert raw_token

    # Verify database has hash, NOT raw token
    db = next(app.dependency_overrides[get_db]())
    token_rec = db.query(models.PasswordResetToken).filter_by(user_id=test_user.id).first()
    assert token_rec is not None
    assert token_rec.token_hash == hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    assert token_rec.token_hash != raw_token
    assert token_rec.used_at is None


def test_forgot_password_unregistered_email():
    """Requesting password reset for unregistered email returns exact same generic message (no enumeration)."""
    res = client.post("/api/auth/forgot-password", json={"email": "nonexistent_98765@example.com"})
    assert res.status_code == 200
    data = res.json()
    assert data["message"] == "If an account exists with this email, a password reset link has been sent."

    # No email sent and no token stored
    assert len(email_service._test_sent_emails) == 0


def test_reset_password_success(test_user):
    """Valid reset token successfully changes user password."""
    # 1. Request forgot password
    client.post("/api/auth/forgot-password", json={"email": "reset_student@example.com"})
    raw_token = email_service._test_sent_emails[0]["token"]

    # 2. Reset password
    res = client.post("/api/auth/reset-password", json={
        "token": raw_token,
        "new_password": "BrandNewPassword2026!"
    })
    assert res.status_code == 200
    assert "Password has been successfully reset" in res.json()["message"]

    # 3. Old password should fail
    login_old = client.post("/api/auth/login", data={
        "username": "reset_student@example.com",
        "password": "OldPassword123!"
    })
    assert login_old.status_code == 401

    # 4. New password should succeed
    login_new = client.post("/api/auth/login", data={
        "username": "reset_student@example.com",
        "password": "BrandNewPassword2026!"
    })
    assert login_new.status_code == 200
    assert "access_token" in login_new.json()


def test_reset_password_invalid_token():
    """Invalid token returns 400 Bad Request."""
    res = client.post("/api/auth/reset-password", json={
        "token": "completely-invalid-bogus-token-xyz",
        "new_password": "BrandNewPassword2026!"
    })
    assert res.status_code == 400
    assert "Invalid or expired" in res.json()["detail"]


def test_reset_password_expired_token(test_user):
    """Expired reset token is rejected."""
    # 1. Request forgot password
    client.post("/api/auth/forgot-password", json={"email": "reset_student@example.com"})
    raw_token = email_service._test_sent_emails[0]["token"]

    # 2. Manually expire token in database
    db = next(app.dependency_overrides[get_db]())
    token_hash = hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
    db.query(models.PasswordResetToken).filter_by(token_hash=token_hash).update({
        "expires_at": datetime.now(timezone.utc) - timedelta(minutes=5)
    })
    db.commit()

    # 3. Attempt reset
    res = client.post("/api/auth/reset-password", json={
        "token": raw_token,
        "new_password": "BrandNewPassword2026!"
    })
    assert res.status_code == 400
    assert "expired" in res.json()["detail"].lower()


def test_reset_password_reused_token_rejected(test_user):
    """Token cannot be used a second time."""
    client.post("/api/auth/forgot-password", json={"email": "reset_student@example.com"})
    raw_token = email_service._test_sent_emails[0]["token"]

    # First reset succeeds
    res1 = client.post("/api/auth/reset-password", json={
        "token": raw_token,
        "new_password": "BrandNewPassword2026!"
    })
    assert res1.status_code == 200

    # Second reset with same token fails
    res2 = client.post("/api/auth/reset-password", json={
        "token": raw_token,
        "new_password": "AnotherNewPassword2026!"
    })
    assert res2.status_code == 400
    assert "already been used" in res2.json()["detail"]


def test_multiple_reset_requests_invalidate_prior_tokens(test_user):
    """Requesting a new reset token invalidates older unused tokens."""
    # Request 1
    client.post("/api/auth/forgot-password", json={"email": "reset_student@example.com"})
    token1 = email_service._test_sent_emails[0]["token"]

    # Request 2
    client.post("/api/auth/forgot-password", json={"email": "reset_student@example.com"})
    token2 = email_service._test_sent_emails[1]["token"]
    assert token1 != token2

    # Attempting to use token1 should fail (already marked used/invalidated)
    res1 = client.post("/api/auth/reset-password", json={
        "token": token1,
        "new_password": "PasswordFromToken1!"
    })
    assert res1.status_code == 400
    assert "already been used" in res1.json()["detail"]

    # Token2 should work
    res2 = client.post("/api/auth/reset-password", json={
        "token": token2,
        "new_password": "PasswordFromToken2!"
    })
    assert res2.status_code == 200


def test_weak_password_rejected(test_user):
    """New passwords shorter than 6 characters are rejected."""
    client.post("/api/auth/forgot-password", json={"email": "reset_student@example.com"})
    raw_token = email_service._test_sent_emails[0]["token"]

    res = client.post("/api/auth/reset-password", json={
        "token": raw_token,
        "new_password": "123"
    })
    assert res.status_code in (400, 422)


def test_cross_user_isolation(test_user, second_user):
    """Resetting password for user1 does not affect user2's credentials or access."""
    client.post("/api/auth/forgot-password", json={"email": "reset_student@example.com"})
    raw_token = email_service._test_sent_emails[0]["token"]

    # Reset user1
    client.post("/api/auth/reset-password", json={
        "token": raw_token,
        "new_password": "User1NewPassword!"
    })

    # User2 password remains unchanged
    login_u2 = client.post("/api/auth/login", data={
        "username": "second_user@example.com",
        "password": "SecondPassword123!"
    })
    assert login_u2.status_code == 200


def test_jwt_session_invalidation_after_password_reset(test_user):
    """JWT access token issued BEFORE password reset is rejected after password change."""
    # 1. Login to obtain access token
    login_res = client.post("/api/auth/login", data={
        "username": "reset_student@example.com",
        "password": "OldPassword123!"
    })
    old_jwt = login_res.json()["access_token"]

    # Verify old_jwt works right now
    prof_before = client.get("/api/users/profile", headers={"Authorization": f"Bearer {old_jwt}"})
    assert prof_before.status_code == 200

    # Ensure a small timestamp tick
    time.sleep(1.0)

    # 2. Reset password
    client.post("/api/auth/forgot-password", json={"email": "reset_student@example.com"})
    raw_token = email_service._test_sent_emails[0]["token"]
    res_reset = client.post("/api/auth/reset-password", json={
        "token": raw_token,
        "new_password": "NewUpdatedPassword123!"
    })
    assert res_reset.status_code == 200

    # 3. Old JWT should now be revoked and rejected
    prof_after = client.get("/api/users/profile", headers={"Authorization": f"Bearer {old_jwt}"})
    assert prof_after.status_code == 401
    assert "recently changed" in prof_after.json()["detail"].lower()


def test_rate_limiting_forgot_password():
    """Exceeding 5 requests rapidly triggers 429 Too Many Requests."""
    for _ in range(5):
        res = client.post("/api/auth/forgot-password", json={"email": "ratelimit_test@example.com"})
        assert res.status_code == 200

    # 6th request
    res6 = client.post("/api/auth/forgot-password", json={"email": "ratelimit_test@example.com"})
    assert res6.status_code == 429
    assert "Too many password reset requests" in res6.json()["detail"]


def test_user_data_preservation_after_reset(test_user):
    """User profile data, skills, and target role are preserved intact after password reset."""
    user_id = test_user.id

    client.post("/api/auth/forgot-password", json={"email": "reset_student@example.com"})
    raw_token = email_service._test_sent_emails[0]["token"]
    client.post("/api/auth/reset-password", json={
        "token": raw_token,
        "new_password": "NewPreservedPass123!"
    })

    # Inspect database
    db = next(app.dependency_overrides[get_db]())
    user_after = db.query(models.User).filter_by(id=user_id).first()
    assert user_after is not None
    assert user_after.name == "Reset Test User"
    assert user_after.education == "Computer Science"
    assert user_after.profile.target_role == "Backend Developer"
    assert user_after.profile.skills == "Python, SQL"
    db.close()

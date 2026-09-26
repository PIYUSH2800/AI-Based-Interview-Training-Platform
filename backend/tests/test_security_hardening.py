"""
Checkpoint 8B — Security Hardening & Configuration Audit Tests

Covers:
- AUTH: SECRET_KEY not hardcoded / default
- AUTH: JWT tokens use timezone-aware expiry
- AUTH: Password hashing behaves correctly
- CORS: allow_origins no longer uses wildcard '*'
- SCHEMAS: No Pydantic v2 class-based Config usage (ConfigDict only)
- RESUME: Path traversal guards in download endpoint
- ENV: .env.example does not contain the old insecure default key
- ENV: .env file exists and has a non-empty SECRET_KEY
"""

import os
import sys
import importlib
import inspect
import pytest
from datetime import timezone

# ── resolve paths ───────────────────────────────────────────────────────────
# __file__ lives at  <project>/backend/tests/test_security_hardening.py
TESTS_DIR    = os.path.abspath(os.path.dirname(__file__))          # …/backend/tests
BACKEND_ROOT = os.path.abspath(os.path.join(TESTS_DIR, ".."))     # …/backend
PROJECT_ROOT = os.path.abspath(os.path.join(BACKEND_ROOT, ".."))  # …/AI_interview_platform
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

# ---------------------------------------------------------------------------
# 1. AUTH — SECRET_KEY validation
# ---------------------------------------------------------------------------

class TestSecretKeyHardening:
    _KNOWN_INSECURE = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

    def _get_secret_key(self):
        # Force a fresh import so environment manipulations take effect
        if "app.auth.auth" in sys.modules:
            del sys.modules["app.auth.auth"]
        from app.auth import auth as auth_module
        return auth_module.SECRET_KEY

    def test_secret_key_not_empty(self):
        key = self._get_secret_key()
        assert key, "SECRET_KEY must not be empty"

    def test_secret_key_is_not_known_insecure_default(self):
        key = self._get_secret_key()
        assert key != self._KNOWN_INSECURE, (
            "SECRET_KEY must not be the publicly-known insecure default. "
            "Set a unique value in your .env file."
        )

    def test_secret_key_minimum_length(self):
        """A hex-encoded 32-byte (256-bit) key is 64 characters long."""
        key = self._get_secret_key()
        assert len(key) >= 32, (
            f"SECRET_KEY is only {len(key)} chars. Use at least 32 chars (64 recommended)."
        )


# ---------------------------------------------------------------------------
# 2. AUTH — JWT token expiry uses timezone-aware datetime
# ---------------------------------------------------------------------------

class TestJWTTokenSecurity:
    def _create_token(self):
        if "app.auth.auth" in sys.modules:
            del sys.modules["app.auth.auth"]
        from app.auth.auth import create_access_token
        from jose import jwt as jose_jwt
        from app.auth.auth import SECRET_KEY, ALGORITHM
        token = create_access_token({"sub": "test@example.com"})
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload

    def test_token_has_exp_claim(self):
        payload = self._create_token()
        assert "exp" in payload, "JWT must contain an 'exp' (expiry) claim"

    def test_token_has_sub_claim(self):
        payload = self._create_token()
        assert payload.get("sub") == "test@example.com"

    def test_create_access_token_source_uses_timezone_aware(self):
        """Verify the source of create_access_token does not call deprecated utcnow()."""
        if "app.auth.auth" in sys.modules:
            del sys.modules["app.auth.auth"]
        import app.auth.auth as auth_mod
        source = inspect.getsource(auth_mod.create_access_token)
        assert "utcnow" not in source, (
            "create_access_token must not use deprecated datetime.utcnow(). "
            "Use datetime.now(timezone.utc) instead."
        )


# ---------------------------------------------------------------------------
# 3. AUTH — Password hashing
# ---------------------------------------------------------------------------

class TestPasswordHashing:
    def test_hash_and_verify_roundtrip(self):
        from app.auth.auth import get_password_hash, verify_password
        pw = "SecureP@ssword123"
        hashed = get_password_hash(pw)
        assert verify_password(pw, hashed), "Password should verify against its hash"

    def test_wrong_password_rejected(self):
        from app.auth.auth import get_password_hash, verify_password
        hashed = get_password_hash("correct_password")
        assert not verify_password("wrong_password", hashed), "Wrong password must not verify"

    def test_hash_is_not_plaintext(self):
        from app.auth.auth import get_password_hash
        pw = "plaintext_password"
        hashed = get_password_hash(pw)
        assert hashed != pw, "Hash must never equal the plaintext password"


# ---------------------------------------------------------------------------
# 4. CORS — No wildcard origin
# ---------------------------------------------------------------------------

class TestCORSHardening:
    def test_cors_allowed_origins_not_wildcard(self):
        """The app must not configure allow_origins=['*']."""
        if "app.main" in sys.modules:
            del sys.modules["app.main"]
        import app.main as main_mod
        source = inspect.getsource(main_mod)
        # The string allow_origins=["*"] or allow_origins=['*'] must not appear
        assert '"*"' not in source or 'allow_origins=["*"]' not in source, (
            "CORS must not use allow_origins=[\"*\"]. "
            "Restrict to specific allowed origins."
        )
        # More specific: look for the pattern allow_origins=["*"]
        assert 'allow_origins=["*"]' not in source, (
            'CORS wildcard allow_origins=["*"] is forbidden.'
        )

    def test_cors_uses_env_or_localhost_defaults(self):
        """Allowed origins must be a concrete list, not a catch-all."""
        if "app.main" in sys.modules:
            del sys.modules["app.main"]
        import app.main as main_mod
        # Check that localhost appears in source as a safe dev default
        assert "localhost" in inspect.getsource(main_mod), (
            "CORS configuration should include localhost as a dev default origin."
        )


# ---------------------------------------------------------------------------
# 5. SCHEMAS — Pydantic v2 ConfigDict (no deprecated class-based Config)
# ---------------------------------------------------------------------------

class TestPydanticSchemas:
    def test_no_class_based_config_in_schemas(self):
        """All models in schemas.py must use ConfigDict, not class Config."""
        schemas_path = os.path.join(BACKEND_ROOT, "app", "schemas", "schemas.py")
        with open(schemas_path, "r", encoding="utf-8") as f:
            source = f.read()

        # Check that old-style class Config is not present
        import re
        # Pattern: "    class Config:" inside a BaseModel subclass
        matches = re.findall(r"\bclass Config\b", source)
        assert len(matches) == 0, (
            f"schemas.py still contains {len(matches)} deprecated 'class Config' definitions. "
            "Migrate to ConfigDict."
        )

    def test_configdict_imported_in_schemas(self):
        schemas_path = os.path.join(BACKEND_ROOT, "app", "schemas", "schemas.py")
        with open(schemas_path, "r", encoding="utf-8") as f:
            source = f.read()
        assert "ConfigDict" in source, "schemas.py must import and use ConfigDict from pydantic"


# ---------------------------------------------------------------------------
# 6. RESUME — Path traversal guard in download endpoint
# ---------------------------------------------------------------------------

class TestResumePathTraversalGuard:
    def test_download_endpoint_has_path_traversal_check(self):
        resume_path = os.path.join(BACKEND_ROOT, "app", "api", "resume_routes.py")
        with open(resume_path, "r", encoding="utf-8") as f:
            source = f.read()
        # The download route must check the resolved path starts with UPLOAD_DIR
        assert "UPLOAD_DIR" in source, "resume_routes.py must define UPLOAD_DIR"
        assert "startswith(UPLOAD_DIR)" in source, (
            "Download endpoint must validate resolved path starts within UPLOAD_DIR "
            "to prevent path traversal attacks."
        )

    def test_upload_validates_extension(self):
        resume_path = os.path.join(BACKEND_ROOT, "app", "api", "resume_routes.py")
        with open(resume_path, "r", encoding="utf-8") as f:
            source = f.read()
        assert "ALLOWED_EXTENSIONS" in source, (
            "resume_routes.py must define and check ALLOWED_EXTENSIONS"
        )
        assert "ALLOWED_EXTENSIONS" in source and ".pdf" in source, (
            "Upload must only permit .pdf and .docx file types"
        )

    def test_upload_validates_file_size(self):
        resume_path = os.path.join(BACKEND_ROOT, "app", "api", "resume_routes.py")
        with open(resume_path, "r", encoding="utf-8") as f:
            source = f.read()
        assert "MAX_FILE_SIZE" in source, (
            "resume_routes.py must define and enforce MAX_FILE_SIZE"
        )


# ---------------------------------------------------------------------------
# 7. ENV FILES — Configuration hygiene
# ---------------------------------------------------------------------------

class TestEnvFileHygiene:
    _KNOWN_INSECURE = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

    def _env_path(self):
        return os.path.join(BACKEND_ROOT, ".env")

    def _example_path(self):
        return os.path.join(BACKEND_ROOT, ".env.example")

    def test_env_file_exists(self):
        assert os.path.exists(self._env_path()), (
            "backend/.env file must exist. Copy backend/.env.example to backend/.env "
            "and fill in your values."
        )

    def test_env_file_has_secret_key(self):
        env_path = self._env_path()
        if not os.path.exists(env_path):
            pytest.skip(".env file does not exist")
        with open(env_path, "r") as f:
            content = f.read()
        assert "SECRET_KEY=" in content, ".env must define SECRET_KEY"
        # Extract value
        for line in content.splitlines():
            if line.startswith("SECRET_KEY="):
                value = line.split("=", 1)[1].strip()
                assert value, "SECRET_KEY in .env must not be empty"
                assert value != self._KNOWN_INSECURE, (
                    "SECRET_KEY in .env must not be the known insecure default"
                )
                break

    def test_env_example_does_not_expose_secret_key_value(self):
        example_path = self._example_path()
        if not os.path.exists(example_path):
            pytest.skip(".env.example not found")
        with open(example_path, "r") as f:
            content = f.read()
        assert self._KNOWN_INSECURE not in content, (
            ".env.example must NOT contain the known insecure default SECRET_KEY value. "
            "Remove it to prevent accidental use."
        )

    def test_env_file_is_in_gitignore(self):
        """The .env file must be gitignored at the repo root."""
        root_gitignore = os.path.join(PROJECT_ROOT, ".gitignore")
        if not os.path.exists(root_gitignore):
            pytest.skip("No root .gitignore found")
        with open(root_gitignore, "r") as f:
            content = f.read()
        assert ".env" in content, (
            ".env must be listed in .gitignore to prevent accidental secret exposure"
        )


# ---------------------------------------------------------------------------
# 8. AUTH SOURCE — No deprecated auth module patterns
# ---------------------------------------------------------------------------

class TestAuthSourcePatterns:
    def test_auth_does_not_use_utcnow(self):
        auth_path = os.path.join(BACKEND_ROOT, "app", "auth", "auth.py")
        with open(auth_path, "r", encoding="utf-8") as f:
            source = f.read()
        assert "utcnow()" not in source, (
            "auth.py must not use deprecated datetime.utcnow(). "
            "Use datetime.now(timezone.utc) instead."
        )

    def test_auth_imports_timezone(self):
        auth_path = os.path.join(BACKEND_ROOT, "app", "auth", "auth.py")
        with open(auth_path, "r", encoding="utf-8") as f:
            source = f.read()
        assert "timezone" in source, (
            "auth.py must import and use timezone for timezone-aware datetime."
        )

    def test_auth_has_startup_validation(self):
        """auth.py must validate SECRET_KEY at import time."""
        auth_path = os.path.join(BACKEND_ROOT, "app", "auth", "auth.py")
        with open(auth_path, "r", encoding="utf-8") as f:
            source = f.read()
        assert "RuntimeError" in source or "raise" in source, (
            "auth.py must raise an error when SECRET_KEY is missing or insecure in production."
        )

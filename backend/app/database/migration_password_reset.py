"""
migration_password_reset.py

Explicit, versioned, non-destructive migration for Checkpoint 10I.
- Preserves interview_platform.db and creates local backup before applying changes.
- Adds password_changed_at column to users table if missing.
- Creates password_reset_tokens table if missing.
- Idempotent: safe to run repeatedly without modifying existing data.
"""

import os
import shutil
import logging
from sqlalchemy import text
from app.database.database import engine, Base
import app.models.models  # ensure models are registered

logger = logging.getLogger("db_migration")


def backup_sqlite_db_if_exists(db_path: str = "interview_platform.db") -> str:
    """Creates a local backup copy of the SQLite database before running migration if one does not already exist."""
    abs_path = os.path.abspath(db_path)
    if not os.path.exists(abs_path):
        return ""

    backup_path = f"{abs_path}.backup_checkpoint10i.db"
    if os.path.exists(backup_path):
        logger.info(f"Database backup already exists at: {backup_path} - preserving existing backup.")
        return backup_path

    try:
        shutil.copy2(abs_path, backup_path)
        logger.info(f"Database backup created: {backup_path} ({os.path.getsize(backup_path)} bytes)")
        return backup_path
    except Exception as e:
        logger.warning(f"Could not create database backup: {e}")
        return ""


def run_password_reset_migration(target_engine=None):
    """
    Executes non-destructive schema migration for password reset and account recovery.
    1. Backs up database if local SQLite file and no backup exists yet.
    2. Adds password_changed_at column to users if not present.
    3. Creates password_reset_tokens table with proper indexes and foreign keys.
    """
    eng = target_engine or engine

    # SQLite file backup
    if hasattr(eng, "url") and eng.url.database and eng.url.drivername.startswith("sqlite"):
        db_file = eng.url.database
        if db_file and db_file != ":memory:" and os.path.exists(db_file):
            backup_sqlite_db_if_exists(db_file)

    with eng.connect() as conn:
        # 1. Add password_changed_at column to users if missing
        res = conn.execute(text("PRAGMA table_info(users)"))
        cols = [r[1] for r in res.fetchall()]
        if "password_changed_at" not in cols:
            logger.info("Adding column password_changed_at to users table...")
            conn.execute(text("ALTER TABLE users ADD COLUMN password_changed_at DATETIME"))
            conn.commit()

        # 2. Create password_reset_tokens table if not exists
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash VARCHAR(64) NOT NULL UNIQUE,
                expires_at DATETIME NOT NULL,
                used_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            )
        """))
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_user_id ON password_reset_tokens (user_id)
        """))
        conn.execute(text("""
            CREATE UNIQUE INDEX IF NOT EXISTS ix_password_reset_tokens_token_hash ON password_reset_tokens (token_hash)
        """))
        conn.commit()

    logger.info("Password reset migration completed successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_password_reset_migration()
    print("Migration executed successfully.")

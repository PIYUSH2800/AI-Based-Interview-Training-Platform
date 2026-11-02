

"""
migration_coding_system.py

Explicit, versioned, non-destructive migration for Checkpoint 10C.
- Preserves interview_platform.db and creates local backup before applying changes.
- Creates coding_modules table if missing.
- Adds module_id and order_index columns to coding_problems if missing.
- Idempotent: safe to run repeatedly without modifying existing data.
"""

import os
import shutil
import logging
from sqlalchemy import text
from app.database.database import engine

logger = logging.getLogger("db_migration")


def backup_sqlite_db_if_exists(db_path: str = "interview_platform.db") -> str:
    """Creates a local backup copy of the SQLite database before running migration if one does not already exist."""
    abs_path = os.path.abspath(db_path)
    if not os.path.exists(abs_path):
        return ""

    backup_path = f"{abs_path}.backup_checkpoint10c.db"
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


def run_coding_system_migration(target_engine=None):
    """
    Executes non-destructive schema migration and idempotent data backfill for the progressive coding system.
    1. Backs up database if local SQLite file and no backup exists yet.
    2. Creates coding_modules table with prerequisites and order indices.
    3. Adds module_id and order_index to coding_problems if not present.
    4. Idempotently seeds the 6 core learning modules and backfills module_id and order_index
       for the original six coding problems.
    """
    eng = target_engine or engine

    # SQLite file backup
    if hasattr(eng, "url") and eng.url.database and eng.url.drivername.startswith("sqlite"):
        db_file = eng.url.database
        if db_file and db_file != ":memory:" and os.path.exists(db_file):
            backup_sqlite_db_if_exists(db_file)

    with eng.connect() as conn:
        # 1. Create coding_modules table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS coding_modules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug VARCHAR(50) UNIQUE NOT NULL,
                title VARCHAR(100) NOT NULL,
                description TEXT,
                order_index INTEGER DEFAULT 1,
                icon_name VARCHAR(50) DEFAULT 'Code',
                prerequisite_module_id INTEGER REFERENCES coding_modules(id),
                required_prerequisite_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_coding_modules_slug ON coding_modules (slug);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_coding_modules_id ON coding_modules (id);"))

        # 2. Add columns to coding_problems if missing
        cursor = conn.execute(text("PRAGMA table_info(coding_problems);"))
        existing_cols = {row[1] for row in cursor.fetchall()}

        if "module_id" not in existing_cols:
            logger.info("Migrating coding_problems: adding column module_id")
            conn.execute(text("ALTER TABLE coding_problems ADD COLUMN module_id INTEGER REFERENCES coding_modules(id);"))

        if "order_index" not in existing_cols:
            logger.info("Migrating coding_problems: adding column order_index")
            conn.execute(text("ALTER TABLE coding_problems ADD COLUMN order_index INTEGER DEFAULT 1;"))

        conn.commit()

    # 3. Idempotently seed coding modules and backfill module assignments for existing problems
    from sqlalchemy.orm import Session
    from app.services.coding_progress import seed_coding_system_if_needed

    with Session(bind=eng) as session:
        seed_coding_system_if_needed(session)

    logger.info("Progressive coding system migration and module synchronization applied successfully.")

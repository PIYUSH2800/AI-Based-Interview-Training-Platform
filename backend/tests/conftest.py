import os
import sys

# Ensure backend directory is in sys.path
backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app as fastapi_app
from app.database.database import Base, get_db
import app.models.models  # Ensure all SQLAlchemy models are loaded into Base.metadata

TEST_DATABASE_URL = "sqlite:///./test_runner.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=test_engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override FastAPI DB dependency globally for all test modules
fastapi_app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_test_db():
    """Fixture to ensure all tables are created cleanly before each test and dropped afterwards."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_runner.db"):
        try:
            os.remove("./test_runner.db")
        except Exception:
            pass

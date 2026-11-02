import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.database.database import engine, Base
from app.database.migration_coding_system import run_coding_system_migration
from app.database.migration_password_reset import run_password_reset_migration
from app.api import auth_routes, profile_routes, interview_routes, ai_routes, resume_routes, coding_routes, analytics_routes, module_routes

load_dotenv()

logger = logging.getLogger("main")

# Create database tables and execute non-destructive migrations
Base.metadata.create_all(bind=engine)
run_coding_system_migration(engine)
run_password_reset_migration(engine)

app = FastAPI(
    title="AI Interview Platform API",
    description="Backend API for the AI-Based Interview Training Platform",
    version="1.0.0",
)

# ---------------------------------------------------------------------------
# CORS Configuration
# In development, defaults to allowing localhost frontend origins.
# In production, set ALLOWED_ORIGINS in the environment as a
# comma-separated list of exact origins, e.g.:
#   ALLOWED_ORIGINS=https://yourapp.com,https://www.yourapp.com
# ---------------------------------------------------------------------------
_raw_origins = os.getenv("ALLOWED_ORIGINS", "")
if _raw_origins.strip():
    allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]
    logger.info(f"CORS: restricting to configured origins: {allowed_origins}")
else:
    # Development defaults — localhost on common frontend ports
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ]
    logger.info("CORS: no ALLOWED_ORIGINS set — using development localhost origins.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.include_router(auth_routes.router)
app.include_router(profile_routes.router)
app.include_router(interview_routes.router)
app.include_router(ai_routes.router)
app.include_router(resume_routes.router)
app.include_router(coding_routes.router)
app.include_router(analytics_routes.router)
app.include_router(module_routes.router)


@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Interview Platform API"}

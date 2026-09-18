from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database.database import engine, Base
from app.api import auth_routes, profile_routes, interview_routes, ai_routes, resume_routes

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Interview Platform API",
    description="Backend API for the AI-Based Interview Training Platform",
    version="1.0.0",
)

# CORS Configuration for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this should be specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_routes.router)
app.include_router(profile_routes.router)
app.include_router(interview_routes.router)
app.include_router(ai_routes.router)
app.include_router(resume_routes.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the AI Interview Platform API"}

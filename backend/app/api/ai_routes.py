import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.database.database import get_db
from app.models import models
from app.api.profile_routes import get_current_user
from app.services.ai_service import ai_service
from app.services.resume_parser import extract_text_from_file

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)

class GenerateQuestionRequest(BaseModel):
    job_role: str
    interview_type: str
    difficulty: str
    skills: Optional[str] = ""

class EvaluateAnswerRequest(BaseModel):
    question_text: str
    answer_text: str
    job_role: Optional[str] = "Software Developer"
    interview_type: Optional[str] = "Technical Interview"
    difficulty: Optional[str] = "Intermediate"


@router.get("/status")
def get_status():
    """Returns AI service provider status and active mode (Real AI vs Mock AI)."""
    return ai_service.get_ai_status()


@router.post("/generate-question")
def api_generate_question(
    req: GenerateQuestionRequest, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch candidate profile & resume context if available
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    
    candidate_context = {
        "education": current_user.education or (profile.degree if profile else None),
        "experience_level": current_user.experience_level,
        "skills": req.skills or (profile.skills if profile else ""),
        "target_role": profile.target_role if profile else req.job_role,
        "resume_text": ""
    }

    # Extract resume text if resume uploaded (Checkpoint 3 integration)
    if profile and profile.resume_path:
        full_resume_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", profile.resume_path))
        if os.path.exists(full_resume_path):
            resume_text = extract_text_from_file(full_resume_path)
            candidate_context["resume_text"] = resume_text[:600] # Pass snippet as context

    question = ai_service.generate_question(
        job_role=req.job_role,
        interview_type=req.interview_type,
        difficulty=req.difficulty,
        skills=req.skills or "",
        candidate_context=candidate_context
    )
    
    return {"question": question}


@router.post("/evaluate-answer")
def api_evaluate_answer(
    req: EvaluateAnswerRequest, 
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(models.Profile).filter(models.Profile.user_id == current_user.id).first()
    candidate_context = {
        "education": current_user.education,
        "experience_level": current_user.experience_level,
        "skills": profile.skills if profile else "",
    }

    evaluation = ai_service.evaluate_answer(
        question_text=req.question_text,
        answer_text=req.answer_text,
        job_role=req.job_role,
        interview_type=req.interview_type,
        difficulty=req.difficulty,
        candidate_context=candidate_context
    )
    return evaluation


@router.post("/generate-feedback/{interview_id}")
def api_generate_feedback(
    interview_id: int, 
    current_user: models.User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    interview = db.query(models.Interview).filter(
        models.Interview.id == interview_id, 
        models.Interview.user_id == current_user.id
    ).first()

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    questions = db.query(models.Question).filter(models.Question.interview_id == interview_id).all()
    feedback = ai_service.generate_interview_feedback(questions)

    return feedback

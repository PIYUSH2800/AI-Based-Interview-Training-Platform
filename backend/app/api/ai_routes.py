import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import Dict, Any, Optional, List
from pydantic import BaseModel

from app.database.database import get_db
from app.models import models
from app.api.profile_routes import get_current_user
from app.services.ai_service import ai_service
from app.services.mock_ai_service import generate_adaptive_question_mock
from app.services.resume_parser import extract_text_from_file

router = APIRouter(
    prefix="/api/ai",
    tags=["AI"]
)

DIFFICULTY_LEVELS = ["Easy", "Intermediate", "Hard"]


def normalize_difficulty(diff_str: str) -> str:
    d = (diff_str or "").strip().lower()
    if d in ["easy", "basic", "beginner"]:
        return "Easy"
    if d in ["hard", "advanced"]:
        return "Hard"
    return "Intermediate"


def adjust_difficulty(current_diff: str, recent_score: Optional[float]) -> str:
    current = normalize_difficulty(current_diff)
    if recent_score is None:
        return current
    idx = DIFFICULTY_LEVELS.index(current)
    if recent_score >= 85 and idx < len(DIFFICULTY_LEVELS) - 1:
        return DIFFICULTY_LEVELS[idx + 1]  # Step up difficulty for strong performance
    elif recent_score <= 50 and idx > 0:
        return DIFFICULTY_LEVELS[idx - 1]  # Step down difficulty for weaker performance
    return current


def get_interview_strategy_guidance(interview_type: str, job_role: str) -> str:
    itype = (interview_type or "").strip().lower()
    if "behavioral" in itype:
        return (
            f"Focus on STAR-method past experiences, teamwork, communication, "
            f"leadership, conflict resolution, and handling workplace challenges appropriate for a {job_role}."
        )
    elif "hr" in itype:
        return (
            f"Focus on career goals, motivation, work culture fit, adaptability, "
            f"collaboration, and general professional background for a {job_role}."
        )
    elif "system design" in itype or "design" in itype:
        return (
            f"Focus on system architecture, data modeling, scalability, API design, "
            f"trade-offs, performance, and component organization for a {job_role}."
        )
    else:  # Technical Interview (default)
        return (
            f"Focus on core technical fundamentals, language features, data structures, "
            f"algorithms, problem solving, and hands-on domain knowledge required for a {job_role}."
        )


class GenerateQuestionRequest(BaseModel):
    job_role: str
    interview_type: str
    difficulty: str
    skills: Optional[str] = ""
    interview_id: Optional[int] = None

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
            candidate_context["resume_text"] = resume_text[:600]  # Pass snippet as context

    # Check if adaptive question generation with session history is requested
    if req.interview_id is not None:
        interview = (
            db.query(models.Interview)
            .filter(
                models.Interview.id == req.interview_id,
                models.Interview.user_id == current_user.id,
            )
            .first()
        )
        if not interview:
            raise HTTPException(status_code=404, detail="Interview not found.")

        questions = (
            db.query(models.Question)
            .options(joinedload(models.Question.answer))
            .filter(models.Question.interview_id == req.interview_id)
            .order_by(models.Question.sequence_number)
            .all()
        )

        previous_questions = [q.question_text for q in questions if q.question_text]
        answered_qs = [q for q in questions if q.answer]

        # Topic coverage state calculation
        topics_covered = [q.topic for q in questions if q.topic]
        raw_skills = req.skills or (profile.skills if profile else "")
        candidate_skills_list = [s.strip() for s in raw_skills.split(",") if s.strip()]

        all_candidate_topics = candidate_skills_list or [req.job_role]
        under_covered_topics = [
            t for t in all_candidate_topics
            if not any(t.lower() in (cov or "").lower() for cov in topics_covered)
        ]

        # Identify weak areas from lower scores (score <= 60)
        weak_areas = []
        for q in answered_qs:
            ans = q.answer
            if ans:
                if ans.technical_score is not None and ans.technical_score <= 60:
                    weak_areas.append(f"{q.topic or req.job_role} (technical)")
                elif ans.communication_score is not None and ans.communication_score <= 60:
                    weak_areas.append("Communication & Clarity")
                elif ans.relevance_score is not None and ans.relevance_score <= 60:
                    weak_areas.append("Answer Relevance")

        strategy_guidance = get_interview_strategy_guidance(req.interview_type, req.job_role)

        last_answer_ctx = None
        last_score = None
        if answered_qs:
            last_q = answered_qs[-1]
            last_ans = last_q.answer
            last_score = last_ans.score
            last_answer_ctx = {
                "question_text": last_q.question_text,
                "answer_text": last_ans.answer_text,
                "score": last_ans.score,
                "technical_score": last_ans.technical_score,
                "communication_score": last_ans.communication_score,
                "relevance_score": last_ans.relevance_score,
                "completeness_score": last_ans.completeness_score,
                "feedback": last_ans.feedback,
            }

        # Calculate difficulty adaptation
        adapted_difficulty = adjust_difficulty(req.difficulty, last_score)

        result = ai_service.generate_adaptive_question(
            job_role=req.job_role,
            interview_type=req.interview_type,
            difficulty=adapted_difficulty,
            skills=raw_skills,
            candidate_context=candidate_context,
            previous_questions=previous_questions,
            last_answer_context=last_answer_ctx,
            topics_covered=topics_covered,
            under_covered_topics=under_covered_topics,
            weak_areas=weak_areas,
            interview_strategy_guidance=strategy_guidance,
            category=req.interview_type,
        )

        # Deterministic guardrails validation
        gen_question = (result.get("question") or "").strip()
        gen_q_normalized = " ".join(gen_question.lower().strip().split())
        prev_set = {" ".join(q.lower().strip().split()) for q in previous_questions}

        if not gen_question or gen_q_normalized in prev_set:
            # Fallback to mock deduplicated adaptive question if repeat or empty
            result = generate_adaptive_question_mock(
                job_role=req.job_role,
                interview_type=req.interview_type,
                difficulty=adapted_difficulty,
                skills=raw_skills,
                previous_questions=previous_questions,
                last_answer_context=last_answer_ctx,
                topics_covered=topics_covered,
                under_covered_topics=under_covered_topics,
                category=req.interview_type,
            )

        final_difficulty = normalize_difficulty(result.get("difficulty", adapted_difficulty))
        final_topic = (result.get("topic") or req.job_role).strip()
        final_category = (result.get("category") or req.interview_type).strip()

        return {
            "question": result["question"],
            "difficulty": final_difficulty,
            "topic": final_topic,
            "category": final_category,
            "reason": result.get("reason", "Adapted to previous answer and topic coverage strategy."),
        }

    # Standard non-adaptive fallback generation
    question = ai_service.generate_question(
        job_role=req.job_role,
        interview_type=req.interview_type,
        difficulty=req.difficulty,
        skills=req.skills or "",
        candidate_context=candidate_context
    )
    
    return {
        "question": question,
        "difficulty": req.difficulty,
        "topic": req.job_role,
        "reason": "Initial interview question."
    }


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

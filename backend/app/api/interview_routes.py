from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.api.profile_routes import get_current_user

router = APIRouter(
    prefix="/api/interviews",
    tags=["Interviews"]
)

@router.post("", response_model=schemas.Interview)
def create_interview(interview: schemas.InterviewCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if interview.total_questions not in schemas.ALLOWED_TOTAL_QUESTIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"total_questions must be one of {schemas.ALLOWED_TOTAL_QUESTIONS}, got {interview.total_questions}"
        )
    db_interview = models.Interview(
        user_id=current_user.id,
        job_role=interview.job_role,
        interview_type=interview.interview_type,
        difficulty=interview.difficulty,
        mode=interview.mode,
        total_questions=interview.total_questions
    )
    db.add(db_interview)
    db.commit()
    db.refresh(db_interview)
    return db_interview

@router.get("", response_model=List[schemas.Interview])
def get_interviews(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Interview).filter(models.Interview.user_id == current_user.id).order_by(models.Interview.created_at.desc(), models.Interview.id.desc()).all()

@router.get("/{id}", response_model=schemas.Interview)
def get_interview(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == id, models.Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.get("/{id}/details", response_model=schemas.InterviewDetail)
def get_interview_details(id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == id, models.Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview

@router.post("/{id}/questions", response_model=schemas.Question)
def create_question(id: int, question: schemas.QuestionCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == id, models.Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    db_question = models.Question(
        interview_id=id,
        question_text=question.question_text,
        question_type=question.question_type,
        difficulty=question.difficulty,
        topic=question.topic,
        sequence_number=question.sequence_number
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

@router.post("/{id}/questions/{question_id}/answers", response_model=schemas.Answer)
def save_answer(id: int, question_id: int, answer: schemas.AnswerCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == id, models.Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    question = db.query(models.Question).filter(models.Question.id == question_id, models.Question.interview_id == id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    # Check if answer already exists
    existing_answer = db.query(models.Answer).filter(models.Answer.question_id == question_id).first()
    if existing_answer:
        existing_answer.answer_text = answer.answer_text
        existing_answer.score = answer.score
        existing_answer.technical_score = answer.technical_score
        existing_answer.communication_score = answer.communication_score
        existing_answer.relevance_score = answer.relevance_score
        existing_answer.completeness_score = answer.completeness_score
        existing_answer.feedback = answer.feedback
        db.commit()
        db.refresh(existing_answer)
        return existing_answer
    
    db_answer = models.Answer(
        question_id=question_id,
        answer_text=answer.answer_text,
        score=answer.score,
        technical_score=answer.technical_score,
        communication_score=answer.communication_score,
        relevance_score=answer.relevance_score,
        completeness_score=answer.completeness_score,
        feedback=answer.feedback
    )
    db.add(db_answer)
    db.commit()
    db.refresh(db_answer)
    return db_answer

@router.post("/{id}/complete", response_model=schemas.Interview)
def complete_interview(id: int, payload: dict = {}, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    interview = db.query(models.Interview).filter(models.Interview.id == id, models.Interview.user_id == current_user.id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Calculate overall score across all answered questions
    questions = db.query(models.Question).filter(models.Question.interview_id == id).all()
    scores = []
    for q in questions:
        if q.answer and q.answer.score is not None:
            scores.append(q.answer.score)
            
    if scores:
        interview.overall_score = round(sum(scores) / len(scores), 1)
    else:
        interview.overall_score = 0.0
        
    if "duration" in payload:
        interview.duration = payload["duration"]
        
    db.commit()
    db.refresh(interview)
    return interview


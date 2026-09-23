"""
analytics_routes.py

GET /api/interviews/{interview_id}/communication-analytics

Returns per-answer communication analytics (deterministic) plus optional
AI qualitative feedback for a completed interview owned by the current user.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.database.database import get_db
from app.models import models
from app.schemas import schemas
from app.api.profile_routes import get_current_user
from app.services.communication_analytics import analyze_answer, compute_aggregate
from app.services.ai_service import ai_service

logger = logging.getLogger("analytics_routes")

router = APIRouter(
    prefix="/api/interviews",
    tags=["Analytics"],
)


@router.get(
    "/{interview_id}/communication-analytics",
    response_model=schemas.CommunicationAnalyticsResponse,
)
def get_communication_analytics(
    interview_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return communication analytics for every answered question in the interview.

    Ownership: only the interview's owner can access this endpoint.
    Deterministic metrics are always computed.
    AI qualitative feedback is attempted per-answer and silently omitted on failure.
    """
    # ── Ownership check ──────────────────────────────────────────────────────
    interview = (
        db.query(models.Interview)
        .filter(
            models.Interview.id == interview_id,
            models.Interview.user_id == current_user.id,
        )
        .first()
    )
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found.")

    # ── Gather answered questions, ordered by sequence ────────────────────────
    questions = (
        db.query(models.Question)
        .options(joinedload(models.Question.answer))
        .filter(models.Question.interview_id == interview_id)
        .order_by(models.Question.sequence_number)
        .all()
    )

    per_question = []
    aggregate_inputs = []  # list of dicts fed to compute_aggregate

    for question in questions:
        answer = question.answer
        if not answer:
            continue  # skip unanswered questions

        answer_text = answer.answer_text or ""

        # 1. Deterministic metrics — always runs
        det = analyze_answer(answer_text)

        # 2. AI qualitative feedback — best-effort
        ai_fb = None
        try:
            raw_fb = ai_service.generate_communication_feedback(
                question_text=question.question_text,
                answer_text=answer_text,
            )
            ai_fb = schemas.AiCommunicationFeedback(
                directness=raw_fb.get("directness", ""),
                structure=raw_fb.get("structure", ""),
                conciseness=raw_fb.get("conciseness", ""),
                suggestion=raw_fb.get("suggestion", ""),
            )
        except Exception as exc:
            logger.warning(
                f"[analytics] AI communication feedback skipped for question "
                f"{question.id}: {exc}"
            )

        per_question.append(
            schemas.AnswerAnalytics(
                question_id=question.id,
                sequence_number=question.sequence_number,
                question_text=question.question_text,
                answer_text=answer_text,
                word_count=det["word_count"],
                sentence_count=det["sentence_count"],
                avg_sentence_length=det["avg_sentence_length"],
                max_sentence_length=det["max_sentence_length"],
                estimated_speaking_time_seconds=det["estimated_speaking_time_seconds"],
                estimated_wpm=det["estimated_wpm"],
                filler_word_count=det["filler_word_count"],
                filler_word_rate=det["filler_word_rate"],
                detected_fillers=det["detected_fillers"],
                ai_feedback=ai_fb,
            )
        )

        # Aggregate inputs need filler_rate key (compute_aggregate uses it)
        aggregate_inputs.append({**det, "filler_rate": det["filler_word_rate"]})

    # ── Aggregate ─────────────────────────────────────────────────────────────
    agg = compute_aggregate(aggregate_inputs)

    return schemas.CommunicationAnalyticsResponse(
        interview_id=interview_id,
        total_words=agg["total_words"],
        total_sentences=agg["total_sentences"],
        total_filler_words=agg["total_filler_words"],
        avg_filler_rate=agg["avg_filler_rate"],
        avg_wpm=agg["avg_wpm"],
        overall_suggestion=agg["overall_suggestion"],
        per_question=per_question,
    )

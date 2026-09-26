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


@router.get(
    "/{interview_id}/intelligence",
    response_model=schemas.InterviewIntelligenceResponse,
)
def get_interview_intelligence(
    interview_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Return a structured Intelligence & Final Evaluation Report for a completed interview.

    - Authenticates user and enforces ownership (404 if not found/not owned).
    - All category scores, overall score, and topic averages are computed deterministically
      from stored database values. The AI is only used for qualitative synthesis.
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

    # ── Load questions with answers ──────────────────────────────────────────
    questions = (
        db.query(models.Question)
        .options(joinedload(models.Question.answer))
        .filter(models.Question.interview_id == interview_id)
        .order_by(models.Question.sequence_number)
        .all()
    )

    answered = [q for q in questions if q.answer is not None]

    # ── 1. Category scores — deterministic arithmetic from stored values ──────
    def _avg(vals):
        clean = [v for v in vals if v is not None]
        return round(sum(clean) / len(clean), 1) if clean else 0.0

    tech_scores  = [q.answer.technical_score    for q in answered]
    comm_scores  = [q.answer.communication_score for q in answered]
    rel_scores   = [q.answer.relevance_score     for q in answered]
    comp_scores  = [q.answer.completeness_score  for q in answered]
    overall_scores = [q.answer.score             for q in answered]

    cat_scores = schemas.CategoryScores(
        technical    = _avg(tech_scores),
        communication= _avg(comm_scores),
        relevance    = _avg(rel_scores),
        completeness = _avg(comp_scores),
    )

    # Use stored overall_score if available; else recompute from answers
    overall_score = (
        round(interview.overall_score, 1)
        if interview.overall_score is not None
        else _avg(overall_scores)
    )

    # ── 2. Topic performance — group by topic ─────────────────────────────────
    topic_map: dict = {}
    for q in answered:
        topic_key = (q.topic or "General").strip()
        if topic_key not in topic_map:
            topic_map[topic_key] = []
        if q.answer.score is not None:
            topic_map[topic_key].append(q.answer.score)

    topic_performance = []
    for topic, scores in topic_map.items():
        avg_s = round(sum(scores) / len(scores), 1) if scores else 0.0
        if avg_s >= 80:
            status = "Strong"
        elif avg_s >= 65:
            status = "Good"
        else:
            status = "Needs Practice"
        topic_performance.append(
            schemas.TopicPerformance(
                topic=topic,
                question_count=len(scores),
                average_score=avg_s,
                coverage_status=status,
            )
        )

    # Sort: weakest topics first so they appear prominently
    topic_performance.sort(key=lambda t: t.average_score)

    # ── 3. Strengths — data-backed ────────────────────────────────────────────
    strengths: list[str] = []
    if cat_scores.technical >= 80:
        strengths.append(f"Strong technical knowledge (avg {cat_scores.technical})")
    if cat_scores.communication >= 80:
        strengths.append(f"Clear and well-structured communication (avg {cat_scores.communication})")
    if cat_scores.relevance >= 80:
        strengths.append(f"Highly relevant answers aligned to the question (avg {cat_scores.relevance})")
    if cat_scores.completeness >= 80:
        strengths.append(f"Comprehensive and complete responses (avg {cat_scores.completeness})")
    for tp in topic_performance:
        if tp.average_score >= 80:
            strengths.append(f"Strong performance in {tp.topic} ({tp.question_count} question(s), avg {tp.average_score})")
    if not strengths:
        strengths.append("Successfully attempted all questions across the interview session")

    # ── 4. Improvement areas — data-backed ───────────────────────────────────
    improvement_areas: list[str] = []
    if cat_scores.technical < 70:
        improvement_areas.append(f"Technical depth needs improvement (avg {cat_scores.technical})")
    if cat_scores.communication < 70:
        improvement_areas.append(f"Communication clarity could be stronger (avg {cat_scores.communication})")
    if cat_scores.relevance < 70:
        improvement_areas.append(f"Answers could more directly address the questions (avg {cat_scores.relevance})")
    if cat_scores.completeness < 70:
        improvement_areas.append(f"More complete answers recommended (avg {cat_scores.completeness})")
    for tp in topic_performance:
        if tp.average_score < 65:
            improvement_areas.append(f"{tp.topic} requires further practice (avg {tp.average_score})")

    # ── 5. Practice recommendations — linked to weak areas ────────────────────
    practice_recommendations: list[str] = []
    if cat_scores.technical < 70:
        practice_recommendations.append("Review core technical fundamentals for your target role")
    if cat_scores.communication < 70:
        practice_recommendations.append("Practice structuring answers using the STAR or Problem-Approach-Result format")
    if cat_scores.completeness < 70:
        practice_recommendations.append("Aim to explain both 'what' and 'why' in each answer")
    if cat_scores.relevance < 70:
        practice_recommendations.append("Before answering, re-read the question carefully to stay on-topic")
    for tp in topic_performance:
        if tp.average_score < 65:
            practice_recommendations.append(f"Study and practice {tp.topic} fundamentals before your next interview")
    if not practice_recommendations:
        practice_recommendations.append("Review interview history to reinforce your strengths")

    # ── 6. Optional communication analytics for AI summary context ────────────
    comm_metrics = None
    try:
        comm_inputs = []
        for q in answered:
            from app.services.communication_analytics import analyze_answer
            det = analyze_answer(q.answer.answer_text or "")
            comm_inputs.append({**det, "filler_rate": det["filler_word_rate"]})
        if comm_inputs:
            from app.services.communication_analytics import compute_aggregate
            agg = compute_aggregate(comm_inputs)
            comm_metrics = {
                "total_words": agg["total_words"],
                "total_filler_words": agg["total_filler_words"],
                "avg_wpm": agg["avg_wpm"],
            }
    except Exception as exc:
        logger.warning(f"[intelligence] Communication analytics skipped: {exc}")

    # ── 7. AI qualitative summary — best-effort, never overrides DB values ────
    ai_summary = ""
    try:
        ai_summary = ai_service.generate_interview_intelligence_summary(
            job_role=interview.job_role,
            interview_type=interview.interview_type,
            difficulty=interview.difficulty,
            overall_score=overall_score,
            category_scores={
                "technical":     cat_scores.technical,
                "communication": cat_scores.communication,
                "relevance":     cat_scores.relevance,
                "completeness":  cat_scores.completeness,
            },
            topic_performance=[t.model_dump() for t in topic_performance],
            strengths=strengths,
            improvement_areas=improvement_areas,
            communication_metrics=comm_metrics,
        )
    except Exception as exc:
        logger.warning(f"[intelligence] AI summary skipped: {exc}")

    return schemas.InterviewIntelligenceResponse(
        interview_id=interview_id,
        job_role=interview.job_role,
        interview_type=interview.interview_type,
        difficulty=interview.difficulty,
        overall_score=overall_score,
        category_scores=cat_scores,
        topic_performance=topic_performance,
        strengths=strengths[:5],
        improvement_areas=improvement_areas[:5],
        practice_recommendations=practice_recommendations[:5],
        ai_summary=ai_summary,
    )


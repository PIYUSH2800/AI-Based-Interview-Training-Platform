import os
import logging
from app.services.real_ai_service import RealAIService
from app.services.mock_ai_service import generate_question_mock, evaluate_answer_mock, generate_coding_feedback_mock

logger = logging.getLogger("ai_service")

class AIService:
    def __init__(self):
        self.real_ai = RealAIService()

    def is_ai_enabled(self) -> bool:
        env_val = os.getenv("AI_ENABLED", "true").lower()
        return env_val in ["true", "1", "yes"]

    def is_fallback_enabled(self) -> bool:
        env_val = os.getenv("AI_FALLBACK_TO_MOCK", "true").lower()
        return env_val in ["true", "1", "yes"]

    def get_ai_status(self) -> dict:
        configured = self.real_ai.is_configured()
        enabled = self.is_ai_enabled()
        active_mode = "real" if (configured and enabled) else "mock"

        return {
            "provider": os.getenv("AI_PROVIDER", "gemini"),
            "configured": configured,
            "enabled": enabled,
            "fallback_enabled": self.is_fallback_enabled(),
            "active_mode": active_mode,
            "model": self.real_ai.model_name
        }

    def generate_question(
        self, 
        job_role: str, 
        interview_type: str, 
        difficulty: str, 
        skills: str = "",
        candidate_context: dict = None
    ) -> str:
        if self.real_ai.is_configured() and self.is_ai_enabled():
            try:
                question = self.real_ai.generate_question(
                    job_role=job_role,
                    interview_type=interview_type,
                    difficulty=difficulty,
                    skills=skills,
                    candidate_context=candidate_context
                )
                logger.info("Generated question via Gemini API.")
                return question
            except Exception as e:
                logger.warning(f"[AI Fallback] Gemini question generation failed ({e}). Falling back to Mock AI.")
                if not self.is_fallback_enabled():
                    raise e

        # Fallback to Mock AI
        return generate_question_mock(job_role, interview_type, difficulty, skills)

    def evaluate_answer(
        self, 
        question_text: str, 
        answer_text: str,
        job_role: str = "Software Developer",
        interview_type: str = "Technical Interview",
        difficulty: str = "Intermediate",
        candidate_context: dict = None
    ) -> dict:
        if self.real_ai.is_configured() and self.is_ai_enabled():
            try:
                evaluation = self.real_ai.evaluate_answer(
                    question_text=question_text,
                    answer_text=answer_text,
                    job_role=job_role,
                    interview_type=interview_type,
                    difficulty=difficulty,
                    candidate_context=candidate_context
                )
                logger.info("Evaluated answer via Gemini API.")
                return evaluation
            except Exception as e:
                logger.warning(f"[AI Fallback] Gemini answer evaluation failed ({e}). Falling back to Mock AI.")
                if not self.is_fallback_enabled():
                    raise e

        # Fallback to Mock AI
        return evaluate_answer_mock(question_text, answer_text)

    def generate_interview_feedback(self, db_questions: list) -> dict:
        """Generates comprehensive feedback summary based on candidate's saved question/answers."""
        answers = [q.answer for q in db_questions if q.answer is not None]

        if not answers:
            return {
                "overall_score": 75.0,
                "category_breakdown": [
                    {"name": "Technical", "score": 75.0},
                    {"name": "Comm.", "score": 75.0},
                    {"name": "Relevance", "score": 75.0},
                    {"name": "Completeness", "score": 75.0},
                ],
                "strengths": ["Completed mock interview session"],
                "weaknesses": ["Provide more detailed answers"],
                "recommendations": ["Practice core fundamental questions for your target role"]
            }

        tech_scores = [a.technical_score for a in answers if a.technical_score is not None]
        comm_scores = [a.communication_score for a in answers if a.communication_score is not None]
        rel_scores = [a.relevance_score for a in answers if a.relevance_score is not None]
        comp_scores = [a.completeness_score for a in answers if a.completeness_score is not None]
        overall_scores = [a.score for a in answers if a.score is not None]

        avg_tech = round(sum(tech_scores) / len(tech_scores), 1) if tech_scores else 75.0
        avg_comm = round(sum(comm_scores) / len(comm_scores), 1) if comm_scores else 75.0
        avg_rel = round(sum(rel_scores) / len(rel_scores), 1) if rel_scores else 75.0
        avg_comp = round(sum(comp_scores) / len(comp_scores), 1) if comp_scores else 75.0
        avg_overall = round(sum(overall_scores) / len(overall_scores), 1) if overall_scores else 75.0

        # Collect unique feedback insights
        strengths = []
        weaknesses = []
        for a in answers:
            if a.feedback:
                if a.score and a.score >= 75:
                    strengths.append(a.feedback)
                else:
                    weaknesses.append(a.feedback)

        if not strengths:
            strengths = ["Solid effort and technical understanding", "Good problem-solving approach"]
        if not weaknesses:
            weaknesses = ["Incorporate practical architectural examples", "Refine answer structure"]

        recommendations = [
            f"Focus on improving {min([('Technical', avg_tech), ('Communication', avg_comm), ('Relevance', avg_rel), ('Completeness', avg_comp)], key=lambda x: x[1])[0]} skills.",
            "Practice explaining concepts concisely before expanding into implementation details.",
            "Review past interview history Q&A to track score improvements."
        ]

        return {
            "overall_score": avg_overall,
            "category_breakdown": [
                {"name": "Technical", "score": avg_tech},
                {"name": "Comm.", "score": avg_comm},
                {"name": "Relevance", "score": avg_rel},
                {"name": "Completeness", "score": avg_comp},
            ],
            "strengths": list(set(strengths))[:3],
            "weaknesses": list(set(weaknesses))[:3],
            "recommendations": recommendations
        }

    def generate_coding_feedback(
        self,
        problem_title: str,
        problem_description: str,
        difficulty: str,
        category: str,
        language: str,
        source_code: str,
        status: str,
        score: float,
        passed_tests: int,
        total_tests: int
    ) -> dict:
        if self.real_ai.is_configured() and self.is_ai_enabled():
            try:
                feedback = self.real_ai.generate_coding_feedback(
                    problem_title=problem_title,
                    problem_description=problem_description,
                    difficulty=difficulty,
                    category=category,
                    language=language,
                    source_code=source_code,
                    status=status,
                    score=score,
                    passed_tests=passed_tests,
                    total_tests=total_tests
                )
                logger.info("Generated coding feedback via Gemini API.")
                feedback["provider"] = "gemini"
                return feedback
            except Exception as e:
                logger.warning(f"[AI Fallback] Gemini coding feedback failed ({e}). Falling back to Mock AI.")
                if not self.is_fallback_enabled():
                    raise e

        # Fallback to Mock AI
        feedback = generate_coding_feedback_mock(
            problem_title=problem_title,
            language=language,
            source_code=source_code,
            status=status,
            score=score,
            passed=passed_tests,
            total=total_tests
        )
        feedback["provider"] = "mock"
        return feedback


# Singleton instance
ai_service = AIService()

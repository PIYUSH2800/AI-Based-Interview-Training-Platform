import os
import re
import json
try:
    from google import genai
except ImportError:
    genai = None

from app.services.prompts import (
    QUESTION_GENERATION_PROMPT,
    ANSWER_EVALUATION_PROMPT,
    CODING_FEEDBACK_PROMPT,
    COMMUNICATION_FEEDBACK_PROMPT,
    ADAPTIVE_QUESTION_PROMPT,
)

class RealAIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("AI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"
        self.client = None
        if self.api_key and genai is not None:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini Client: {e}")


    def is_configured(self) -> bool:
        return bool(self.api_key and self.client is not None)

    def _clean_and_parse_json(self, response_text: str) -> dict:
        """Helper to extract and parse JSON object from LLM response string."""
        text = response_text.strip()
        
        # Strip markdown block formatting ```json ... ``` if present
        if "```" in text:
            match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
            if match:
                text = match.group(1)
            else:
                text = re.sub(r'```(?:json)?', '', text).replace('```', '').strip()

        # Extract first JSON object boundaries
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1 and end > start:
            text = text[start:end+1]

        return json.loads(text)

    def generate_question(
        self, 
        job_role: str, 
        interview_type: str, 
        difficulty: str, 
        skills: str = "",
        candidate_context: dict = None
    ) -> str:
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured.")

        ctx = candidate_context or {}
        education = ctx.get("education", "Not specified")
        experience_level = ctx.get("experience_level", "Entry Level")
        resume_context = ctx.get("resume_text", "No resume provided")

        prompt = QUESTION_GENERATION_PROMPT.format(
            job_role=job_role,
            interview_type=interview_type,
            difficulty=difficulty,
            skills=skills or ctx.get("skills", ""),
            education=education,
            experience_level=experience_level,
            resume_context=resume_context[:500]
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        if not response or not response.text:
            raise ValueError("Empty response received from Gemini model.")

        parsed = self._clean_and_parse_json(response.text)
        
        if "question" in parsed and isinstance(parsed["question"], str) and parsed["question"].strip():
            return parsed["question"].strip()
        
        raise ValueError("Invalid JSON schema returned by model for question generation.")

    def evaluate_answer(
        self, 
        question_text: str, 
        answer_text: str,
        job_role: str = "Software Developer",
        interview_type: str = "Technical Interview",
        difficulty: str = "Intermediate",
        candidate_context: dict = None
    ) -> dict:
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured.")

        prompt = ANSWER_EVALUATION_PROMPT.format(
            job_role=job_role,
            interview_type=interview_type,
            difficulty=difficulty,
            question_text=question_text,
            answer_text=answer_text
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        if not response or not response.text:
            raise ValueError("Empty response received from Gemini model.")

        parsed = self._clean_and_parse_json(response.text)
        
        def clamp_score(val, default=75):
            try:
                num = int(float(val))
                return max(0, min(100, num))
            except (ValueError, TypeError):
                return default

        overall = clamp_score(parsed.get("overall_score", parsed.get("score", 75)))
        tech = clamp_score(parsed.get("technical_score", overall))
        comm = clamp_score(parsed.get("communication_score", overall))
        rel = clamp_score(parsed.get("relevance_score", overall))
        comp = clamp_score(parsed.get("completeness_score", overall))

        feedback = str(parsed.get("feedback", "Evaluation completed.")).strip()
        strengths = parsed.get("strengths", ["Good effort"])
        if not isinstance(strengths, list):
            strengths = [str(strengths)]

        improvements = parsed.get("improvements", parsed.get("weaknesses", ["Provide more technical depth"]))
        if not isinstance(improvements, list):
            improvements = [str(improvements)]

        return {
            "score": overall,
            "technical_score": tech,
            "communication_score": comm,
            "relevance_score": rel,
            "completeness_score": comp,
            "feedback": feedback,
            "strengths": [str(s) for s in strengths],
            "improvements": [str(i) for i in improvements]
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
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured.")

        prompt = CODING_FEEDBACK_PROMPT.format(
            title=problem_title,
            description=problem_description,
            difficulty=difficulty,
            category=category,
            language=language,
            source_code=source_code,
            status=status,
            score=score,
            passed_tests=passed_tests,
            total_tests=total_tests
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        if not response or not response.text:
            raise ValueError("Empty response received from Gemini model.")

        parsed = self._clean_and_parse_json(response.text)
        
        # Ensure array fields are actually lists of strings
        for list_field in ["strengths", "issues", "improvements", "interview_tips"]:
            val = parsed.get(list_field, [])
            if not isinstance(val, list):
                parsed[list_field] = [str(val)]
            else:
                parsed[list_field] = [str(v) for v in val]

        # Ensure string fields are strings
        for str_field in ["summary", "approach", "correctness", "time_complexity", "space_complexity", "better_approach"]:
            val = parsed.get(str_field, "")
            parsed[str_field] = str(val).strip()

        return parsed

    def generate_communication_feedback(
        self,
        question_text: str,
        answer_text: str,
    ) -> dict:
        """Generate qualitative communication feedback for a single answer."""
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured.")

        prompt = COMMUNICATION_FEEDBACK_PROMPT.format(
            question_text=question_text,
            answer_text=answer_text,
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        if not response or not response.text:
            raise ValueError("Empty response received from Gemini model.")

        parsed = self._clean_and_parse_json(response.text)

        # Ensure all expected keys are present with safe string defaults
        for key in ["directness", "structure", "conciseness", "suggestion"]:
            if key not in parsed or not isinstance(parsed[key], str):
                parsed[key] = ""

        return {
            "directness": parsed["directness"].strip(),
            "structure": parsed["structure"].strip(),
            "conciseness": parsed["conciseness"].strip(),
            "suggestion": parsed["suggestion"].strip(),
        }

    def generate_adaptive_question(
        self,
        job_role: str,
        interview_type: str,
        difficulty: str,
        skills: str = "",
        candidate_context: dict = None,
        previous_questions: list = None,
        last_answer_context: dict = None,
        topics_covered: list = None,
        under_covered_topics: list = None,
        weak_areas: list = None,
        interview_strategy_guidance: str = "",
    ) -> dict:
        """Generates an adaptive, strategically covered question using Gemini."""
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured.")

        ctx = candidate_context or {}
        education = ctx.get("education", "Not specified")
        experience_level = ctx.get("experience_level", "Entry Level")
        resume_context = ctx.get("resume_text", "No resume provided")

        prev_qs_str = "\n".join([f"- {q}" for q in (previous_questions or [])]) if previous_questions else "None (First question)"
        topics_cov_str = ", ".join(topics_covered) if topics_covered else "None so far"
        under_cov_str = ", ".join(under_covered_topics) if under_covered_topics else "All target role topics"
        weak_areas_str = ", ".join(weak_areas) if weak_areas else "None identified so far"
        strategy_str = interview_strategy_guidance or f"Conduct a standard {interview_type} for a {job_role} candidate."

        if last_answer_context:
            last_ans_str = (
                f"Question: {last_answer_context.get('question_text', 'N/A')}\n"
                f"Candidate Answer: {last_answer_context.get('answer_text', 'N/A')}\n"
                f"Overall Score: {last_answer_context.get('score', 'N/A')}/100 "
                f"(Technical: {last_answer_context.get('technical_score', 'N/A')}, "
                f"Comm: {last_answer_context.get('communication_score', 'N/A')}, "
                f"Relevance: {last_answer_context.get('relevance_score', 'N/A')}, "
                f"Completeness: {last_answer_context.get('completeness_score', 'N/A')})\n"
                f"Evaluator Feedback: {last_answer_context.get('feedback', 'N/A')}"
            )
        else:
            last_ans_str = "None (Initial question in session)"

        prompt = ADAPTIVE_QUESTION_PROMPT.format(
            job_role=job_role,
            interview_type=interview_type,
            difficulty=difficulty,
            skills=skills or ctx.get("skills", ""),
            education=education,
            experience_level=experience_level,
            resume_context=resume_context[:500],
            interview_strategy_guidance=strategy_str,
            topics_covered_text=topics_cov_str,
            under_covered_topics_text=under_cov_str,
            weak_areas_text=weak_areas_str,
            previous_questions_text=prev_qs_str,
            last_answer_context=last_ans_str,
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        if not response or not response.text:
            raise ValueError("Empty response received from Gemini model for adaptive question.")

        parsed = self._clean_and_parse_json(response.text)

        if "question" in parsed and isinstance(parsed["question"], str) and parsed["question"].strip():
            return {
                "question": parsed["question"].strip(),
                "difficulty": str(parsed.get("difficulty", difficulty)).strip(),
                "topic": str(parsed.get("topic", job_role)).strip(),
                "category": str(parsed.get("category", interview_type)).strip(),
                "reason": str(parsed.get("reason", "Adapted based on candidate performance and topic strategy.")).strip(),
            }

        raise ValueError("Invalid JSON schema returned by model for adaptive question generation.")



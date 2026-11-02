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
    INTERVIEW_INTELLIGENCE_SUMMARY_PROMPT,
    CODING_HINT_PROMPT,
    CODING_EXPLANATION_PROMPT,
)

class RealAIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("AI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"
        self.client = None
        self._init_client()

    def _init_client(self):
        self.api_key = os.getenv("GEMINI_API_KEY", "").strip()
        self.model_name = os.getenv("AI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"
        if self.api_key and self.api_key != "your_gemini_api_key_here" and genai is not None:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Warning: Failed to initialize Gemini Client: {e}")
                self.client = None

    def is_configured(self) -> bool:
        if self.client is None:
            self._init_client()
        if not self.api_key or self.api_key == "your_gemini_api_key_here":
            return False
        return bool(self.client is not None)

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
        # Step 1: Pre-flight check for meaningless / random / gibberish input
        from app.services.answer_validator import validate_answer_meaningfulness
        val = validate_answer_meaningfulness(question_text, answer_text)
        if not val.is_valid:
            return {
                "score": 0,
                "technical_score": 0,
                "communication_score": 0,
                "relevance_score": 0,
                "completeness_score": 0,
                "feedback": (
                    "The submitted response is unintelligible, empty, or contains no meaningful "
                    "technical explanation addressing the question. Please provide a relevant and structured answer."
                ),
                "strengths": [],
                "improvements": [
                    "Provide a coherent answer addressing the core question",
                    "Explain the concept using standard technical terminology"
                ]
            }

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
        
        def clamp_score(val, default=0):
            try:
                num = int(float(val))
                return max(0, min(100, num))
            except (ValueError, TypeError):
                return default

        tech = clamp_score(parsed.get("technical_score", 0))
        rel = clamp_score(parsed.get("relevance_score", 0))
        comp = clamp_score(parsed.get("completeness_score", 0))
        comm = clamp_score(parsed.get("communication_score", 0))

        # Ground overall score
        raw_overall = clamp_score(parsed.get("overall_score", parsed.get("score", 0)))
        if tech == 0 and rel == 0:
            overall = 0
        else:
            overall = raw_overall

        feedback = str(parsed.get("feedback", "Evaluation completed.")).strip()
        strengths = parsed.get("strengths", ["Attempted question"])
        if not isinstance(strengths, list):
            strengths = [str(strengths)]
        if overall == 0:
            strengths = []

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

    def generate_interview_intelligence_summary(
        self,
        job_role: str,
        interview_type: str,
        difficulty: str,
        overall_score: float,
        category_scores: dict,
        topic_performance: list,
        strengths: list,
        improvement_areas: list,
        communication_metrics: dict = None,
    ) -> str:
        """Synthesizes a qualitative interview summary using Gemini based on deterministic metrics."""
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured.")

        cat_str = ", ".join([f"{k.capitalize()}: {v}" for k, v in (category_scores or {}).items()])
        top_str = "; ".join([f"{t.get('topic', 'General')} ({t.get('coverage_status', 'N/A')}, avg: {t.get('average_score', 0)})" for t in (topic_performance or [])])
        str_str = "; ".join(strengths or ["General competence"])
        imp_str = "; ".join(improvement_areas or ["None noted"])
        comm_str = f"Words: {communication_metrics.get('total_words', 0)}, Fillers: {communication_metrics.get('total_filler_words', 0)}" if communication_metrics else "N/A"

        prompt = INTERVIEW_INTELLIGENCE_SUMMARY_PROMPT.format(
            job_role=job_role,
            interview_type=interview_type,
            difficulty=difficulty,
            overall_score=round(overall_score, 1),
            category_scores_text=cat_str,
            topic_performance_text=top_str,
            strengths_text=str_str,
            improvement_areas_text=imp_str,
            communication_metrics_text=comm_str,
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        if not response or not response.text:
            raise ValueError("Empty response received from Gemini for intelligence summary.")

        return response.text.strip()

    def generate_coding_hint(
        self,
        problem_title: str,
        problem_description: str,
        difficulty: str,
        category: str,
        level: int,
    ) -> dict:
        """Generate a progressive hint for a coding problem (Level 1, 2, or 3)."""
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured.")

        level_names = {
            1: "Conceptual Guidance",
            2: "Approach Guidance",
            3: "Detailed Guidance",
        }
        level_name = level_names.get(level, f"Level {level} Guidance")

        prompt = CODING_HINT_PROMPT.format(
            title=problem_title,
            difficulty=difficulty,
            category=category,
            description=problem_description,
            level=level,
            level_name=level_name,
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        if not response or not response.text:
            raise ValueError("Empty response received from Gemini model for hint.")

        parsed = self._clean_and_parse_json(response.text)

        # Validate and sanitize fields
        title = parsed.get("title", f"Level {level} — {level_name}")
        hint = parsed.get("hint", "")
        key_takeaways = parsed.get("key_takeaways", [])
        if not isinstance(key_takeaways, list):
            key_takeaways = [str(key_takeaways)]
        edge_cases = parsed.get("edge_cases", [])
        if not isinstance(edge_cases, list):
            edge_cases = [str(edge_cases)]

        return {
            "level": level,
            "title": str(title).strip(),
            "hint": str(hint).strip(),
            "key_takeaways": [str(t).strip() for t in key_takeaways if t],
            "edge_cases": [str(e).strip() for e in edge_cases if e],
            "provider": "gemini",
        }

    def generate_coding_explanation(
        self,
        problem_title: str,
        problem_description: str,
        difficulty: str,
        category: str,
    ) -> dict:
        """Generate educational explanation of optimal algorithm and concepts for a coding problem."""
        if not self.is_configured():
            raise RuntimeError("Gemini API key is not configured.")

        prompt = CODING_EXPLANATION_PROMPT.format(
            title=problem_title,
            difficulty=difficulty,
            category=category,
            description=problem_description,
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        if not response or not response.text:
            raise ValueError("Empty response received from Gemini model for explanation.")

        parsed = self._clean_and_parse_json(response.text)

        def sanitize_list(lst):
            if not isinstance(lst, list):
                return [str(lst)] if lst else []
            return [str(x).strip() for x in lst if x]

        return {
            "title": problem_title,
            "difficulty": difficulty,
            "category": category,
            "intuition": str(parsed.get("intuition", "")).strip(),
            "brute_force": str(parsed.get("brute_force", "")).strip(),
            "optimized_approach": str(parsed.get("optimized_approach", "")).strip(),
            "step_by_step": sanitize_list(parsed.get("step_by_step", [])),
            "time_complexity": str(parsed.get("time_complexity", "")).strip(),
            "space_complexity": str(parsed.get("space_complexity", "")).strip(),
            "common_mistakes": sanitize_list(parsed.get("common_mistakes", [])),
            "edge_cases": sanitize_list(parsed.get("edge_cases", [])),
            "interview_tips": sanitize_list(parsed.get("interview_tips", [])),
            "provider": "gemini",
        }




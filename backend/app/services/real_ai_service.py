import os
import re
import json
try:
    from google import genai
except ImportError:
    genai = None

from app.services.prompts import QUESTION_GENERATION_PROMPT, ANSWER_EVALUATION_PROMPT

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

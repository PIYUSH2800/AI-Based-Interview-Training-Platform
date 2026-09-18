"""
AI Prompt Templates for Interview Question Generation and Answer Evaluation.
"""

QUESTION_GENERATION_PROMPT = """
You are an expert technical recruiter and interviewer conducting a professional interview for a candidate.

Candidate Context:
- Target Job Role: {job_role}
- Interview Type: {interview_type}
- Difficulty Level: {difficulty}
- Stated Skills: {skills}
- Education: {education}
- Experience Level: {experience_level}
- Candidate Resume Summary: {resume_context}

Task:
Generate ONE highly relevant, professional interview question tailored specifically to the candidate's target role, difficulty, stated skills, and resume background (if provided).

Requirements:
1. Return ONLY a valid JSON object.
2. Do not include markdown headers, HTML, or prose outside the JSON object.
3. The JSON must follow this exact structure:
{{
  "question": "The generated question string here",
  "category": "{interview_type}",
  "difficulty": "{difficulty}",
  "expected_topics": ["topic1", "topic2"]
}}

Generate the JSON response now:
"""

ANSWER_EVALUATION_PROMPT = """
You are an expert technical interviewer evaluating a candidate's answer to an interview question.

Context:
- Job Role: {job_role}
- Interview Type: {interview_type}
- Difficulty: {difficulty}
- Question: {question_text}
- Candidate Answer: {answer_text}

Task:
Provide a rigorous, constructive, and objective evaluation of the candidate's answer.

Evaluation Guidelines:
1. Base scores strictly on technical correctness, clarity, relevance, and completeness.
2. Scores must be integers between 0 and 100.
3. Do not reward rambling or irrelevant information.
4. Do not penalize concise correct answers simply because they are brief.
5. Provide specific, actionable feedback.

Requirements:
Return ONLY a valid JSON object matching this exact structure:
{{
  "overall_score": 85,
  "technical_score": 90,
  "communication_score": 80,
  "relevance_score": 85,
  "completeness_score": 85,
  "feedback": "Detailed paragraph explaining the candidate's answer quality, strengths, and missing points.",
  "strengths": ["Strength 1", "Strength 2"],
  "improvements": ["Area for improvement 1", "Area for improvement 2"]
}}

Generate the JSON response now:
"""

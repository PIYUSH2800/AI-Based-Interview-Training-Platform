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
3. If the candidate's answer is completely irrelevant, nonsensical, blank, or fails to address the question, you MUST assign 0 for technical_score, relevance_score, completeness_score, and overall_score.
4. For valid concise answers that directly answer the question (such as 'O(log n)' or 'HTTP 404'), evaluate technical accuracy without penalizing for brevity.
5. Award justified partial credit for partially correct answers; do not reward answers purely for verbosity or unrelated filler words.
6. Provide specific, actionable feedback explaining where the answer succeeded or fell short.

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

CODING_FEEDBACK_PROMPT = """
You are an expert technical interviewer reviewing a candidate's submitted code for a coding problem.

Context:
- Problem Title: {title}
- Difficulty: {difficulty}
- Category: {category}
- Description: {description}
- Submitted Language: {language}
- Execution Status: {status}
- Tests Passed: {passed_tests}/{total_tests}
- Score: {score}/100

Candidate's Code:
{source_code}

Task:
Provide constructive, educational interview feedback. 
- If the code has compile or runtime errors, explain likely issues based on the code.
- If the status is wrong_answer or timeout, explain potential logical flaws or inefficiencies.
- DO NOT invent hidden test cases or guess them.
- DO NOT claim the code is fully correct if the Execution Status says otherwise. The Execution Status is the ultimate source of truth.
- Evaluate Time and Space Complexity correctly based on the provided code.

Requirements:
Return ONLY a valid JSON object matching this exact structure:
{{
  "summary": "Brief overall summary of the submission",
  "approach": "Explanation of the algorithm/approach used by the candidate",
  "correctness": "Feedback on whether it works, and if not, why based on the execution status",
  "time_complexity": "O(N) with explanation",
  "space_complexity": "O(N) with explanation",
  "strengths": ["Strength 1", "Strength 2"],
  "issues": ["Issue 1", "Issue 2"],
  "improvements": ["Improvement 1", "Improvement 2"],
  "better_approach": "Explanation of a more optimal approach if one exists",
  "interview_tips": ["Tip 1", "Tip 2"]
}}

Generate the JSON response now:
"""

COMMUNICATION_FEEDBACK_PROMPT = """
You are an experienced interview coach reviewing a candidate's answer to an interview question.
Your goal is to provide a brief, objective, and constructive communication assessment.

Question asked:
{question_text}

Candidate's answer:
{answer_text}

Task:
Describe ONLY the observable characteristics of this specific answer.
Do NOT infer emotion, personality, confidence, intelligence, or mental state.
Do NOT make global claims about the candidate as a communicator.
Keep each field to 1–2 clear sentences.

Return ONLY a valid JSON object with this exact structure:
{{
  "directness": "One sentence describing how directly the answer addresses the question.",
  "structure": "One sentence describing whether the answer has a clear intro, body, and conclusion.",
  "conciseness": "One sentence on whether the answer is appropriately brief or verbose.",
  "suggestion": "One concrete, specific improvement the candidate can make for this type of answer."
}}

Generate the JSON response now:
"""

ADAPTIVE_QUESTION_PROMPT = """
You are an expert interviewer conducting a strategic, adaptive interview for a candidate.

Candidate & Interview Context:
- Target Job Role: {job_role}
- Interview Type: {interview_type}
- Target Difficulty Level: {difficulty}
- Stated Skills: {skills}
- Education: {education}
- Experience Level: {experience_level}
- Candidate Resume Summary: {resume_context}

Interview Strategy Guidance for {interview_type}:
{interview_strategy_guidance}

Current Session Coverage State:
- Topics Already Covered: {topics_covered_text}
- Under-Covered Skills/Topics: {under_covered_topics_text}
- Identified Weak Areas to Address: {weak_areas_text}

Previous Questions Asked in Session:
{previous_questions_text}

Candidate's Latest Answer Performance & Feedback:
{last_answer_context}

Task:
Generate EXACTLY ONE follow-up or next interview question that balances adaptive performance with strategic topic coverage.

Requirements:
1. Return ONLY a valid JSON object.
2. Do not include markdown headers, HTML, or prose outside the JSON object.
3. The next question MUST NOT repeat or closely rephrase any of the previously asked questions.
4. Maintain balanced topic distribution: prioritize under-covered topics or candidate skills if the previous topic has already been covered multiple times.
5. If addressing weak areas, do so constructively without repeatedly hammering the exact same question.
6. The JSON must follow this exact structure:
{{
  "question": "The generated next interview question string here",
  "difficulty": "{difficulty}",
  "topic": "Primary topic or skill covered by this question e.g. Python, SQL, Communication, Scalability",
  "category": "{interview_type}",
  "reason": "Brief internal explanation of why this question was selected based on performance and coverage strategy"
}}

Generate the JSON response now:
"""


INTERVIEW_INTELLIGENCE_SUMMARY_PROMPT = """
You are an expert executive interview coach synthesizing a completed candidate interview.

Interview Context:
- Target Job Role: {job_role}
- Interview Type: {interview_type}
- Difficulty Level: {difficulty}

Deterministic Performance Metrics (Source of Truth - DO NOT ALTER):
- Overall Score: {overall_score}/100
- Category Scores: {category_scores_text}
- Topic Performance Summary: {topic_performance_text}
- Data-Backed Strengths: {strengths_text}
- Data-Backed Areas for Improvement: {improvement_areas_text}
- Communication Analytics: {communication_metrics_text}

Task:
Synthesize a concise, 3-4 sentence professional qualitative interview summary.
- Highlight major observed strengths and key focus areas.
- Summarize communication effectiveness based on the provided metrics.
- Keep the feedback encouraging, objective, and actionable.
- DO NOT recalculate or contradict any numeric scores or database metrics.
- DO NOT invent facts, candidate traits, or background info not provided.

Return ONLY a clear 3-4 sentence text paragraph (no JSON wrapping, no markdown codeblocks).
"""


CODING_HINT_PROMPT = """
You are an expert technical interview mentor providing progressive hints to a student solving a coding problem.

Context:
- Problem Title: {title}
- Difficulty: {difficulty}
- Category: {category}
- Description: {description}
- Requested Hint Level: {level} ({level_name})

Guidelines by Hint Level:
- If Level 1 (Conceptual Guidance):
  * Explain the fundamental algorithmic intuition or mental model.
  * Frame the problem logically and ask guiding questions to spark ideas.
  * DO NOT reveal data structures, code syntax, or concrete steps.
- If Level 2 (Approach Guidance):
  * Suggest appropriate data structures (e.g. hash map, two pointers, stack, sliding window).
  * Outline the general algorithmic strategy and invariants.
  * Point out 1-2 critical edge cases to think about.
  * DO NOT provide full code or line-by-line solutions.
- If Level 3 (Detailed Guidance):
  * Provide a clear step-by-step algorithmic outline or structured pseudocode.
  * Walk through the state transitions or pointer movements.
  * DO NOT expose a complete copy-paste code solution.

Strict Rules:
1. Never invent or reveal hidden test cases.
2. Return ONLY a valid JSON object matching the exact structure below.
3. No markdown code blocks, backticks, or text outside the JSON.

Expected JSON Structure:
{{
  "title": "Level {level} — {level_name}",
  "hint": "Clear, instructive guidance text tailored strictly to this hint level",
  "key_takeaways": ["Takeaway 1", "Takeaway 2"],
  "edge_cases": ["Edge case consideration 1", "Edge case consideration 2"]
}}

Generate the JSON response now:
"""


CODING_EXPLANATION_PROMPT = """
You are a senior computer science instructor explaining an optimal algorithmic solution for a technical interview problem.

Problem Details:
- Title: {title}
- Difficulty: {difficulty}
- Category: {category}
- Description: {description}

Task:
Produce a comprehensive, educational deep-dive explaining the problem concepts from first principles.

Requirements:
1. Explain the intuitive problem breakdown.
2. Discuss a naive/brute-force approach and explain why it is suboptimal.
3. Detail the optimal algorithm and the core insight making it efficient.
4. List step-by-step execution phases.
5. Provide precise Big-O Time Complexity with clear mathematical reasoning.
6. Provide precise Big-O Space Complexity with auxiliary memory justification.
7. Highlight common traps or mistakes candidates make in interviews.
8. Detail critical edge cases (e.g. empty inputs, duplicates, negatives, boundary sizes).
9. Offer practical interview communication tips.
10. Return ONLY a valid JSON object matching this exact structure:

{{
  "intuition": "High-level intuition and conceptual breakdown of what the problem is asking",
  "brute_force": "Explanation of naive brute force approach and its limitations",
  "optimized_approach": "Explanation of the optimal approach and why it works",
  "step_by_step": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "time_complexity": "O(...) - detailed justification",
  "space_complexity": "O(...) - detailed justification",
  "common_mistakes": [
    "Mistake 1: ...",
    "Mistake 2: ..."
  ],
  "edge_cases": [
    "Edge case 1: ...",
    "Edge case 2: ..."
  ],
  "interview_tips": [
    "Tip 1: ...",
    "Tip 2: ..."
  ]
}}

Generate the JSON response now:
"""

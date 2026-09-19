import random

QUESTIONS_BANK = {
    "Software Developer": [
        "Explain the difference between a list and a tuple in Python.",
        "How do you handle exceptions in Python and what is the purpose of finally?",
        "What is REST API and what are the main HTTP methods used?",
        "Describe the MVC architecture and the responsibility of each layer.",
        "How would you optimize a slow SQL query with indexes?"
    ],
    "Data Scientist": [
        "Explain what overfitting is and how you would prevent it.",
        "What is the difference between supervised and unsupervised learning?",
        "How do you handle missing values in a dataset during preprocessing?",
        "Explain the concept of p-value and statistical significance.",
        "What are the pros and cons of Decision Trees vs Random Forests?"
    ],
    "Data Analyst": [
        "What is the difference between INNER JOIN, LEFT JOIN, and FULL OUTER JOIN in SQL?",
        "How do group by and having clauses work together in SQL queries?",
        "How do you handle outliers in data visualization?",
        "Explain the difference between categorical and numerical variables."
    ],
    "AI/ML Engineer": [
        "What is gradient descent and how does learning rate affect optimization?",
        "Explain the difference between Precision and Recall.",
        "What is transfer learning and when would you use it?",
        "How do Convolutional Neural Networks (CNNs) process image data?"
    ],
    "Product Manager": [
        "How do you prioritize features when resources are limited?",
        "Describe how you define key performance metrics for a new product launch.",
        "How do you handle conflicting user feedback during product discovery?"
    ]
}

GENERIC_QUESTIONS = [
    "Tell me about your technical background and key projects.",
    "What are your greatest technical strengths and areas for improvement?",
    "Describe a challenging problem you faced in a project and how you resolved it.",
    "How do you stay up-to-date with emerging tools and technologies in your field?",
    "Where do you see yourself professionally in the next 3 to 5 years?"
]


def generate_question_mock(job_role: str, interview_type: str, difficulty: str, skills: str = "") -> str:
    """Generates a fallback mock question based on job role and skills."""
    role_qs = QUESTIONS_BANK.get(job_role, GENERIC_QUESTIONS)
    
    # If candidate specified custom skills, check if any question matches skills
    if skills:
        skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
        for q in role_qs:
            if any(sk in q.lower() for sk in skill_list):
                return q

    return random.choice(role_qs)


def evaluate_answer_mock(question_text: str, answer_text: str) -> dict:
    """Evaluates answer quality using deterministic heuristics + length rules."""
    words = answer_text.strip().split()
    length = len(words)
    
    if length > 45:
        base_score = 88
        feedback = "Great answer! Your explanation is detailed, thorough, and covers key concepts well."
        strengths = ["Comprehensive details", "Clear explanation of core concept"]
        improvements = ["Could add a practical code example"]
    elif length > 20:
        base_score = 75
        feedback = "Good answer. You outlined the main points, but adding more context or examples would improve completeness."
        strengths = ["Accurate core answer", "Good structure"]
        improvements = ["Elaborate on practical edge cases"]
    elif length > 5:
        base_score = 55
        feedback = "Answer is too brief. Try to explain the 'why' and 'how' behind your answer rather than just a one-liner."
        strengths = ["Direct answer"]
        improvements = ["Provide significantly more detail and context"]
    else:
        base_score = 40
        feedback = "Incomplete response. Please provide a full technical explanation."
        strengths = ["Attempted response"]
        improvements = ["Give a complete answer with explanations"]

    return {
        "score": base_score,
        "technical_score": base_score,
        "communication_score": min(100, base_score + 5),
        "relevance_score": base_score,
        "completeness_score": max(30, base_score - 5),
        "feedback": feedback,
        "strengths": strengths,
        "improvements": improvements
    }

def generate_coding_feedback_mock(problem_title: str, language: str, source_code: str, status: str, score: float, passed: int, total: int) -> dict:
    """Generates mock AI coding feedback."""
    return {
        "summary": "This is mock AI feedback. In production, Gemini provides a full analysis of your code.",
        "approach": f"Based on the code, you attempted to solve '{problem_title}' using {language}.",
        "correctness": f"The submission scored {score}/100, passing {passed}/{total} tests. Status: {status}.",
        "time_complexity": "O(N) (Mock estimation)",
        "space_complexity": "O(N) (Mock estimation)",
        "strengths": ["Clear syntax structure", "Valid language usage"],
        "issues": ["Mock issue: Consider edge cases"],
        "improvements": ["Mock improvement: Optimize internal loops"],
        "better_approach": "A mock better approach would be to use a hash map or built-in optimization.",
        "interview_tips": ["Always explain your complexity to the interviewer"]
    }

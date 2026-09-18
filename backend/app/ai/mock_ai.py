import random

def generate_question(job_role: str, interview_type: str, difficulty: str, skills: str = ""):
    questions = {
        "Software Developer": [
            "Explain the difference between a list and a tuple in Python.",
            "How do you handle exceptions in Python?",
            "What is REST API?",
            "Describe the MVC architecture.",
            "How would you optimize a slow SQL query?"
        ],
        "Data Scientist": [
            "Explain what overfitting is and how you would prevent it.",
            "What is the difference between supervised and unsupervised learning?",
            "How do you handle missing values in a dataset?",
            "Explain the concept of p-value.",
            "What are the pros and cons of decision trees?"
        ]
    }
    
    role_questions = questions.get(job_role, [
        "Tell me about your background.",
        "What are your greatest strengths and weaknesses?",
        "Why do you want to work in this field?",
        "Describe a challenging problem you faced and how you solved it.",
        "Where do you see yourself in 5 years?"
    ])
    
    # Simple mock: return a random question
    return random.choice(role_questions)

def evaluate_answer(question: str, answer: str):
    # Mock evaluation logic
    length = len(answer.split())
    if length > 50:
        base_score = 90
        feedback = "Great answer, very detailed."
    elif length > 20:
        base_score = 75
        feedback = "Good answer, but could use more detail."
    else:
        base_score = 50
        feedback = "Too short. Please provide more context."

    # Add some randomness to make it look real
    return {
        "score": base_score + random.randint(-5, 5),
        "technical_score": base_score + random.randint(-5, 5),
        "communication_score": base_score + random.randint(-5, 5),
        "relevance_score": base_score + random.randint(-5, 5),
        "completeness_score": base_score + random.randint(-5, 5),
        "feedback": feedback
    }

def generate_feedback(interview_id: int):
    return {
        "strengths": ["Good technical understanding", "Clear explanations"],
        "weaknesses": ["Improve explanation structure", "Provide more concrete examples"],
        "recommendations": ["Practice 20 Python questions", "Revise OOP concepts"]
    }

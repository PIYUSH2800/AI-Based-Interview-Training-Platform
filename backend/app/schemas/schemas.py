from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# --- User Schemas ---
class UserBase(BaseModel):
    name: str
    email: EmailStr
    education: Optional[str] = None
    experience_level: Optional[str] = None

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Profile Schemas ---
class ProfileBase(BaseModel):
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    skills: Optional[str] = None
    certifications: Optional[str] = None
    target_role: Optional[str] = None

class ProfileCreate(ProfileBase):
    pass

class Profile(ProfileBase):
    id: int
    user_id: int
    resume_path: Optional[str] = None
    
    class Config:
        from_attributes = True

# --- Unified User Profile Schemas ---
class UserProfileResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    education: Optional[str] = None
    experience_level: Optional[str] = None
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    skills: Optional[str] = None
    certifications: Optional[str] = None
    target_role: Optional[str] = None
    resume_path: Optional[str] = None

    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    education: Optional[str] = None
    experience_level: Optional[str] = None
    phone: Optional[str] = None
    college: Optional[str] = None
    degree: Optional[str] = None
    skills: Optional[str] = None
    certifications: Optional[str] = None
    target_role: Optional[str] = None
    resume_path: Optional[str] = None

# --- Auth Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- Answer Schemas ---
class AnswerBase(BaseModel):
    answer_text: str
    score: Optional[float] = None
    technical_score: Optional[float] = None
    communication_score: Optional[float] = None
    relevance_score: Optional[float] = None
    completeness_score: Optional[float] = None
    feedback: Optional[str] = None

class AnswerCreate(AnswerBase):
    pass

class Answer(AnswerBase):
    id: int
    question_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Question Schemas ---
class QuestionBase(BaseModel):
    question_text: str
    question_type: str
    difficulty: str
    topic: Optional[str] = None
    sequence_number: int

class QuestionCreate(QuestionBase):
    pass

class Question(QuestionBase):
    id: int
    interview_id: int
    answer: Optional[Answer] = None
    
    class Config:
        from_attributes = True

# --- Interview Schemas ---
class InterviewBase(BaseModel):
    job_role: str
    interview_type: str
    difficulty: str
    mode: str
    total_questions: int

class InterviewCreate(InterviewBase):
    pass

class Interview(InterviewBase):
    id: int
    user_id: int
    overall_score: Optional[float] = None
    duration: Optional[int] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class InterviewDetail(Interview):
    questions: List[Question] = []
    
    class Config:
        from_attributes = True


# --- Coding Problem Schemas ---
class CodingProblemSummary(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: str
    category: str

    class Config:
        from_attributes = True

class CodingProblemDetail(BaseModel):
    id: int
    title: str
    slug: str
    difficulty: str
    category: str
    description: str
    examples: str  # JSON formatted string or list
    constraints: str  # JSON formatted string or list
    starter_code: str  # JSON formatted string or dict
    supported_languages: str  # JSON formatted string or list
    created_at: datetime

    class Config:
        from_attributes = True


# --- Code Execution Schemas ---
class TestCaseSchema(BaseModel):
    id: int
    problem_id: int
    input: str
    expected_output: str
    is_sample: bool

    class Config:
        from_attributes = True


class CodeRunRequest(BaseModel):
    problem_id: int
    language: str
    code: str


class TestCaseResult(BaseModel):
    test_case_id: Optional[int] = None
    is_sample: bool = False
    passed: bool
    input: Optional[str] = None
    expected_output: Optional[str] = None
    output: Optional[str] = None
    execution_time_ms: Optional[float] = None
    error: Optional[str] = None


class CodeRunResponse(BaseModel):
    status: str  # completed, compile_error, runtime_error, timeout, execution_error
    language: str
    passed: int
    failed: int
    total: int
    results: List[TestCaseResult] = []
    error: Optional[str] = None


class CodingSubmissionBase(BaseModel):
    problem_id: int
    language: str
    status: str
    score: float
    passed_tests: int
    total_tests: int
    execution_time_ms: Optional[float] = None
    error_message: Optional[str] = None

class CodingSubmissionResponse(CodingSubmissionBase):
    id: int
    created_at: datetime
    problem_title: Optional[str] = None

    class Config:
        from_attributes = True

class CodingFeedbackBase(BaseModel):
    summary: str
    approach: str
    correctness: str
    time_complexity: str
    space_complexity: str
    strengths: List[str]
    issues: List[str]
    improvements: List[str]
    better_approach: str
    interview_tips: List[str]

class CodingFeedbackCreate(CodingFeedbackBase):
    provider: str

class CodingFeedbackResponse(CodingFeedbackBase):
    id: int
    submission_id: int
    provider: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class CodingSubmissionDetail(CodingSubmissionResponse):
    source_code: str
    feedback: Optional[CodingFeedbackResponse] = None
    
    class Config:
        from_attributes = True



# --- Communication Analytics Schemas ---

class AiCommunicationFeedback(BaseModel):
    directness: str = ""
    structure: str = ""
    conciseness: str = ""
    suggestion: str = ""


class AnswerAnalytics(BaseModel):
    question_id: int
    sequence_number: int
    question_text: str
    answer_text: str
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    max_sentence_length: int
    estimated_speaking_time_seconds: int
    estimated_wpm: int
    filler_word_count: int
    filler_word_rate: float
    detected_fillers: dict
    ai_feedback: Optional[AiCommunicationFeedback] = None


class CommunicationAnalyticsResponse(BaseModel):
    interview_id: int
    total_words: int
    total_sentences: int
    total_filler_words: int
    avg_filler_rate: float
    avg_wpm: int
    overall_suggestion: str
    per_question: List[AnswerAnalytics] = []


# --- Checkpoint 7C Interview Intelligence Schemas ---

class TopicPerformance(BaseModel):
    topic: str
    question_count: int
    average_score: float
    coverage_status: str  # e.g. "Strong", "Good", "Needs Practice"


class CategoryScores(BaseModel):
    technical: float
    communication: float
    relevance: float
    completeness: float


class InterviewIntelligenceResponse(BaseModel):
    interview_id: int
    job_role: str
    interview_type: str
    difficulty: str
    overall_score: float
    category_scores: CategoryScores
    topic_performance: List[TopicPerformance] = []
    strengths: List[str] = []
    improvement_areas: List[str] = []
    practice_recommendations: List[str] = []
    ai_summary: str = ""


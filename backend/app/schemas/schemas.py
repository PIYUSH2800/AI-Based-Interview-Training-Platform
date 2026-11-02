from pydantic import BaseModel, ConfigDict, EmailStr, field_validator
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
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime

# --- Password Reset Schemas ---
class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ForgotPasswordResponse(BaseModel):
    message: str

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return v

class ResetPasswordResponse(BaseModel):
    message: str

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
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    resume_path: Optional[str] = None

# --- Unified User Profile Schemas ---
class UserProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    model_config = ConfigDict(from_attributes=True)

    id: int
    question_id: int
    created_at: datetime

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
    model_config = ConfigDict(from_attributes=True)

    id: int
    interview_id: int
    answer: Optional[Answer] = None

# --- Interview Schemas ---
ALLOWED_TOTAL_QUESTIONS = [3, 5, 10, 15, 20]

class InterviewBase(BaseModel):
    job_role: str
    interview_type: str
    difficulty: str
    mode: str
    total_questions: int

class InterviewCreate(InterviewBase):
    @field_validator("total_questions")
    @classmethod
    def validate_total_questions(cls, v: int) -> int:
        if v not in ALLOWED_TOTAL_QUESTIONS:
            raise ValueError(f"total_questions must be one of {ALLOWED_TOTAL_QUESTIONS}, got {v}")
        return v

class Interview(InterviewBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    overall_score: Optional[float] = None
    duration: Optional[int] = None
    created_at: datetime

class InterviewDetail(Interview):
    model_config = ConfigDict(from_attributes=True)

    questions: List[Question] = []


# --- Coding Problem Schemas ---
class CodingProblemSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    difficulty: str
    category: str
    module_id: Optional[int] = None
    order_index: Optional[int] = 1
    is_solved: Optional[bool] = False
    is_locked: Optional[bool] = False

class CodingProblemDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

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
    module_id: Optional[int] = None
    order_index: Optional[int] = 1
    is_solved: Optional[bool] = False
    is_locked: Optional[bool] = False


# --- Coding Module & Progressive Learning Schemas ---
class CodingModuleSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    title: str
    description: Optional[str] = None
    order_index: int
    icon_name: str = "Code"
    prerequisite_module_id: Optional[int] = None
    required_prerequisite_count: int = 0
    total_problems: int = 0
    solved_problems: int = 0
    is_unlocked: bool = True
    unlock_requirement: str = "Available"

class CodingModuleDetail(CodingModuleSummary):
    model_config = ConfigDict(from_attributes=True)

    problems: List[CodingProblemSummary] = []

class UserCodingProgressResponse(BaseModel):
    total_problems: int
    total_unique_solved: int
    overall_progress_percent: float
    unlocked_modules_count: int
    total_modules_count: int
    modules: List[CodingModuleSummary] = []


# --- Code Execution Schemas ---
class TestCaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_id: int
    input: str
    expected_output: str
    is_sample: bool


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
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    problem_title: Optional[str] = None

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
    model_config = ConfigDict(from_attributes=True)

    id: int
    submission_id: int
    provider: str
    created_at: datetime

class CodingSubmissionDetail(CodingSubmissionResponse):
    model_config = ConfigDict(from_attributes=True)

    source_code: str
    feedback: Optional[CodingFeedbackResponse] = None


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


# --- Checkpoint 10F AI Coding Mentor Schemas ---

class CodingHintRequest(BaseModel):
    level: int  # 1, 2, or 3


class CodingHintResponse(BaseModel):
    problem_id: int
    level: int
    title: str
    hint: str
    key_takeaways: List[str] = []
    edge_cases: List[str] = []
    provider: str = "mock"


class CodingExplanationResponse(BaseModel):
    problem_id: int
    title: str
    difficulty: str
    category: str
    intuition: str
    brute_force: str
    optimized_approach: str
    step_by_step: List[str] = []
    time_complexity: str
    space_complexity: str
    common_mistakes: List[str] = []
    edge_cases: List[str] = []
    interview_tips: List[str] = []
    solution_code: Optional[dict] = None
    provider: str = "mock"


class ProblemRecommendationItem(BaseModel):
    problem: CodingProblemSummary
    category: str  # "Continue Learning" | "Practice Weak Topics" | "Increase Difficulty" | "Review Previous Mistakes"
    reason: str
    priority: int


class ProblemRecommendationsResponse(BaseModel):
    total_recommended: int
    recommendations: List[ProblemRecommendationItem] = []


class TopicSkillStats(BaseModel):
    topic: str
    total_problems: int
    solved_problems: int
    attempts: int
    success_rate: float


class DifficultySkillStats(BaseModel):
    difficulty: str
    total_problems: int
    solved_problems: int
    attempts: int
    success_rate: float


class CodingSkillsResponse(BaseModel):
    total_unique_solved: int
    total_problems: int
    total_submissions: int
    overall_acceptance_rate: float
    difficulty_breakdown: List[DifficultySkillStats] = []
    topic_breakdown: List[TopicSkillStats] = []
    stronger_topics: List[str] = []
    topics_needing_practice: List[str] = []
    suggested_next_steps: List[str] = []

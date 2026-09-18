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


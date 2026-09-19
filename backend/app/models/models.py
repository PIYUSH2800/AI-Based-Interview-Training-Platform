from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)
    education = Column(String)
    experience_level = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    profile = relationship("Profile", back_populates="user", uselist=False)
    interviews = relationship("Interview", back_populates="user")
    recommendations = relationship("Recommendation", back_populates="user")
    coding_submissions = relationship("CodingSubmission", back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    phone = Column(String, nullable=True)
    college = Column(String, nullable=True)
    degree = Column(String, nullable=True)
    skills = Column(Text, nullable=True) # Comma separated or JSON string
    certifications = Column(Text, nullable=True)
    target_role = Column(String, nullable=True)
    resume_path = Column(String, nullable=True)

    user = relationship("User", back_populates="profile")


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    job_role = Column(String)
    interview_type = Column(String)
    difficulty = Column(String)
    mode = Column(String) # Text or Voice
    total_questions = Column(Integer)
    overall_score = Column(Float, nullable=True)
    duration = Column(Integer, nullable=True) # in seconds
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="interviews")
    questions = relationship("Question", back_populates="interview")


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    question_text = Column(Text)
    question_type = Column(String)
    difficulty = Column(String)
    topic = Column(String, nullable=True)
    sequence_number = Column(Integer)

    interview = relationship("Interview", back_populates="questions")
    answer = relationship("Answer", back_populates="question", uselist=False)


class Answer(Base):
    __tablename__ = "answers"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(Integer, ForeignKey("questions.id"), unique=True)
    answer_text = Column(Text)
    score = Column(Float, nullable=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    relevance_score = Column(Float, nullable=True)
    completeness_score = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    question = relationship("Question", back_populates="answer")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String)
    recommendation = Column(Text)
    priority = Column(Integer) # e.g., 1=High, 2=Medium, 3=Low
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="recommendations")


class CodingProblem(Base):
    __tablename__ = "coding_problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    slug = Column(String, unique=True, index=True)
    difficulty = Column(String) # Easy, Medium, Hard
    category = Column(String) # Arrays, Strings, Stack, etc.
    description = Column(Text)
    examples = Column(Text) # JSON string of examples
    constraints = Column(Text) # JSON string of constraints
    starter_code = Column(Text) # JSON string mapping language to code template
    supported_languages = Column(Text) # JSON string list of supported languages
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    test_cases = relationship("TestCase", back_populates="problem", cascade="all, delete-orphan")


class TestCase(Base):
    __tablename__ = "test_cases"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("coding_problems.id"))
    input = Column(Text)
    expected_output = Column(Text)
    is_sample = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    problem = relationship("CodingProblem", back_populates="test_cases")


class CodingSubmission(Base):
    __tablename__ = "coding_submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    problem_id = Column(Integer, ForeignKey("coding_problems.id"))
    language = Column(String)
    source_code = Column(Text)
    status = Column(String) # accepted, wrong_answer, compile_error, runtime_error, timeout, execution_error
    score = Column(Float)
    passed_tests = Column(Integer)
    total_tests = Column(Integer)
    execution_time_ms = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="coding_submissions")
    problem = relationship("CodingProblem")
    feedback = relationship("CodingFeedback", back_populates="submission", uselist=False, cascade="all, delete-orphan")

class CodingFeedback(Base):
    __tablename__ = "coding_feedback"

    id = Column(Integer, primary_key=True, index=True)
    submission_id = Column(Integer, ForeignKey("coding_submissions.id"), unique=True)
    summary = Column(Text)
    approach = Column(Text)
    correctness = Column(Text)
    time_complexity = Column(Text)
    space_complexity = Column(Text)
    strengths = Column(Text) # JSON string
    issues = Column(Text) # JSON string
    improvements = Column(Text) # JSON string
    better_approach = Column(Text)
    interview_tips = Column(Text) # JSON string
    provider = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    submission = relationship("CodingSubmission", back_populates="feedback")

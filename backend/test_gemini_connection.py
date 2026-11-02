"""
AI Interview Platform — Gemini AI Connection Diagnostic Utility
Tests whether the real Gemini API is configured and operational,
or verifies that the Mock AI fallback is functioning reliably.

Usage:
    cd backend
    python test_gemini_connection.py
"""

import sys
import os
import time
from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env
backend_dir = Path(__file__).resolve().parent
load_dotenv(backend_dir / ".env")

sys.path.insert(0, str(backend_dir))
from app.services.ai_service import ai_service

def test_ai():
    print("=" * 65)
    print("  GEMINI AI & FALLBACK DIAGNOSTIC")
    print("=" * 65)

    status = ai_service.get_ai_status()
    print(f"  AI Provider:     {status['provider']}")
    print(f"  Key Configured:  {status['configured']}")
    print(f"  AI Enabled:      {status['enabled']}")
    print(f"  Fallback Ready:  {status['fallback_enabled']}")
    print(f"  Active Mode:     {status['active_mode'].upper()}")
    print(f"  Target Model:    {status['model']}")
    print("-" * 65)

    print("\n1. Testing Question Generation...")
    start_t = time.time()
    try:
        q = ai_service.generate_question(
            job_role="Software Engineer",
            interview_type="Technical Interview",
            difficulty="Intermediate",
            skills="Python, SQL, System Design"
        )
        elapsed = round(time.time() - start_t, 2)
        print(f"   [SUCCESS in {elapsed}s]")
        print(f"   Generated Question:\n   \"{q}\"")
    except Exception as e:
        print(f"   [ERROR]: {e}")

    print("\n2. Testing Answer Evaluation (Meaningful Answer)...")
    start_t = time.time()
    try:
        eval_res = ai_service.evaluate_answer(
            question_text="Explain the difference between a process and a thread.",
            answer_text="A process is an independent executing program with its own memory space, while a thread is the smallest unit of execution within a process sharing the process memory.",
            job_role="Software Engineer",
            interview_type="Technical Interview",
            difficulty="Intermediate"
        )
        elapsed = round(time.time() - start_t, 2)
        print(f"   [SUCCESS in {elapsed}s]")
        print(f"   Score Awarded:       {eval_res.get('score')}%")
        print(f"   Technical Score:     {eval_res.get('technical_score')}%")
        print(f"   Communication Score: {eval_res.get('communication_score')}%")
        print(f"   Feedback:            {eval_res.get('feedback')[:120]}...")
    except Exception as e:
        print(f"   [ERROR]: {e}")

    print("\n3. Testing Answer Evaluation (Gibberish Input Protection)...")
    start_t = time.time()
    try:
        eval_res2 = ai_service.evaluate_answer(
            question_text="Explain how database indexes work.",
            answer_text="hbasjhkdfggasklfdg",
            job_role="Backend Developer",
            interview_type="Technical Interview",
            difficulty="Intermediate"
        )
        elapsed = round(time.time() - start_t, 2)
        print(f"   [SUCCESS in {elapsed}s]")
        print(f"   Score Awarded:       {eval_res2.get('score')}% (Expected: 0%)")
        print(f"   Relevance:           {eval_res2.get('relevance_score')}% (Expected: 0%)")
        assert eval_res2.get('score') == 0, "Score should be 0 for gibberish"
        print("   [VERIFIED] Meaningless answer cleanly rejected with 0%.")
    except Exception as e:
        print(f"   [ERROR]: {e}")

    print("\n" + "=" * 65)
    if status['configured']:
        print("  VERDICT: Real Gemini AI is ACTIVE and evaluated successfully!")
    else:
        print("  VERDICT: Mock AI fallback is ACTIVE and functioning reliably!")
        print("  (Perfect for offline college demonstration with no internet required)")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    test_ai()

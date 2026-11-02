import json
from typing import List, Union, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import CodingProblem, TestCase, User
from app.schemas.schemas import (
    CodingProblemSummary,
    CodingProblemDetail,
    CodeRunRequest,
    CodeRunResponse,
    CodingSubmissionResponse,
    CodingSubmissionDetail,
    CodingFeedbackResponse,
    CodingHintRequest,
    CodingHintResponse,
    CodingExplanationResponse,
    ProblemRecommendationsResponse,
    CodingSkillsResponse,
)
from app.api.profile_routes import get_current_user
from app.services.executor import get_code_executor, CODE_MAX_SOURCE_SIZE
from app.services.coding_progress import check_problem_access
from app.services.coding_mentor import get_problem_recommendations, get_user_skill_analytics

router = APIRouter(
    prefix="/api/coding",
    tags=["Coding Problems"]
)

INITIAL_PROBLEMS = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "difficulty": "Easy",
        "category": "Arrays & Hashing",
        "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice. You can return the answer in any order.",
        "examples": json.dumps([
            {
                "input": "nums = [2, 7, 11, 15], target = 9",
                "output": "[0, 1]",
                "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
            },
            {
                "input": "nums = [3, 2, 4], target = 6",
                "output": "[1, 2]",
                "explanation": "Because nums[1] + nums[2] == 6, we return [1, 2]."
            },
            {
                "input": "nums = [3, 3], target = 6",
                "output": "[0, 1]",
                "explanation": "Because nums[0] + nums[1] == 6, we return [0, 1]."
            }
        ]),
        "constraints": json.dumps([
            "2 <= nums.length <= 10^4",
            "-10^9 <= nums[i] <= 10^9",
            "-10^9 <= target <= 10^9",
            "Only one valid answer exists."
        ]),
        "starter_code": json.dumps({
            "python": "def twoSum(nums: list[int], target: int) -> list[int]:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        // Write your solution here\n        return new int[]{};\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"])
    },
    {
        "title": "Reverse a String",
        "slug": "reverse-string",
        "difficulty": "Easy",
        "category": "Strings",
        "description": "Write a function that reverses a string. The input string is given as an array of characters `s`.\n\nYou must do this by modifying the input array in-place with O(1) extra memory.",
        "examples": json.dumps([
            {
                "input": 's = ["h","e","l","l","o"]',
                "output": '["o","l","l","e","h"]',
                "explanation": "Reverse the character array in-place."
            },
            {
                "input": 's = ["H","a","n","n","a","h"]',
                "output": '["h","a","n","n","a","H"]',
                "explanation": "Reverse the character array in-place."
            }
        ]),
        "constraints": json.dumps([
            "1 <= s.length <= 10^5",
            "s[i] is a printable ascii character."
        ]),
        "starter_code": json.dumps({
            "python": "def reverseString(s: list[str]) -> None:\n    # Do not return anything, modify s in-place instead.\n    pass",
            "java": "class Solution {\n    public void reverseString(char[] s) {\n        // Modify s in-place\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    void reverseString(vector<char>& s) {\n        // Modify s in-place\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"])
    },
    {
        "title": "Valid Parentheses",
        "slug": "valid-parentheses",
        "difficulty": "Easy",
        "category": "Stack",
        "description": "Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.",
        "examples": json.dumps([
            {
                "input": 's = "()"',
                "output": "true",
                "explanation": "Matching parentheses."
            },
            {
                "input": 's = "()[]{}"',
                "output": "true",
                "explanation": "All pairs are correctly closed."
            },
            {
                "input": 's = "(]"',
                "output": "false",
                "explanation": "Mismatched bracket types."
            }
        ]),
        "constraints": json.dumps([
            "1 <= s.length <= 10^4",
            "s consists of parentheses characters only '()[]{}'."
        ]),
        "starter_code": json.dumps({
            "python": "def isValid(s: str) -> bool:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public boolean isValid(String s) {\n        // Write your solution here\n        return false;\n    }\n}",
            "cpp": "#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool isValid(string s) {\n        // Write your solution here\n        return false;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"])
    },
    {
        "title": "Maximum Subarray",
        "slug": "maximum-subarray",
        "difficulty": "Medium",
        "category": "Arrays & DP",
        "description": "Given an integer array `nums`, find the contiguous subarray (containing at least one number) which has the largest sum and return its sum.\n\nA subarray is a contiguous part of an array.",
        "examples": json.dumps([
            {
                "input": "nums = [-2,1,-3,4,-1,2,1,-5,4]",
                "output": "6",
                "explanation": "Subarray [4,-1,2,1] has the largest sum = 6."
            },
            {
                "input": "nums = [1]",
                "output": "1",
                "explanation": "Subarray [1] has the largest sum = 1."
            },
            {
                "input": "nums = [5,4,-1,7,8]",
                "output": "23",
                "explanation": "Subarray [5,4,-1,7,8] has the largest sum = 23."
            }
        ]),
        "constraints": json.dumps([
            "1 <= nums.length <= 10^5",
            "-10^4 <= nums[i] <= 10^4"
        ]),
        "starter_code": json.dumps({
            "python": "def maxSubArray(nums: list[int]) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int maxSubArray(int[] nums) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int maxSubArray(vector<int>& nums) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"])
    },
    {
        "title": "Binary Search",
        "slug": "binary-search",
        "difficulty": "Easy",
        "category": "Binary Search",
        "description": "Given an array of integers `nums` which is sorted in ascending order, and an integer `target`, write a function to search `target` in `nums`.\n\nIf `target` exists, then return its index. Otherwise, return `-1`.\n\nYou must write an algorithm with O(log n) runtime complexity.",
        "examples": json.dumps([
            {
                "input": "nums = [-1,0,3,5,9,12], target = 9",
                "output": "4",
                "explanation": "9 exists in nums and its index is 4."
            },
            {
                "input": "nums = [-1,0,3,5,9,12], target = 2",
                "output": "-1",
                "explanation": "2 does not exist in nums so return -1."
            }
        ]),
        "constraints": json.dumps([
            "1 <= nums.length <= 10^4",
            "-10^4 < nums[i], target < 10^4",
            "All the integers in nums are unique.",
            "nums is sorted in ascending order."
        ]),
        "starter_code": json.dumps({
            "python": "def search(nums: list[int], target: int) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int search(int[] nums, int target) {\n        // Write your solution here\n        return -1;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int search(vector<int>& nums, int target) {\n        // Write your solution here\n        return -1;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"])
    },
    {
        "title": "Palindrome Check",
        "slug": "palindrome-check",
        "difficulty": "Easy",
        "category": "Strings",
        "description": "A phrase is a palindrome if, after converting all uppercase letters into lowercase letters and removing all non-alphanumeric characters, it reads the same forward and backward.\n\nGiven a string `s`, return `true` if it is a palindrome, or `false` otherwise.",
        "examples": json.dumps([
            {
                "input": 's = "A man, a plan, a canal: Panama"',
                "output": "true",
                "explanation": '"amanaplanacanalpanama" is a palindrome.'
            },
            {
                "input": 's = "race a car"',
                "output": "false",
                "explanation": '"raceacar" is not a palindrome.'
            },
            {
                "input": 's = " "',
                "output": "true",
                "explanation": 's is an empty string "" after removing non-alphanumeric characters, which reads the same forward and backward.'
            }
        ]),
        "constraints": json.dumps([
            "1 <= s.length <= 2 * 10^5",
            "s consists only of printable ASCII characters."
        ]),
        "starter_code": json.dumps({
            "python": "def isPalindrome(s: str) -> bool:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public boolean isPalindrome(String s) {\n        // Write your solution here\n        return false;\n    }\n}",
            "cpp": "#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool isPalindrome(string s) {\n        // Write your solution here\n        return false;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"])
    }
]

INITIAL_TEST_CASES = {
    "two-sum": [
        {"input": "[2, 7, 11, 15]\n9", "expected_output": "[0, 1]", "is_sample": True},
        {"input": "[3, 2, 4]\n6", "expected_output": "[1, 2]", "is_sample": True},
        {"input": "[3, 3]\n6", "expected_output": "[0, 1]", "is_sample": False},
        {"input": "[1, 5, 8, 3]\n11", "expected_output": "[2, 3]", "is_sample": False},
        {"input": "[-1, -2, -3, -4, -5]\n-8", "expected_output": "[2, 4]", "is_sample": False},
    ],
    "reverse-string": [
        {"input": '["h","e","l","l","o"]', "expected_output": '["o","l","l","e","h"]', "is_sample": True},
        {"input": '["H","a","n","n","a","h"]', "expected_output": '["h","a","n","n","a","H"]', "is_sample": True},
        {"input": '["a","b","c"]', "expected_output": '["c","b","a"]', "is_sample": False},
        {"input": '["A"]', "expected_output": '["A"]', "is_sample": False},
    ],
    "valid-parentheses": [
        {"input": "()", "expected_output": "true", "is_sample": True},
        {"input": "()[]{}", "expected_output": "true", "is_sample": True},
        {"input": "(]", "expected_output": "false", "is_sample": True},
        {"input": "([{}])", "expected_output": "true", "is_sample": False},
        {"input": "]", "expected_output": "false", "is_sample": False},
    ],
    "maximum-subarray": [
        {"input": "[-2,1,-3,4,-1,2,1,-5,4]", "expected_output": "6", "is_sample": True},
        {"input": "[1]", "expected_output": "1", "is_sample": True},
        {"input": "[5,4,-1,7,8]", "expected_output": "23", "is_sample": True},
        {"input": "[-1,-2,-3,-4]", "expected_output": "-1", "is_sample": False},
    ],
    "binary-search": [
        {"input": "[-1,0,3,5,9,12]\n9", "expected_output": "4", "is_sample": True},
        {"input": "[-1,0,3,5,9,12]\n2", "expected_output": "-1", "is_sample": True},
        {"input": "[5]\n5", "expected_output": "0", "is_sample": False},
        {"input": "[1, 3, 5, 7, 9]\n1", "expected_output": "0", "is_sample": False},
    ],
    "palindrome-check": [
        {"input": "A man, a plan, a canal: Panama", "expected_output": "true", "is_sample": True},
        {"input": "race a car", "expected_output": "false", "is_sample": True},
        {"input": " ", "expected_output": "true", "is_sample": True},
        {"input": "0P", "expected_output": "false", "is_sample": False},
    ]
}

def seed_problems_if_needed(db: Session):
    existing_count = db.query(CodingProblem).count()
    if existing_count == 0:
        for problem_data in INITIAL_PROBLEMS:
            problem = CodingProblem(**problem_data)
            db.add(problem)
        db.commit()

    # Seed test cases for original problems if missing
    problems = db.query(CodingProblem).all()
    for prob in problems:
        tc_count = db.query(TestCase).filter(TestCase.problem_id == prob.id).count()
        if tc_count == 0 and prob.slug in INITIAL_TEST_CASES:
            for tc_data in INITIAL_TEST_CASES[prob.slug]:
                test_case = TestCase(
                    problem_id=prob.id,
                    input=tc_data["input"],
                    expected_output=tc_data["expected_output"],
                    is_sample=tc_data["is_sample"]
                )
                db.add(test_case)
            db.commit()

    # Seed modules and expanded curriculum idempotently
    from app.services.coding_progress import seed_coding_system_if_needed
    seed_coding_system_if_needed(db)

@router.get("/problems", response_model=List[CodingProblemSummary])
def get_coding_problems(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    seed_problems_if_needed(db)
    problems = db.query(CodingProblem).all()
    return problems

@router.get("/problems/{problem_id}", response_model=CodingProblemDetail)
def get_coding_problem_detail(
    problem_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    seed_problems_if_needed(db)

    # Allow lookup by integer ID or string slug
    if problem_id.isdigit():
        problem = db.query(CodingProblem).filter(CodingProblem.id == int(problem_id)).first()
    else:
        problem = db.query(CodingProblem).filter(CodingProblem.slug == problem_id).first()

    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding problem not found"
        )

    return problem

@router.post("/run", response_model=CodeRunResponse)
def run_code(
    payload: CodeRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    seed_problems_if_needed(db)

    # 1. Validate problem_id
    problem = db.query(CodingProblem).filter(CodingProblem.id == payload.problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding problem not found"
        )

    # 1b. Server-side module unlock authorization check
    from app.services.coding_progress import check_problem_access
    accessible, reason = check_problem_access(db, problem, current_user.id if current_user else None)
    if not accessible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=reason or "Problem is locked. Complete prerequisite module requirements to unlock."
        )

    # 2. Validate language against allowlist
    supported_langs = json.loads(problem.supported_languages) if problem.supported_languages else ["python", "java", "cpp"]
    lang_clean = payload.language.lower().strip()
    if lang_clean not in supported_langs or lang_clean not in ["python", "java", "cpp"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported language '{payload.language}'. Supported languages are: {', '.join(supported_langs)}"
        )

    # 3. Validate code size & presence
    if not payload.code or not payload.code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code cannot be empty"
        )

    if len(payload.code.encode('utf-8')) > CODE_MAX_SOURCE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Source code size exceeds maximum limit of {CODE_MAX_SOURCE_SIZE} bytes"
        )

    # 4. Fetch test cases
    db_test_cases = db.query(TestCase).filter(TestCase.problem_id == problem.id).all()
    test_cases_list = [
        {
            "id": tc.id,
            "input": tc.input,
            "expected_output": tc.expected_output,
            "is_sample": tc.is_sample
        }
        for tc in db_test_cases
    ]

    if not test_cases_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No test cases configured for this coding problem"
        )

    # 5. Execute code in isolated execution environment
    try:
        executor = get_code_executor()
        execution_result = executor.execute(
            code=payload.code,
            language=lang_clean,
            test_cases=test_cases_list
        )
        return execution_result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Execution service error occurred"
        )


@router.post("/submit", response_model=CodingSubmissionDetail)
def submit_code(
    payload: CodeRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    seed_problems_if_needed(db)

    problem = db.query(CodingProblem).filter(CodingProblem.id == payload.problem_id).first()
    if not problem:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Coding problem not found")

    # Server-side module unlock authorization check
    from app.services.coding_progress import check_problem_access
    accessible, reason = check_problem_access(db, problem, current_user.id if current_user else None)
    if not accessible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=reason or "Problem is locked. Complete prerequisite module requirements to unlock."
        )

    supported_langs = json.loads(problem.supported_languages) if problem.supported_languages else ["python", "java", "cpp"]
    lang_clean = payload.language.lower().strip()
    if lang_clean not in supported_langs or lang_clean not in ["python", "java", "cpp"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported language '{payload.language}'.")

    if not payload.code or not payload.code.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Code cannot be empty")

    if len(payload.code.encode('utf-8')) > CODE_MAX_SOURCE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source code size exceeds maximum limit")

    db_test_cases = db.query(TestCase).filter(TestCase.problem_id == problem.id).all()
    test_cases_list = [{"id": tc.id, "input": tc.input, "expected_output": tc.expected_output, "is_sample": tc.is_sample} for tc in db_test_cases]

    if not test_cases_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No test cases configured")

    try:
        executor = get_code_executor()
        execution_result = executor.execute(code=payload.code, language=lang_clean, test_cases=test_cases_list)

        # Calculate score and determine status
        passed = execution_result.get("passed", 0)
        total = execution_result.get("total", len(test_cases_list))
        exec_status = execution_result.get("status", "execution_error")

        score = round((passed / total) * 100) if total > 0 else 0

        if exec_status == "completed":
            final_status = "accepted" if passed == total else "wrong_answer"
        else:
            final_status = exec_status

        # Calculate execution time
        total_time_ms = sum([r.get("execution_time_ms", 0) for r in execution_result.get("results", [])])

        # Save submission
        from app.models.models import CodingSubmission
        submission = CodingSubmission(
            user_id=current_user.id,
            problem_id=problem.id,
            language=lang_clean,
            source_code=payload.code,
            status=final_status,
            score=score,
            passed_tests=passed,
            total_tests=total,
            execution_time_ms=total_time_ms,
            error_message=execution_result.get("error")
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)

        # We don't expose hidden tests inputs/outputs, even in the execution results if it was passed through.
        # But this is just saving the record. The submission detail will be returned.

        return {
            "id": submission.id,
            "problem_id": submission.problem_id,
            "problem_title": problem.title,
            "language": submission.language,
            "status": submission.status,
            "score": submission.score,
            "passed_tests": submission.passed_tests,
            "total_tests": submission.total_tests,
            "execution_time_ms": submission.execution_time_ms,
            "error_message": submission.error_message,
            "created_at": submission.created_at,
            "source_code": submission.source_code
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Execution service error occurred")


@router.get("/submissions", response_model=List[CodingSubmissionResponse])
def get_submissions(
    problem_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.models import CodingSubmission
    query = db.query(CodingSubmission).filter(CodingSubmission.user_id == current_user.id)
    if problem_id:
        query = query.filter(CodingSubmission.problem_id == problem_id)

    submissions = query.order_by(CodingSubmission.created_at.desc()).all()

    results = []
    for sub in submissions:
        prob = db.query(CodingProblem).filter(CodingProblem.id == sub.problem_id).first()
        results.append({
            "id": sub.id,
            "problem_id": sub.problem_id,
            "problem_title": prob.title if prob else None,
            "language": sub.language,
            "status": sub.status,
            "score": sub.score,
            "passed_tests": sub.passed_tests,
            "total_tests": sub.total_tests,
            "execution_time_ms": sub.execution_time_ms,
            "error_message": sub.error_message,
            "created_at": sub.created_at
        })
    return results


@router.get("/submissions/{submission_id}", response_model=CodingSubmissionDetail)
def get_submission_detail(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.models import CodingSubmission
    submission = db.query(CodingSubmission).filter(
        CodingSubmission.id == submission_id,
        CodingSubmission.user_id == current_user.id
    ).first()

    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found or unauthorized")

    prob = db.query(CodingProblem).filter(CodingProblem.id == submission.problem_id).first()

    result = {
        "id": submission.id,
        "problem_id": submission.problem_id,
        "problem_title": prob.title if prob else None,
        "language": submission.language,
        "status": submission.status,
        "score": submission.score,
        "passed_tests": submission.passed_tests,
        "total_tests": submission.total_tests,
        "execution_time_ms": submission.execution_time_ms,
        "error_message": submission.error_message,
        "created_at": submission.created_at,
        "source_code": submission.source_code
    }

    if submission.feedback:
        result["feedback"] = {
            "id": submission.feedback.id,
            "submission_id": submission.feedback.submission_id,
            "summary": submission.feedback.summary,
            "approach": submission.feedback.approach,
            "correctness": submission.feedback.correctness,
            "time_complexity": submission.feedback.time_complexity,
            "space_complexity": submission.feedback.space_complexity,
            "strengths": json.loads(submission.feedback.strengths) if submission.feedback.strengths else [],
            "issues": json.loads(submission.feedback.issues) if submission.feedback.issues else [],
            "improvements": json.loads(submission.feedback.improvements) if submission.feedback.improvements else [],
            "better_approach": submission.feedback.better_approach,
            "interview_tips": json.loads(submission.feedback.interview_tips) if submission.feedback.interview_tips else [],
            "provider": submission.feedback.provider,
            "created_at": submission.feedback.created_at
        }

    return result

@router.post("/submissions/{submission_id}/feedback", response_model=CodingFeedbackResponse)
def get_coding_feedback(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.models.models import CodingSubmission, CodingFeedback
    from app.services.ai_service import ai_service
    seed_problems_if_needed(db)

    submission = db.query(CodingSubmission).filter(
        CodingSubmission.id == submission_id,
        CodingSubmission.user_id == current_user.id
    ).first()

    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found or unauthorized")

    if submission.feedback:
        return {
            "id": submission.feedback.id,
            "submission_id": submission.feedback.submission_id,
            "summary": submission.feedback.summary,
            "approach": submission.feedback.approach,
            "correctness": submission.feedback.correctness,
            "time_complexity": submission.feedback.time_complexity,
            "space_complexity": submission.feedback.space_complexity,
            "strengths": json.loads(submission.feedback.strengths) if submission.feedback.strengths else [],
            "issues": json.loads(submission.feedback.issues) if submission.feedback.issues else [],
            "improvements": json.loads(submission.feedback.improvements) if submission.feedback.improvements else [],
            "better_approach": submission.feedback.better_approach,
            "interview_tips": json.loads(submission.feedback.interview_tips) if submission.feedback.interview_tips else [],
            "provider": submission.feedback.provider,
            "created_at": submission.feedback.created_at
        }

    prob = db.query(CodingProblem).filter(CodingProblem.id == submission.problem_id).first()

    try:
        feedback_data = ai_service.generate_coding_feedback(
            problem_title=prob.title,
            problem_description=prob.description,
            difficulty=prob.difficulty,
            category=prob.category,
            language=submission.language,
            source_code=submission.source_code,
            status=submission.status,
            score=submission.score,
            passed_tests=submission.passed_tests,
            total_tests=submission.total_tests
        )

        feedback = CodingFeedback(
            submission_id=submission.id,
            summary=feedback_data.get("summary", ""),
            approach=feedback_data.get("approach", ""),
            correctness=feedback_data.get("correctness", ""),
            time_complexity=feedback_data.get("time_complexity", ""),
            space_complexity=feedback_data.get("space_complexity", ""),
            strengths=json.dumps(feedback_data.get("strengths", [])),
            issues=json.dumps(feedback_data.get("issues", [])),
            improvements=json.dumps(feedback_data.get("improvements", [])),
            better_approach=feedback_data.get("better_approach", ""),
            interview_tips=json.dumps(feedback_data.get("interview_tips", [])),
            provider=feedback_data.get("provider", "mock")
        )

        db.add(feedback)
        db.commit()
        db.refresh(feedback)

        return {
            "id": feedback.id,
            "submission_id": feedback.submission_id,
            "summary": feedback.summary,
            "approach": feedback.approach,
            "correctness": feedback.correctness,
            "time_complexity": feedback.time_complexity,
            "space_complexity": feedback.space_complexity,
            "strengths": json.loads(feedback.strengths) if feedback.strengths else [],
            "issues": json.loads(feedback.issues) if feedback.issues else [],
            "improvements": json.loads(feedback.improvements) if feedback.improvements else [],
            "better_approach": feedback.better_approach,
            "interview_tips": json.loads(feedback.interview_tips) if feedback.interview_tips else [],
            "provider": feedback.provider,
            "created_at": feedback.created_at
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to generate AI feedback: {str(e)}")


@router.post("/problems/{problem_id}/hints", response_model=CodingHintResponse)
def get_progressive_hint(
    problem_id: int,
    payload: CodingHintRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns a progressive hint (Level 1: Conceptual, Level 2: Approach, Level 3: Detailed).
    Enforces server-side problem access authorization.
    """
    if payload.level not in [1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hint level must be 1, 2, or 3."
        )

    seed_problems_if_needed(db)
    problem = db.query(CodingProblem).filter(CodingProblem.id == problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding problem not found"
        )

    # Server-side module unlock authorization check
    accessible, reason = check_problem_access(db, problem, current_user.id if current_user else None)
    if not accessible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=reason or "Problem is locked. Complete prerequisite module requirements to unlock."
        )

    from app.services.ai_service import ai_service
    hint_data = ai_service.generate_coding_hint(
        problem_title=problem.title,
        problem_description=problem.description,
        difficulty=problem.difficulty,
        category=problem.category,
        level=payload.level,
    )

    return {
        "problem_id": problem.id,
        "level": payload.level,
        "title": hint_data.get("title", f"Level {payload.level} Guidance"),
        "hint": hint_data.get("hint", ""),
        "key_takeaways": hint_data.get("key_takeaways", []),
        "edge_cases": hint_data.get("edge_cases", []),
        "provider": hint_data.get("provider", "mock"),
    }


@router.get("/problems/{problem_id}/explanation", response_model=CodingExplanationResponse)
def get_problem_explanation(
    problem_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns an educational solution explanation covering intuition, brute-force, optimal approach,
    complexities, common mistakes, edge cases, and interview tips.
    Enforces server-side problem access authorization.
    """
    seed_problems_if_needed(db)
    problem = db.query(CodingProblem).filter(CodingProblem.id == problem_id).first()
    if not problem:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coding problem not found"
        )

    # Server-side module unlock authorization check
    accessible, reason = check_problem_access(db, problem, current_user.id if current_user else None)
    if not accessible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=reason or "Problem is locked. Complete prerequisite module requirements to unlock."
        )

    from app.services.ai_service import ai_service
    explanation_data = ai_service.generate_coding_explanation(
        problem_title=problem.title,
        problem_description=problem.description,
        difficulty=problem.difficulty,
        category=problem.category,
    )

    # Starter/solution templates provided safely
    starter_code_dict = {}
    if problem.starter_code:
        try:
            starter_code_dict = json.loads(problem.starter_code)
        except Exception:
            pass

    return {
        "problem_id": problem.id,
        "title": problem.title,
        "difficulty": problem.difficulty,
        "category": problem.category,
        "intuition": explanation_data.get("intuition", ""),
        "brute_force": explanation_data.get("brute_force", ""),
        "optimized_approach": explanation_data.get("optimized_approach", ""),
        "step_by_step": explanation_data.get("step_by_step", []),
        "time_complexity": explanation_data.get("time_complexity", "O(N)"),
        "space_complexity": explanation_data.get("space_complexity", "O(1)"),
        "common_mistakes": explanation_data.get("common_mistakes", []),
        "edge_cases": explanation_data.get("edge_cases", []),
        "interview_tips": explanation_data.get("interview_tips", []),
        "solution_code": starter_code_dict,
        "provider": explanation_data.get("provider", "mock"),
    }


@router.get("/recommendations", response_model=ProblemRecommendationsResponse)
def get_recommendations_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns personalized, explainable problem recommendations across 4 categories:
    Continue Learning, Review Previous Mistakes, Practice Weak Topics, Increase Difficulty.
    """
    seed_problems_if_needed(db)
    return get_problem_recommendations(db, current_user.id)


@router.get("/skills", response_model=CodingSkillsResponse)
def get_skills_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Returns personalized coding skill analytics, difficulty breakdown, topic stats,
    stronger topics, topics needing practice, and suggested next steps.
    """
    seed_problems_if_needed(db)
    return get_user_skill_analytics(db, current_user.id)

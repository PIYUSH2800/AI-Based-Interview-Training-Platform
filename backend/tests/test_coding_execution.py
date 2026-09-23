import os
import sys

# Ensure current working directory is at top of sys.path and remove conflicting paths
backend_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
sys.path = [p for p in sys.path if "aiva_mock_interviews" not in p]

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.models.models import User, CodingProblem, TestCase
from app.auth.auth import create_access_token, get_password_hash
from app.services.executor import FORCE_MOCK_EXECUTOR, MockCodeExecutor
from unittest.mock import patch
from tests.conftest import TestingSessionLocal

@pytest.fixture(autouse=True)
def seed_test_user():
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "testuser@example.com").first()
    if not user:
        user = User(
            name="Test User",
            email="testuser@example.com",
            password_hash=get_password_hash("password123"),
            education="B.Tech",
            experience_level="Intermediate"
        )
        db.add(user)
        db.commit()
    db.close()
    yield

client = TestClient(app)

def get_auth_headers():
    token = create_access_token({"sub": "testuser@example.com"})
    return {"Authorization": f"Bearer {token}"}


def test_unauthenticated_execution_rejected():
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "python",
        "code": "print('hello')"
    })
    assert response.status_code == 401


def test_invalid_problem_id():
    response = client.post("/api/coding/run", json={
        "problem_id": 99999,
        "language": "python",
        "code": "def twoSum(nums, target): return [0, 1]"
    }, headers=get_auth_headers())
    assert response.status_code == 404
    assert "Coding problem not found" in response.json()["detail"]


def test_unsupported_language_rejected():
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "ruby",
        "code": "puts 'hello'"
    }, headers=get_auth_headers())
    assert response.status_code == 400
    assert "Unsupported language" in response.json()["detail"]


def test_empty_code_rejected():
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "python",
        "code": "   "
    }, headers=get_auth_headers())
    assert response.status_code == 400
    assert "Code cannot be empty" in response.json()["detail"]


def test_oversized_code_rejected():
    large_code = "a = 1\n" * 20000  # > 64 KB
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "python",
        "code": large_code
    }, headers=get_auth_headers())
    assert response.status_code == 400
    assert "exceeds maximum limit" in response.json()["detail"]


@patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor())
def test_mock_python_execution_success(mock_get_executor):
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "python",
        "code": "def twoSum(nums: list[int], target: int) -> list[int]:\n    seen = {}\n    for i, num in enumerate(nums):\n        if target - num in seen:\n            return [seen[target - num], i]\n        seen[num] = i\n    return []"
    }, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["language"] == "python"
    assert data["total"] > 0
    assert data["passed"] == data["total"]


@patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor())
def test_mock_java_execution_success(mock_get_executor):
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "java",
        "code": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        java.util.Map<Integer, Integer> map = new java.util.HashMap<>();\n        for (int i = 0; i < nums.length; i++) {\n            if (map.containsKey(target - nums[i])) {\n                return new int[]{map.get(target - nums[i]), i};\n            }\n            map.put(nums[i], i);\n        }\n        return new int[]{};\n    }\n}"
    }, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["language"] == "java"
    assert data["passed"] > 0


@patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor())
def test_mock_cpp_execution_success(mock_get_executor):
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "cpp",
        "code": "#include <vector>\n#include <unordered_map>\nusing namespace std;\nclass Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        unordered_map<int, int> m;\n        for (int i = 0; i < nums.size(); i++) {\n            if (m.count(target - nums[i])) return {m[target - nums[i]], i};\n            m[nums[i]] = i;\n        }\n        return {};\n    }\n};"
    }, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["language"] == "cpp"


@patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor())
def test_mock_compilation_error(mock_get_executor):
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "java",
        "code": "class InvalidCode compile_error_trigger {"
    }, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "compile_error"
    assert "Compilation error" in data["error"]


@patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor())
def test_mock_runtime_error(mock_get_executor):
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "python",
        "code": "def twoSum(nums, target):\n    raise Exception('runtime_error_trigger')"
    }, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "runtime_error"
    assert "Runtime Error" in data["error"]


@patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor())
def test_mock_timeout(mock_get_executor):
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "python",
        "code": "def twoSum(nums, target):\n    while True: pass"
    }, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "timeout"
    assert "timed out" in data["error"]


@patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor())
def test_hidden_test_data_privacy(mock_get_executor):
    response = client.post("/api/coding/run", json={
        "problem_id": 1,
        "language": "python",
        "code": "def twoSum(nums, target): return []"
    }, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()

    for result in data["results"]:
        if not result["is_sample"]:
            # Hidden test case must NOT return input or expected output
            assert result["input"] is None
            assert result["expected_output"] is None

def test_unauthenticated_submit_rejected():
    response = client.post("/api/coding/submit", json={
        "problem_id": 1,
        "language": "python",
        "code": "print('hello')"
    })
    assert response.status_code == 401

@patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor())
def test_submit_success_score(mock_get_executor):
    # Test valid submission giving 100 score
    response = client.post("/api/coding/submit", json={
        "problem_id": 1,
        "language": "python",
        "code": "def twoSum(nums, target): return [0, 1]"  # Mock assumes success
    }, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "accepted"
    assert data["score"] == 100
    assert data["language"] == "python"
    assert "source_code" in data
    
    # Store submission id for next test
    sub_id = data["id"]
    
    # Test getting submission history
    hist_resp = client.get("/api/coding/submissions", headers=get_auth_headers())
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()
    assert len(hist_data) >= 1
    assert hist_data[0]["id"] == sub_id
    assert "source_code" not in hist_data[0]  # list should not have source code
    
    # Test getting specific submission details
    detail_resp = client.get(f"/api/coding/submissions/{sub_id}", headers=get_auth_headers())
    assert detail_resp.status_code == 200
    detail_data = detail_resp.json()
    assert detail_data["source_code"] == "def twoSum(nums, target): return [0, 1]"
    
    # Test user isolation: another user tries to fetch
    other_token = create_access_token({"sub": "other@example.com"})
    
    # Create the other user directly in db
    db = TestingSessionLocal()
    from app.models.models import User
    other_user = User(name="Other", email="other@example.com", password_hash="hash")
    db.add(other_user)
    db.commit()
    db.close()
    
    iso_resp = client.get(f"/api/coding/submissions/{sub_id}", headers={"Authorization": f"Bearer {other_token}"})
    assert iso_resp.status_code == 404

@patch("app.api.coding_routes.get_code_executor", return_value=MockCodeExecutor())
def test_submit_incorrect_score(mock_get_executor):
    # Mock timeout will result in 0 passed
    response = client.post("/api/coding/submit", json={
        "problem_id": 1,
        "language": "python",
        "code": "def twoSum(nums, target):\n    while True: pass"
    }, headers=get_auth_headers())
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "timeout"
    assert data["score"] == 0

import os
import sys

# Remove other app paths
sys.path = [p for p in sys.path if 'aiva_mock_interviews' not in p]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.executor import DockerCodeExecutor, ExecutionLimits

def run_tests():
    executor = DockerCodeExecutor()
    print("Docker available:", executor.is_docker_available())

    limits = ExecutionLimits(timeout=10.0)
    
    test_cases_two_sum = [
        {"id": 1, "input": "[2, 7, 11, 15]\n9", "expected_output": "[0, 1]", "is_sample": True}
    ]

    print("\n--- Python Correct ---")
    res = executor.execute(
        code="def twoSum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i]+nums[j] == target:\n                return [i, j]",
        language="python",
        test_cases=test_cases_two_sum,
        limits=limits
    )
    print(res["status"], res["passed"], "/", res["total"])

    print("\n--- Python Incorrect ---")
    res = executor.execute(
        code="def twoSum(nums, target):\n    return [0, 0]",
        language="python",
        test_cases=test_cases_two_sum,
        limits=limits
    )
    print(res["status"], res["passed"], "/", res["total"])

    print("\n--- Python Syntax Error ---")
    res = executor.execute(
        code="def twoSum(nums, target) # missing colon\n    return [0, 1]",
        language="python",
        test_cases=test_cases_two_sum,
        limits=limits
    )
    print(res["status"], (res.get("error") or "")[:50].replace("\n", " "))

    print("\n--- Python Runtime Error ---")
    res = executor.execute(
        code="def twoSum(nums, target):\n    return nums[100]",
        language="python",
        test_cases=test_cases_two_sum,
        limits=limits
    )
    print(res["status"], (res.get("error") or "")[:50].replace("\n", " "))

    print("\n--- Python Timeout ---")
    res = executor.execute(
        code="def twoSum(nums, target):\n    while True:\n        pass",
        language="python",
        test_cases=test_cases_two_sum,
        limits=limits
    )
    print(res["status"])

    test_cases_cpp = [
        {"id": 1, "input": "", "expected_output": "Hello", "is_sample": True}
    ]

    print("\n--- C++ Execution ---")
    res = executor.execute(
        code="#include <iostream>\nusing namespace std;\nint main() { cout << \"Hello\"; return 0; }",
        language="cpp",
        test_cases=test_cases_cpp,
        limits=limits
    )
    print(res["status"], res["passed"], "/", res["total"])

    print("\n--- C++ Compile Error ---")
    res = executor.execute(
        code="#include <iostream>\nusing namespace std;\nint main() { cout << \"Hello\" return 0; }",
        language="cpp",
        test_cases=test_cases_cpp,
        limits=limits
    )
    print(res["status"], (res.get("error") or "")[:50].replace("\n", " "))

    test_cases_java = [
        {"id": 1, "input": "", "expected_output": "Hello", "is_sample": True}
    ]

    print("\n--- Java Execution ---")
    res = executor.execute(
        code="public class Solution { public static void main(String[] args) { System.out.print(\"Hello\"); } }",
        language="java",
        test_cases=test_cases_java,
        limits=limits
    )
    print(res["status"], res["passed"], "/", res["total"])

    print("\n--- Java Compile Error ---")
    res = executor.execute(
        code="public class Solution { public static void main(String[] args) { System.out.print(\"Hello\") } }",
        language="java",
        test_cases=test_cases_java,
        limits=limits
    )
    print(res["status"], (res.get("error") or "")[:50].replace("\n", " "))

if __name__ == '__main__':
    run_tests()

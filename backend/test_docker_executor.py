import os
import sys
import json

# Adjust path to import app modules
sys.path = [p for p in sys.path if 'aiva_mock_interviews' not in p]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.executor import DockerCodeExecutor, ExecutionLimits

def run_tests():
    executor = DockerCodeExecutor()
    if not executor.is_docker_available():
        print("DOCKER NOT AVAILABLE")
        return
    else:
        print("DOCKER IS AVAILABLE")

    limits = ExecutionLimits(timeout=2.0)
    
    # 1. Python correct solution
    print("--- 1. Python correct solution ---")
    code_py_correct = "def twoSum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i+1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []"
    tc_py = [{"id": 1, "input": "[2,7,11,15]\n9", "expected_output": "[0, 1]", "is_sample": True}]
    res = executor.execute(code_py_correct, "python", tc_py, limits)
    print(json.dumps(res, indent=2))

    # 2. Python incorrect solution
    print("--- 2. Python incorrect solution ---")
    code_py_incorrect = "def twoSum(nums, target):\n    return [0, 0]"
    res = executor.execute(code_py_incorrect, "python", tc_py, limits)
    print(json.dumps(res, indent=2))

    # 3. Python syntax/runtime error
    print("--- 3. Python syntax/runtime error ---")
    code_py_err = "def twoSum(nums, target):\n    1 / 0\n    return []"
    res = executor.execute(code_py_err, "python", tc_py, limits)
    print(json.dumps(res, indent=2))

    # 4. Python infinite loop / timeout
    print("--- 4. Python infinite loop / timeout ---")
    code_py_inf = "def twoSum(nums, target):\n    while True:\n        pass\n    return []"
    res = executor.execute(code_py_inf, "python", tc_py, limits)
    print(json.dumps(res, indent=2))

    # 5. C++ successful execution
    print("--- 5. C++ successful execution ---")
    code_cpp = """#include <iostream>
int main() {
    std::cout << "[0, 1]" << std::endl;
    return 0;
}"""
    res = executor.execute(code_cpp, "cpp", tc_py, limits)
    print(json.dumps(res, indent=2))

    # 6. Java successful execution
    print("--- 6. Java successful execution ---")
    code_java = """public class Solution {
    public static void main(String[] args) {
        System.out.println("[0, 1]");
    }
}"""
    res = executor.execute(code_java, "java", tc_py, limits)
    print(json.dumps(res, indent=2))

if __name__ == "__main__":
    run_tests()

"""
Module 1 — Programming Foundations & Logic
Curriculum definition: 8 problems covering core logic, mathematics, and fundamentals.
"""

import json

MODULE1_PROBLEMS = [
    {
        "title": "Even or Odd",
        "slug": "even-or-odd",
        "difficulty": "Easy",
        "category": "Math & Logic",
        "description": "Given an integer `n`, determine whether it is even or odd.\n\nReturn `\"Even\"` if the number is evenly divisible by 2, otherwise return `\"Odd\"`.",
        "examples": json.dumps([
            {"input": "n = 4", "output": '"Even"', "explanation": "4 % 2 == 0, so it is even."},
            {"input": "n = 7", "output": '"Odd"', "explanation": "7 % 2 != 0, so it is odd."}
        ]),
        "constraints": json.dumps(["-10^9 <= n <= 10^9"]),
        "starter_code": json.dumps({
            "python": "def evenOrOdd(n: int) -> str:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public String evenOrOdd(int n) {\n        // Write your solution here\n        return \"\";\n    }\n}",
            "cpp": "#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    string evenOrOdd(int n) {\n        // Write your solution here\n        return \"\";\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 1
    },
    {
        "title": "FizzBuzz",
        "slug": "fizzbuzz",
        "difficulty": "Easy",
        "category": "Math & Logic",
        "description": "Given an integer `n`, return a list of strings representing the numbers from 1 to `n` where:\n- If divisible by both 3 and 5, replace with `\"FizzBuzz\"`.\n- If divisible by 3, replace with `\"Fizz\"`.\n- If divisible by 5, replace with `\"Buzz\"`.\n- Otherwise, use the number as a string.",
        "examples": json.dumps([
            {"input": "n = 3", "output": '["1", "2", "Fizz"]', "explanation": "3 is divisible by 3."},
            {"input": "n = 5", "output": '["1", "2", "Fizz", "4", "Buzz"]', "explanation": "5 is divisible by 5."}
        ]),
        "constraints": json.dumps(["1 <= n <= 10^4"]),
        "starter_code": json.dumps({
            "python": "def fizzBuzz(n: int) -> list[str]:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public List<String> fizzBuzz(int n) {\n        // Write your solution here\n        return new ArrayList<>();\n    }\n}",
            "cpp": "#include <vector>\n#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<string> fizzBuzz(int n) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 2
    },
    {
        "title": "Sum of Digits",
        "slug": "sum-of-digits",
        "difficulty": "Easy",
        "category": "Math & Logic",
        "description": "Given an integer `n`, calculate and return the sum of its digits. If `n` is negative, consider the absolute value of the digits.",
        "examples": json.dumps([
            {"input": "n = 123", "output": "6", "explanation": "1 + 2 + 3 = 6."},
            {"input": "n = 409", "output": "13", "explanation": "4 + 0 + 9 = 13."}
        ]),
        "constraints": json.dumps(["-10^9 <= n <= 10^9"]),
        "starter_code": json.dumps({
            "python": "def sumOfDigits(n: int) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int sumOfDigits(int n) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <cstdlib>\nusing namespace std;\n\nclass Solution {\npublic:\n    int sumOfDigits(int n) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 3
    },
    {
        "title": "Leap Year",
        "slug": "leap-year",
        "difficulty": "Easy",
        "category": "Math & Logic",
        "description": "Given an integer `year`, determine if it is a leap year.\n\nA year is a leap year if:\n1. It is divisible by 4, AND\n2. It is not divisible by 100, UNLESS it is also divisible by 400.\n\nReturn `true` if it is a leap year, otherwise return `false`.",
        "examples": json.dumps([
            {"input": "year = 2000", "output": "true", "explanation": "2000 is divisible by 400, so it is a leap year."},
            {"input": "year = 1900", "output": "false", "explanation": "1900 is divisible by 100 but not 400, so not a leap year."}
        ]),
        "constraints": json.dumps(["1 <= year <= 9999"]),
        "starter_code": json.dumps({
            "python": "def isLeapYear(year: int) -> bool:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public boolean isLeapYear(int year) {\n        // Write your solution here\n        return false;\n    }\n}",
            "cpp": "class Solution {\npublic:\n    bool isLeapYear(int year) {\n        // Write your solution here\n        return false;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 4
    },
    {
        "title": "Prime Number",
        "slug": "prime-number",
        "difficulty": "Easy",
        "category": "Math & Logic",
        "description": "Given an integer `n`, determine whether it is a prime number.\n\nA prime number is a natural number strictly greater than 1 that is divisible only by 1 and itself.\n\nReturn `true` if `n` is prime, otherwise `false`.",
        "examples": json.dumps([
            {"input": "n = 7", "output": "true", "explanation": "7 is divisible only by 1 and 7."},
            {"input": "n = 4", "output": "false", "explanation": "4 is divisible by 2."}
        ]),
        "constraints": json.dumps(["-10^7 <= n <= 10^7"]),
        "starter_code": json.dumps({
            "python": "def isPrime(n: int) -> bool:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public boolean isPrime(int n) {\n        // Write your solution here\n        return false;\n    }\n}",
            "cpp": "class Solution {\npublic:\n    bool isPrime(int n) {\n        // Write your solution here\n        return false;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 5
    },
    {
        "title": "Factorial",
        "slug": "factorial",
        "difficulty": "Easy",
        "category": "Math & Logic",
        "description": "Given a non-negative integer `n`, return its factorial `n!`.\n\nThe factorial of 0 is 1. The factorial of `n` is the product of all positive integers less than or equal to `n`.",
        "examples": json.dumps([
            {"input": "n = 5", "output": "120", "explanation": "5 * 4 * 3 * 2 * 1 = 120."},
            {"input": "n = 0", "output": "1", "explanation": "0! = 1 by definition."}
        ]),
        "constraints": json.dumps(["0 <= n <= 12"]),
        "starter_code": json.dumps({
            "python": "def factorial(n: int) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int factorial(int n) {\n        // Write your solution here\n        return 1;\n    }\n}",
            "cpp": "class Solution {\npublic:\n    int factorial(int n) {\n        // Write your solution here\n        return 1;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 6
    },
    {
        "title": "Minimum and Maximum",
        "slug": "min-max",
        "difficulty": "Easy",
        "category": "Arrays & Logic",
        "description": "Given a non-empty array of integers `nums`, find and return the minimum and maximum values as a two-element array `[min_val, max_val]`.",
        "examples": json.dumps([
            {"input": "nums = [3, 1, 4, 1, 5, 9]", "output": "[1, 9]", "explanation": "Minimum is 1, maximum is 9."},
            {"input": "nums = [42]", "output": "[42, 42]", "explanation": "Single element is both min and max."}
        ]),
        "constraints": json.dumps(["1 <= nums.length <= 10^5", "-10^9 <= nums[i] <= 10^9"]),
        "starter_code": json.dumps({
            "python": "def findMinMax(nums: list[int]) -> list[int]:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int[] findMinMax(int[] nums) {\n        // Write your solution here\n        return new int[]{};\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> findMinMax(vector<int>& nums) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 7
    },
    {
        "title": "Fibonacci Sequence",
        "slug": "fibonacci-number",
        "difficulty": "Easy",
        "category": "Math & Recursion",
        "description": "The Fibonacci numbers form a sequence where each number is the sum of the two preceding ones, starting from 0 and 1:\n- F(0) = 0\n- F(1) = 1\n- F(n) = F(n-1) + F(n-2) for n > 1\n\nGiven `n`, calculate `F(n)`.",
        "examples": json.dumps([
            {"input": "n = 2", "output": "1", "explanation": "F(2) = F(1) + F(0) = 1 + 0 = 1."},
            {"input": "n = 4", "output": "3", "explanation": "F(4) = F(3) + F(2) = 2 + 1 = 3."}
        ]),
        "constraints": json.dumps(["0 <= n <= 30"]),
        "starter_code": json.dumps({
            "python": "def fib(n: int) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int fib(int n) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "class Solution {\npublic:\n    int fib(int n) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 8
    }
]

MODULE1_TEST_CASES = {
    "even-or-odd": [
        {"input": "4", "expected_output": "Even", "is_sample": True},
        {"input": "7", "expected_output": "Odd", "is_sample": True},
        {"input": "0", "expected_output": "Even", "is_sample": False},
        {"input": "-3", "expected_output": "Odd", "is_sample": False},
    ],
    "fizzbuzz": [
        {"input": "3", "expected_output": '["1", "2", "Fizz"]', "is_sample": True},
        {"input": "5", "expected_output": '["1", "2", "Fizz", "4", "Buzz"]', "is_sample": True},
        {"input": "15", "expected_output": '["1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz", "11", "Fizz", "13", "14", "FizzBuzz"]', "is_sample": False},
        {"input": "1", "expected_output": '["1"]', "is_sample": False},
    ],
    "sum-of-digits": [
        {"input": "123", "expected_output": "6", "is_sample": True},
        {"input": "409", "expected_output": "13", "is_sample": True},
        {"input": "0", "expected_output": "0", "is_sample": False},
        {"input": "-45", "expected_output": "9", "is_sample": False},
    ],
    "leap-year": [
        {"input": "2000", "expected_output": "true", "is_sample": True},
        {"input": "1900", "expected_output": "false", "is_sample": True},
        {"input": "2024", "expected_output": "true", "is_sample": False},
        {"input": "2023", "expected_output": "false", "is_sample": False},
    ],
    "prime-number": [
        {"input": "7", "expected_output": "true", "is_sample": True},
        {"input": "4", "expected_output": "false", "is_sample": True},
        {"input": "1", "expected_output": "false", "is_sample": False},
        {"input": "2", "expected_output": "true", "is_sample": False},
        {"input": "29", "expected_output": "true", "is_sample": False},
    ],
    "factorial": [
        {"input": "5", "expected_output": "120", "is_sample": True},
        {"input": "0", "expected_output": "1", "is_sample": True},
        {"input": "1", "expected_output": "1", "is_sample": False},
        {"input": "7", "expected_output": "5040", "is_sample": False},
    ],
    "min-max": [
        {"input": "[3, 1, 4, 1, 5, 9]", "expected_output": "[1, 9]", "is_sample": True},
        {"input": "[42]", "expected_output": "[42, 42]", "is_sample": True},
        {"input": "[-5, -1, -10, -2]", "expected_output": "[-10, -1]", "is_sample": False},
        {"input": "[0, 0, 0]", "expected_output": "[0, 0]", "is_sample": False},
    ],
    "fibonacci-number": [
        {"input": "2", "expected_output": "1", "is_sample": True},
        {"input": "4", "expected_output": "3", "is_sample": True},
        {"input": "0", "expected_output": "0", "is_sample": False},
        {"input": "10", "expected_output": "55", "is_sample": False},
    ],
}

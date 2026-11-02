"""
Module 3 — Linear Data Structures
Curriculum definition: 7 new problems + mapping for 1 existing problem (valid-parentheses).
Total 8 problems.
"""

import json

MODULE3_NEW_PROBLEMS = [
    {
        "title": "Reverse Linked List",
        "slug": "reverse-linked-list",
        "difficulty": "Easy",
        "category": "Linked List",
        "description": "Given the `head` of a singly linked list represented as a list of integers, reverse the list, and return the reversed list.",
        "examples": json.dumps([
            {"input": "head = [1,2,3,4,5]", "output": "[5, 4, 3, 2, 1]", "explanation": "The reversed list is [5, 4, 3, 2, 1]."},
            {"input": "head = [1,2]", "output": "[2, 1]", "explanation": "Reversing [1, 2] yields [2, 1]."},
            {"input": "head = []", "output": "[]", "explanation": "Reversing an empty list yields []."}
        ]),
        "constraints": json.dumps(["0 <= head.length <= 5000", "-5000 <= head[i] <= 5000"]),
        "starter_code": json.dumps({
            "python": "def reverseList(head: list[int]) -> list[int]:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int[] reverseList(int[] head) {\n        // Write your solution here\n        return new int[]{};\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> reverseList(vector<int>& head) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 2
    },
    {
        "title": "Remove Duplicates from Sorted List",
        "slug": "remove-duplicates-sorted-list",
        "difficulty": "Easy",
        "category": "Linked List",
        "description": "Given the `head` of a sorted linked list represented as a list of integers, delete all duplicates such that each element appears only once. Return the linked list sorted as well.",
        "examples": json.dumps([
            {"input": "head = [1,1,2]", "output": "[1, 2]", "explanation": "The duplicate 1 is removed."},
            {"input": "head = [1,1,2,3,3]", "output": "[1, 2, 3]", "explanation": "Duplicates of 1 and 3 are removed."}
        ]),
        "constraints": json.dumps(["0 <= head.length <= 300", "-100 <= head[i] <= 100", "The list is guaranteed to be sorted in ascending order."]),
        "starter_code": json.dumps({
            "python": "def deleteDuplicates(head: list[int]) -> list[int]:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int[] deleteDuplicates(int[] head) {\n        // Write your solution here\n        return new int[]{};\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> deleteDuplicates(vector<int>& head) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 3
    },
    {
        "title": "Min Stack",
        "slug": "min-stack",
        "difficulty": "Medium",
        "category": "Stack",
        "description": "Design a stack that supports push, pop, top, and retrieving the minimum element in constant time O(1).\n\nImplement `runMinStack(operations, values)` where operations are `[\"push\", \"pop\", \"top\", \"getMin\"]` and return the result of each operation (`null` for void methods).",
        "examples": json.dumps([
            {"input": "operations = [\"push\",\"push\",\"push\",\"getMin\",\"pop\",\"top\",\"getMin\"]\nvalues = [[-2],[0],[-3],[],[],[],[]]", "output": "[null, null, null, -3, null, 0, -2]", "explanation": "minStack.push(-2);\nminStack.push(0);\nminStack.push(-3);\nminStack.getMin(); // return -3\nminStack.pop();\nminStack.top();    // return 0\nminStack.getMin(); // return -2"},
            {"input": "operations = [\"push\",\"getMin\",\"top\"]\nvalues = [[5],[],[]]", "output": "[null, 5, 5]", "explanation": "Single item push, getMin is 5, top is 5."}
        ]),
        "constraints": json.dumps(["-2^31 <= val <= 2^31 - 1", "Methods pop, top and getMin operations will always be called on non-empty stacks.", "At most 3 * 10^4 calls will be made."]),
        "starter_code": json.dumps({
            "python": "def runMinStack(operations: list[str], values: list) -> list:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public List<Object> runMinStack(String[] operations, int[][] values) {\n        // Write your solution here\n        return new ArrayList<>();\n    }\n}",
            "cpp": "#include <vector>\n#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<string> runMinStack(vector<string>& operations, vector<vector<int>>& values) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 4
    },
    {
        "title": "Queue Using Stacks",
        "slug": "queue-using-stacks",
        "difficulty": "Easy",
        "category": "Stack & Queue",
        "description": "Implement a first in first out (FIFO) queue using only two stacks. The implemented queue should support all the functions of a normal queue (`push`, `peek`, `pop`, and `empty`).\n\nImplement `runQueue(operations, values)` and return the output of each method call.",
        "examples": json.dumps([
            {"input": "operations = [\"push\",\"push\",\"peek\",\"pop\",\"empty\"]\nvalues = [[1],[2],[],[],[]]", "output": "[null, null, 1, 1, false]", "explanation": "Queue sequence pushes 1, 2, peeks 1, pops 1, and is not empty."},
            {"input": "operations = [\"push\",\"pop\",\"empty\"]\nvalues = [[10],[],[]]", "output": "[null, 10, true]", "explanation": "Pushes 10, pops 10, queue is now empty."}
        ]),
        "constraints": json.dumps(["1 <= x <= 9", "At most 100 calls will be made to push, pop, peek, and empty.", "All calls to pop and peek are valid."]),
        "starter_code": json.dumps({
            "python": "def runQueue(operations: list[str], values: list) -> list:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public List<Object> runQueue(String[] operations, int[][] values) {\n        // Write your solution here\n        return new ArrayList<>();\n    }\n}",
            "cpp": "#include <vector>\n#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<string> runQueue(vector<string>& operations, vector<vector<int>>& values) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 5
    },
    {
        "title": "Container With Most Water",
        "slug": "container-with-most-water",
        "difficulty": "Medium",
        "category": "Two Pointers",
        "description": "You are given an integer array `height` of length `n`. There are `n` vertical lines drawn such that the two endpoints of the `i-th` line are `(i, 0)` and `(i, height[i])`.\n\nFind two lines that together with the x-axis form a container, such that the container contains the most water. Return the maximum amount of water a container can store.",
        "examples": json.dumps([
            {"input": "height = [1,8,6,2,5,4,8,3,7]", "output": "49", "explanation": "The maximum area is formed between indices 1 and 8 (height 8 and 7) with width 7 -> 7 * 7 = 49."},
            {"input": "height = [1,1]", "output": "1", "explanation": "Area = 1 * 1 = 1."}
        ]),
        "constraints": json.dumps(["n == height.length", "2 <= n <= 10^5", "0 <= height[i] <= 10^4"]),
        "starter_code": json.dumps({
            "python": "def maxArea(height: list[int]) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int maxArea(int[] height) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int maxArea(vector<int>& height) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 6
    },
    {
        "title": "Evaluate Reverse Polish Notation",
        "slug": "evaluate-reverse-polish-notation",
        "difficulty": "Medium",
        "category": "Stack",
        "description": "You are given an array of strings `tokens` that represents an arithmetic expression in a Reverse Polish Notation.\n\nEvaluate the expression. Return an integer that represents the value of the expression.\n\nValid operators are `+`, `-`, `*`, and `/`. Division between two integers truncates toward zero.",
        "examples": json.dumps([
            {"input": "tokens = [\"2\",\"1\",\"+\",\"3\",\"*\"]", "output": "9", "explanation": "((2 + 1) * 3) = 9"},
            {"input": "tokens = [\"4\",\"13\",\"5\",\"/\",\"+\"]", "output": "6", "explanation": "(4 + (13 / 5)) = 6"}
        ]),
        "constraints": json.dumps(["1 <= tokens.length <= 10^4", "tokens[i] is either an operator: \"+\", \"-\", \"*\", or \"/\", or an integer in the range [-200, 200]."]),
        "starter_code": json.dumps({
            "python": "def evalRPN(tokens: list[str]) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int evalRPN(String[] tokens) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\n#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    int evalRPN(vector<string>& tokens) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 7
    },
    {
        "title": "3Sum",
        "slug": "3sum",
        "difficulty": "Medium",
        "category": "Two Pointers",
        "description": "Given an integer array `nums`, return all the triplets `[nums[i], nums[j], nums[k]]` such that `i != j`, `i != k`, and `j != k`, and `nums[i] + nums[j] + nums[k] == 0`.\n\nNotice that the solution set must not contain duplicate triplets. Triplets and internal numbers should be returned sorted.",
        "examples": json.dumps([
            {"input": "nums = [-1,0,1,2,-1,-4]", "output": "[[-1, -1, 2], [-1, 0, 1]]", "explanation": "Distinct triplets summing to 0."},
            {"input": "nums = [0,1,1]", "output": "[]", "explanation": "No possible triplet sums to 0."}
        ]),
        "constraints": json.dumps(["3 <= nums.length <= 3000", "-10^5 <= nums[i] <= 10^5"]),
        "starter_code": json.dumps({
            "python": "def threeSum(nums: list[int]) -> list[list[int]]:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public List<List<Integer>> threeSum(int[] nums) {\n        // Write your solution here\n        return new ArrayList<>();\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<vector<int>> threeSum(vector<int>& nums) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 8
    }
]

MODULE3_NEW_TEST_CASES = {
    "reverse-linked-list": [
        {"input": "[1, 2, 3, 4, 5]", "expected_output": "[5, 4, 3, 2, 1]", "is_sample": True},
        {"input": "[1, 2]", "expected_output": "[2, 1]", "is_sample": True},
        {"input": "[]", "expected_output": "[]", "is_sample": False},
        {"input": "[42]", "expected_output": "[42]", "is_sample": False},
    ],
    "remove-duplicates-sorted-list": [
        {"input": "[1, 1, 2]", "expected_output": "[1, 2]", "is_sample": True},
        {"input": "[1, 1, 2, 3, 3]", "expected_output": "[1, 2, 3]", "is_sample": True},
        {"input": "[]", "expected_output": "[]", "is_sample": False},
        {"input": "[1, 1, 1, 1]", "expected_output": "[1]", "is_sample": False},
    ],
    "min-stack": [
        {"input": '["push","push","push","getMin","pop","top","getMin"]\n[[-2],[0],[-3],[],[],[],[]]', "expected_output": "[null, null, null, -3, null, 0, -2]", "is_sample": True},
        {"input": '["push","getMin","top"]\n[[5],[],[]]', "expected_output": "[null, 5, 5]", "is_sample": True},
        {"input": '["push","push","getMin"]\n[[1],[2],[]]', "expected_output": "[null, null, 1]", "is_sample": False},
        {"input": '["push","push","getMin","pop","getMin"]\n[[10],[5],[],[],[]]', "expected_output": "[null, null, 5, null, 10]", "is_sample": False},
    ],
    "queue-using-stacks": [
        {"input": '["push","push","peek","pop","empty"]\n[[1],[2],[],[],[]]', "expected_output": "[null, null, 1, 1, false]", "is_sample": True},
        {"input": '["push","pop","empty"]\n[[10],[],[]]', "expected_output": "[null, 10, true]", "is_sample": True},
        {"input": '["push","push","push","pop","peek"]\n[[3],[5],[7],[],[]]', "expected_output": "[null, null, null, 3, 5]", "is_sample": False},
        {"input": '["empty"]\n[[]]', "expected_output": "[true]", "is_sample": False},
    ],
    "container-with-most-water": [
        {"input": "[1, 8, 6, 2, 5, 4, 8, 3, 7]", "expected_output": "49", "is_sample": True},
        {"input": "[1, 1]", "expected_output": "1", "is_sample": True},
        {"input": "[4, 3, 2, 1, 4]", "expected_output": "16", "is_sample": False},
        {"input": "[1, 2, 1]", "expected_output": "2", "is_sample": False},
    ],
    "evaluate-reverse-polish-notation": [
        {"input": '["2","1","+","3","*"]', "expected_output": "9", "is_sample": True},
        {"input": '["4","13","5","/","+"]', "expected_output": "6", "is_sample": True},
        {"input": '["10","6","9","3","+","-11","*","/","*","17","+","5","+"]', "expected_output": "22", "is_sample": False},
        {"input": '["3"]', "expected_output": "3", "is_sample": False},
    ],
    "3sum": [
        {"input": "[-1, 0, 1, 2, -1, -4]", "expected_output": "[[-1, -1, 2], [-1, 0, 1]]", "is_sample": True},
        {"input": "[0, 1, 1]", "expected_output": "[]", "is_sample": True},
        {"input": "[0, 0, 0]", "expected_output": "[[0, 0, 0]]", "is_sample": False},
        {"input": "[-2, 0, 1, 1, 2]", "expected_output": "[[-2, 0, 2], [-2, 1, 1]]", "is_sample": False},
    ]
}

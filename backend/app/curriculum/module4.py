"""
Module 4 — Searching, Sorting & Recursion
Curriculum definition: 6 new problems + mappings for 2 existing problems (binary-search, maximum-subarray).
Total 8 problems.
"""

import json

MODULE4_NEW_PROBLEMS = [
    {
        "title": "First and Last Position in Sorted Array",
        "slug": "first-and-last-position",
        "difficulty": "Medium",
        "category": "Binary Search",
        "description": "Given an array of integers `nums` sorted in non-decreasing order, find the starting and ending position of a given `target` value.\n\nIf `target` is not found in the array, return `[-1, -1]`.\n\nYou must write an algorithm with O(log n) runtime complexity.",
        "examples": json.dumps([
            {"input": "nums = [5,7,7,8,8,10], target = 8", "output": "[3, 4]", "explanation": "Target 8 appears first at index 3 and last at index 4."},
            {"input": "nums = [5,7,7,8,8,10], target = 6", "output": "[-1, -1]", "explanation": "Target 6 does not exist in nums."}
        ]),
        "constraints": json.dumps(["0 <= nums.length <= 10^5", "-10^9 <= nums[i] <= 10^9", "nums is a non-decreasing array.", "-10^9 <= target <= 10^9"]),
        "starter_code": json.dumps({
            "python": "def searchRange(nums: list[int], target: int) -> list[int]:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int[] searchRange(int[] nums, int target) {\n        // Write your solution here\n        return new int[]{-1, -1};\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> searchRange(vector<int>& nums, int target) {\n        // Write your solution here\n        return {-1, -1};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 3
    },
    {
        "title": "Search in Rotated Sorted Array",
        "slug": "search-in-rotated-sorted-array",
        "difficulty": "Medium",
        "category": "Binary Search",
        "description": "There is an integer array `nums` sorted in ascending order (with distinct values).\nPrior to being passed to your function, `nums` is possibly rotated at an unknown pivot index.\n\nGiven the array `nums` after the possible rotation and an integer `target`, return the index of `target` if it is in `nums`, or `-1` if it is not in `nums`.\n\nYou must achieve O(log n) runtime complexity.",
        "examples": json.dumps([
            {"input": "nums = [4,5,6,7,0,1,2], target = 0", "output": "4", "explanation": "0 is found at index 4."},
            {"input": "nums = [4,5,6,7,0,1,2], target = 3", "output": "-1", "explanation": "3 does not exist in nums."}
        ]),
        "constraints": json.dumps(["1 <= nums.length <= 5000", "-10^4 <= nums[i] <= 10^4", "All values of nums are unique.", "nums is an ascending array that is possibly rotated."]),
        "starter_code": json.dumps({
            "python": "def searchRotated(nums: list[int], target: int) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int searchRotated(int[] nums, int target) {\n        // Write your solution here\n        return -1;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int searchRotated(vector<int>& nums, int target) {\n        // Write your solution here\n        return -1;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 4
    },
    {
        "title": "Minimum Size Subarray Sum",
        "slug": "min-size-subarray-sum",
        "difficulty": "Medium",
        "category": "Sliding Window",
        "description": "Given an array of positive integers `nums` and a positive integer `target`, return the minimal length of a contiguous subarray of which the sum is greater than or equal to `target`. If there is no such subarray, return `0` instead.",
        "examples": json.dumps([
            {"input": "target = 7, nums = [2,3,1,2,4,3]", "output": "2", "explanation": "The subarray [4,3] has the minimal length under the problem constraint."},
            {"input": "target = 4, nums = [1,4,4]", "output": "1", "explanation": "Subarray [4] has length 1."},
            {"input": "target = 11, nums = [1,1,1,1,1,1,1,1]", "output": "0", "explanation": "No subarray sums to >= 11."}
        ]),
        "constraints": json.dumps(["1 <= target <= 10^9", "1 <= nums.length <= 10^5", "1 <= nums[i] <= 10^4"]),
        "starter_code": json.dumps({
            "python": "def minSubArrayLen(target: int, nums: list[int]) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int minSubArrayLen(int target, int[] nums) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int minSubArrayLen(int target, vector<int>& nums) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 5
    },
    {
        "title": "Longest Substring Without Repeating Characters",
        "slug": "longest-substring-without-repeating-characters",
        "difficulty": "Medium",
        "category": "Sliding Window",
        "description": "Given a string `s`, find the length of the longest substring without repeating characters.",
        "examples": json.dumps([
            {"input": "s = \"abcabcbb\"", "output": "3", "explanation": "The answer is \"abc\", with the length of 3."},
            {"input": "s = \"bbbbb\"", "output": "1", "explanation": "The answer is \"b\", with the length of 1."},
            {"input": "s = \"pwwkew\"", "output": "3", "explanation": "The answer is \"wke\", with the length of 3."}
        ]),
        "constraints": json.dumps(["0 <= s.length <= 5 * 10^4", "s consists of English letters, digits, symbols and spaces."]),
        "starter_code": json.dumps({
            "python": "def lengthOfLongestSubstring(s: str) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int lengthOfLongestSubstring(String s) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    int lengthOfLongestSubstring(string s) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 6
    },
    {
        "title": "Kth Largest Element in an Array",
        "slug": "kth-largest-element",
        "difficulty": "Medium",
        "category": "Heap & Quickselect",
        "description": "Given an integer array `nums` and an integer `k`, return the `k-th` largest element in the array.\n\nNote that it is the `k-th` largest element in the sorted order, not the `k-th` distinct element.\n\nCan you solve it in O(n) average time complexity?",
        "examples": json.dumps([
            {"input": "nums = [3,2,1,5,6,4], k = 2", "output": "5", "explanation": "Sorted: [6,5,4,3,2,1], 2nd largest is 5."},
            {"input": "nums = [3,2,3,1,2,4,5,5,6], k = 4", "output": "4", "explanation": "4th largest is 4."}
        ]),
        "constraints": json.dumps(["1 <= k <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4"]),
        "starter_code": json.dumps({
            "python": "def findKthLargest(nums: list[int], k: int) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int findKthLargest(int[] nums, int k) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int findKthLargest(vector<int>& nums, int k) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 7
    },
    {
        "title": "Top K Frequent Elements",
        "slug": "top-k-frequent-elements",
        "difficulty": "Medium",
        "category": "Heap & Hashing",
        "description": "Given an integer array `nums` and an integer `k`, return the `k` most frequent elements.\nYou may return the answer in any order (sorted order preferred).",
        "examples": json.dumps([
            {"input": "nums = [1,1,1,2,2,3], k = 2", "output": "[1, 2]", "explanation": "1 appears 3 times, 2 appears 2 times."},
            {"input": "nums = [1], k = 1", "output": "[1]", "explanation": "1 appears 1 time."}
        ]),
        "constraints": json.dumps(["1 <= nums.length <= 10^5", "-10^4 <= nums[i] <= 10^4", "k is in the range [1, the number of unique elements in the array].", "It is guaranteed that the answer is unique."]),
        "starter_code": json.dumps({
            "python": "def topKFrequent(nums: list[int], k: int) -> list[int]:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public int[] topKFrequent(int[] nums, int k) {\n        // Write your solution here\n        return new int[]{};\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> topKFrequent(vector<int>& nums, int k) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 8
    }
]

MODULE4_NEW_TEST_CASES = {
    "first-and-last-position": [
        {"input": "[5, 7, 7, 8, 8, 10]\n8", "expected_output": "[3, 4]", "is_sample": True},
        {"input": "[5, 7, 7, 8, 8, 10]\n6", "expected_output": "[-1, -1]", "is_sample": True},
        {"input": "[]\n0", "expected_output": "[-1, -1]", "is_sample": False},
        {"input": "[8, 8, 8, 8]\n8", "expected_output": "[0, 3]", "is_sample": False},
    ],
    "search-in-rotated-sorted-array": [
        {"input": "[4, 5, 6, 7, 0, 1, 2]\n0", "expected_output": "4", "is_sample": True},
        {"input": "[4, 5, 6, 7, 0, 1, 2]\n3", "expected_output": "-1", "is_sample": True},
        {"input": "[1]\n0", "expected_output": "-1", "is_sample": False},
        {"input": "[1, 3]\n3", "expected_output": "1", "is_sample": False},
    ],
    "min-size-subarray-sum": [
        {"input": "7\n[2, 3, 1, 2, 4, 3]", "expected_output": "2", "is_sample": True},
        {"input": "4\n[1, 4, 4]", "expected_output": "1", "is_sample": True},
        {"input": "11\n[1, 1, 1, 1, 1, 1, 1, 1]", "expected_output": "0", "is_sample": False},
        {"input": "15\n[1, 2, 3, 4, 5]", "expected_output": "5", "is_sample": False},
    ],
    "longest-substring-without-repeating-characters": [
        {"input": "abcabcbb", "expected_output": "3", "is_sample": True},
        {"input": "bbbbb", "expected_output": "1", "is_sample": True},
        {"input": "pwwkew", "expected_output": "3", "is_sample": False},
        {"input": "", "expected_output": "0", "is_sample": False},
    ],
    "kth-largest-element": [
        {"input": "[3, 2, 1, 5, 6, 4]\n2", "expected_output": "5", "is_sample": True},
        {"input": "[3, 2, 3, 1, 2, 4, 5, 5, 6]\n4", "expected_output": "4", "is_sample": True},
        {"input": "[1]\n1", "expected_output": "1", "is_sample": False},
        {"input": "[-1, 2, 0]\n1", "expected_output": "2", "is_sample": False},
    ],
    "top-k-frequent-elements": [
        {"input": "[1, 1, 1, 2, 2, 3]\n2", "expected_output": "[1, 2]", "is_sample": True},
        {"input": "[1]\n1", "expected_output": "[1]", "is_sample": True},
        {"input": "[4, 1, -1, 2, -1, 2, 3]\n2", "expected_output": "[-1, 2]", "is_sample": False},
        {"input": "[1, 2]\n2", "expected_output": "[1, 2]", "is_sample": False},
    ]
}

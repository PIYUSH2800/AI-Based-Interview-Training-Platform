"""
Module 2 — Arrays & Strings
Curriculum definition: 5 new problems + mappings for 3 existing problems.
Total 8 problems.
"""

import json

MODULE2_NEW_PROBLEMS = [
    {
        "title": "Valid Anagram",
        "slug": "valid-anagram",
        "difficulty": "Easy",
        "category": "Arrays & Hashing",
        "description": "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.\n\nAn Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.",
        "examples": json.dumps([
            {"input": "s = \"anagram\", t = \"nagaram\"", "output": "true", "explanation": "Both strings contain the exact same characters with the same frequencies."},
            {"input": "s = \"rat\", t = \"car\"", "output": "false", "explanation": "Characters differ."}
        ]),
        "constraints": json.dumps(["1 <= s.length, t.length <= 5 * 10^4", "s and t consist of lowercase English letters."]),
        "starter_code": json.dumps({
            "python": "def isAnagram(s: str, t: str) -> bool:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public boolean isAnagram(String s, String t) {\n        // Write your solution here\n        return false;\n    }\n}",
            "cpp": "#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool isAnagram(string s, string t) {\n        // Write your solution here\n        return false;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 4
    },
    {
        "title": "Longest Common Prefix",
        "slug": "longest-common-prefix",
        "difficulty": "Easy",
        "category": "Strings",
        "description": "Write a function to find the longest common prefix string amongst an array of strings.\n\nIf there is no common prefix, return an empty string `\"\"`.",
        "examples": json.dumps([
            {"input": "strs = [\"flower\",\"flow\",\"flight\"]", "output": "\"fl\"", "explanation": "The prefix \"fl\" is common to all three words."},
            {"input": "strs = [\"dog\",\"racecar\",\"car\"]", "output": "\"\"", "explanation": "There is no common prefix."}
        ]),
        "constraints": json.dumps(["1 <= strs.length <= 200", "0 <= strs[i].length <= 200", "strs[i] consists of only lowercase English letters."]),
        "starter_code": json.dumps({
            "python": "def longestCommonPrefix(strs: list[str]) -> str:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public String longestCommonPrefix(String[] strs) {\n        // Write your solution here\n        return \"\";\n    }\n}",
            "cpp": "#include <vector>\n#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    string longestCommonPrefix(vector<string>& strs) {\n        // Write your solution here\n        return \"\";\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 5
    },
    {
        "title": "Rotate Array",
        "slug": "rotate-array",
        "difficulty": "Medium",
        "category": "Arrays",
        "description": "Given an integer array `nums`, rotate the array to the right by `k` steps, where `k` is non-negative.\n\nReturn the rotated array.",
        "examples": json.dumps([
            {"input": "nums = [1,2,3,4,5,6,7], k = 3", "output": "[5, 6, 7, 1, 2, 3, 4]", "explanation": "Rotate 1 step right: [7,1,2,3,4,5,6]\nRotate 2 steps right: [6,7,1,2,3,4,5]\nRotate 3 steps right: [5,6,7,1,2,3,4]"},
            {"input": "nums = [-1,-100,3,99], k = 2", "output": "[3, 99, -1, -100]", "explanation": "Rotated 2 steps to the right."}
        ]),
        "constraints": json.dumps(["1 <= nums.length <= 10^5", "-2^31 <= nums[i] <= 2^31 - 1", "0 <= k <= 10^5"]),
        "starter_code": json.dumps({
            "python": "def rotate(nums: list[int], k: int) -> list[int]:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int[] rotate(int[] nums, int k) {\n        // Write your solution here\n        return new int[]{};\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> rotate(vector<int>& nums, int k) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 6
    },
    {
        "title": "Merge Sorted Arrays",
        "slug": "merge-sorted-arrays",
        "difficulty": "Easy",
        "category": "Arrays",
        "description": "You are given two integer arrays `nums1` and `nums2`, sorted in non-decreasing order.\n\nMerge `nums1` and `nums2` into a single sorted array sorted in non-decreasing order, and return it.",
        "examples": json.dumps([
            {"input": "nums1 = [1,2,3], nums2 = [2,5,6]", "output": "[1, 2, 2, 3, 5, 6]", "explanation": "Merged into a single sorted array."},
            {"input": "nums1 = [1], nums2 = []", "output": "[1]", "explanation": "nums2 is empty, so result is nums1."}
        ]),
        "constraints": json.dumps(["0 <= nums1.length, nums2.length <= 10^4", "-10^9 <= nums1[i], nums2[j] <= 10^9"]),
        "starter_code": json.dumps({
            "python": "def merge(nums1: list[int], nums2: list[int]) -> list[int]:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int[] merge(int[] nums1, int[] nums2) {\n        // Write your solution here\n        return new int[]{};\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<int> merge(vector<int>& nums1, vector<int>& nums2) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 7
    },
    {
        "title": "String Compression",
        "slug": "string-compression",
        "difficulty": "Easy",
        "category": "Strings",
        "description": "Given a string `s`, perform basic string compression using the counts of repeated characters.\n\nFor example, the string `\"aabcccccaaa\"` would become `\"a2b1c5a3\"`.\nIf the input string is empty, return an empty string.",
        "examples": json.dumps([
            {"input": "s = \"aabcccccaaa\"", "output": "\"a2b1c5a3\"", "explanation": "'a' appears 2 times, 'b' 1 time, 'c' 5 times, 'a' 3 times."},
            {"input": "s = \"abc\"", "output": "\"a1b1c1\"", "explanation": "Each character appears once."}
        ]),
        "constraints": json.dumps(["0 <= s.length <= 5 * 10^4", "s consists of English letters."]),
        "starter_code": json.dumps({
            "python": "def compressString(s: str) -> str:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public String compressString(String s) {\n        // Write your solution here\n        return \"\";\n    }\n}",
            "cpp": "#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    string compressString(string s) {\n        // Write your solution here\n        return \"\";\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 8
    }
]

MODULE2_NEW_TEST_CASES = {
    "valid-anagram": [
        {"input": "anagram\nnagaram", "expected_output": "true", "is_sample": True},
        {"input": "rat\ncar", "expected_output": "false", "is_sample": True},
        {"input": "a\na", "expected_output": "true", "is_sample": False},
        {"input": "ab\na", "expected_output": "false", "is_sample": False},
    ],
    "longest-common-prefix": [
        {"input": '["flower","flow","flight"]', "expected_output": "fl", "is_sample": True},
        {"input": '["dog","racecar","car"]', "expected_output": "", "is_sample": True},
        {"input": '["interspecies","interstellar","interstate"]', "expected_output": "inters", "is_sample": False},
        {"input": '["throne"]', "expected_output": "throne", "is_sample": False},
    ],
    "rotate-array": [
        {"input": "[1, 2, 3, 4, 5, 6, 7]\n3", "expected_output": "[5, 6, 7, 1, 2, 3, 4]", "is_sample": True},
        {"input": "[-1, -100, 3, 99]\n2", "expected_output": "[3, 99, -1, -100]", "is_sample": True},
        {"input": "[1, 2]\n3", "expected_output": "[2, 1]", "is_sample": False},
        {"input": "[1]\n0", "expected_output": "[1]", "is_sample": False},
    ],
    "merge-sorted-arrays": [
        {"input": "[1, 2, 3]\n[2, 5, 6]", "expected_output": "[1, 2, 2, 3, 5, 6]", "is_sample": True},
        {"input": "[1]\n[]", "expected_output": "[1]", "is_sample": True},
        {"input": "[]\n[1]", "expected_output": "[1]", "is_sample": False},
        {"input": "[2, 4, 6]\n[1, 3, 5]", "expected_output": "[1, 2, 3, 4, 5, 6]", "is_sample": False},
    ],
    "string-compression": [
        {"input": "aabcccccaaa", "expected_output": "a2b1c5a3", "is_sample": True},
        {"input": "abc", "expected_output": "a1b1c1", "is_sample": True},
        {"input": "aaaa", "expected_output": "a4", "is_sample": False},
        {"input": "", "expected_output": "", "is_sample": False},
    ]
}

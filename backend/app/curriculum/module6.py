"""
Module 6 — Dynamic Programming & Advanced DSA
Curriculum definition: 8 problems covering dynamic programming, optimization, and greedy algorithms.
"""

import json

MODULE6_PROBLEMS = [
    {
        "title": "Climbing Stairs",
        "slug": "climbing-stairs",
        "difficulty": "Easy",
        "category": "Dynamic Programming",
        "description": "You are climbing a staircase. It takes `n` steps to reach the top.\n\nEach time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
        "examples": json.dumps([
            {"input": "n = 2", "output": "2", "explanation": "There are two ways to climb to the top:\n1. 1 step + 1 step\n2. 2 steps"},
            {"input": "n = 3", "output": "3", "explanation": "There are three ways to climb to the top:\n1. 1 + 1 + 1\n2. 1 + 2\n3. 2 + 1"}
        ]),
        "constraints": json.dumps(["1 <= n <= 45"]),
        "starter_code": json.dumps({
            "python": "def climbStairs(n: int) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int climbStairs(int n) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "class Solution {\npublic:\n    int climbStairs(int n) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 1
    },
    {
        "title": "Coin Change",
        "slug": "coin-change",
        "difficulty": "Medium",
        "category": "Dynamic Programming",
        "description": "You are given an integer array `coins` representing coins of different denominations and an integer `amount` representing a total amount of money.\n\nReturn the fewest number of coins that you need to make up that amount. If that amount of money cannot be made up by any combination of the coins, return `-1`.\n\nYou may assume that you have an infinite number of each kind of coin.",
        "examples": json.dumps([
            {"input": "coins = [1,2,5], amount = 11", "output": "3", "explanation": "11 = 5 + 5 + 1 (3 coins)."},
            {"input": "coins = [2], amount = 3", "output": "-1", "explanation": "3 cannot be formed using only 2s."},
            {"input": "coins = [1], amount = 0", "output": "0", "explanation": "0 coins needed for amount 0."}
        ]),
        "constraints": json.dumps(["1 <= coins.length <= 12", "1 <= coins[i] <= 2^31 - 1", "0 <= amount <= 10^4"]),
        "starter_code": json.dumps({
            "python": "def coinChange(coins: list[int], amount: int) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int coinChange(int[] coins, int amount) {\n        // Write your solution here\n        return -1;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int coinChange(vector<int>& coins, int amount) {\n        // Write your solution here\n        return -1;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 2
    },
    {
        "title": "Longest Increasing Subsequence",
        "slug": "longest-increasing-subsequence",
        "difficulty": "Medium",
        "category": "Dynamic Programming",
        "description": "Given an integer array `nums`, return the length of the longest strictly increasing subsequence.\n\nA subsequence is an array that can be derived from another array by deleting some or no elements without changing the order of the remaining elements.",
        "examples": json.dumps([
            {"input": "nums = [10,9,2,5,3,7,101,18]", "output": "4", "explanation": "The longest increasing subsequence is [2,3,7,101], therefore the length is 4."},
            {"input": "nums = [0,1,0,3,2,3]", "output": "4", "explanation": "The longest increasing subsequence is [0,1,2,3]."},
            {"input": "nums = [7,7,7,7,7,7,7]", "output": "1", "explanation": "Length is 1 because subsequence must be strictly increasing."}
        ]),
        "constraints": json.dumps(["1 <= nums.length <= 2500", "-10^4 <= nums[i] <= 10^4"]),
        "starter_code": json.dumps({
            "python": "def lengthOfLIS(nums: list[int]) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int lengthOfLIS(int[] nums) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int lengthOfLIS(vector<int>& nums) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 3
    },
    {
        "title": "House Robber",
        "slug": "house-robber",
        "difficulty": "Medium",
        "category": "Dynamic Programming",
        "description": "You are a professional robber planning to rob houses along a street. Each house has a certain amount of money stashed, the only constraint stopping you from robbing each of them is that adjacent houses have security systems connected and it will automatically contact the police if two adjacent houses were broken into on the same night.\n\nGiven an integer array `nums` representing the amount of money of each house, return the maximum amount of money you can rob tonight without alerting the police.",
        "examples": json.dumps([
            {"input": "nums = [1,2,3,1]", "output": "4", "explanation": "Rob house 1 (money = 1) and then rob house 3 (money = 3). Total = 4."},
            {"input": "nums = [2,7,9,3,1]", "output": "12", "explanation": "Rob house 1 (2), house 3 (9) and house 5 (1). Total = 12."}
        ]),
        "constraints": json.dumps(["1 <= nums.length <= 100", "0 <= nums[i] <= 400"]),
        "starter_code": json.dumps({
            "python": "def rob(nums: list[int]) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int rob(int[] nums) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int rob(vector<int>& nums) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 4
    },
    {
        "title": "0/1 Knapsack",
        "slug": "knapsack-01",
        "difficulty": "Medium",
        "category": "Dynamic Programming",
        "description": "Given weights and values of `n` items, put these items in a knapsack of capacity `W` to get the maximum total value in the knapsack.\n\nYou cannot break an item, either pick the complete item or do not pick it (0-1 property).\n\nReturn the maximum value that can be put into the knapsack.",
        "examples": json.dumps([
            {"input": "values = [60,100,120], weights = [10,20,30], W = 50", "output": "220", "explanation": "Pick items 2 and 3 (weights 20 + 30 = 50, value = 100 + 120 = 220)."},
            {"input": "values = [10,40,30,50], weights = [5,4,6,3], W = 5", "output": "50", "explanation": "Pick the item with weight 3 and value 50."}
        ]),
        "constraints": json.dumps(["1 <= n <= 100", "1 <= W <= 1000", "1 <= values[i], weights[i] <= 1000"]),
        "starter_code": json.dumps({
            "python": "def knapsack(values: list[int], weights: list[int], W: int) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int knapsack(int[] values, int[] weights, int W) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int knapsack(vector<int>& values, vector<int>& weights, int W) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 5
    },
    {
        "title": "Edit Distance",
        "slug": "edit-distance",
        "difficulty": "Hard",
        "category": "Dynamic Programming",
        "description": "Given two strings `word1` and `word2`, return the minimum number of operations required to convert `word1` to `word2`.\n\nYou have the following three operations permitted on a word:\n- Insert a character\n- Delete a character\n- Replace a character",
        "examples": json.dumps([
            {"input": "word1 = \"horse\", word2 = \"ros\"", "output": "3", "explanation": "horse -> rorse (replace 'h' with 'r')\nrorse -> rose (remove 'r')\nrose -> ros (remove 'e')"},
            {"input": "word1 = \"intention\", word2 = \"execution\"", "output": "5", "explanation": "intention -> inention -> enention -> exention -> exection -> execution"}
        ]),
        "constraints": json.dumps(["0 <= word1.length, word2.length <= 500", "word1 and word2 consist of lowercase English letters."]),
        "starter_code": json.dumps({
            "python": "def minDistance(word1: str, word2: str) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int minDistance(String word1, String word2) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    int minDistance(string word1, string word2) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 6
    },
    {
        "title": "Word Break",
        "slug": "word-break",
        "difficulty": "Medium",
        "category": "Dynamic Programming",
        "description": "Given a string `s` and a dictionary of strings `wordDict`, return `true` if `s` can be segmented into a space-separated sequence of one or more dictionary words.\n\nNote that the same word in the dictionary may be reused multiple times in the segmentation.",
        "examples": json.dumps([
            {"input": "s = \"leetcode\", wordDict = [\"leet\",\"code\"]", "output": "true", "explanation": "Return true because \"leetcode\" can be segmented as \"leet code\"."},
            {"input": "s = \"applepenapple\", wordDict = [\"apple\",\"pen\"]", "output": "true", "explanation": "Return true because \"applepenapple\" can be segmented as \"apple pen apple\"."},
            {"input": "s = \"catsandog\", wordDict = [\"cats\",\"dog\",\"sand\",\"and\",\"cat\"]", "output": "false", "explanation": "Cannot be fully segmented."}
        ]),
        "constraints": json.dumps(["1 <= s.length <= 300", "1 <= wordDict.length <= 1000", "1 <= wordDict[i].length <= 20", "s and wordDict[i] consist of only lowercase English letters."]),
        "starter_code": json.dumps({
            "python": "def wordBreak(s: str, wordDict: list[str]) -> bool:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public boolean wordBreak(String s, List<String> wordDict) {\n        // Write your solution here\n        return false;\n    }\n}",
            "cpp": "#include <string>\n#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool wordBreak(string s, vector<string>& wordDict) {\n        // Write your solution here\n        return false;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 7
    },
    {
        "title": "Jump Game",
        "slug": "jump-game",
        "difficulty": "Medium",
        "category": "Greedy & DP",
        "description": "You are given an integer array `nums`. You are initially positioned at the array's first index, and each element in the array represents your maximum jump length at that position.\n\nReturn `true` if you can reach the last index, or `false` otherwise.",
        "examples": json.dumps([
            {"input": "nums = [2,3,1,1,4]", "output": "true", "explanation": "Jump 1 step from index 0 to 1, then 3 steps to the last index."},
            {"input": "nums = [3,2,1,0,4]", "output": "false", "explanation": "You will always arrive at index 3 no matter what. Its maximum jump length is 0, which makes it impossible to reach the last index."}
        ]),
        "constraints": json.dumps(["1 <= nums.length <= 10^4", "0 <= nums[i] <= 10^5"]),
        "starter_code": json.dumps({
            "python": "def canJump(nums: list[int]) -> bool:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public boolean canJump(int[] nums) {\n        // Write your solution here\n        return false;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool canJump(vector<int>& nums) {\n        // Write your solution here\n        return false;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 8
    }
]

MODULE6_TEST_CASES = {
    "climbing-stairs": [
        {"input": "2", "expected_output": "2", "is_sample": True},
        {"input": "3", "expected_output": "3", "is_sample": True},
        {"input": "1", "expected_output": "1", "is_sample": False},
        {"input": "5", "expected_output": "8", "is_sample": False},
    ],
    "coin-change": [
        {"input": "[1, 2, 5]\n11", "expected_output": "3", "is_sample": True},
        {"input": "[2]\n3", "expected_output": "-1", "is_sample": True},
        {"input": "[1]\n0", "expected_output": "0", "is_sample": True},
        {"input": "[2, 5, 10, 1]\n27", "expected_output": "4", "is_sample": False},
    ],
    "longest-increasing-subsequence": [
        {"input": "[10, 9, 2, 5, 3, 7, 101, 18]", "expected_output": "4", "is_sample": True},
        {"input": "[0, 1, 0, 3, 2, 3]", "expected_output": "4", "is_sample": True},
        {"input": "[7, 7, 7, 7, 7, 7, 7]", "expected_output": "1", "is_sample": True},
        {"input": "[4, 10, 4, 3, 8, 9]", "expected_output": "3", "is_sample": False},
    ],
    "house-robber": [
        {"input": "[1, 2, 3, 1]", "expected_output": "4", "is_sample": True},
        {"input": "[2, 7, 9, 3, 1]", "expected_output": "12", "is_sample": True},
        {"input": "[0]", "expected_output": "0", "is_sample": False},
        {"input": "[2, 1, 1, 2]", "expected_output": "4", "is_sample": False},
    ],
    "knapsack-01": [
        {"input": "[60, 100, 120]\n[10, 20, 30]\n50", "expected_output": "220", "is_sample": True},
        {"input": "[10, 40, 30, 50]\n[5, 4, 6, 3]\n5", "expected_output": "50", "is_sample": True},
        {"input": "[20, 30, 40]\n[1, 2, 3]\n6", "expected_output": "90", "is_sample": False},
        {"input": "[15]\n[10]\n5", "expected_output": "0", "is_sample": False},
    ],
    "edit-distance": [
        {"input": "horse\nros", "expected_output": "3", "is_sample": True},
        {"input": "intention\nexecution", "expected_output": "5", "is_sample": True},
        {"input": "a\nb", "expected_output": "1", "is_sample": False},
        {"input": "abc\nabc", "expected_output": "0", "is_sample": False},
    ],
    "word-break": [
        {"input": 'leetcode\n["leet", "code"]', "expected_output": "true", "is_sample": True},
        {"input": 'applepenapple\n["apple", "pen"]', "expected_output": "true", "is_sample": True},
        {"input": 'catsandog\n["cats", "dog", "sand", "and", "cat"]', "expected_output": "false", "is_sample": True},
        {"input": 'aaaaaaa\n["aaaa", "aaa"]', "expected_output": "true", "is_sample": False},
    ],
    "jump-game": [
        {"input": "[2, 3, 1, 1, 4]", "expected_output": "true", "is_sample": True},
        {"input": "[3, 2, 1, 0, 4]", "expected_output": "false", "is_sample": True},
        {"input": "[0]", "expected_output": "true", "is_sample": False},
        {"input": "[1, 0, 1, 0]", "expected_output": "false", "is_sample": False},
    ]
}

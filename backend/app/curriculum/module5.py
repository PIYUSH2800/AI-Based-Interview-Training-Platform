"""
Module 5 — Trees, Heaps & Graphs
Curriculum definition: 8 problems covering binary trees, BSTs, heaps, and graph algorithms.
Level-order JSON array representation used for trees, 2D grids/edge lists for graphs.
"""

import json

MODULE5_PROBLEMS = [
    {
        "title": "Invert Binary Tree",
        "slug": "invert-binary-tree",
        "difficulty": "Easy",
        "category": "Trees",
        "description": "Given the `root` of a binary tree represented as a level-order JSON array (where `null` represents a missing node), invert the tree, and return its level-order representation.",
        "examples": json.dumps([
            {"input": "root = [4,2,7,1,3,6,9]", "output": "[4, 7, 2, 9, 6, 3, 1]", "explanation": "The left and right subtrees at each node are swapped."},
            {"input": "root = [2,1,3]", "output": "[2, 3, 1]", "explanation": "Children 1 and 3 are inverted to 3 and 1."},
            {"input": "root = []", "output": "[]", "explanation": "An empty tree inverts to an empty tree."}
        ]),
        "constraints": json.dumps(["The number of nodes in the tree is in the range [0, 100].", "-100 <= Node.val <= 100"]),
        "starter_code": json.dumps({
            "python": "def invertTree(root: list) -> list:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public List<Object> invertTree(List<Object> root) {\n        // Write your solution here\n        return new ArrayList<>();\n    }\n}",
            "cpp": "#include <vector>\n#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<string> invertTree(vector<string>& root) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 1
    },
    {
        "title": "Maximum Depth of Binary Tree",
        "slug": "maximum-depth-of-binary-tree",
        "difficulty": "Easy",
        "category": "Trees",
        "description": "Given the `root` of a binary tree represented as a level-order JSON array, return its maximum depth.\n\nA binary tree's maximum depth is the number of nodes along the longest path from the root node down to the farthest leaf node.",
        "examples": json.dumps([
            {"input": "root = [3,9,20,null,null,15,7]", "output": "3", "explanation": "The longest path 3 -> 20 -> 15 has length 3."},
            {"input": "root = [1,null,2]", "output": "2", "explanation": "Depth is 2."}
        ]),
        "constraints": json.dumps(["The number of nodes in the tree is in the range [0, 10^4].", "-100 <= Node.val <= 100"]),
        "starter_code": json.dumps({
            "python": "def maxDepth(root: list) -> int:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public int maxDepth(List<Object> root) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\n#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    int maxDepth(vector<string>& root) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 2
    },
    {
        "title": "Same Tree",
        "slug": "same-tree",
        "difficulty": "Easy",
        "category": "Trees",
        "description": "Given the roots of two binary trees `p` and `q` represented as level-order arrays, write a function to check if they are the same or not.\n\nTwo binary trees are considered the same if they are structurally identical, and the nodes have the same value.",
        "examples": json.dumps([
            {"input": "p = [1,2,3], q = [1,2,3]", "output": "true", "explanation": "Both trees have identical values and structure."},
            {"input": "p = [1,2], q = [1,null,2]", "output": "false", "explanation": "Structures differ."}
        ]),
        "constraints": json.dumps(["The number of nodes in both trees is in the range [0, 100].", "-10^4 <= Node.val <= 10^4"]),
        "starter_code": json.dumps({
            "python": "def isSameTree(p: list, q: list) -> bool:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public boolean isSameTree(List<Object> p, List<Object> q) {\n        // Write your solution here\n        return false;\n    }\n}",
            "cpp": "#include <vector>\n#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool isSameTree(vector<string>& p, vector<string>& q) {\n        // Write your solution here\n        return false;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 3
    },
    {
        "title": "Binary Tree Level Order Traversal",
        "slug": "binary-tree-level-order-traversal",
        "difficulty": "Medium",
        "category": "Trees & BFS",
        "description": "Given the `root` of a binary tree represented as a level-order array, return the level order traversal of its nodes' values (i.e., from left to right, level by level).",
        "examples": json.dumps([
            {"input": "root = [3,9,20,null,null,15,7]", "output": "[[3], [9, 20], [15, 7]]", "explanation": "Level 0: [3], Level 1: [9, 20], Level 2: [15, 7]."},
            {"input": "root = [1]", "output": "[[1]]", "explanation": "Single node at level 0."},
            {"input": "root = []", "output": "[]", "explanation": "Empty tree returns empty list."}
        ]),
        "constraints": json.dumps(["The number of nodes in the tree is in the range [0, 2000].", "-1000 <= Node.val <= 1000"]),
        "starter_code": json.dumps({
            "python": "def levelOrder(root: list) -> list[list[int]]:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public List<List<Integer>> levelOrder(List<Object> root) {\n        // Write your solution here\n        return new ArrayList<>();\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    vector<vector<int>> levelOrder(vector<string>& root) {\n        // Write your solution here\n        return {};\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 4
    },
    {
        "title": "Validate Binary Search Tree",
        "slug": "validate-binary-search-tree",
        "difficulty": "Medium",
        "category": "Trees",
        "description": "Given the `root` of a binary tree represented as a level-order array, determine if it is a valid binary search tree (BST).\n\nA valid BST is defined as follows:\n- The left subtree of a node contains only nodes with keys strictly less than the node's key.\n- The right subtree of a node contains only nodes with keys strictly greater than the node's key.\n- Both the left and right subtrees must also be binary search trees.",
        "examples": json.dumps([
            {"input": "root = [2,1,3]", "output": "true", "explanation": "1 < 2 < 3, so it is a valid BST."},
            {"input": "root = [5,1,4,null,null,3,6]", "output": "false", "explanation": "The root node's value is 5 but its right child's value is 4."}
        ]),
        "constraints": json.dumps(["The number of nodes in the tree is in the range [1, 10^4].", "-2^31 <= Node.val <= 2^31 - 1"]),
        "starter_code": json.dumps({
            "python": "def isValidBST(root: list) -> bool:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public boolean isValidBST(List<Object> root) {\n        // Write your solution here\n        return false;\n    }\n}",
            "cpp": "#include <vector>\n#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool isValidBST(vector<string>& root) {\n        // Write your solution here\n        return false;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 5
    },
    {
        "title": "Lowest Common Ancestor of a Binary Search Tree",
        "slug": "lowest-common-ancestor",
        "difficulty": "Medium",
        "category": "Trees",
        "description": "Given a binary search tree (BST) represented as a level-order array and two values `p` and `q`, find the lowest common ancestor (LCA) node value of the two given nodes.\n\nThe lowest common ancestor is defined between two nodes `p` and `q` as the lowest node in `T` that has both `p` and `q` as descendants (where we allow a node to be a descendant of itself).",
        "examples": json.dumps([
            {"input": "root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 8", "output": "6", "explanation": "The LCA of nodes 2 and 8 is 6."},
            {"input": "root = [6,2,8,0,4,7,9,null,null,3,5], p = 2, q = 4", "output": "2", "explanation": "The LCA of nodes 2 and 4 is 2, since a node can be a descendant of itself."}
        ]),
        "constraints": json.dumps(["The number of nodes in the tree is in the range [2, 10^5].", "-10^9 <= Node.val <= 10^9", "All Node.val are unique.", "p and q exist in the BST."]),
        "starter_code": json.dumps({
            "python": "def lowestCommonAncestor(root: list, p: int, q: int) -> int:\n    # Write your solution here\n    pass",
            "java": "import java.util.*;\n\nclass Solution {\n    public int lowestCommonAncestor(List<Object> root, int p, int q) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\n#include <string>\nusing namespace std;\n\nclass Solution {\npublic:\n    int lowestCommonAncestor(vector<string>& root, int p, int q) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 6
    },
    {
        "title": "Number of Islands",
        "slug": "number-of-islands",
        "difficulty": "Medium",
        "category": "Graphs & BFS/DFS",
        "description": "Given an `m x n` 2D binary grid `grid` which represents a map of `'1'`s (land) and `'0'`s (water), return the number of islands.\n\nAn island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically. You may assume all four edges of the grid are all surrounded by water.",
        "examples": json.dumps([
            {
                "input": "grid = [[\"1\",\"1\",\"1\",\"1\",\"0\"],[\"1\",\"1\",\"0\",\"1\",\"0\"],[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"0\",\"0\",\"0\",\"0\",\"0\"]]",
                "output": "1",
                "explanation": "All adjacent 1s form a single connected island."
            },
            {
                "input": "grid = [[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"1\",\"1\",\"0\",\"0\",\"0\"],[\"0\",\"0\",\"1\",\"0\",\"0\"],[\"0\",\"0\",\"0\",\"1\",\"1\"]]",
                "output": "3",
                "explanation": "There are three distinct islands."
            }
        ]),
        "constraints": json.dumps(["m == grid.length", "n == grid[i].length", "1 <= m, n <= 300", "grid[i][j] is '0' or '1'."]),
        "starter_code": json.dumps({
            "python": "def numIslands(grid: list[list[str]]) -> int:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public int numIslands(char[][] grid) {\n        // Write your solution here\n        return 0;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    int numIslands(vector<vector<char>>& grid) {\n        // Write your solution here\n        return 0;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 7
    },
    {
        "title": "Course Schedule",
        "slug": "course-schedule",
        "difficulty": "Medium",
        "category": "Graphs & Topological Sort",
        "description": "There are a total of `numCourses` courses you have to take, labeled from `0` to `numCourses - 1`.\nYou are given an array `prerequisites` where `prerequisites[i] = [a, b]` indicates that you must take course `b` first if you want to take course `a`.\n\nReturn `true` if you can finish all courses. Otherwise, return `false` (i.e. if there is a cycle).",
        "examples": json.dumps([
            {"input": "numCourses = 2, prerequisites = [[1,0]]", "output": "true", "explanation": "There are 2 courses to take. Course 0 then Course 1. It is possible."},
            {"input": "numCourses = 2, prerequisites = [[1,0],[0,1]]", "output": "false", "explanation": "To take course 1 you should take 0, and to take 0 you should take 1. Impossible cycle."}
        ]),
        "constraints": json.dumps(["1 <= numCourses <= 2000", "0 <= prerequisites.length <= 5000", "prerequisites[i].length == 2", "All the pairs prerequisites[i] are unique."]),
        "starter_code": json.dumps({
            "python": "def canFinish(numCourses: int, prerequisites: list[list[int]]) -> bool:\n    # Write your solution here\n    pass",
            "java": "class Solution {\n    public boolean canFinish(int numCourses, int[][] prerequisites) {\n        // Write your solution here\n        return false;\n    }\n}",
            "cpp": "#include <vector>\nusing namespace std;\n\nclass Solution {\npublic:\n    bool canFinish(int numCourses, vector<vector<int>>& prerequisites) {\n        // Write your solution here\n        return false;\n    }\n};"
        }),
        "supported_languages": json.dumps(["python", "java", "cpp"]),
        "order_index": 8
    }
]

MODULE5_TEST_CASES = {
    "invert-binary-tree": [
        {"input": "[4, 2, 7, 1, 3, 6, 9]", "expected_output": "[4, 7, 2, 9, 6, 3, 1]", "is_sample": True},
        {"input": "[2, 1, 3]", "expected_output": "[2, 3, 1]", "is_sample": True},
        {"input": "[]", "expected_output": "[]", "is_sample": False},
        {"input": "[1, 2]", "expected_output": "[1, null, 2]", "is_sample": False},
    ],
    "maximum-depth-of-binary-tree": [
        {"input": "[3, 9, 20, null, null, 15, 7]", "expected_output": "3", "is_sample": True},
        {"input": "[1, null, 2]", "expected_output": "2", "is_sample": True},
        {"input": "[]", "expected_output": "0", "is_sample": False},
        {"input": "[1]", "expected_output": "1", "is_sample": False},
    ],
    "same-tree": [
        {"input": "[1, 2, 3]\n[1, 2, 3]", "expected_output": "true", "is_sample": True},
        {"input": "[1, 2]\n[1, null, 2]", "expected_output": "false", "is_sample": True},
        {"input": "[1, 2, 1]\n[1, 1, 2]", "expected_output": "false", "is_sample": False},
        {"input": "[]\n[]", "expected_output": "true", "is_sample": False},
    ],
    "binary-tree-level-order-traversal": [
        {"input": "[3, 9, 20, null, null, 15, 7]", "expected_output": "[[3], [9, 20], [15, 7]]", "is_sample": True},
        {"input": "[1]", "expected_output": "[[1]]", "is_sample": True},
        {"input": "[]", "expected_output": "[]", "is_sample": False},
        {"input": "[1, 2, 3, 4, 5]", "expected_output": "[[1], [2, 3], [4, 5]]", "is_sample": False},
    ],
    "validate-binary-search-tree": [
        {"input": "[2, 1, 3]", "expected_output": "true", "is_sample": True},
        {"input": "[5, 1, 4, null, null, 3, 6]", "expected_output": "false", "is_sample": True},
        {"input": "[1]", "expected_output": "true", "is_sample": False},
        {"input": "[10, 5, 15, null, null, 6, 20]", "expected_output": "false", "is_sample": False},
    ],
    "lowest-common-ancestor": [
        {"input": "[6, 2, 8, 0, 4, 7, 9, null, null, 3, 5]\n2\n8", "expected_output": "6", "is_sample": True},
        {"input": "[6, 2, 8, 0, 4, 7, 9, null, null, 3, 5]\n2\n4", "expected_output": "2", "is_sample": True},
        {"input": "[2, 1]\n2\n1", "expected_output": "2", "is_sample": False},
        {"input": "[5, 3, 6, 2, 4, null, null, 1]\n1\n4", "expected_output": "3", "is_sample": False},
    ],
    "number-of-islands": [
        {
            "input": '[["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]',
            "expected_output": "1",
            "is_sample": True
        },
        {
            "input": '[["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]',
            "expected_output": "3",
            "is_sample": True
        },
        {
            "input": '[["0","0"],["0","0"]]',
            "expected_output": "0",
            "is_sample": False
        },
        {
            "input": '[["1","0","1"],["0","1","0"],["1","0","1"]]',
            "expected_output": "5",
            "is_sample": False
        },
    ],
    "course-schedule": [
        {"input": "2\n[[1, 0]]", "expected_output": "true", "is_sample": True},
        {"input": "2\n[[1, 0], [0, 1]]", "expected_output": "false", "is_sample": True},
        {"input": "3\n[[0, 1], [0, 2], [1, 2]]", "expected_output": "true", "is_sample": False},
        {"input": "3\n[[1, 0], [2, 1], [0, 2]]", "expected_output": "false", "is_sample": False},
    ]
}

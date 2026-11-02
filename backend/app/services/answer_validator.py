"""
Answer Meaningfulness & Validity Validator for AI Interview Training Platform.

This module inspects candidate interview responses to detect uninterpretable,
nonsensical, empty, or random character input (e.g., 'hbasjhkdfggasklfdg', '???',
'asdf asdf asdf') while strictly preserving valid concise technical responses
(e.g., 'O(log n)', 'HTTP 404', 'A tuple is immutable.', 'SELECT * FROM users').
"""

import re
from typing import NamedTuple, Optional, Set

# Known valid technical acronyms
COMMON_ACRONYMS: Set[str] = {
    "API", "SDK", "REST", "SOAP", "CRUD", "JSON", "XML", "YAML", "HTML", "CSS",
    "SQL", "NOSQL", "ACID", "BASE", "CAP", "DRY", "SOLID", "KISS", "YAGNI",
    "OOP", "FP", "ORM", "DOM", "JVM", "CLR", "CPU", "GPU", "RAM", "ROM", "SSD",
    "HDD", "RAID", "TCP", "UDP", "IP", "DNS", "DHCP", "BGP", "ARP", "ICMP",
    "HTTP", "HTTPS", "SSH", "FTP", "SFTP", "SMTP", "IMAP", "POP3", "TLS", "SSL",
    "CORS", "CSRF", "XSS", "JWT", "SSO", "OAUTH", "SAML", "CI", "CD", "AWS",
    "GCP", "AZURE", "EC2", "S3", "IAM", "VPC", "CLI", "GUI", "IDE", "VCS",
    "PR", "MR", "SHA", "MD5", "AES", "RSA", "FIFO", "LIFO", "LRU", "LFU",
    "DFS", "BFS", "DAG", "BST", "AVL", "TDD", "BDD", "MVC", "MVVM", "MVW",
    "RPC", "GRPC", "RDBMS", "UUID", "GUID", "URI", "URL", "URN", "WSDL", "PWA"
}

# Common technical and programming terminology keywords
COMMON_TECH_TERMS: Set[str] = {
    # Data structures & Algorithms
    "array", "arrays", "tuple", "tuples", "list", "lists", "vector", "vectors",
    "string", "strings", "hash", "hashes", "hashmap", "hashtable", "dictionary",
    "dict", "set", "sets", "stack", "stacks", "queue", "queues", "deque",
    "heap", "heaps", "tree", "trees", "graph", "graphs", "node", "nodes",
    "vertex", "vertices", "edge", "edges", "matrix", "matrices", "trie",
    "recursion", "recursive", "iterative", "iteration", "pointer", "pointers",
    "reference", "references", "memory", "allocation", "garbage", "collector",
    "complexity", "logarithmic", "linear", "quadratic", "exponential", "factorial",
    "polynomial", "asymptotic", "amortized", "big-o", "omega", "theta",
    "sort", "sorting", "search", "searching", "traversal", "binary", "quicksort",
    "mergesort", "heapsort", "dfs", "bfs", "dijkstra", "memoization", "dynamic",
    "programming", "greedy", "backtracking", "divide", "conquer", "sliding", "window",
    "two-pointer", "two-pointers", "prefix", "suffix", "immutable", "mutable",
    # Object-Oriented & Architecture
    "class", "classes", "object", "objects", "instance", "instances", "inheritance",
    "polymorphism", "encapsulation", "abstraction", "interface", "interfaces",
    "abstract", "concrete", "override", "overload", "constructor", "destructor",
    "static", "dynamic", "singleton", "factory", "observer", "strategy", "adapter",
    "microservice", "microservices", "monolith", "monolithic", "serverless",
    "stateless", "stateful", "concurrency", "thread", "threads", "process",
    "processes", "deadlock", "race", "condition", "mutex", "semaphore", "lock",
    "async", "asynchronous", "sync", "synchronous", "promise", "future", "coroutine",
    "thread-safe", "atomic", "idempotent", "idempotency", "scalability", "latency",
    "throughput", "bandwidth", "caching", "cache", "redis", "memcached", "kafka",
    "rabbitmq", "sharding", "replication", "partitioning", "indexing", "index",
    # Web & Database & DevOps
    "database", "databases", "table", "tables", "column", "columns", "row", "rows",
    "primary", "key", "foreign", "join", "joins", "query", "queries", "schema",
    "normalization", "denormalization", "transaction", "transactions", "commit",
    "rollback", "acid", "isolation", "endpoint", "endpoints", "request", "response",
    "header", "headers", "cookie", "cookies", "session", "sessions", "token", "tokens",
    "payload", "status", "code", "client", "server", "middleware", "gateway",
    "reverse", "proxy", "load", "balancer", "docker", "container", "containers",
    "kubernetes", "k8s", "pod", "pods", "pipeline", "deployment", "kubernetes",
    "git", "branch", "merge", "rebase", "commit", "checkout", "stash", "repository"
}

# Basic English vocabulary common in interview explanations
BASIC_ENGLISH_WORDS: Set[str] = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "can", "could", "will", "would",
    "shall", "should", "may", "might", "must", "and", "or", "but", "nor", "so",
    "for", "yet", "at", "by", "for", "from", "in", "into", "of", "off", "on",
    "onto", "out", "over", "to", "up", "with", "about", "above", "across", "after",
    "against", "along", "among", "around", "as", "before", "behind", "below",
    "beneath", "beside", "between", "beyond", "during", "inside", "near", "outside",
    "since", "through", "throughout", "till", "toward", "under", "until", "upon",
    "within", "without", "i", "you", "he", "she", "it", "we", "they", "me", "him",
    "her", "us", "them", "my", "your", "his", "its", "our", "their", "mine",
    "yours", "hers", "ours", "theirs", "this", "that", "these", "those", "which",
    "who", "whom", "whose", "what", "whatever", "whoever", "whomever", "whichever",
    "when", "where", "why", "how", "all", "any", "both", "each", "few", "more",
    "most", "other", "some", "such", "no", "not", "only", "same", "than", "too",
    "very", "just", "because", "while", "if", "then", "else", "true", "false",
    "null", "none", "yes", "no", "first", "last", "next", "previous", "fast",
    "slow", "better", "best", "worse", "worst", "high", "low", "great", "small",
    "big", "large", "efficient", "optimal", "simple", "complex", "easy", "hard",
    "store", "stores", "stored", "storing", "find", "finds", "found", "finding",
    "use", "uses", "used", "using", "take", "takes", "took", "taking", "give",
    "gives", "gave", "giving", "make", "makes", "made", "making", "create", "creates",
    "created", "creating", "return", "returns", "returned", "returning", "run", "runs",
    "ran", "running", "pass", "passes", "passed", "passing", "check", "checks", "checked",
    "allow", "allows", "allowed", "allowing", "provide", "provides", "provided",
    "value", "values", "data", "type", "types", "function", "functions", "method",
    "methods", "variable", "variables", "constant", "constants", "parameter", "parameters",
    "argument", "arguments", "return", "returns", "result", "results", "output", "input",
    "error", "errors", "exception", "exceptions", "handle", "handles", "handled",
    "write", "writes", "wrote", "writing", "read", "reads", "reading", "call", "calls",
    "called", "calling", "implement", "implements", "implemented", "implementation",
    "system", "systems", "application", "applications", "program", "programs", "code"
}

# Regex matchers for concise legitimate technical representations
RE_BIG_O = re.compile(
    r"^(?:Big[- ]?O\s*:?\s*)?(?:[O0o]|Omega|omega|Theta|theta)\s*\(\s*[a-zA-Z0-9\s\^\*\+\-\/\!\_]+\s*\)$",
    re.IGNORECASE
)
RE_HTTP_STATUS = re.compile(
    r"^(?:HTTP\s*)?[1-5][0-9]{2}(?:\s+[a-zA-Z\s]+)?$",
    re.IGNORECASE
)
RE_SQL_QUERY = re.compile(
    r"^\s*(?:SELECT|INSERT|UPDATE|DELETE|CREATE|ALTER|DROP|TRUNCATE|WITH|EXPLAIN)\s+[\s\S]+$",
    re.IGNORECASE
)
RE_CODE_KEYWORD = re.compile(
    r"\b(def|class|return|function|const|let|var|public|private|protected|static|void|int|float|double|import|from|console\.log|System\.out|printf|cout)\b"
)
RE_VALID_OPERATORS = {
    "[]", "{}", "()", "==", "!=", "<=", ">=", "->", "=>", "&&", "||", "++", "--",
    "+=", "-=", "*=", "/=", "//", "**", "null", "None", "nil", "undefined"
}

# Long consonant cluster pattern (6 or more consonants in a row without a vowel)
RE_LONG_CONSONANTS = re.compile(r"[bcdfghjklmnpqrstvwxyz]{6,}", re.IGNORECASE)

# Standard QWERTY keyboard walk sequences
KEYBOARD_WALKS = [
    "asdfghjkl", "qwertyuiop", "zxcvbnm", "qazwsxedcrfv", "1234567890",
    "asdfgh", "qwerty", "zxcvbn"
]


class ValidationResult(NamedTuple):
    is_valid: bool
    reason: Optional[str]
    is_technical_shortcut: bool


def is_recognized_word(word: str) -> bool:
    """Checks whether a word belongs to known English, tech terminology, or acronym sets."""
    clean = re.sub(r"[^a-zA-Z0-9_-]", "", word).strip()
    if not clean:
        return False

    # Pure numbers are recognized
    if clean.isdigit():
        return True

    upper = clean.upper()
    lower = clean.lower()

    if upper in COMMON_ACRONYMS:
        return True
    if lower in COMMON_TECH_TERMS:
        return True
    if lower in BASIC_ENGLISH_WORDS:
        return True

    # Common plural or past-tense suffixes
    if lower.endswith("s") and lower[:-1] in (COMMON_TECH_TERMS | BASIC_ENGLISH_WORDS):
        return True
    if lower.endswith("ed") and lower[:-2] in (COMMON_TECH_TERMS | BASIC_ENGLISH_WORDS):
        return True
    if lower.endswith("ing") and lower[:-3] in (COMMON_TECH_TERMS | BASIC_ENGLISH_WORDS):
        return True

    return False


def is_keyboard_mash(word: str) -> bool:
    """Checks if a string is a keyboard mash sequence."""
    lower = word.lower()
    for walk in KEYBOARD_WALKS:
        if walk in lower or lower in walk and len(lower) >= 6:
            return True
    return False


def validate_answer_meaningfulness(question_text: str, answer_text: str) -> ValidationResult:
    """
    Validates whether an answer contains meaningful, interpretable content.

    Returns ValidationResult(is_valid=True, ...) if the answer is legitimate,
    or ValidationResult(is_valid=False, reason=...) if it is clearly meaningless gibberish.
    """
    raw = (answer_text or "").strip()

    # 1. Empty or whitespace-only
    if not raw:
        return ValidationResult(
            is_valid=False,
            reason="The answer is empty or contains only whitespace.",
            is_technical_shortcut=False
        )

    # 2. Check for legitimate technical shortcuts first
    if raw in RE_VALID_OPERATORS:
        return ValidationResult(is_valid=True, reason=None, is_technical_shortcut=True)
    if RE_BIG_O.match(raw):
        return ValidationResult(is_valid=True, reason=None, is_technical_shortcut=True)
    if RE_HTTP_STATUS.match(raw):
        return ValidationResult(is_valid=True, reason=None, is_technical_shortcut=True)
    if RE_SQL_QUERY.match(raw):
        return ValidationResult(is_valid=True, reason=None, is_technical_shortcut=True)
    if RE_CODE_KEYWORD.search(raw):
        return ValidationResult(is_valid=True, reason=None, is_technical_shortcut=True)

    # 3. Punctuation / Symbol-only answers without alphanumeric content
    alnum_chars = [c for c in raw if c.isalnum()]
    if not alnum_chars:
        return ValidationResult(
            is_valid=False,
            reason="The answer contains only punctuation and symbols without meaningful content.",
            is_technical_shortcut=False
        )

    # 4. Repeated character spam (e.g. 'aaaaaaa', 'xxxxxxxxxxxxxx')
    clean_chars = [c.lower() for c in alnum_chars]
    if len(clean_chars) >= 4 and len(set(clean_chars)) == 1:
        return ValidationResult(
            is_valid=False,
            reason="The answer consists of a single repeating character.",
            is_technical_shortcut=False
        )
    if len(clean_chars) >= 8 and len(set(clean_chars)) <= 2:
        return ValidationResult(
            is_valid=False,
            reason="The answer consists of a repeated two-character loop.",
            is_technical_shortcut=False
        )

    # Tokenize words
    words = re.findall(r"[a-zA-Z0-9_\-\.\:\(\)]+", raw)
    if not words:
        return ValidationResult(
            is_valid=False,
            reason="No interpretable alphanumeric tokens detected.",
            is_technical_shortcut=False
        )

    # 5. Repeated token spam (e.g. 'asdf asdf asdf', 'bla bla bla bla')
    clean_words = [w.lower() for w in words]
    if len(clean_words) >= 3 and len(set(clean_words)) == 1:
        return ValidationResult(
            is_valid=False,
            reason="The answer consists of the same repeated word.",
            is_technical_shortcut=False
        )
    if len(clean_words) >= 6 and len(set(clean_words)) <= 2:
        return ValidationResult(
            is_valid=False,
            reason="The answer consists of a looping two-word phrase.",
            is_technical_shortcut=False
        )

    # 6. Single long gibberish token (like 'hbasjhkdfggasklfdg')
    if len(words) == 1:
        single = words[0]
        # Allow legitimate acronyms or tech words
        if is_recognized_word(single):
            return ValidationResult(is_valid=True, reason=None, is_technical_shortcut=False)

        # Check for keyboard mash walk
        if is_keyboard_mash(single):
            return ValidationResult(
                is_valid=False,
                reason="The answer appears to be keyboard mash.",
                is_technical_shortcut=False
            )

        # Check for impossible consonant cluster (e.g. 6+ consonants in a row like 'jhkdfgg')
        if RE_LONG_CONSONANTS.search(single):
            return ValidationResult(
                is_valid=False,
                reason="The answer contains an uninterpretable consonant cluster.",
                is_technical_shortcut=False
            )

        # Check vowel presence for words longer than 5 letters (unless recognized acronym)
        vowels = [c for c in single.lower() if c in "aeiouy"]
        if len(single) > 5 and not vowels and not single.isupper():
            return ValidationResult(
                is_valid=False,
                reason="The word has no vowels and is not a recognized acronym.",
                is_technical_shortcut=False
            )

        # Words of length >= 12 that are completely unrecognized
        if len(single) >= 12 and not is_recognized_word(single):
            # Check vowel-to-consonant distribution
            vowel_ratio = len(vowels) / len(single)
            if vowel_ratio < 0.20 or vowel_ratio > 0.80:
                return ValidationResult(
                    is_valid=False,
                    reason="The word has an unnatural vowel-to-consonant distribution.",
                    is_technical_shortcut=False
                )

    # 7. Multi-word gibberish check
    recognized_count = sum(1 for w in words if is_recognized_word(w))
    unrecognized_count = len(words) - recognized_count

    # Check if words contain impossible consonant clusters or keyboard mash
    has_gibberish_word = any(RE_LONG_CONSONANTS.search(w) or is_keyboard_mash(w) for w in words)

    if len(words) >= 1 and recognized_count == 0 and has_gibberish_word:
        return ValidationResult(
            is_valid=False,
            reason="The answer contains gibberish tokens with no recognizable vocabulary.",
            is_technical_shortcut=False
        )

    if len(words) >= 3 and recognized_count == 0:
        return ValidationResult(
            is_valid=False,
            reason="None of the words in the answer belong to known vocabulary.",
            is_technical_shortcut=False
        )

    return ValidationResult(
        is_valid=True,
        reason=None,
        is_technical_shortcut=False
    )

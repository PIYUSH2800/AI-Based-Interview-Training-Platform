def normalize_output(text: str) -> str:
    """
    Normalizes text output for clean deterministic comparison:
    1. Replaces Windows CRLF with LF.
    2. Trims trailing whitespace from each line.
    3. Strips overall leading/trailing newlines and blank spaces.
    """
    if text is None:
        return ""
    # Standardize newlines
    lines = text.replace('\r\n', '\n').split('\n')
    # Strip trailing whitespace on each line
    cleaned_lines = [line.rstrip() for line in lines]
    # Join back and strip surrounding blank newlines
    return '\n'.join(cleaned_lines).strip()


def compare_outputs(actual: str, expected: str) -> bool:
    """
    Compares actual stdout with expected output deterministically.
    Supports exact text match, JSON structure equivalence, and boolean case-insensitivity.
    """
    norm_actual = normalize_output(actual)
    norm_expected = normalize_output(expected)
    if norm_actual == norm_expected:
        return True

    # Check boolean case-insensitivity (e.g. true vs True)
    if norm_actual.lower() in ("true", "false") and norm_expected.lower() in ("true", "false"):
        return norm_actual.lower() == norm_expected.lower()

    # Check JSON equivalence for arrays or objects
    if (norm_actual.startswith(("{", "[")) and norm_actual.endswith(("}", "]"))) or \
       (norm_expected.startswith(("{", "[")) and norm_expected.endswith(("}", "]"))):
        try:
            import json
            if json.loads(norm_actual) == json.loads(norm_expected):
                return True
        except Exception:
            pass

    return False

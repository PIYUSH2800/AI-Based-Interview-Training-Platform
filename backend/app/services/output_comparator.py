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
    """
    norm_actual = normalize_output(actual)
    norm_expected = normalize_output(expected)
    return norm_actual == norm_expected

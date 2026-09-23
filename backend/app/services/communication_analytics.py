"""
communication_analytics.py

Deterministic text analytics for interview answer transcripts.
All metrics are calculated purely from the final answer string —
no audio, no microphone data, no machine-learning models.

Labelling convention:
  - Metrics derived from word count and a fixed speech-rate baseline are
    clearly labelled as *estimated* in the output keys.
  - No claim is made about emotion, confidence, personality, or competence.
"""

import re
from typing import Dict, Any

# ---------------------------------------------------------------------------
# Configurable filler-word list
# Phrase fillers must appear before single-word fillers so phrase matching
# has priority during the scan.
# ---------------------------------------------------------------------------
FILLER_PHRASES = [
    "you know",
    "sort of",
    "kind of",
    "i mean",
]

FILLER_WORDS = [
    "um",
    "uh",
    "er",
    "like",
    "basically",
    "actually",
    "right",
    "okay",
    "so",
]

# Baseline speaking rate used for duration/WPM estimation.
# 130 wpm is a measured average for interview-style speech (not reading aloud).
BASELINE_WPM: int = 130


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _tokenize_words(text: str):
    """
    Return a list of lowercase word tokens.
    Strips punctuation from word boundaries so 'like,' → 'like'
    but 'liked' stays 'liked'.
    """
    return re.findall(r"\b[a-zA-Z']+\b", text.lower())


def _count_sentences(text: str) -> int:
    """
    Split on sentence-ending punctuation followed by whitespace or end-of-string.
    Returns at least 1 for any non-empty text.
    """
    text = text.strip()
    if not text:
        return 0
    parts = re.split(r'(?<=[.!?])\s+', text)
    # Filter out empty fragments
    parts = [p for p in parts if p.strip()]
    return max(len(parts), 1) if parts else 0


def _sentence_lengths(text: str):
    """Return a list of word counts per sentence."""
    text = text.strip()
    if not text:
        return []
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [len(_tokenize_words(s)) for s in parts if s.strip()]


def _detect_fillers(tokens: list) -> Dict[str, int]:
    """
    Detect filler words and phrases using whole-word / whole-phrase matching.

    Strategy:
      1. Re-join tokens to a normalised string for phrase scanning.
      2. For each phrase, count non-overlapping occurrences.
      3. For each single word, count occurrences in the token list
         (exact token equality, so 'liked' ≠ 'like').

    Returns a dict mapping filler → count (only those with count > 0).
    """
    detected: Dict[str, int] = {}

    # Phrase detection on the joined token string
    joined = " ".join(tokens)
    for phrase in FILLER_PHRASES:
        # \b-equivalent for multi-word phrase: ensure boundaries
        pattern = r"(?<![a-z'])" + re.escape(phrase) + r"(?![a-z'])"
        count = len(re.findall(pattern, joined))
        if count:
            detected[phrase] = count

    # Single-word detection on the token list
    for word in FILLER_WORDS:
        count = tokens.count(word)
        if count:
            detected[word] = detected.get(word, 0) + count

    return detected


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_answer(answer_text: str) -> Dict[str, Any]:
    """
    Analyse a single answer string and return a dict of communication metrics.

    All returned values are labelled to reflect how they were derived:
      - Counts (word_count, sentence_count, etc.) are exact.
      - estimated_speaking_time_seconds and estimated_wpm are derived from
        BASELINE_WPM and clearly described as estimates.

    Returns a zero-filled dict for empty / whitespace-only input so callers
    never encounter KeyError or ZeroDivisionError.
    """
    text = (answer_text or "").strip()

    if not text:
        return {
            "word_count": 0,
            "sentence_count": 0,
            "avg_sentence_length": 0.0,
            "max_sentence_length": 0,
            "estimated_speaking_time_seconds": 0,
            "estimated_wpm": 0,
            "filler_word_count": 0,
            "filler_word_rate": 0.0,
            "detected_fillers": {},
        }

    tokens = _tokenize_words(text)
    word_count = len(tokens)

    sentence_count = _count_sentences(text)
    sent_lengths = _sentence_lengths(text)
    avg_sent_len = round(sum(sent_lengths) / len(sent_lengths), 1) if sent_lengths else 0.0
    max_sent_len = max(sent_lengths) if sent_lengths else 0

    # Estimated speaking time based on BASELINE_WPM (at least 1 sec for non-empty text)
    if word_count > 0:
        speaking_seconds = max(1, round((word_count / BASELINE_WPM) * 60))
        speaking_minutes = speaking_seconds / 60.0
        estimated_wpm = round(word_count / speaking_minutes)
    else:
        speaking_seconds = 0
        estimated_wpm = 0

    # Filler detection
    detected = _detect_fillers(tokens)
    filler_count = sum(detected.values())
    filler_rate = round((filler_count / word_count) * 100, 1) if word_count > 0 else 0.0

    return {
        "word_count": word_count,
        "sentence_count": sentence_count,
        "avg_sentence_length": avg_sent_len,
        "max_sentence_length": max_sent_len,
        "estimated_speaking_time_seconds": speaking_seconds,
        "estimated_wpm": estimated_wpm,
        "filler_word_count": filler_count,
        "filler_word_rate": filler_rate,
        "detected_fillers": detected,
    }


def compute_aggregate(per_answer_stats: list) -> Dict[str, Any]:
    """
    Aggregate analytics across multiple answers for an interview-level summary.
    Returns zero-safe totals and averages.
    """
    if not per_answer_stats:
        return {
            "total_words": 0,
            "total_sentences": 0,
            "total_filler_words": 0,
            "avg_filler_rate": 0.0,
            "avg_wpm": 0,
            "overall_suggestion": "No answers found to analyse.",
        }

    total_words = sum(s["word_count"] for s in per_answer_stats)
    total_sentences = sum(s["sentence_count"] for s in per_answer_stats)
    total_fillers = sum(s["filler_word_count"] for s in per_answer_stats)

    filler_rates = [s["filler_rate"] for s in per_answer_stats if "filler_rate" in s]
    avg_filler_rate = round(sum(filler_rates) / len(filler_rates), 1) if filler_rates else 0.0

    wpms = [s["estimated_wpm"] for s in per_answer_stats if s["estimated_wpm"] > 0]
    avg_wpm = round(sum(wpms) / len(wpms)) if wpms else 0

    # Derive a neutral, descriptive overall suggestion
    if total_fillers == 0:
        suggestion = "Excellent — no filler words detected across all answers."
    elif avg_filler_rate < 3.0:
        suggestion = "Low filler-word usage. Keep practising to maintain clarity."
    elif avg_filler_rate < 7.0:
        suggestion = (
            "Moderate filler-word usage detected. Practising deliberate pausing "
            "instead of filler words can improve interview delivery."
        )
    else:
        suggestion = (
            "Frequent filler words were detected. Focus on pausing briefly when "
            "collecting thoughts rather than using filler words — it sounds more confident."
        )

    return {
        "total_words": total_words,
        "total_sentences": total_sentences,
        "total_filler_words": total_fillers,
        "avg_filler_rate": avg_filler_rate,
        "avg_wpm": avg_wpm,
        "overall_suggestion": suggestion,
    }

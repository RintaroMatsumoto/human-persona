"""
Shared metrics module for human-persona analysis and benchmarking.

Provides 7 language-agnostic structural metrics that distinguish
human-like text from formal AI-generated text:

    1. sentence_length_cv — Coefficient of variation of sentence lengths
    2. hedge_rate — Hedging expressions per sentence
    3. self_correction_rate — Self-correction markers per sentence
    4. words_per_sentence — Average words per sentence
    5. flesch_reading_ease — Flesch Reading Ease score
    6. cushion_rate — Whether response opens with a soft expression
    7. filler_rate — Filler/discourse markers per sentence

Used by:
    - analysis/dpo_parameter_extraction.py (dataset analysis)
    - benchmarks/dpo_benchmark.py (pipeline evaluation)
"""

from __future__ import annotations

import re
import statistics
from typing import Optional

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False


# ---------------------------------------------------------------------------
# Pattern constants
# ---------------------------------------------------------------------------

HEDGE_PATTERNS: list[str] = [
    r"\bprobably\b", r"\bmaybe\b", r"\bi think\b", r"\bmight\b",
    r"\bperhaps\b", r"\blikely\b", r"\bi guess\b", r"\bsort of\b",
    r"\bkind of\b", r"\bseems like\b", r"\bi believe\b", r"\bnot sure\b",
    r"\bpossibly\b", r"\bi suppose\b", r"\baround\b", r"\bapproximately\b",
    r"\broughly\b", r"\bmore or less\b",
]

SELF_CORRECTION_PATTERNS: list[str] = [
    r"\blet me rephrase\b", r"\bcorrection\b", r"\bwait,", r"\bno,",
    r"\brather,", r"\bsorry,",
    # NOTE: 'actually', 'i mean', 'well,' removed to avoid double-counting
    # with FILLER_PATTERNS (see Issue #8 validation)
]

FILLER_PATTERNS: list[str] = [
    r"\bwell\b", r"\bso\b", r"\byou know\b", r"\bi mean\b", r"\blike\b",
    r"\bbasically\b", r"\bactually\b", r"\bhonestly\b", r"\bokay\b",
    # NOTE: 'right' removed — conflicts with SHORT_INTERJECTIONS and
    # has high false-positive rate in normal text
]

CUSHION_PATTERNS: list[str] = [
    r"\bthanks\b", r"\bthank you\b", r"\bgreat question\b",
    r"\bi understand\b", r"\bgood point\b", r"\bthat's a great\b",
    r"\bi appreciate\b", r"\bsure\b", r"\bof course\b", r"\babsolutely\b",
]


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def split_sentences(text: str) -> list[str]:
    """Split text into sentences using punctuation boundaries."""
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    return [s for s in sentences if len(s.strip()) > 0]


def count_pattern_matches(text: str, patterns: list[str]) -> int:
    """Count total matches of regex patterns in text."""
    text_lower = text.lower()
    return sum(len(re.findall(p, text_lower)) for p in patterns)


def word_count(text: str) -> int:
    """Count words in text."""
    return len(text.split())


# ---------------------------------------------------------------------------
# Metric functions (public API)
# ---------------------------------------------------------------------------

def measure_sentence_length_cv(text: str) -> Optional[float]:
    """Calculate coefficient of variation of sentence lengths (chars).

    Returns None if text has fewer than 2 sentences.
    """
    sentences = split_sentences(text)
    if len(sentences) < 2:
        return None
    lengths = [len(s) for s in sentences]
    mean = statistics.mean(lengths)
    if mean == 0:
        return None
    return statistics.stdev(lengths) / mean


def measure_hedge_rate(text: str) -> float:
    """Calculate hedging expression rate (per sentence)."""
    sentences = split_sentences(text)
    if not sentences:
        return 0.0
    matches = count_pattern_matches(text, HEDGE_PATTERNS)
    return matches / len(sentences)


def measure_self_correction_rate(text: str) -> float:
    """Calculate self-correction marker rate (per sentence)."""
    sentences = split_sentences(text)
    if not sentences:
        return 0.0
    matches = count_pattern_matches(text, SELF_CORRECTION_PATTERNS)
    return matches / len(sentences)


def measure_words_per_sentence(text: str) -> float:
    """Calculate average words per sentence."""
    sentences = split_sentences(text)
    if not sentences:
        return 0.0
    return word_count(text) / len(sentences)


def measure_flesch_score(text: str) -> float:
    """Calculate Flesch Reading Ease score.

    Returns 0.0 if textstat is not installed.
    """
    if not HAS_TEXTSTAT:
        return 0.0
    if not text.strip():
        return 0.0
    return textstat.flesch_reading_ease(text)


def measure_cushion_rate(text: str) -> bool:
    """Check if response opens with a cushion expression."""
    sentences = split_sentences(text)
    if not sentences:
        return False
    first = sentences[0].lower()
    return any(re.search(p, first) for p in CUSHION_PATTERNS)


def measure_filler_rate(text: str) -> float:
    """Calculate filler/discourse marker rate (per sentence)."""
    sentences = split_sentences(text)
    if not sentences:
        return 0.0
    matches = count_pattern_matches(text, FILLER_PATTERNS)
    return matches / len(sentences)

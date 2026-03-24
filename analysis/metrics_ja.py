"""
Japanese-specific metrics module for human-persona analysis.

Provides 7 structural metrics adapted for Japanese text:

    1. sentence_length_cv — CV of sentence lengths (「。」「！」「？」で分割)
    2. hedge_rate — 曖昧表現の出現率
    3. self_correction_rate — 自己訂正表現の出現率
    4. morphemes_per_sentence — MeCabによる1文あたり平均形態素数
    5. kanji_ratio — 漢字含有率 (Flesch代替: 漢字多い=硬い文章)
    6. cushion_rate — 冒頭クッション表現の出現率
    7. filler_rate — フィラー表現の出現率

MeCab fallback:
    MeCabが未インストールの場合、morphemes_per_sentenceは
    文字数ベースの概算(1形態素≒2.5文字)にフォールバックする。
"""

from __future__ import annotations

import re
import statistics
import unicodedata
from typing import Optional

from analysis.ja_keywords import (
    HEDGE_KEYWORDS_JA,
    SELF_CORRECTION_JA,
    CUSHION_JA,
    FILLER_JA,
)

try:
    import MeCab
    _TAGGER = MeCab.Tagger()
    # Force lazy initialization
    _TAGGER.parse("")
    HAS_MECAB = True
except (ImportError, RuntimeError):
    _TAGGER = None
    HAS_MECAB = False


# ---------------------------------------------------------------------------
# Text utilities
# ---------------------------------------------------------------------------

def split_sentences_ja(text: str) -> list[str]:
    """Split Japanese text into sentences using 。！？ and newlines."""
    sentences = re.split(r'[。！？\n]+', text.strip())
    return [s.strip() for s in sentences if s.strip()]


def count_keywords(text: str, keywords: list[str]) -> int:
    """Count total occurrences of keyword strings in text."""
    return sum(text.count(kw) for kw in keywords)


def count_morphemes(text: str) -> int:
    """Count morphemes using MeCab, or fallback to character-based estimate."""
    if HAS_MECAB and _TAGGER is not None:
        parsed = _TAGGER.parse(text)
        # Each line is a morpheme except the final "EOS\n"
        lines = parsed.strip().split("\n")
        return sum(1 for line in lines if line and line != "EOS")
    else:
        # Fallback: ~2.5 characters per morpheme in Japanese
        chars = len(re.sub(r'\s+', '', text))
        return max(1, round(chars / 2.5))


def _is_kanji(ch: str) -> bool:
    """Check if a character is a CJK Unified Ideograph (漢字)."""
    try:
        name = unicodedata.name(ch, "")
        return "CJK UNIFIED IDEOGRAPH" in name
    except ValueError:
        return False


# ---------------------------------------------------------------------------
# Metric functions (public API)
# ---------------------------------------------------------------------------

def measure_sentence_length_cv_ja(text: str) -> Optional[float]:
    """Calculate coefficient of variation of sentence lengths (characters).

    Returns None if text has fewer than 2 sentences.
    """
    sentences = split_sentences_ja(text)
    if len(sentences) < 2:
        return None
    lengths = [len(s) for s in sentences]
    mean = statistics.mean(lengths)
    if mean == 0:
        return None
    return statistics.stdev(lengths) / mean


def measure_hedge_rate_ja(text: str) -> float:
    """Calculate Japanese hedging expression rate (per sentence)."""
    sentences = split_sentences_ja(text)
    if not sentences:
        return 0.0
    matches = count_keywords(text, HEDGE_KEYWORDS_JA)
    return matches / len(sentences)


def measure_self_correction_rate_ja(text: str) -> float:
    """Calculate Japanese self-correction rate (per sentence)."""
    sentences = split_sentences_ja(text)
    if not sentences:
        return 0.0
    matches = count_keywords(text, SELF_CORRECTION_JA)
    return matches / len(sentences)


def measure_morphemes_per_sentence_ja(text: str) -> float:
    """Calculate average morphemes per sentence using MeCab.

    Falls back to character-based estimation if MeCab is unavailable.
    """
    sentences = split_sentences_ja(text)
    if not sentences:
        return 0.0
    total = sum(count_morphemes(s) for s in sentences)
    return total / len(sentences)


def measure_kanji_ratio_ja(text: str) -> float:
    """Calculate kanji ratio (漢字含有率).

    Replaces Flesch Reading Ease for Japanese:
    - High kanji ratio = formal/hard text
    - Low kanji ratio = casual/soft text
    """
    chars = re.sub(r'\s+', '', text)
    if not chars:
        return 0.0
    kanji_count = sum(1 for ch in chars if _is_kanji(ch))
    return kanji_count / len(chars)


def measure_cushion_rate_ja(text: str) -> bool:
    """Check if response opens with a cushion expression."""
    sentences = split_sentences_ja(text)
    if not sentences:
        return False
    first = sentences[0]
    return any(kw in first for kw in CUSHION_JA)


def measure_filler_rate_ja(text: str) -> float:
    """Calculate Japanese filler/discourse marker rate (per sentence)."""
    sentences = split_sentences_ja(text)
    if not sentences:
        return 0.0
    matches = count_keywords(text, FILLER_JA)
    return matches / len(sentences)

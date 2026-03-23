"""
Tests for analysis/dpo_parameter_extraction.py

Validates the metric extraction functions using synthetic test data,
without requiring the actual HuggingFace dataset.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.dpo_parameter_extraction import (
    split_sentences,
    count_pattern_matches,
    word_count,
    calc_sentence_length_variance,
    calc_hedge_rate,
    calc_self_correction_rate,
    calc_verbosity,
    calc_cushion_rate,
    calc_filler_rate,
    compute_statistics,
    generate_recommended_params,
    HEDGE_PATTERNS,
    SELF_CORRECTION_PATTERNS,
    FILLER_PATTERNS,
    CUSHION_PATTERNS,
)


# ---------------------------------------------------------------------------
# split_sentences
# ---------------------------------------------------------------------------

class TestSplitSentences:
    def test_basic_split(self):
        result = split_sentences("Hello world. How are you? I'm fine!")
        assert len(result) == 3

    def test_single_sentence(self):
        result = split_sentences("Just one sentence")
        assert len(result) == 1

    def test_empty_string(self):
        result = split_sentences("")
        assert len(result) == 0

    def test_multiple_spaces(self):
        result = split_sentences("First.  Second.  Third.")
        assert len(result) == 3


# ---------------------------------------------------------------------------
# count_pattern_matches
# ---------------------------------------------------------------------------

class TestCountPatternMatches:
    def test_hedge_patterns(self):
        text = "I think maybe this might work, probably."
        count = count_pattern_matches(text, HEDGE_PATTERNS)
        # "I think", "maybe", "might", "probably" = 4
        assert count == 4

    def test_no_matches(self):
        text = "The cat sat on the mat."
        count = count_pattern_matches(text, HEDGE_PATTERNS)
        assert count == 0

    def test_case_insensitive(self):
        text = "I THINK this MIGHT work."
        count = count_pattern_matches(text, HEDGE_PATTERNS)
        assert count == 2


# ---------------------------------------------------------------------------
# word_count
# ---------------------------------------------------------------------------

class TestWordCount:
    def test_basic(self):
        assert word_count("hello world foo bar") == 4

    def test_empty(self):
        assert word_count("") == 0


# ---------------------------------------------------------------------------
# calc_sentence_length_variance
# ---------------------------------------------------------------------------

class TestSentenceLengthVariance:
    def test_uniform_sentences(self):
        # Nearly identical sentence lengths → low CV
        text = "Hello world. Bye world. Hey world."
        cv = calc_sentence_length_variance(text)
        assert cv is not None
        assert cv < 0.2  # low variance

    def test_varied_sentences(self):
        # Very different sentence lengths → high CV
        text = "Hi. This is a much longer sentence with many more words in it."
        cv = calc_sentence_length_variance(text)
        assert cv is not None
        assert cv > 0.5  # high variance

    def test_single_sentence_returns_none(self):
        cv = calc_sentence_length_variance("Just one sentence")
        assert cv is None

    def test_empty_returns_none(self):
        cv = calc_sentence_length_variance("")
        assert cv is None


# ---------------------------------------------------------------------------
# calc_hedge_rate
# ---------------------------------------------------------------------------

class TestHedgeRate:
    def test_with_hedges(self):
        text = "I think this probably works. Maybe it does."
        rate = calc_hedge_rate(text)
        # 3 hedges in 2 sentences = 1.5
        assert rate > 1.0

    def test_no_hedges(self):
        text = "The answer is 42. This is certain."
        rate = calc_hedge_rate(text)
        assert rate == 0.0

    def test_empty(self):
        rate = calc_hedge_rate("")
        assert rate == 0.0


# ---------------------------------------------------------------------------
# calc_self_correction_rate
# ---------------------------------------------------------------------------

class TestSelfCorrectionRate:
    def test_with_corrections(self):
        text = "Well, actually I mean the other thing. Sorry, let me rephrase."
        rate = calc_self_correction_rate(text)
        assert rate > 0.0

    def test_no_corrections(self):
        text = "The project is complete. It works as expected."
        rate = calc_self_correction_rate(text)
        assert rate == 0.0


# ---------------------------------------------------------------------------
# calc_verbosity
# ---------------------------------------------------------------------------

class TestVerbosity:
    def test_basic(self):
        text = "This is a sentence. Here is another one."
        result = calc_verbosity(text)
        assert "words_per_sentence" in result
        assert result["words_per_sentence"] > 0

    def test_empty(self):
        result = calc_verbosity("")
        assert result["words_per_sentence"] == 0.0


# ---------------------------------------------------------------------------
# calc_cushion_rate
# ---------------------------------------------------------------------------

class TestCushionRate:
    def test_with_cushion(self):
        text = "Thanks for asking! The answer is 42."
        assert calc_cushion_rate(text) is True

    def test_without_cushion(self):
        text = "The answer is 42. Nothing more to say."
        assert calc_cushion_rate(text) is False

    def test_sure_cushion(self):
        text = "Sure, I can help with that. Let me check."
        assert calc_cushion_rate(text) is True

    def test_empty(self):
        assert calc_cushion_rate("") is False


# ---------------------------------------------------------------------------
# calc_filler_rate
# ---------------------------------------------------------------------------

class TestFillerRate:
    def test_with_fillers(self):
        text = "Well, you know, basically it works. Honestly, it does."
        rate = calc_filler_rate(text)
        assert rate > 1.0  # multiple fillers per sentence

    def test_no_fillers(self):
        text = "The project is complete. Deliverables are ready."
        rate = calc_filler_rate(text)
        assert rate == 0.0


# ---------------------------------------------------------------------------
# compute_statistics
# ---------------------------------------------------------------------------

class TestComputeStatistics:
    def test_basic_statistics(self):
        results = {
            "human": {
                "sentence_length_cv": [0.5, 0.6, 0.7],
                "hedge_rate": [0.1, 0.2, 0.3],
                "self_correction_rate": [0.01, 0.02, 0.03],
                "words_per_sentence": [10.0, 12.0, 14.0],
                "flesch_reading_ease": [60.0, 70.0, 80.0],
                "cushion": [1.0, 0.0, 1.0],
                "filler_rate": [0.2, 0.3, 0.4],
            },
            "formal": {
                "sentence_length_cv": [0.3, 0.4, 0.5],
                "hedge_rate": [0.01, 0.02, 0.03],
                "self_correction_rate": [0.0, 0.0, 0.01],
                "words_per_sentence": [18.0, 20.0, 22.0],
                "flesch_reading_ease": [30.0, 35.0, 40.0],
                "cushion": [0.0, 0.0, 1.0],
                "filler_rate": [0.05, 0.1, 0.15],
            },
        }

        summary = compute_statistics(results)

        # Check all metrics present
        assert "hedge_rate" in summary
        assert "sentence_length_cv" in summary
        assert "self_correction_rate" in summary
        assert "words_per_sentence" in summary
        assert "cushion" in summary
        assert "filler_rate" in summary

        # Check structure
        for metric_data in summary.values():
            assert "human_mean" in metric_data
            assert "formal_mean" in metric_data
            assert "t_statistic" in metric_data
            assert "p_value" in metric_data
            assert "human_ci_95" in metric_data

        # Human hedge rate should be higher than formal
        assert summary["hedge_rate"]["human_mean"] > summary["hedge_rate"]["formal_mean"]


# ---------------------------------------------------------------------------
# generate_recommended_params
# ---------------------------------------------------------------------------

class TestGenerateRecommendedParams:
    def test_output_structure(self):
        summary = {
            "sentence_length_cv": {"human_mean": 0.63, "human_std": 0.14},
            "hedge_rate": {"human_mean": 0.08},
            "self_correction_rate": {"human_mean": 0.04},
            "words_per_sentence": {"human_mean": 13.5, "formal_mean": 18.3},
            "cushion": {"human_mean": 0.16, "formal_mean": 0.02},
            "filler_rate": {"human_mean": 0.33, "formal_mean": 0.10},
        }

        params = generate_recommended_params(summary)

        assert "sentence_length_variance" in params
        assert "min_ratio" in params["sentence_length_variance"]
        assert "max_ratio" in params["sentence_length_variance"]
        assert "hedge_probability" in params
        assert "self_correction_rate" in params
        assert "verbosity_human_avg" in params
        assert "verbosity_formal_avg" in params
        assert "cushion_rate_human" in params
        assert "filler_rate_human" in params

        # min_ratio should be positive
        assert params["sentence_length_variance"]["min_ratio"] > 0

        # max_ratio > min_ratio
        assert params["sentence_length_variance"]["max_ratio"] > params["sentence_length_variance"]["min_ratio"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

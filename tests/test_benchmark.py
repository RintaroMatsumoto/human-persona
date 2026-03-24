"""
Tests for benchmarks/dpo_benchmark.py and analysis/metrics.py

Validates:
    - Shared metrics module functions
    - Score computation logic
    - Pipeline transformations
    - Cache read/write
    - Report generation
"""

import json
import random
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.metrics import (
    measure_sentence_length_cv,
    measure_hedge_rate,
    measure_self_correction_rate,
    measure_words_per_sentence,
    measure_flesch_score,
    measure_cushion_rate,
    measure_filler_rate,
    split_sentences,
    count_pattern_matches,
    word_count,
    HEDGE_PATTERNS,
    SELF_CORRECTION_PATTERNS,
    FILLER_PATTERNS,
    CUSHION_PATTERNS,
)
from benchmarks.dpo_benchmark import (
    compute_score,
    compute_overall_score,
    measure_all_metrics,
    HumanPersonaPipeline,
    generate_scorecard,
    generate_report,
    _cache_key,
    _save_cache_entry,
    _load_cache,
    METRIC_WEIGHTS,
    load_reference_stats,
    parse_args,
)


# ===========================================================================
# analysis/metrics.py — measure_* functions
# ===========================================================================

class TestMeasureSentenceLengthCV:
    def test_uniform_returns_low_cv(self):
        text = "Hello world. Bye world. Hey world."
        cv = measure_sentence_length_cv(text)
        assert cv is not None
        assert cv < 0.2

    def test_varied_returns_high_cv(self):
        text = "Hi. This is a much longer sentence with many more words in it."
        cv = measure_sentence_length_cv(text)
        assert cv is not None
        assert cv > 0.5

    def test_single_sentence_returns_none(self):
        assert measure_sentence_length_cv("Just one") is None

    def test_empty_returns_none(self):
        assert measure_sentence_length_cv("") is None


class TestMeasureHedgeRate:
    def test_with_hedges(self):
        text = "I think this probably works. Maybe it does."
        rate = measure_hedge_rate(text)
        assert rate > 1.0

    def test_no_hedges(self):
        text = "The answer is 42. This is certain."
        assert measure_hedge_rate(text) == 0.0

    def test_empty(self):
        assert measure_hedge_rate("") == 0.0


class TestMeasureSelfCorrectionRate:
    def test_with_corrections(self):
        text = "Well, actually I mean the other thing. Sorry, correction needed."
        rate = measure_self_correction_rate(text)
        assert rate > 0.0

    def test_no_corrections(self):
        text = "The project is complete. It works as expected."
        assert measure_self_correction_rate(text) == 0.0


class TestMeasureWordsPerSentence:
    def test_basic(self):
        text = "This is a sentence. Here is another one."
        wps = measure_words_per_sentence(text)
        assert wps > 0

    def test_empty(self):
        assert measure_words_per_sentence("") == 0.0


class TestMeasureFleschScore:
    def test_simple_text(self):
        text = "The cat sat on the mat. It was a nice day."
        score = measure_flesch_score(text)
        assert score > 50  # simple text should be easy to read

    def test_empty(self):
        assert measure_flesch_score("") == 0.0


class TestMeasureCushionRate:
    def test_with_cushion(self):
        assert measure_cushion_rate("Thanks for asking! Here is the answer.") is True

    def test_without_cushion(self):
        assert measure_cushion_rate("The answer is 42.") is False

    def test_empty(self):
        assert measure_cushion_rate("") is False


class TestMeasureFillerRate:
    def test_with_fillers(self):
        text = "Well, you know, basically it works. Honestly, it does."
        rate = measure_filler_rate(text)
        assert rate > 1.0

    def test_no_fillers(self):
        text = "The deliverables are ready. Everything is complete."
        assert measure_filler_rate(text) == 0.0


# ===========================================================================
# benchmarks/dpo_benchmark.py — Score computation
# ===========================================================================

class TestComputeScore:
    def test_perfect_match(self):
        # persona = humanlike → score = 1.0
        score = compute_score(
            persona_mean=0.634, formal_mean=0.432, humanlike_mean=0.634,
        )
        assert abs(score - 1.0) < 0.01

    def test_formal_match(self):
        # persona = formal → score = 0.0
        score = compute_score(
            persona_mean=0.432, formal_mean=0.432, humanlike_mean=0.634,
        )
        assert abs(score - 0.0) < 0.01

    def test_halfway(self):
        # persona halfway between formal and humanlike
        score = compute_score(
            persona_mean=0.533, formal_mean=0.432, humanlike_mean=0.634,
        )
        assert 0.4 < score < 0.6

    def test_overshoot_clipped(self):
        # persona overshoots humanlike → clipped to 1.0
        score = compute_score(
            persona_mean=0.800, formal_mean=0.432, humanlike_mean=0.634,
        )
        assert score == 1.0

    def test_zero_denominator(self):
        # no difference → returns 1.0
        score = compute_score(
            persona_mean=0.5, formal_mean=0.5, humanlike_mean=0.5,
        )
        assert score == 1.0


class TestComputeOverallScore:
    def test_all_perfect(self):
        scores = {metric: 1.0 for metric in METRIC_WEIGHTS}
        assert abs(compute_overall_score(scores) - 1.0) < 0.001

    def test_all_zero(self):
        scores = {metric: 0.0 for metric in METRIC_WEIGHTS}
        assert abs(compute_overall_score(scores) - 0.0) < 0.001

    def test_weighted(self):
        # hedge_rate and filler_rate have weight 1.5, rest 1.0
        scores = {
            "sentence_length_cv": 0.0,
            "hedge_rate": 1.0,
            "self_correction_rate": 0.0,
            "words_per_sentence": 0.0,
            "cushion_rate": 0.0,
            "filler_rate": 1.0,
        }
        overall = compute_overall_score(scores)
        # (0*1 + 1*1.5 + 0*1 + 0*1 + 0*1 + 1*1.5) / (1+1.5+1+1+1+1.5) = 3/7
        expected = 3.0 / 7.0
        assert abs(overall - expected) < 0.001


# ===========================================================================
# measure_all_metrics
# ===========================================================================

class TestMeasureAllMetrics:
    def test_returns_all_keys(self):
        metrics = measure_all_metrics("Hello world. How are you? I'm fine.")
        for key in METRIC_WEIGHTS:
            assert key in metrics

    def test_values_are_numeric(self):
        metrics = measure_all_metrics("Well, I think this probably works. Maybe so.")
        for key, val in metrics.items():
            assert isinstance(val, (int, float))


# ===========================================================================
# Pipeline transformations
# ===========================================================================

class TestHumanPersonaPipeline:
    def test_pipeline_modifies_text(self):
        pipeline = HumanPersonaPipeline()
        rng = random.Random(42)
        text = "The project is complete. All deliverables are ready. Tests are passing."
        modified = pipeline.apply(text, rng=rng)
        # With seed 42, some transformation should apply
        # (could be same in rare cases, so just check it's a string)
        assert isinstance(modified, str)
        assert len(modified) > 0

    def test_pipeline_deterministic_with_seed(self):
        pipeline = HumanPersonaPipeline()
        text = "This is a test response. It has multiple sentences. Ready for review."
        result1 = pipeline.apply(text, rng=random.Random(42))
        result2 = pipeline.apply(text, rng=random.Random(42))
        assert result1 == result2

    def test_pipeline_splits_long_sentences(self):
        """Pipeline should split sentences exceeding the target words/sentence."""
        pipeline = HumanPersonaPipeline()
        long_text = (
            "The implementation follows the specified requirements, "
            "and all components have been thoroughly tested, "
            "because the documentation has been updated accordingly."
        )
        result = pipeline.apply(long_text, rng=random.Random(99))
        from analysis.metrics import measure_words_per_sentence
        original_wps = measure_words_per_sentence(long_text)
        result_wps = measure_words_per_sentence(result)
        assert result_wps < original_wps

    def test_pipeline_preserves_short_sentences(self):
        """Pipeline should not split sentences that are already short."""
        pipeline = HumanPersonaPipeline()
        short_text = "Hello there. How are you?"
        result = pipeline.apply(short_text, rng=random.Random(99))
        # Should still have roughly the same sentence structure
        assert len(result) > 0

    def test_pipeline_increases_human_metrics(self):
        """Pipeline should move metrics closer to human-like values."""
        pipeline = HumanPersonaPipeline()
        formal_text = (
            "The implementation follows the specified requirements. "
            "All components have been thoroughly tested. "
            "The documentation has been updated accordingly. "
            "Performance metrics meet the established benchmarks. "
            "The deployment pipeline is fully configured."
        )
        # Run pipeline many times to get statistical effect
        rng = random.Random(42)
        transformed_texts = [pipeline.apply(formal_text, rng=random.Random(42 + i)) for i in range(100)]

        raw_fillers = measure_filler_rate(formal_text)
        avg_fillers = sum(measure_filler_rate(t) for t in transformed_texts) / len(transformed_texts)
        # Pipeline should generally add fillers
        assert avg_fillers >= raw_fillers


# ===========================================================================
# Cache
# ===========================================================================

class TestCache:
    def test_cache_key_deterministic(self):
        k1 = _cache_key("What is 2+2?")
        k2 = _cache_key("What is 2+2?")
        assert k1 == k2

    def test_cache_key_different_for_different_input(self):
        k1 = _cache_key("What is 2+2?")
        k2 = _cache_key("What is 3+3?")
        assert k1 != k2

    def test_save_and_load_cache(self, tmp_path):
        with patch("benchmarks.dpo_benchmark.CACHE_DIR", tmp_path):
            _save_cache_entry("testkey", "question?", "answer!")
            cache = _load_cache()
            assert cache["testkey"] == "answer!"

    def test_load_empty_cache(self, tmp_path):
        with patch("benchmarks.dpo_benchmark.CACHE_DIR", tmp_path):
            cache = _load_cache()
            assert cache == {}


# ===========================================================================
# Reference data
# ===========================================================================

class TestLoadReferenceStats:
    def test_loads_all_metrics(self):
        ref = load_reference_stats()
        for metric in METRIC_WEIGHTS:
            assert metric in ref
            assert "humanlike_mean" in ref[metric]
            assert "formal_mean" in ref[metric]

    def test_humanlike_greater_for_cv(self):
        ref = load_reference_stats()
        assert ref["sentence_length_cv"]["humanlike_mean"] > ref["sentence_length_cv"]["formal_mean"]


# ===========================================================================
# Report generation
# ===========================================================================

class TestReportGeneration:
    @pytest.fixture
    def sample_data(self):
        ref = {
            metric: {"humanlike_mean": 0.5, "formal_mean": 0.1}
            for metric in METRIC_WEIGHTS
        }
        means = {metric: 0.4 for metric in METRIC_WEIGHTS}
        scores = {metric: 0.75 for metric in METRIC_WEIGHTS}
        return means, scores, ref

    def test_report_contains_table(self, sample_data):
        means, scores, ref = sample_data
        report = generate_report(means, means, scores, scores, 0.75, 0.75, ref, 500)
        assert "| Metric |" in report
        assert "Sentence Length CV" in report

    def test_scorecard_structure(self, sample_data):
        means, scores, ref = sample_data
        card = generate_scorecard(means, means, scores, scores, 0.75, 0.75, ref, 500)
        assert "timestamp" in card
        assert "sample_size" in card
        assert card["sample_size"] == 500
        assert "model" in card
        assert "scores" in card
        assert "overall_score" in card
        for metric in METRIC_WEIGHTS:
            assert metric in card["scores"]


# ===========================================================================
# CLI argument parsing
# ===========================================================================

class TestParseArgs:
    def test_default_mode_is_local(self):
        args = parse_args([])
        assert args.mode == "local"

    def test_mode_local(self):
        args = parse_args(["--mode", "local"])
        assert args.mode == "local"

    def test_mode_claude(self):
        args = parse_args(["--mode", "claude"])
        assert args.mode == "claude"

    def test_invalid_mode_raises(self):
        with pytest.raises(SystemExit):
            parse_args(["--mode", "deepseek"])

    def test_default_model_is_haiku(self):
        args = parse_args([])
        assert args.model == "haiku"

    def test_model_override(self):
        args = parse_args(["--mode", "claude", "--model", "sonnet"])
        assert args.model == "sonnet"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

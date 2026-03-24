"""
DPO Benchmark Evaluation Pipeline — Phase A

Evaluates how closely human-persona's pipeline output matches the
Human-Like distribution from the DPO dataset.

Strategy:
    1. Sample 500 questions from HumanLLMs/Human-Like-DPO-Dataset (seed=42)
    2. Obtain raw responses (local dataset or Claude Code CLI)
    3. Pass through human-persona pipeline transformations
    4. Measure 6 metrics on both raw and pipeline outputs
    5. Score against Human-Like and Formal reference distributions

Score definition (per metric):
    score = |persona_mean - formal_mean| / |humanlike_mean - formal_mean|
    Clipped to [0.0, 1.0]. 1.0 = matches Human-Like, 0.0 = matches Formal.

Modes:
    --mode local  : Use DPO dataset's 'rejected' field (no API, instant)
    --mode claude : Use Claude Code CLI via 'claude -p' (Max plan, no extra cost)

Usage:
    python -m benchmarks.dpo_benchmark                  # local (default)
    python -m benchmarks.dpo_benchmark --mode claude    # Claude Code CLI
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from analysis.metrics import (
    measure_sentence_length_cv,
    measure_hedge_rate,
    measure_self_correction_rate,
    measure_words_per_sentence,
    measure_flesch_score,
    measure_cushion_rate,
    measure_filler_rate,
    HEDGE_PATTERNS,
    FILLER_PATTERNS,
    CUSHION_PATTERNS,
    split_sentences,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SAMPLE_SIZE = 500
SEED = 42
CACHE_DIR = Path(__file__).parent / "cache"
RESULTS_DIR = Path(__file__).parent / "results"
CLAUDE_CLI = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")

# Weighted average weights for overall score
METRIC_WEIGHTS: dict[str, float] = {
    "sentence_length_cv": 1.0,
    "hedge_rate": 1.5,
    "self_correction_rate": 1.0,
    "words_per_sentence": 1.0,
    "cushion_rate": 1.0,
    "filler_rate": 1.5,
}

# Reference values from Phase B analysis (analysis/results/full_statistics.json)
REFERENCE_FILE = Path(__file__).parent.parent / "analysis" / "results" / "full_statistics.json"


# ---------------------------------------------------------------------------
# Pipeline transformations (human-persona core logic)
# ---------------------------------------------------------------------------

class HumanPersonaPipeline:
    """Applies human-persona transformations to raw text.

    Mirrors the transformations in core/base_persona.py:
    - Ambiguity injection (hedging, self-correction)
    - Filler word insertion
    - Cushion expression prepending
    - Sentence length variation

    Uses config/en.json parameters for English benchmarking.
    """

    def __init__(self, config_path: str | Path | None = None):
        config_path = config_path or (
            Path(__file__).parent.parent / "config" / "en.json"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            self._config = json.load(f)

        ambiguity = self._config.get("ambiguity", {})
        self._hedge_prob = ambiguity.get("hedge_probability", 0.0817)
        self._self_correction_rate = ambiguity.get("self_correction_rate", 0.043)

        style = self._config.get("style", {})
        self._filler_rate = style.get("filler_rate", 0.334)
        self._uncertainty_rate = style.get("uncertainty_rate", 0.10)

        dpo = self._config.get("dpo_calibration", {})
        self._cushion_rate = dpo.get("cushion_rate", 0.1578)

        self._fillers = ["Hmm, ", "Yeah, ", "So, ", "Oh, ", "Actually, ", "Well, "]
        self._hedges = [
            "I think ", "probably ", "maybe ", "sort of ", "kind of ",
            "I guess ", "I believe ",
        ]
        self._cushions = [
            "Sure, ", "Of course, ", "Great question! ",
            "I understand. ", "Good point. ",
        ]
        self._corrections = [
            "well, actually, ",
            "I mean, ",
            "wait, let me rephrase — ",
            "sorry, what I meant was ",
        ]

    def apply(self, text: str, rng: random.Random | None = None) -> str:
        """Apply full pipeline to raw text."""
        rng = rng or random.Random()
        result = text

        # 1. Cushion injection (at start of response)
        if rng.random() < self._cushion_rate:
            cushion = rng.choice(self._cushions)
            result = cushion + result[0].lower() + result[1:] if result else result

        # 2. Filler insertion (per sentence)
        sentences = split_sentences(result)
        if len(sentences) > 1:
            new_sentences = []
            for i, sent in enumerate(sentences):
                if i > 0 and rng.random() < self._filler_rate:
                    filler = rng.choice(self._fillers)
                    sent = filler + sent[0].lower() + sent[1:] if sent else sent
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # 3. Hedge injection
        sentences = split_sentences(result)
        if sentences:
            new_sentences = []
            for sent in sentences:
                if rng.random() < self._hedge_prob:
                    hedge = rng.choice(self._hedges)
                    sent = hedge + sent[0].lower() + sent[1:] if sent else sent
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # 4. Self-correction injection (rare)
        if rng.random() < self._self_correction_rate:
            sentences = split_sentences(result)
            if len(sentences) >= 2:
                idx = rng.randint(1, len(sentences) - 1)
                correction = rng.choice(self._corrections)
                sentences[idx] = correction + sentences[idx][0].lower() + sentences[idx][1:]
                result = " ".join(sentences)

        return result


# ---------------------------------------------------------------------------
# API client with caching
# ---------------------------------------------------------------------------

def _cache_key(question: str) -> str:
    """Generate a deterministic cache key for a question."""
    return hashlib.sha256(question.encode("utf-8")).hexdigest()[:16]


def _load_cache() -> dict[str, str]:
    """Load all cached API responses."""
    cache: dict[str, str] = {}
    if not CACHE_DIR.exists():
        return cache
    for fp in CACHE_DIR.glob("*.json"):
        try:
            data = json.loads(fp.read_text(encoding="utf-8"))
            cache[data["key"]] = data["response"]
        except (json.JSONDecodeError, KeyError):
            continue
    return cache


def _save_cache_entry(key: str, question: str, response: str) -> None:
    """Save a single API response to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    entry = {"key": key, "question": question, "response": response}
    fp = CACHE_DIR / f"{key}.json"
    fp.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")


def generate_claude_response(
    question: str,
    cache: dict[str, str],
    model: str = "haiku",
) -> str:
    """Generate a response via Claude Code CLI ('claude -p'), with caching."""
    key = _cache_key(question)
    if key in cache:
        return cache[key]

    result = subprocess.run(
        [CLAUDE_CLI, "-p", question, "--model", model],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"claude -p failed: {result.stderr}")
    text = result.stdout.strip()
    _save_cache_entry(key, question, text)
    cache[key] = text
    return text


# ---------------------------------------------------------------------------
# Metrics measurement
# ---------------------------------------------------------------------------

def measure_all_metrics(text: str) -> dict[str, float]:
    """Measure all 6 benchmark metrics on a text."""
    cv = measure_sentence_length_cv(text)
    return {
        "sentence_length_cv": cv if cv is not None else 0.0,
        "hedge_rate": measure_hedge_rate(text),
        "self_correction_rate": measure_self_correction_rate(text),
        "words_per_sentence": measure_words_per_sentence(text),
        "cushion_rate": 1.0 if measure_cushion_rate(text) else 0.0,
        "filler_rate": measure_filler_rate(text),
    }


def compute_score(
    persona_mean: float,
    formal_mean: float,
    humanlike_mean: float,
) -> float:
    """Compute normalized score for a single metric.

    score = |persona_mean - formal_mean| / |humanlike_mean - formal_mean|
    Clipped to [0.0, 1.0].
    """
    denominator = abs(humanlike_mean - formal_mean)
    if denominator < 1e-9:
        return 1.0  # no difference between human and formal
    raw = abs(persona_mean - formal_mean) / denominator
    return min(raw, 1.0)


def compute_overall_score(scores: dict[str, float]) -> float:
    """Compute weighted average overall score."""
    total_weight = sum(METRIC_WEIGHTS.values())
    weighted_sum = sum(
        scores[metric] * weight
        for metric, weight in METRIC_WEIGHTS.items()
    )
    return weighted_sum / total_weight


# ---------------------------------------------------------------------------
# Reference data loader
# ---------------------------------------------------------------------------

def load_reference_stats() -> dict[str, dict[str, float]]:
    """Load Human-Like and Formal reference means from Phase B results."""
    if not REFERENCE_FILE.exists():
        raise FileNotFoundError(
            f"Phase B results not found: {REFERENCE_FILE}\n"
            "Run analysis/dpo_parameter_extraction.py first."
        )
    data = json.loads(REFERENCE_FILE.read_text(encoding="utf-8"))

    # Map from full_statistics.json keys to benchmark metric names
    mapping = {
        "sentence_length_cv": "sentence_length_cv",
        "hedge_rate": "hedge_rate",
        "self_correction_rate": "self_correction_rate",
        "words_per_sentence": "words_per_sentence",
        "cushion": "cushion_rate",
        "filler_rate": "filler_rate",
    }

    ref: dict[str, dict[str, float]] = {}
    for src_key, dst_key in mapping.items():
        ref[dst_key] = {
            "humanlike_mean": data[src_key]["human_mean"],
            "formal_mean": data[src_key]["formal_mean"],
        }
    return ref


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_report(
    raw_means: dict[str, float],
    pipeline_means: dict[str, float],
    raw_scores: dict[str, float],
    pipeline_scores: dict[str, float],
    raw_overall: float,
    pipeline_overall: float,
    ref: dict[str, dict[str, float]],
    sample_size: int,
    model_name: str = "local",
) -> str:
    """Generate markdown benchmark report."""
    lines = [
        "# DPO Benchmark Evaluation Report",
        "",
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Model:** {model_name}",
        f"**Sample Size:** {sample_size}",
        f"**Seed:** {SEED}",
        "",
        "---",
        "",
        "## Results",
        "",
        "| Metric | Raw API | +Pipeline | Human-Like Target | Score (Raw) | Score (+Pipeline) |",
        "|--------|---------|-----------|-------------------|-------------|-------------------|",
    ]

    metric_labels = {
        "sentence_length_cv": "Sentence Length CV",
        "hedge_rate": "Hedge Rate",
        "self_correction_rate": "Self-Correction Rate",
        "words_per_sentence": "Words/Sentence",
        "cushion_rate": "Cushion Rate",
        "filler_rate": "Filler Rate",
    }

    for metric, label in metric_labels.items():
        target = ref[metric]["humanlike_mean"]
        lines.append(
            f"| {label} | {raw_means[metric]:.4f} | {pipeline_means[metric]:.4f} | "
            f"{target:.4f} | {raw_scores[metric]:.3f} | {pipeline_scores[metric]:.3f} |"
        )

    improvement = pipeline_overall - raw_overall
    lines += [
        "",
        f"**Overall Score (Raw API):** {raw_overall:.3f}",
        f"**Overall Score (+Pipeline):** {pipeline_overall:.3f}",
        f"**Pipeline Improvement:** {improvement:+.3f} ({improvement / max(raw_overall, 1e-9) * 100:+.1f}%)",
        "",
        "---",
        "",
        "## Score Interpretation",
        "",
        "- **1.0** = Matches Human-Like distribution perfectly",
        "- **0.0** = Matches Formal (AI) distribution",
        "- Score = |persona_mean - formal_mean| / |humanlike_mean - formal_mean|",
        "",
        "## Weights",
        "",
        "| Metric | Weight |",
        "|--------|--------|",
    ]
    for metric, weight in METRIC_WEIGHTS.items():
        lines.append(f"| {metric_labels[metric]} | {weight} |")

    # Recommendations
    lines += [
        "",
        "---",
        "",
        "## Improvement Recommendations",
        "",
    ]
    weak_metrics = sorted(
        pipeline_scores.items(), key=lambda x: x[1],
    )[:3]
    for metric, score in weak_metrics:
        target = ref[metric]["humanlike_mean"]
        current = pipeline_means[metric]
        lines.append(
            f"- **{metric_labels[metric]}**: score={score:.3f}, "
            f"current={current:.4f}, target={target:.4f}"
        )

    return "\n".join(lines)


def generate_scorecard(
    raw_means: dict[str, float],
    pipeline_means: dict[str, float],
    raw_scores: dict[str, float],
    pipeline_scores: dict[str, float],
    raw_overall: float,
    pipeline_overall: float,
    ref: dict[str, dict[str, float]],
    sample_size: int,
    model_name: str = "local",
) -> dict[str, Any]:
    """Generate machine-readable scorecard JSON."""
    scores: dict[str, Any] = {}
    for metric in METRIC_WEIGHTS:
        scores[metric] = {
            "raw": round(raw_means[metric], 4),
            "pipeline": round(pipeline_means[metric], 4),
            "target": round(ref[metric]["humanlike_mean"], 4),
            "score_raw": round(raw_scores[metric], 4),
            "score_pipeline": round(pipeline_scores[metric], 4),
        }

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sample_size": sample_size,
        "model": model_name,
        "seed": SEED,
        "scores": scores,
        "overall_score": {
            "raw": round(raw_overall, 4),
            "pipeline": round(pipeline_overall, 4),
        },
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="DPO Benchmark Evaluation Pipeline")
    parser.add_argument(
        "--mode",
        choices=["local", "claude"],
        default="local",
        help="Response source: 'local' uses dataset rejected field (default), "
             "'claude' uses Claude Code CLI (Max plan, no extra cost)",
    )
    parser.add_argument(
        "--model",
        default="haiku",
        help="Claude model for --mode claude (default: haiku). "
             "Examples: haiku, sonnet, opus",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    mode = args.mode
    claude_model = args.model
    if mode == "local":
        model_label = "local (DPO rejected)"
    else:
        model_label = f"claude -p --model {claude_model} (Max plan)"

    from datasets import load_dataset

    pipeline = HumanPersonaPipeline()

    # Load reference data
    print("Loading reference statistics from Phase B...")
    ref = load_reference_stats()

    # Load and sample dataset
    print("Loading HumanLLMs/Human-Like-DPO-Dataset...")
    dataset = load_dataset("HumanLLMs/Human-Like-DPO-Dataset", split="train")
    print(f"Loaded {len(dataset):,} samples. Sampling {SAMPLE_SIZE} (seed={SEED})...")

    rng = random.Random(SEED)
    indices = rng.sample(range(len(dataset)), SAMPLE_SIZE)
    questions = [dataset[i]["prompt"] for i in indices]

    # Generate / load raw responses
    print(f"Mode: {mode} ({model_label})")
    raw_responses: list[str] = []
    pipeline_responses: list[str] = []
    pipeline_rng = random.Random(SEED)

    if mode == "local":
        # Use dataset's 'rejected' field directly — no API calls
        for i, idx in enumerate(indices):
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i + 1}/{SAMPLE_SIZE}")
            raw = dataset[idx]["rejected"]
            raw_responses.append(raw)
            transformed = pipeline.apply(raw, rng=pipeline_rng)
            pipeline_responses.append(transformed)
    else:
        # claude mode — use Claude Code CLI
        cache = _load_cache()
        cached_count = sum(1 for q in questions if _cache_key(q) in cache)
        print(f"Cache: {cached_count}/{SAMPLE_SIZE} responses cached.")

        for i, question in enumerate(questions):
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i + 1}/{SAMPLE_SIZE}")

            raw = generate_claude_response(question, cache, model=claude_model)
            raw_responses.append(raw)

            transformed = pipeline.apply(raw, rng=pipeline_rng)
            pipeline_responses.append(transformed)

    # Measure metrics
    print("Measuring metrics...")
    raw_metrics_list = [measure_all_metrics(r) for r in raw_responses]
    pipeline_metrics_list = [measure_all_metrics(r) for r in pipeline_responses]

    # Compute means
    metric_names = list(METRIC_WEIGHTS.keys())
    raw_means: dict[str, float] = {}
    pipeline_means: dict[str, float] = {}
    for metric in metric_names:
        raw_vals = [m[metric] for m in raw_metrics_list]
        pipeline_vals = [m[metric] for m in pipeline_metrics_list]
        raw_means[metric] = sum(raw_vals) / len(raw_vals)
        pipeline_means[metric] = sum(pipeline_vals) / len(pipeline_vals)

    # Compute scores
    raw_scores: dict[str, float] = {}
    pipeline_scores: dict[str, float] = {}
    for metric in metric_names:
        raw_scores[metric] = compute_score(
            raw_means[metric],
            ref[metric]["formal_mean"],
            ref[metric]["humanlike_mean"],
        )
        pipeline_scores[metric] = compute_score(
            pipeline_means[metric],
            ref[metric]["formal_mean"],
            ref[metric]["humanlike_mean"],
        )

    raw_overall = compute_overall_score(raw_scores)
    pipeline_overall = compute_overall_score(pipeline_scores)

    # Output results
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    report = generate_report(
        raw_means, pipeline_means, raw_scores, pipeline_scores,
        raw_overall, pipeline_overall, ref, SAMPLE_SIZE, model_label,
    )
    report_path = RESULTS_DIR / "benchmark_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport: {report_path}")

    scorecard = generate_scorecard(
        raw_means, pipeline_means, raw_scores, pipeline_scores,
        raw_overall, pipeline_overall, ref, SAMPLE_SIZE, model_label,
    )
    scorecard_path = RESULTS_DIR / "scorecard.json"
    scorecard_path.write_text(
        json.dumps(scorecard, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Scorecard: {scorecard_path}")

    # Print summary
    print(f"\n{'='*60}")
    print("BENCHMARK RESULTS")
    print(f"{'='*60}")
    print(f"{'Metric':<25} {'Raw':>8} {'Pipeline':>10} {'Target':>8} {'Score':>7}")
    print(f"{'-'*60}")
    metric_labels = {
        "sentence_length_cv": "Sentence Length CV",
        "hedge_rate": "Hedge Rate",
        "self_correction_rate": "Self-Correction",
        "words_per_sentence": "Words/Sentence",
        "cushion_rate": "Cushion Rate",
        "filler_rate": "Filler Rate",
    }
    for metric in metric_names:
        print(
            f"{metric_labels[metric]:<25} "
            f"{raw_means[metric]:>8.4f} "
            f"{pipeline_means[metric]:>10.4f} "
            f"{ref[metric]['humanlike_mean']:>8.4f} "
            f"{pipeline_scores[metric]:>7.3f}"
        )
    print(f"{'-'*60}")
    print(f"{'Overall (Raw)':<25} {raw_overall:>37.3f}")
    print(f"{'Overall (+Pipeline)':<25} {pipeline_overall:>37.3f}")
    improvement = pipeline_overall - raw_overall
    print(f"{'Improvement':<25} {improvement:>+37.3f}")


if __name__ == "__main__":
    main()

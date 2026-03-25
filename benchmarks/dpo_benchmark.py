"""
DPO Benchmark Evaluation Pipeline — v2 (Scientifically Rigorous)

Evaluates how closely human-persona's pipeline output matches the
Human-Like distribution from the DPO dataset.

Key improvements over v1:
    - Held-out evaluation: 80/20 train/test split (reference from train, eval on test)
    - Bootstrap 95% confidence intervals (1000 resamples)
    - Cohen's d effect sizes per metric
    - Wasserstein distance for distributional comparison
    - Effect-size-based metric weights (not arbitrary)
    - Fixed filler pattern false positives (position-aware detection)

Score definition (per metric):
    score = 1.0 - |persona_mean - humanlike_mean| / |humanlike_mean - formal_mean|
    Clipped to [0.0, 1.0]. 1.0 = matches Human-Like exactly, 0.0 = off by full range.
    Penalizes both undershoot AND overshoot symmetrically.

Modes:
    --mode local  : Use DPO dataset's 'rejected' field (no API, instant)
    --mode claude : Use Claude Code CLI via 'claude -p' (Max plan, no extra cost)

Usage:
    python -m benchmarks.dpo_benchmark                  # local, held-out
    python -m benchmarks.dpo_benchmark --mode claude    # Claude Code CLI
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
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

import numpy as np
from scipy import stats as scipy_stats
from scipy.stats import wasserstein_distance

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
TRAIN_RATIO = 0.8  # 80% for reference calibration, 20% for evaluation
BOOTSTRAP_N = 1000  # Number of bootstrap resamples for CI
CACHE_DIR = Path(__file__).parent / "cache"
RESULTS_DIR = Path(__file__).parent / "results"
CLAUDE_CLI = shutil.which("claude") or os.path.expanduser("~/.local/bin/claude")

# Metric names used throughout
METRIC_NAMES = [
    "sentence_length_cv",
    "hedge_rate",
    "self_correction_rate",
    "words_per_sentence",
    "cushion_rate",
    "filler_rate",
]


# ---------------------------------------------------------------------------
# Pipeline transformations (human-persona core logic)
# ---------------------------------------------------------------------------

def _lowercase_first(text: str) -> str:
    """Lowercase the first character, but preserve 'I' and 'I\\'...' pronouns."""
    if not text:
        return text
    if text[0] == "I" and (len(text) == 1 or not text[1].isalpha()):
        return text
    return text[0].lower() + text[1:]


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
        self._max_words_per_sentence = dpo.get("verbosity_words_per_sentence", 13.53)

        # Filler words — must match FILLER_PATTERNS in metrics.py (no overlap
        # with SELF_CORRECTION_PATTERNS or HEDGE_PATTERNS)
        self._fillers = [
            "Well, ", "So, ", "You know, ", "I mean, ", "Like, ",
            "Basically, ", "Actually, ", "Honestly, ", "Okay, ",
        ]
        # Hedges — must match HEDGE_PATTERNS only
        self._hedges = [
            "I think ", "probably ", "maybe ", "sort of ", "kind of ",
            "I guess ", "I believe ",
        ]
        self._cushions = [
            "Sure, ", "Of course, ", "Great question! ",
            "I understand. ", "Good point. ",
        ]
        # Self-corrections — each triggers exactly 1 SELF_CORRECTION_PATTERN match
        self._corrections = [
            "wait, ",           # matches 'wait,'
            "sorry, ",          # matches 'sorry,'
            "rather, ",         # matches 'rather,'
            "no, ",             # matches 'no,'
        ]

    def apply(self, text: str, rng: random.Random | None = None) -> str:
        """Apply full pipeline to raw text."""
        rng = rng or random.Random()
        result = text

        # 1. Sentence splitting (shorten long sentences FIRST so later
        #    stages operate on the correct sentence count)
        result = self._split_long_sentences(result, rng)

        # 2. Cushion injection (at start of response)
        if rng.random() < self._cushion_rate:
            cushion = rng.choice(self._cushions)
            result = cushion + _lowercase_first(result) if result else result

        # 3. Filler insertion (per sentence, skip first)
        #    Coefficient 1.2 compensates for first-sentence skip: with N sentences,
        #    only N-1 are eligible, so rate * 1.2 * (N-1)/N ≈ target rate.
        #    Empirically validated: coeff=1.2 → measured 0.1669 vs target 0.1652.
        sentences = split_sentences(result)
        if len(sentences) > 1:
            effective_filler_rate = self._filler_rate * 1.2
            new_sentences = []
            for i, sent in enumerate(sentences):
                if i > 0 and rng.random() < effective_filler_rate:
                    filler = rng.choice(self._fillers)
                    sent = filler + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # 4. Hedge injection
        sentences = split_sentences(result)
        if sentences:
            new_sentences = []
            for sent in sentences:
                if rng.random() < self._hedge_prob:
                    hedge = rng.choice(self._hedges)
                    sent = hedge + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # 5. Self-correction injection (per sentence)
        sentences = split_sentences(result)
        if len(sentences) >= 2:
            new_sentences = [sentences[0]]
            for sent in sentences[1:]:
                if rng.random() < self._self_correction_rate:
                    correction = rng.choice(self._corrections)
                    sent = correction + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # 6. Short interjection insertion (increases sentence length CV)
        result = self._inject_short_interjections(result, rng)

        return result

    _SHORT_INTERJECTIONS = [
        "Hmm.", "Yeah.", "Sure.", "True.",
        "Got it.", "Makes sense.", "Fair enough.",
    ]

    def _inject_short_interjections(self, text: str, rng: random.Random) -> str:
        """Insert short 1-3 word interjections to increase sentence length variance.

        Empirically calibrated: prob=0.5 per slot, max_inserts=2 yields
        CV ≈ 0.623 on formal text, close to human-like target 0.633.
        """
        sentences = split_sentences(text)
        if len(sentences) < 3:
            return text

        # Insert 0-2 short interjections between sentences
        n_inserts = sum(1 for _ in range(2) if rng.random() < 0.5)
        for _ in range(n_inserts):
            interjection = rng.choice(self._SHORT_INTERJECTIONS)
            pos = rng.randint(1, len(sentences) - 1)
            sentences.insert(pos, interjection)

        return " ".join(sentences)

    # Conjunctions / relative markers where we can split a long sentence.
    _SPLIT_PATTERN = re.compile(
        r',\s*(?:and|but|so|because|since|although|though|which|where|while|however|yet)\s',
        re.IGNORECASE,
    )

    def _split_long_sentences(self, text: str, rng: random.Random) -> str:
        """Split sentences that exceed the target words-per-sentence.

        Threshold is set 15% above target to compensate for short interjections
        (1-2 word sentences) that pull the average down.
        """
        threshold = int(self._max_words_per_sentence * 1.15)
        sentences = split_sentences(text)
        new_sentences: list[str] = []

        for sent in sentences:
            if len(sent.split()) <= threshold:
                new_sentences.append(sent)
                continue

            # Find split points at conjunctions after a comma
            parts = self._try_split(sent, threshold)
            new_sentences.extend(parts)

        return " ".join(new_sentences)

    def _try_split(self, sent: str, threshold: int) -> list[str]:
        """Try to split a single sentence at conjunction boundaries."""
        matches = list(self._SPLIT_PATTERN.finditer(sent))
        if not matches:
            return [sent]

        # Pick the split point closest to the middle
        mid = len(sent) // 2
        best = min(matches, key=lambda m: abs(m.start() - mid))

        left = sent[:best.start()].rstrip(",").strip()
        right = sent[best.end():].strip()

        # Capitalize the right fragment
        if right:
            right = right[0].upper() + right[1:]

        # End the left fragment with a period if it doesn't have one
        if left and left[-1] not in ".!?":
            left += "."

        parts: list[str] = []
        # Recursively split if still too long
        if len(left.split()) > threshold:
            parts.extend(self._try_split(left, threshold))
        else:
            parts.append(left)

        if len(right.split()) > threshold:
            parts.extend(self._try_split(right, threshold))
        else:
            if right:
                parts.append(right)

        return parts


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


# ---------------------------------------------------------------------------
# Statistical functions
# ---------------------------------------------------------------------------

def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Compute Cohen's d effect size between two groups."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    var1 = np.var(group1, ddof=1)
    var2 = np.var(group2, ddof=1)
    pooled_std = math.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std < 1e-12:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / pooled_std)


def bootstrap_ci(
    values: np.ndarray,
    n_bootstrap: int = BOOTSTRAP_N,
    ci: float = 0.95,
    seed: int = SEED,
) -> tuple[float, float, float]:
    """Compute bootstrap confidence interval for the mean.

    Returns (mean, ci_lower, ci_upper).
    """
    rng = np.random.RandomState(seed)
    means = np.empty(n_bootstrap)
    n = len(values)
    for i in range(n_bootstrap):
        sample = values[rng.randint(0, n, size=n)]
        means[i] = np.mean(sample)
    alpha = (1.0 - ci) / 2.0
    lower = float(np.percentile(means, alpha * 100))
    upper = float(np.percentile(means, (1.0 - alpha) * 100))
    return float(np.mean(values)), lower, upper


def compute_score(
    persona_mean: float,
    formal_mean: float,
    humanlike_mean: float,
) -> float:
    """Compute normalized score for a single metric.

    score = 1.0 - |persona_mean - humanlike_mean| / |humanlike_mean - formal_mean|
    Clipped to [0.0, 1.0]. Penalizes both undershoot and overshoot.
    """
    denominator = abs(humanlike_mean - formal_mean)
    if denominator < 1e-9:
        return 1.0  # no difference between human and formal
    error = abs(persona_mean - humanlike_mean) / denominator
    return max(0.0, 1.0 - error)


def compute_metric_weights(ref: dict[str, dict[str, float]]) -> dict[str, float]:
    """Compute metric weights based on Cohen's d effect sizes.

    Metrics with larger effect sizes (better discriminating power between
    human and formal text) get higher weight. This replaces arbitrary weights.
    """
    raw_weights: dict[str, float] = {}
    for metric in METRIC_NAMES:
        humanlike_mean = ref[metric]["humanlike_mean"]
        formal_mean = ref[metric]["formal_mean"]
        humanlike_std = ref[metric].get("humanlike_std", 1.0)
        formal_std = ref[metric].get("formal_std", 1.0)
        # Approximate Cohen's d from summary stats
        pooled_std = math.sqrt((humanlike_std**2 + formal_std**2) / 2)
        if pooled_std < 1e-12:
            raw_weights[metric] = 0.0
        else:
            raw_weights[metric] = abs(humanlike_mean - formal_mean) / pooled_std

    # Normalize so weights sum to len(METRIC_NAMES)
    total = sum(raw_weights.values())
    if total < 1e-12:
        return {m: 1.0 for m in METRIC_NAMES}
    scale = len(METRIC_NAMES) / total
    return {m: round(w * scale, 4) for m, w in raw_weights.items()}


def compute_overall_score(
    scores: dict[str, float],
    weights: dict[str, float],
) -> float:
    """Compute weighted average overall score."""
    total_weight = sum(weights[m] for m in METRIC_NAMES)
    if total_weight < 1e-12:
        return 0.0
    weighted_sum = sum(scores[m] * weights[m] for m in METRIC_NAMES)
    return weighted_sum / total_weight


# ---------------------------------------------------------------------------
# Reference data — computed from train split
# ---------------------------------------------------------------------------

def compute_reference_from_split(
    dataset,
    indices: list[int],
) -> dict[str, dict[str, Any]]:
    """Compute reference statistics from a subset of the DPO dataset.

    Args:
        dataset: Full HuggingFace dataset.
        indices: Indices for the calibration (train) split.

    Returns:
        Reference dict with humanlike/formal means, stds, and arrays.
    """
    metrics_data: dict[str, dict[str, list[float]]] = {
        metric: {"human": [], "formal": []} for metric in METRIC_NAMES
    }

    for idx in indices:
        chosen = dataset[idx]["chosen"]
        rejected = dataset[idx]["rejected"]

        for text, key in [(chosen, "human"), (rejected, "formal")]:
            m = measure_all_metrics(text)
            for metric in METRIC_NAMES:
                metrics_data[metric][key].append(m[metric])

    ref: dict[str, dict[str, Any]] = {}
    for metric in METRIC_NAMES:
        h = np.array(metrics_data[metric]["human"])
        f = np.array(metrics_data[metric]["formal"])
        ref[metric] = {
            "humanlike_mean": float(np.mean(h)),
            "humanlike_std": float(np.std(h, ddof=1)) if len(h) > 1 else 0.0,
            "formal_mean": float(np.mean(f)),
            "formal_std": float(np.std(f, ddof=1)) if len(f) > 1 else 0.0,
            "cohens_d": cohens_d(h, f),
            "n_train": len(indices),
            "human_array": h,
            "formal_array": f,
        }

    return ref


def load_reference_stats() -> dict[str, dict[str, float]]:
    """Load Human-Like and Formal reference means from Phase B results.

    Fallback for non-holdout mode. Uses precomputed full_statistics.json.
    """
    reference_file = Path(__file__).parent.parent / "analysis" / "results" / "full_statistics.json"
    if not reference_file.exists():
        raise FileNotFoundError(
            f"Phase B results not found: {reference_file}\n"
            "Run analysis/dpo_parameter_extraction.py first."
        )
    data = json.loads(reference_file.read_text(encoding="utf-8"))

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
            "humanlike_std": data[src_key]["human_std"],
            "formal_mean": data[src_key]["formal_mean"],
            "formal_std": data[src_key]["formal_std"],
        }
    return ref


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

METRIC_LABELS = {
    "sentence_length_cv": "Sentence Length CV",
    "hedge_rate": "Hedge Rate",
    "self_correction_rate": "Self-Correction Rate",
    "words_per_sentence": "Words/Sentence",
    "cushion_rate": "Cushion Rate",
    "filler_rate": "Filler Rate",
}


def generate_report(
    raw_means: dict[str, float],
    pipeline_means: dict[str, float],
    raw_scores: dict[str, float],
    pipeline_scores: dict[str, float],
    raw_overall: float,
    pipeline_overall: float,
    ref: dict[str, dict[str, Any]],
    weights: dict[str, float],
    sample_size: int,
    model_name: str = "local",
    pipeline_cis: dict[str, tuple[float, float, float]] | None = None,
    pipeline_wasserstein: dict[str, float] | None = None,
    overall_ci: tuple[float, float, float] | None = None,
    holdout: bool = True,
    wass_scores: dict[str, float] | None = None,
    wass_overall: float | None = None,
    wass_overall_ci: tuple[float, float, float] | None = None,
    ks_results: dict[str, dict[str, float]] | None = None,
) -> str:
    """Generate markdown benchmark report with statistical rigor."""
    lines = [
        "# DPO Benchmark Evaluation Report — v2",
        "",
        f"**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Model:** {model_name}",
        f"**Evaluation Mode:** {'Held-out (80/20 split)' if holdout else 'Full dataset (WARNING: self-referential)'}",
        f"**Evaluation Sample Size:** {sample_size}",
        f"**Seed:** {SEED}",
        f"**Bootstrap Resamples:** {BOOTSTRAP_N}",
        "",
        "---",
        "",
        "## Methodology",
        "",
    ]

    if holdout:
        lines += [
            "This benchmark uses a proper **held-out evaluation** protocol:",
            "1. The DPO dataset is split 80/20 (seed=42)",
            "2. Reference statistics (human-like targets) are computed from the 80% **train** split",
            "3. Pipeline is evaluated on the 20% **test** split (never seen during calibration)",
            "4. This prevents self-referential score inflation",
            "",
        ]
    else:
        lines += [
            "**WARNING:** This benchmark evaluates on the same data used for calibration.",
            "Scores may be inflated due to self-referential evaluation.",
            "",
        ]

    lines += [
        "---",
        "",
        "## Results",
        "",
        "| Metric | Raw | +Pipeline | Target | Score | 95% CI | Wasserstein | Weight |",
        "|--------|-----|-----------|--------|-------|--------|-------------|--------|",
    ]

    for metric in METRIC_NAMES:
        label = METRIC_LABELS[metric]
        target = ref[metric]["humanlike_mean"]
        ci_str = "—"
        if pipeline_cis and metric in pipeline_cis:
            _, lo, hi = pipeline_cis[metric]
            ci_str = f"[{lo:.3f}, {hi:.3f}]"
        wass_str = "—"
        if pipeline_wasserstein and metric in pipeline_wasserstein:
            wass_str = f"{pipeline_wasserstein[metric]:.4f}"
        lines.append(
            f"| {label} | {raw_means[metric]:.4f} | {pipeline_means[metric]:.4f} | "
            f"{target:.4f} | {pipeline_scores[metric]:.3f} | {ci_str} | {wass_str} | {weights[metric]:.2f} |"
        )

    improvement = pipeline_overall - raw_overall
    lines += [
        "",
        "### Dual-Score Summary",
        "",
        "| Scoring Method | Score | 95% CI | Meaning |",
        "|----------------|-------|--------|---------|",
    ]
    mean_ci_str = f"[{overall_ci[1]:.3f}, {overall_ci[2]:.3f}]" if overall_ci else "—"
    lines.append(
        f"| **Mean Alignment** | {pipeline_overall:.3f} | {mean_ci_str} | "
        f"Pipeline means match human-like targets |"
    )
    if wass_overall is not None:
        wass_ci_str = f"[{wass_overall_ci[1]:.3f}, {wass_overall_ci[2]:.3f}]" if wass_overall_ci else "—"
        lines.append(
            f"| **Distribution Alignment** | {wass_overall:.3f} | {wass_ci_str} | "
            f"Full distributional match (Wasserstein) |"
        )
    lines += [
        "",
        f"**Raw API baseline:** {raw_overall:.3f}",
        f"**Pipeline improvement:** {improvement:+.3f}",
        "",
    ]

    # KS test results
    if ks_results:
        ks_pass = sum(1 for v in ks_results.values() if v["p_value"] >= 0.05)
        ks_total = len(ks_results)
        lines += [
            "---",
            "",
            f"## Distribution Tests (KS test, {ks_pass}/{ks_total} pass)",
            "",
            "Kolmogorov-Smirnov test: H0 = pipeline and human-like distributions are identical.",
            "",
            "| Metric | KS Statistic | p-value | Result |",
            "|--------|-------------|---------|--------|",
        ]
        for metric in METRIC_NAMES:
            if metric in ks_results:
                ks = ks_results[metric]
                verdict = "PASS" if ks["p_value"] >= 0.05 else "**FAIL**"
                lines.append(
                    f"| {METRIC_LABELS[metric]} | {ks['ks_stat']:.3f} | "
                    f"{ks['p_value']:.4e} | {verdict} |"
                )
        lines.append("")

    # Wasserstein-based per-metric scores
    if wass_scores:
        lines += [
            "---",
            "",
            "## Wasserstein-Based Scores (per metric)",
            "",
            "Score = 1.0 - W(pipeline, human) / W(formal, human).",
            "Compares full distributions, not just means.",
            "",
            "| Metric | W(formal,human) | W(pipe,human) | Wass Score | Mean Score | Gap |",
            "|--------|----------------|---------------|------------|------------|-----|",
        ]
        for metric in METRIC_NAMES:
            if metric in wass_scores:
                ws = wass_scores[metric]
                ms = pipeline_scores[metric]
                gap = ms - ws
                # Get W distances for display
                w_str = f"{ws:.3f}"
                m_str = f"{ms:.3f}"
                g_str = f"{gap:+.3f}"
                wfh = pipeline_wasserstein.get(metric, 0) if pipeline_wasserstein else 0
                # We need W(formal,human) — not stored directly, compute from wass_score
                # ws = 1 - w_pipe/w_formal → w_formal = w_pipe / (1 - ws) if ws < 1
                if ws < 1.0 and wfh > 0:
                    w_formal_human = wfh / (1.0 - ws) if ws < 1.0 else 0
                    lines.append(
                        f"| {METRIC_LABELS[metric]} | {w_formal_human:.4f} | {wfh:.4f} | "
                        f"{w_str} | {m_str} | {g_str} |"
                    )
                else:
                    lines.append(
                        f"| {METRIC_LABELS[metric]} | — | — | {w_str} | {m_str} | {g_str} |"
                    )
        lines.append("")

    lines += [
        "---",
        "",
        "## Metric Weights (Effect-Size Based)",
        "",
        "Weights are proportional to Cohen's d between human-like and formal distributions.",
        "Metrics that better discriminate human from AI text receive higher weight.",
        "",
        "| Metric | Cohen's d | Weight |",
        "|--------|-----------|--------|",
    ]
    for metric in METRIC_NAMES:
        d = ref[metric].get("cohens_d", "—")
        d_str = f"{d:.3f}" if isinstance(d, float) else str(d)
        lines.append(f"| {METRIC_LABELS[metric]} | {d_str} | {weights[metric]:.2f} |")

    lines += [
        "",
        "---",
        "",
        "## Score Interpretation",
        "",
        "- **1.0** = Matches Human-Like distribution perfectly",
        "- **0.0** = As far from Human-Like as Formal is (or worse)",
        "- Score = 1.0 - |persona_mean - humanlike_mean| / |humanlike_mean - formal_mean|",
        "- Wasserstein distance measures how far the full pipeline *distribution* is from human-like",
        "",
        "---",
        "",
        "## Weakest Metrics",
        "",
    ]
    weak_metrics = sorted(
        pipeline_scores.items(), key=lambda x: x[1],
    )[:3]
    for metric, score in weak_metrics:
        target = ref[metric]["humanlike_mean"]
        current = pipeline_means[metric]
        direction = "overshoot" if current > target else "undershoot"
        lines.append(
            f"- **{METRIC_LABELS[metric]}**: score={score:.3f}, "
            f"current={current:.4f}, target={target:.4f} ({direction})"
        )

    return "\n".join(lines)


def generate_scorecard(
    raw_means: dict[str, float],
    pipeline_means: dict[str, float],
    raw_scores: dict[str, float],
    pipeline_scores: dict[str, float],
    raw_overall: float,
    pipeline_overall: float,
    ref: dict[str, dict[str, Any]],
    weights: dict[str, float],
    sample_size: int,
    model_name: str = "local",
    pipeline_cis: dict[str, tuple[float, float, float]] | None = None,
    pipeline_wasserstein: dict[str, float] | None = None,
    overall_ci: tuple[float, float, float] | None = None,
    holdout: bool = True,
) -> dict[str, Any]:
    """Generate machine-readable scorecard JSON."""
    scores_out: dict[str, Any] = {}
    for metric in METRIC_NAMES:
        entry: dict[str, Any] = {
            "raw": round(raw_means[metric], 4),
            "pipeline": round(pipeline_means[metric], 4),
            "target": round(ref[metric]["humanlike_mean"], 4),
            "score_raw": round(raw_scores[metric], 4),
            "score_pipeline": round(pipeline_scores[metric], 4),
            "weight": round(weights[metric], 4),
        }
        if pipeline_cis and metric in pipeline_cis:
            _, lo, hi = pipeline_cis[metric]
            entry["ci_95"] = [round(lo, 4), round(hi, 4)]
        if pipeline_wasserstein and metric in pipeline_wasserstein:
            entry["wasserstein"] = round(pipeline_wasserstein[metric], 4)
        if "cohens_d" in ref[metric]:
            entry["cohens_d"] = round(ref[metric]["cohens_d"], 4)
        scores_out[metric] = entry

    result: dict[str, Any] = {
        "version": "2.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "evaluation_mode": "holdout_80_20" if holdout else "full_dataset",
        "sample_size": sample_size,
        "model": model_name,
        "seed": SEED,
        "bootstrap_n": BOOTSTRAP_N,
        "scores": scores_out,
        "overall_score": {
            "raw": round(raw_overall, 4),
            "pipeline": round(pipeline_overall, 4),
        },
    }
    if overall_ci:
        _, lo, hi = overall_ci
        result["overall_score"]["ci_95"] = [round(lo, 4), round(hi, 4)]

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="DPO Benchmark Evaluation Pipeline v2")
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
        help="Claude model for --mode claude (default: haiku).",
    )
    parser.add_argument(
        "--no-holdout",
        action="store_true",
        help="Disable held-out evaluation (evaluate on full dataset — NOT recommended).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    mode = args.mode
    claude_model = args.model
    holdout = not args.no_holdout
    if mode == "local":
        model_label = "local (DPO rejected)"
    else:
        model_label = f"claude -p --model {claude_model} (Max plan)"

    from datasets import load_dataset

    pipeline = HumanPersonaPipeline()

    # -----------------------------------------------------------------------
    # Load dataset
    # -----------------------------------------------------------------------
    print("Loading HumanLLMs/Human-Like-DPO-Dataset...")
    dataset = load_dataset("HumanLLMs/Human-Like-DPO-Dataset", split="train")
    n_total = len(dataset)
    print(f"Loaded {n_total:,} samples.")

    rng = random.Random(SEED)
    all_indices = list(range(n_total))
    rng.shuffle(all_indices)

    if holdout:
        # ---------------------------------------------------------------
        # 80/20 split: train for reference, test for evaluation
        # ---------------------------------------------------------------
        n_train = int(n_total * TRAIN_RATIO)
        train_indices = all_indices[:n_train]
        test_indices = all_indices[n_train:]
        eval_size = min(SAMPLE_SIZE, len(test_indices))
        eval_indices = test_indices[:eval_size]

        print(f"Hold-out split: {n_train:,} train / {len(test_indices):,} test")
        print(f"Computing reference statistics from {n_train:,} train samples...")
        ref = compute_reference_from_split(dataset, train_indices)
        print(f"Evaluating on {eval_size} held-out test samples...")
    else:
        # ---------------------------------------------------------------
        # Full dataset (self-referential — not recommended)
        # ---------------------------------------------------------------
        print("WARNING: --no-holdout used. Evaluating on same data as calibration.")
        print("Loading reference statistics from Phase B...")
        ref_flat = load_reference_stats()
        ref = {}
        for metric in METRIC_NAMES:
            ref[metric] = {
                "humanlike_mean": ref_flat[metric]["humanlike_mean"],
                "humanlike_std": ref_flat[metric].get("humanlike_std", 0.0),
                "formal_mean": ref_flat[metric]["formal_mean"],
                "formal_std": ref_flat[metric].get("formal_std", 0.0),
            }
        eval_size = SAMPLE_SIZE
        eval_indices = rng.sample(range(n_total), eval_size)

    # -----------------------------------------------------------------------
    # Compute effect-size-based weights
    # -----------------------------------------------------------------------
    weights = compute_metric_weights(ref)
    print(f"Metric weights (effect-size): {json.dumps(weights, indent=2)}")

    # -----------------------------------------------------------------------
    # Generate / load responses and apply pipeline
    # -----------------------------------------------------------------------
    print(f"Mode: {mode} ({model_label})")
    raw_responses: list[str] = []
    pipeline_responses: list[str] = []
    pipeline_rng = random.Random(SEED)

    if mode == "local":
        for i, idx in enumerate(eval_indices):
            if (i + 1) % 100 == 0:
                print(f"  Progress: {i + 1}/{eval_size}")
            raw = dataset[idx]["rejected"]
            raw_responses.append(raw)
            transformed = pipeline.apply(raw, rng=pipeline_rng)
            pipeline_responses.append(transformed)
    else:
        cache = _load_cache()
        questions = [dataset[idx]["prompt"] for idx in eval_indices]
        cached_count = sum(1 for q in questions if _cache_key(q) in cache)
        print(f"Cache: {cached_count}/{eval_size} responses cached.")

        for i, (idx, question) in enumerate(zip(eval_indices, questions)):
            if (i + 1) % 50 == 0:
                print(f"  Progress: {i + 1}/{eval_size}")
            raw = generate_claude_response(question, cache, model=claude_model)
            raw_responses.append(raw)
            transformed = pipeline.apply(raw, rng=pipeline_rng)
            pipeline_responses.append(transformed)

    # -----------------------------------------------------------------------
    # Also measure human-like test responses (for Wasserstein distance)
    # -----------------------------------------------------------------------
    humanlike_responses: list[str] = []
    if holdout:
        for idx in eval_indices:
            humanlike_responses.append(dataset[idx]["chosen"])

    # -----------------------------------------------------------------------
    # Measure metrics
    # -----------------------------------------------------------------------
    print("Measuring metrics...")
    raw_metrics_list = [measure_all_metrics(r) for r in raw_responses]
    pipeline_metrics_list = [measure_all_metrics(r) for r in pipeline_responses]
    humanlike_metrics_list = (
        [measure_all_metrics(r) for r in humanlike_responses]
        if humanlike_responses else []
    )

    # -----------------------------------------------------------------------
    # Compute means, CIs, scores
    # -----------------------------------------------------------------------
    print("Computing statistics...")
    raw_means: dict[str, float] = {}
    pipeline_means: dict[str, float] = {}
    pipeline_cis: dict[str, tuple[float, float, float]] = {}
    pipeline_wasserstein: dict[str, float] = {}
    raw_scores: dict[str, float] = {}
    pipeline_scores: dict[str, float] = {}

    for metric in METRIC_NAMES:
        raw_vals = np.array([m[metric] for m in raw_metrics_list])
        pipe_vals = np.array([m[metric] for m in pipeline_metrics_list])

        raw_means[metric] = float(np.mean(raw_vals))
        pipeline_means[metric] = float(np.mean(pipe_vals))

        # Bootstrap CI for pipeline mean
        mean, lo, hi = bootstrap_ci(pipe_vals)
        pipeline_cis[metric] = (mean, lo, hi)

        # Wasserstein distance (pipeline vs human-like)
        if humanlike_metrics_list:
            hl_vals = np.array([m[metric] for m in humanlike_metrics_list])
            pipeline_wasserstein[metric] = float(wasserstein_distance(pipe_vals, hl_vals))

        # Scores
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

    raw_overall = compute_overall_score(raw_scores, weights)
    pipeline_overall = compute_overall_score(pipeline_scores, weights)

    # Bootstrap CI for overall score
    print("Computing bootstrap CI for overall score...")
    bootstrap_rng = np.random.RandomState(SEED)
    overall_boots = np.empty(BOOTSTRAP_N)
    n_eval = len(pipeline_metrics_list)
    for b in range(BOOTSTRAP_N):
        boot_idx = bootstrap_rng.randint(0, n_eval, size=n_eval)
        boot_scores: dict[str, float] = {}
        for metric in METRIC_NAMES:
            boot_vals = np.array([pipeline_metrics_list[i][metric] for i in boot_idx])
            boot_mean = float(np.mean(boot_vals))
            boot_scores[metric] = compute_score(
                boot_mean,
                ref[metric]["formal_mean"],
                ref[metric]["humanlike_mean"],
            )
        overall_boots[b] = compute_overall_score(boot_scores, weights)
    overall_ci = (
        float(pipeline_overall),
        float(np.percentile(overall_boots, 2.5)),
        float(np.percentile(overall_boots, 97.5)),
    )

    # -----------------------------------------------------------------------
    # Wasserstein-based scoring & KS tests
    # -----------------------------------------------------------------------
    wass_scores: dict[str, float] = {}
    ks_results: dict[str, dict[str, float]] = {}
    wass_overall: float | None = None
    wass_overall_ci: tuple[float, float, float] | None = None

    if humanlike_metrics_list:
        from scipy.stats import ks_2samp

        print("Computing Wasserstein-based scores and KS tests...")
        for metric in METRIC_NAMES:
            pipe_vals = np.array([m[metric] for m in pipeline_metrics_list])
            hl_vals = np.array([m[metric] for m in humanlike_metrics_list])
            formal_vals = np.array([m[metric] for m in raw_metrics_list])

            # KS test
            ks_stat, ks_p = ks_2samp(pipe_vals, hl_vals)
            ks_results[metric] = {"ks_stat": float(ks_stat), "p_value": float(ks_p)}

            # Wasserstein-based score
            w_formal = float(wasserstein_distance(formal_vals, hl_vals))
            w_pipe = float(wasserstein_distance(pipe_vals, hl_vals))
            if w_formal > 1e-9:
                wass_scores[metric] = max(0.0, 1.0 - w_pipe / w_formal)
            else:
                wass_scores[metric] = 1.0

        wass_overall = compute_overall_score(wass_scores, weights)

        # Bootstrap CI for Wasserstein overall
        print("Computing bootstrap CI for Wasserstein overall score...")
        wass_boots = np.empty(BOOTSTRAP_N)
        for b in range(BOOTSTRAP_N):
            boot_idx = bootstrap_rng.randint(0, n_eval, size=n_eval)
            boot_wass: dict[str, float] = {}
            for metric in METRIC_NAMES:
                boot_pipe = np.array([pipeline_metrics_list[i][metric] for i in boot_idx])
                boot_hl = np.array([humanlike_metrics_list[i][metric] for i in boot_idx])
                boot_formal = np.array([raw_metrics_list[i][metric] for i in boot_idx])
                w_f = float(wasserstein_distance(boot_formal, boot_hl))
                w_p = float(wasserstein_distance(boot_pipe, boot_hl))
                boot_wass[metric] = max(0.0, 1.0 - w_p / w_f) if w_f > 1e-9 else 1.0
            wass_boots[b] = compute_overall_score(boot_wass, weights)
        wass_overall_ci = (
            float(wass_overall),
            float(np.percentile(wass_boots, 2.5)),
            float(np.percentile(wass_boots, 97.5)),
        )

    # -----------------------------------------------------------------------
    # Output results
    # -----------------------------------------------------------------------
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    report = generate_report(
        raw_means, pipeline_means, raw_scores, pipeline_scores,
        raw_overall, pipeline_overall, ref, weights, eval_size, model_label,
        pipeline_cis, pipeline_wasserstein, overall_ci, holdout,
        wass_scores=wass_scores or None,
        wass_overall=wass_overall,
        wass_overall_ci=wass_overall_ci,
        ks_results=ks_results or None,
    )
    report_path = RESULTS_DIR / "benchmark_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"\nReport: {report_path}")

    # Remove numpy arrays from ref before serializing
    ref_serializable = {}
    for metric, data in ref.items():
        ref_serializable[metric] = {
            k: v for k, v in data.items()
            if not isinstance(v, np.ndarray)
        }

    scorecard = generate_scorecard(
        raw_means, pipeline_means, raw_scores, pipeline_scores,
        raw_overall, pipeline_overall, ref_serializable, weights,
        eval_size, model_label,
        pipeline_cis, pipeline_wasserstein, overall_ci, holdout,
    )
    # Add Wasserstein and KS data to scorecard
    if wass_overall is not None:
        scorecard["wasserstein_overall"] = {
            "score": round(wass_overall, 4),
        }
        if wass_overall_ci:
            scorecard["wasserstein_overall"]["ci_95"] = [
                round(wass_overall_ci[1], 4), round(wass_overall_ci[2], 4)
            ]
        scorecard["wasserstein_scores"] = {
            m: round(s, 4) for m, s in wass_scores.items()
        }
    if ks_results:
        scorecard["ks_tests"] = {
            m: {"ks_stat": round(v["ks_stat"], 4), "p_value": round(v["p_value"], 6),
                "pass": v["p_value"] >= 0.05}
            for m, v in ks_results.items()
        }
    scorecard_path = RESULTS_DIR / "scorecard.json"
    scorecard_path.write_text(
        json.dumps(scorecard, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Scorecard: {scorecard_path}")

    # -----------------------------------------------------------------------
    # Print summary
    # -----------------------------------------------------------------------
    print(f"\n{'='*72}")
    print("BENCHMARK RESULTS (v2 — Scientifically Rigorous)")
    print(f"{'='*72}")
    print(f"Evaluation: {'Held-out 80/20' if holdout else 'Full dataset (self-referential)'}")
    print(f"{'Metric':<22} {'Raw':>8} {'Pipeline':>10} {'Target':>8} {'Score':>7} {'95% CI':>16} {'Weight':>7}")
    print(f"{'-'*72}")
    for metric in METRIC_NAMES:
        ci_str = ""
        if metric in pipeline_cis:
            _, lo, hi = pipeline_cis[metric]
            ci_str = f"[{lo:.3f}, {hi:.3f}]"
        print(
            f"{METRIC_LABELS[metric]:<22} "
            f"{raw_means[metric]:>8.4f} "
            f"{pipeline_means[metric]:>10.4f} "
            f"{ref[metric]['humanlike_mean']:>8.4f} "
            f"{pipeline_scores[metric]:>7.3f} "
            f"{ci_str:>16} "
            f"{weights[metric]:>7.2f}"
        )
    print(f"{'-'*72}")
    print(f"{'Overall (Raw)':<22} {raw_overall:>49.3f}")
    print(f"{'Overall (+Pipeline)':<22} {pipeline_overall:>49.3f}")
    if overall_ci:
        _, lo, hi = overall_ci
        print(f"{'Overall 95% CI':<22} {'':>33}[{lo:.3f}, {hi:.3f}]")
    improvement = pipeline_overall - raw_overall
    print(f"{'Improvement':<22} {improvement:>+49.3f}")

    if wass_overall is not None:
        print(f"\n{'='*72}")
        print("DUAL-SCORE SUMMARY")
        print(f"{'='*72}")
        wass_ci_str = ""
        if wass_overall_ci:
            _, wlo, whi = wass_overall_ci
            wass_ci_str = f"  95% CI [{wlo:.3f}, {whi:.3f}]"
        mean_ci_str = ""
        if overall_ci:
            _, mlo, mhi = overall_ci
            mean_ci_str = f"  95% CI [{mlo:.3f}, {mhi:.3f}]"
        print(f"  Mean Alignment:         {pipeline_overall:.3f}{mean_ci_str}")
        print(f"  Distribution Alignment: {wass_overall:.3f}{wass_ci_str}")
        print(f"  Gap:                    {pipeline_overall - wass_overall:+.3f}")

    if ks_results:
        ks_pass = sum(1 for v in ks_results.values() if v["p_value"] >= 0.05)
        print(f"\n  KS test: {ks_pass}/{len(ks_results)} pass")
        for metric in METRIC_NAMES:
            if metric in ks_results:
                ks = ks_results[metric]
                verdict = "PASS" if ks["p_value"] >= 0.05 else "FAIL"
                print(f"    {METRIC_LABELS[metric]:<22} stat={ks['ks_stat']:.3f}  p={ks['p_value']:.4e}  {verdict}")


if __name__ == "__main__":
    main()

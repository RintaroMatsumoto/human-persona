"""
Ablation Study — human-persona benchmark pipeline

Measures each pipeline step's individual contribution to the overall score by
running the benchmark with each step disabled one at a time.

Variants:
  0. No pipeline       — raw input, no transformation
  1. Full pipeline     — all 6 steps enabled (baseline reference)
  2. No sentence split — step 1 disabled
  3. No cushion        — step 2 disabled
  4. No filler         — step 3 disabled
  5. No hedge          — step 4 disabled
  6. No self-correction — step 5 disabled
  7. No interjections  — step 6 disabled

Usage:
    python3 -m benchmarks.ablation_study
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import wasserstein_distance

from benchmarks.dpo_benchmark import (
    HumanPersonaPipeline,
    METRIC_NAMES,
    SAMPLE_SIZE,
    SEED,
    TRAIN_RATIO,
    compute_reference_from_split,
    compute_metric_weights,
    compute_score,
    compute_overall_score,
    measure_all_metrics,
    split_sentences,
    _lowercase_first,
)

RESULTS_DIR = Path(__file__).parent / "results"


# ---------------------------------------------------------------------------
# Ablation subclasses — each disables exactly one pipeline step
# ---------------------------------------------------------------------------

class NoPipelinePipeline(HumanPersonaPipeline):
    """Baseline: returns text unchanged."""

    def apply(self, text: str, rng: random.Random | None = None) -> str:
        return text


class NoSentenceSplitPipeline(HumanPersonaPipeline):
    """Step 1 disabled: skip _split_long_sentences."""

    def apply(self, text: str, rng: random.Random | None = None) -> str:
        rng = rng or random.Random()
        result = text  # Step 1 SKIPPED

        # Step 2: cushion injection
        if rng.random() < self._cushion_rate:
            cushion = rng.choice(self._cushions)
            result = cushion + _lowercase_first(result) if result else result

        # Step 3: filler insertion
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

        # Step 4: hedge injection
        sentences = split_sentences(result)
        if sentences:
            new_sentences = []
            for sent in sentences:
                if rng.random() < self._hedge_prob:
                    hedge = rng.choice(self._hedges)
                    sent = hedge + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # Step 5: self-correction injection
        sentences = split_sentences(result)
        if len(sentences) >= 2:
            new_sentences = [sentences[0]]
            for sent in sentences[1:]:
                if rng.random() < self._self_correction_rate:
                    correction = rng.choice(self._corrections)
                    sent = correction + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # Step 6: short interjection insertion
        result = self._inject_short_interjections(result, rng)

        return result


class NoCushionPipeline(HumanPersonaPipeline):
    """Step 2 disabled: skip cushion injection."""

    def apply(self, text: str, rng: random.Random | None = None) -> str:
        rng = rng or random.Random()

        # Step 1: sentence splitting
        result = self._split_long_sentences(text, rng)

        # Step 2: cushion injection SKIPPED

        # Step 3: filler insertion
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

        # Step 4: hedge injection
        sentences = split_sentences(result)
        if sentences:
            new_sentences = []
            for sent in sentences:
                if rng.random() < self._hedge_prob:
                    hedge = rng.choice(self._hedges)
                    sent = hedge + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # Step 5: self-correction injection
        sentences = split_sentences(result)
        if len(sentences) >= 2:
            new_sentences = [sentences[0]]
            for sent in sentences[1:]:
                if rng.random() < self._self_correction_rate:
                    correction = rng.choice(self._corrections)
                    sent = correction + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # Step 6: short interjection insertion
        result = self._inject_short_interjections(result, rng)

        return result


class NoFillerPipeline(HumanPersonaPipeline):
    """Step 3 disabled: skip filler insertion."""

    def apply(self, text: str, rng: random.Random | None = None) -> str:
        rng = rng or random.Random()

        # Step 1: sentence splitting
        result = self._split_long_sentences(text, rng)

        # Step 2: cushion injection
        if rng.random() < self._cushion_rate:
            cushion = rng.choice(self._cushions)
            result = cushion + _lowercase_first(result) if result else result

        # Step 3: filler insertion SKIPPED

        # Step 4: hedge injection
        sentences = split_sentences(result)
        if sentences:
            new_sentences = []
            for sent in sentences:
                if rng.random() < self._hedge_prob:
                    hedge = rng.choice(self._hedges)
                    sent = hedge + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # Step 5: self-correction injection
        sentences = split_sentences(result)
        if len(sentences) >= 2:
            new_sentences = [sentences[0]]
            for sent in sentences[1:]:
                if rng.random() < self._self_correction_rate:
                    correction = rng.choice(self._corrections)
                    sent = correction + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # Step 6: short interjection insertion
        result = self._inject_short_interjections(result, rng)

        return result


class NoHedgePipeline(HumanPersonaPipeline):
    """Step 4 disabled: skip hedge injection."""

    def apply(self, text: str, rng: random.Random | None = None) -> str:
        rng = rng or random.Random()

        # Step 1: sentence splitting
        result = self._split_long_sentences(text, rng)

        # Step 2: cushion injection
        if rng.random() < self._cushion_rate:
            cushion = rng.choice(self._cushions)
            result = cushion + _lowercase_first(result) if result else result

        # Step 3: filler insertion
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

        # Step 4: hedge injection SKIPPED

        # Step 5: self-correction injection
        sentences = split_sentences(result)
        if len(sentences) >= 2:
            new_sentences = [sentences[0]]
            for sent in sentences[1:]:
                if rng.random() < self._self_correction_rate:
                    correction = rng.choice(self._corrections)
                    sent = correction + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # Step 6: short interjection insertion
        result = self._inject_short_interjections(result, rng)

        return result


class NoSelfCorrectionPipeline(HumanPersonaPipeline):
    """Step 5 disabled: skip self-correction injection."""

    def apply(self, text: str, rng: random.Random | None = None) -> str:
        rng = rng or random.Random()

        # Step 1: sentence splitting
        result = self._split_long_sentences(text, rng)

        # Step 2: cushion injection
        if rng.random() < self._cushion_rate:
            cushion = rng.choice(self._cushions)
            result = cushion + _lowercase_first(result) if result else result

        # Step 3: filler insertion
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

        # Step 4: hedge injection
        sentences = split_sentences(result)
        if sentences:
            new_sentences = []
            for sent in sentences:
                if rng.random() < self._hedge_prob:
                    hedge = rng.choice(self._hedges)
                    sent = hedge + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # Step 5: self-correction injection SKIPPED

        # Step 6: short interjection insertion
        result = self._inject_short_interjections(result, rng)

        return result


class NoInterjectionPipeline(HumanPersonaPipeline):
    """Step 6 disabled: skip _inject_short_interjections."""

    def apply(self, text: str, rng: random.Random | None = None) -> str:
        rng = rng or random.Random()

        # Step 1: sentence splitting
        result = self._split_long_sentences(text, rng)

        # Step 2: cushion injection
        if rng.random() < self._cushion_rate:
            cushion = rng.choice(self._cushions)
            result = cushion + _lowercase_first(result) if result else result

        # Step 3: filler insertion
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

        # Step 4: hedge injection
        sentences = split_sentences(result)
        if sentences:
            new_sentences = []
            for sent in sentences:
                if rng.random() < self._hedge_prob:
                    hedge = rng.choice(self._hedges)
                    sent = hedge + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # Step 5: self-correction injection
        sentences = split_sentences(result)
        if len(sentences) >= 2:
            new_sentences = [sentences[0]]
            for sent in sentences[1:]:
                if rng.random() < self._self_correction_rate:
                    correction = rng.choice(self._corrections)
                    sent = correction + _lowercase_first(sent)
                new_sentences.append(sent)
            result = " ".join(new_sentences)

        # Step 6: short interjection insertion SKIPPED

        return result


# ---------------------------------------------------------------------------
# Variant registry
# ---------------------------------------------------------------------------

VARIANTS: list[tuple[str, type]] = [
    ("No Pipeline (baseline)",    NoPipelinePipeline),
    ("Full Pipeline",             HumanPersonaPipeline),
    ("No Sentence Split (step 1)", NoSentenceSplitPipeline),
    ("No Cushion (step 2)",       NoCushionPipeline),
    ("No Filler (step 3)",        NoFillerPipeline),
    ("No Hedge (step 4)",         NoHedgePipeline),
    ("No Self-Correction (step 5)", NoSelfCorrectionPipeline),
    ("No Interjections (step 6)", NoInterjectionPipeline),
]


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

def _compute_wasserstein_overall(
    variant_metrics: list[dict[str, float]],
    humanlike_metrics: list[dict[str, float]],
    raw_metrics: list[dict[str, float]],
    weights: dict[str, float],
) -> tuple[float, dict[str, float]]:
    """Compute Wasserstein-based overall score for a variant.

    Score per metric = 1 - W(variant, human) / W(raw, human).
    Returns (overall_score, per_metric_scores).
    """
    wass_scores: dict[str, float] = {}
    for metric in METRIC_NAMES:
        variant_vals = np.array([m[metric] for m in variant_metrics])
        hl_vals      = np.array([m[metric] for m in humanlike_metrics])
        raw_vals     = np.array([m[metric] for m in raw_metrics])
        w_raw  = float(wasserstein_distance(raw_vals, hl_vals))
        w_var  = float(wasserstein_distance(variant_vals, hl_vals))
        if w_raw > 1e-9:
            wass_scores[metric] = max(0.0, 1.0 - w_var / w_raw)
        else:
            wass_scores[metric] = 1.0
    overall = compute_overall_score(wass_scores, weights)
    return overall, wass_scores


def _compute_mean_overall(
    variant_metrics: list[dict[str, float]],
    ref: dict[str, dict[str, Any]],
    weights: dict[str, float],
) -> tuple[float, dict[str, float]]:
    """Compute mean-alignment overall score for a variant.

    Returns (overall_score, per_metric_scores).
    """
    means: dict[str, float] = {
        metric: float(np.mean([m[metric] for m in variant_metrics]))
        for metric in METRIC_NAMES
    }
    scores: dict[str, float] = {
        metric: compute_score(
            means[metric],
            ref[metric]["formal_mean"],
            ref[metric]["humanlike_mean"],
        )
        for metric in METRIC_NAMES
    }
    overall = compute_overall_score(scores, weights)
    return overall, scores


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    from datasets import load_dataset

    print("=" * 72)
    print("ABLATION STUDY — human-persona benchmark pipeline")
    print("=" * 72)

    # -----------------------------------------------------------------------
    # Load dataset
    # -----------------------------------------------------------------------
    print("\nLoading HumanLLMs/Human-Like-DPO-Dataset...")
    dataset = load_dataset("HumanLLMs/Human-Like-DPO-Dataset", split="train")
    n_total = len(dataset)
    print(f"Loaded {n_total:,} samples.")

    # -----------------------------------------------------------------------
    # 80/20 holdout split (same logic as dpo_benchmark.py)
    # -----------------------------------------------------------------------
    rng_split = random.Random(SEED)
    all_indices = list(range(n_total))
    rng_split.shuffle(all_indices)

    n_train = int(n_total * TRAIN_RATIO)
    train_indices = all_indices[:n_train]
    test_indices  = all_indices[n_train:]
    eval_size     = min(SAMPLE_SIZE, len(test_indices))
    eval_indices  = test_indices[:eval_size]

    print(f"Hold-out split: {n_train:,} train / {len(test_indices):,} test")
    print(f"Evaluating on {eval_size} held-out test samples (seed={SEED}).")

    # -----------------------------------------------------------------------
    # Reference statistics from TRAIN split (computed once, reused for all)
    # -----------------------------------------------------------------------
    print(f"\nComputing reference statistics from {n_train:,} train samples...")
    ref = compute_reference_from_split(dataset, train_indices)
    weights = compute_metric_weights(ref)
    print(f"Metric weights: {json.dumps(weights)}")

    # -----------------------------------------------------------------------
    # Pre-load raw texts (shared across all variants)
    # -----------------------------------------------------------------------
    print("\nLoading raw texts for eval split...")
    raw_texts: list[str] = [dataset[idx]["rejected"] for idx in eval_indices]
    humanlike_texts: list[str] = [dataset[idx]["chosen"] for idx in eval_indices]

    # -----------------------------------------------------------------------
    # Measure raw and human-like metrics once (reused for Wasserstein baseline)
    # -----------------------------------------------------------------------
    print("Measuring raw metrics...")
    raw_metrics_list: list[dict[str, float]] = [measure_all_metrics(t) for t in raw_texts]
    print("Measuring human-like metrics...")
    humanlike_metrics_list: list[dict[str, float]] = [measure_all_metrics(t) for t in humanlike_texts]

    # -----------------------------------------------------------------------
    # Run each variant
    # -----------------------------------------------------------------------
    results: list[dict[str, Any]] = []

    full_pipeline_mean_overall: float | None = None
    full_pipeline_wass_overall: float | None = None

    for variant_name, pipeline_cls in VARIANTS:
        print(f"\n[{variant_name}] Running...")
        pipeline = pipeline_cls()

        # Use same seed for every variant so RNG differences are isolated
        pipeline_rng = random.Random(SEED)

        if variant_name == "No Pipeline (baseline)":
            # No-pipeline: just use raw texts
            transformed_texts = raw_texts
        else:
            transformed_texts = [
                pipeline.apply(text, rng=pipeline_rng)
                for text in raw_texts
            ]

        # Measure metrics for this variant
        variant_metrics = [measure_all_metrics(t) for t in transformed_texts]

        # Mean-based overall score
        mean_overall, mean_scores = _compute_mean_overall(variant_metrics, ref, weights)

        # Wasserstein-based overall score
        wass_overall, wass_scores = _compute_wasserstein_overall(
            variant_metrics, humanlike_metrics_list, raw_metrics_list, weights
        )

        result: dict[str, Any] = {
            "variant": variant_name,
            "mean_overall": round(mean_overall, 4),
            "wass_overall": round(wass_overall, 4),
            "mean_scores": {m: round(v, 4) for m, v in mean_scores.items()},
            "wass_scores":  {m: round(v, 4) for m, v in wass_scores.items()},
        }
        results.append(result)

        if variant_name == "Full Pipeline":
            full_pipeline_mean_overall = mean_overall
            full_pipeline_wass_overall = wass_overall

        print(f"  Mean Alignment:         {mean_overall:.4f}")
        print(f"  Distribution Alignment: {wass_overall:.4f}")

    # -----------------------------------------------------------------------
    # Compute deltas vs full pipeline
    # -----------------------------------------------------------------------
    assert full_pipeline_mean_overall is not None
    assert full_pipeline_wass_overall is not None

    for r in results:
        r["delta_mean"] = round(r["mean_overall"] - full_pipeline_mean_overall, 4)
        r["delta_wass"] = round(r["wass_overall"] - full_pipeline_wass_overall, 4)

    # -----------------------------------------------------------------------
    # Print comparison table
    # -----------------------------------------------------------------------
    col_w = 30
    print(f"\n{'=' * 72}")
    print("ABLATION STUDY RESULTS")
    print(f"{'=' * 72}")
    print(
        f"{'Variant':<{col_w}}  {'Mean Align':>10}  {'Dist Align':>10}  "
        f"{'Δ Mean':>8}  {'Δ Dist':>8}"
    )
    print("-" * 72)
    for r in results:
        marker = " <-- full" if r["variant"] == "Full Pipeline" else ""
        print(
            f"{r['variant']:<{col_w}}  {r['mean_overall']:>10.4f}  "
            f"{r['wass_overall']:>10.4f}  "
            f"{r['delta_mean']:>+8.4f}  {r['delta_wass']:>+8.4f}{marker}"
        )
    print("-" * 72)

    # -----------------------------------------------------------------------
    # Save results JSON
    # -----------------------------------------------------------------------
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    output: dict[str, Any] = {
        "version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": SEED,
        "eval_size": eval_size,
        "train_size": n_train,
        "metric_weights": weights,
        "full_pipeline_mean_overall": round(full_pipeline_mean_overall, 4),
        "full_pipeline_wass_overall": round(full_pipeline_wass_overall, 4),
        "variants": results,
    }
    out_path = RESULTS_DIR / "ablation_results.json"
    out_path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nResults saved to: {out_path}")


if __name__ == "__main__":
    main()

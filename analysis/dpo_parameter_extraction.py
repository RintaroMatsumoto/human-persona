"""
DPO Dataset Parameter Extraction — Phase B

Extracts 6 language-agnostic structural metrics from the HumanLLMs/Human-Like-DPO-Dataset
to calibrate human-persona config/schema.json base parameters with empirical values.

Metrics:
    1. sentence_length_variance (CV of sentence lengths)
    2. hedge_probability (hedging expressions per sentence)
    3. self_correction_rate (self-correction markers per sentence)
    4. verbosity (words per sentence + Flesch Reading Ease)
    5. cushion_rate (soft opening vs direct answer)
    6. filler_rate (filler/discourse markers per sentence)

Data source: HumanLLMs/Human-Like-DPO-Dataset (10,884 samples)
"""

from __future__ import annotations

import json
import re
import statistics
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

try:
    import textstat
    HAS_TEXTSTAT = True
except ImportError:
    HAS_TEXTSTAT = False


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

HEDGE_PATTERNS = [
    r"\bprobably\b", r"\bmaybe\b", r"\bi think\b", r"\bmight\b",
    r"\bperhaps\b", r"\blikely\b", r"\bi guess\b", r"\bsort of\b",
    r"\bkind of\b", r"\bseems like\b", r"\bi believe\b", r"\bnot sure\b",
    r"\bpossibly\b", r"\bi suppose\b", r"\baround\b", r"\bapproximately\b",
    r"\broughly\b", r"\bmore or less\b",
]

SELF_CORRECTION_PATTERNS = [
    r"\bactually\b", r"\bi mean\b", r"\bwell,", r"\bsorry,",
    r"\blet me rephrase\b", r"\bcorrection\b", r"\bwait,", r"\bno,",
    r"\brather,",
]

FILLER_PATTERNS = [
    r"\bwell\b", r"\bso\b", r"\byou know\b", r"\bi mean\b", r"\blike\b",
    r"\bbasically\b", r"\bactually\b", r"\bhonestly\b", r"\bright\b",
    r"\bokay\b",
]

CUSHION_PATTERNS = [
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
# Metric extractors
# ---------------------------------------------------------------------------

def calc_sentence_length_variance(text: str) -> float | None:
    """Calculate coefficient of variation of sentence lengths (chars)."""
    sentences = split_sentences(text)
    if len(sentences) < 2:
        return None
    lengths = [len(s) for s in sentences]
    mean = statistics.mean(lengths)
    if mean == 0:
        return None
    return statistics.stdev(lengths) / mean


def calc_hedge_rate(text: str) -> float:
    """Calculate hedging expression rate (per sentence)."""
    sentences = split_sentences(text)
    if not sentences:
        return 0.0
    matches = count_pattern_matches(text, HEDGE_PATTERNS)
    return matches / len(sentences)


def calc_self_correction_rate(text: str) -> float:
    """Calculate self-correction marker rate (per sentence)."""
    sentences = split_sentences(text)
    if not sentences:
        return 0.0
    matches = count_pattern_matches(text, SELF_CORRECTION_PATTERNS)
    return matches / len(sentences)


def calc_verbosity(text: str) -> dict[str, float]:
    """Calculate verbosity metrics: words per sentence + Flesch score."""
    sentences = split_sentences(text)
    if not sentences:
        return {"words_per_sentence": 0.0, "flesch_reading_ease": 0.0}

    wps = word_count(text) / len(sentences)
    fre = textstat.flesch_reading_ease(text) if HAS_TEXTSTAT else 0.0
    return {"words_per_sentence": wps, "flesch_reading_ease": fre}


def calc_cushion_rate(text: str) -> bool:
    """Check if response opens with a cushion expression."""
    sentences = split_sentences(text)
    if not sentences:
        return False
    first = sentences[0].lower()
    return any(re.search(p, first) for p in CUSHION_PATTERNS)


def calc_filler_rate(text: str) -> float:
    """Calculate filler/discourse marker rate (per sentence)."""
    sentences = split_sentences(text)
    if not sentences:
        return 0.0
    matches = count_pattern_matches(text, FILLER_PATTERNS)
    return matches / len(sentences)


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyze_dataset(dataset) -> dict[str, Any]:
    """Run all 6 metrics on the full dataset.

    Args:
        dataset: HuggingFace dataset with 'chosen' and 'rejected' columns.

    Returns:
        Dictionary with metric arrays for both human-like and formal responses.
    """
    results = {
        "human": {
            "sentence_length_cv": [],
            "hedge_rate": [],
            "self_correction_rate": [],
            "words_per_sentence": [],
            "flesch_reading_ease": [],
            "cushion": [],
            "filler_rate": [],
        },
        "formal": {
            "sentence_length_cv": [],
            "hedge_rate": [],
            "self_correction_rate": [],
            "words_per_sentence": [],
            "flesch_reading_ease": [],
            "cushion": [],
            "filler_rate": [],
        },
    }

    for sample in dataset:
        chosen = sample["chosen"]
        rejected = sample["rejected"]

        for text, key in [(chosen, "human"), (rejected, "formal")]:
            cv = calc_sentence_length_variance(text)
            if cv is not None:
                results[key]["sentence_length_cv"].append(cv)

            results[key]["hedge_rate"].append(calc_hedge_rate(text))
            results[key]["self_correction_rate"].append(calc_self_correction_rate(text))

            verb = calc_verbosity(text)
            results[key]["words_per_sentence"].append(verb["words_per_sentence"])
            results[key]["flesch_reading_ease"].append(verb["flesch_reading_ease"])

            results[key]["cushion"].append(1.0 if calc_cushion_rate(text) else 0.0)
            results[key]["filler_rate"].append(calc_filler_rate(text))

    return results


def compute_statistics(results: dict[str, Any]) -> dict[str, Any]:
    """Compute summary statistics and t-tests for all metrics."""
    metrics = [
        "sentence_length_cv", "hedge_rate", "self_correction_rate",
        "words_per_sentence", "flesch_reading_ease", "cushion", "filler_rate",
    ]

    summary = {}
    for metric in metrics:
        human_vals = np.array(results["human"][metric])
        formal_vals = np.array(results["formal"][metric])

        t_stat, p_value = stats.ttest_ind(human_vals, formal_vals, equal_var=False)

        summary[metric] = {
            "human_mean": float(np.mean(human_vals)),
            "human_std": float(np.std(human_vals)),
            "human_median": float(np.median(human_vals)),
            "formal_mean": float(np.mean(formal_vals)),
            "formal_std": float(np.std(formal_vals)),
            "formal_median": float(np.median(formal_vals)),
            "t_statistic": float(t_stat),
            "p_value": float(p_value),
            "n_human": len(human_vals),
            "n_formal": len(formal_vals),
            "human_ci_95": (
                float(np.mean(human_vals) - 1.96 * np.std(human_vals) / np.sqrt(len(human_vals))),
                float(np.mean(human_vals) + 1.96 * np.std(human_vals) / np.sqrt(len(human_vals))),
            ),
        }

    return summary


def generate_recommended_params(summary: dict[str, Any]) -> dict[str, Any]:
    """Generate recommended schema.json parameter values from analysis."""
    h_cv = summary["sentence_length_cv"]["human_mean"]
    h_cv_std = summary["sentence_length_cv"]["human_std"]

    return {
        "sentence_length_variance": {
            "min_ratio": round(max(0.1, 1.0 - h_cv - h_cv_std), 2),
            "max_ratio": round(1.0 + h_cv + h_cv_std, 2),
        },
        "hedge_probability": round(summary["hedge_rate"]["human_mean"], 4),
        "self_correction_rate": round(summary["self_correction_rate"]["human_mean"], 4),
        "verbosity_human_avg": round(summary["words_per_sentence"]["human_mean"], 2),
        "verbosity_formal_avg": round(summary["words_per_sentence"]["formal_mean"], 2),
        "cushion_rate_human": round(summary["cushion"]["human_mean"], 4),
        "cushion_rate_formal": round(summary["cushion"]["formal_mean"], 4),
        "filler_rate_human": round(summary["filler_rate"]["human_mean"], 4),
        "filler_rate_formal": round(summary["filler_rate"]["formal_mean"], 4),
    }


def generate_report(summary: dict[str, Any], params: dict[str, Any]) -> str:
    """Generate markdown analysis report."""
    lines = [
        "# DPO Dataset Parameter Analysis Report",
        "",
        "**Data source:** HumanLLMs/Human-Like-DPO-Dataset (HuggingFace)",
        f"**Samples:** {summary['hedge_rate']['n_human']:,} (Human-Like) / "
        f"{summary['hedge_rate']['n_formal']:,} (Formal)",
        f"**Date:** Auto-generated by dpo_parameter_extraction.py",
        "",
        "---",
        "",
        "## Summary Table",
        "",
        "| Metric | Human-Like (mean) | Formal (mean) | Δ | p-value | Significant? |",
        "|--------|-------------------|---------------|---|---------|-------------|",
    ]

    metric_names = {
        "sentence_length_cv": "Sentence Length CV",
        "hedge_rate": "Hedge Rate (per sent)",
        "self_correction_rate": "Self-Correction Rate",
        "words_per_sentence": "Words per Sentence",
        "flesch_reading_ease": "Flesch Reading Ease",
        "cushion": "Cushion Rate",
        "filler_rate": "Filler Rate (per sent)",
    }

    for metric, label in metric_names.items():
        s = summary[metric]
        delta = s["human_mean"] - s["formal_mean"]
        sig = "Yes" if s["p_value"] < 0.05 else "No"
        p_str = f"{s['p_value']:.2e}" if s["p_value"] < 0.001 else f"{s['p_value']:.4f}"
        lines.append(
            f"| {label} | {s['human_mean']:.4f} | {s['formal_mean']:.4f} | "
            f"{delta:+.4f} | {p_str} | {sig} |"
        )

    lines += [
        "",
        "---",
        "",
        "## Detailed Metrics",
        "",
    ]

    for metric, label in metric_names.items():
        s = summary[metric]
        ci_lo, ci_hi = s["human_ci_95"]
        lines += [
            f"### {label}",
            "",
            f"- **Human-Like:** mean={s['human_mean']:.4f}, std={s['human_std']:.4f}, "
            f"median={s['human_median']:.4f}",
            f"- **Formal:** mean={s['formal_mean']:.4f}, std={s['formal_std']:.4f}, "
            f"median={s['formal_median']:.4f}",
            f"- **95% CI (Human-Like mean):** [{ci_lo:.4f}, {ci_hi:.4f}]",
            f"- **t-statistic:** {s['t_statistic']:.4f}, **p-value:** {s['p_value']:.2e}",
            "",
        ]

    lines += [
        "---",
        "",
        "## Recommended Parameters",
        "",
        "```json",
        json.dumps(params, indent=2),
        "```",
        "",
        "These values are derived from the Human-Like response distribution and can be",
        "used to calibrate config/schema.json defaults.",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    from datasets import load_dataset

    print("Loading HumanLLMs/Human-Like-DPO-Dataset...")
    dataset = load_dataset("HumanLLMs/Human-Like-DPO-Dataset", split="train")
    print(f"Loaded {len(dataset):,} samples.")

    print("Analyzing all samples (6 metrics)...")
    results = analyze_dataset(dataset)

    print("Computing statistics...")
    summary = compute_statistics(results)

    print("Generating recommended parameters...")
    params = generate_recommended_params(summary)

    # Write results
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    report = generate_report(summary, params)
    report_path = results_dir / "dpo_analysis_report.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Report written to {report_path}")

    params_path = results_dir / "recommended_params.json"
    params_path.write_text(json.dumps(params, indent=2) + "\n", encoding="utf-8")
    print(f"Parameters written to {params_path}")

    # Also dump full summary for debugging
    summary_path = results_dir / "full_statistics.json"

    def _serialize(obj):
        if isinstance(obj, tuple):
            return list(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        raise TypeError(f"Not serializable: {type(obj)}")

    summary_path.write_text(
        json.dumps(summary, indent=2, default=_serialize) + "\n",
        encoding="utf-8",
    )
    print(f"Full statistics written to {summary_path}")

    # Print summary
    print("\n=== RESULTS ===")
    for metric, data in summary.items():
        print(f"\n{metric}:")
        print(f"  Human-Like: {data['human_mean']:.4f} (±{data['human_std']:.4f})")
        print(f"  Formal:     {data['formal_mean']:.4f} (±{data['formal_std']:.4f})")
        print(f"  p-value:    {data['p_value']:.2e}")

    print("\n=== RECOMMENDED PARAMS ===")
    print(json.dumps(params, indent=2))


if __name__ == "__main__":
    main()

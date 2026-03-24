"""
Japanese Parameter Extraction — Phase B-ja

Extracts 7 structural metrics from Japanese text corpora to calibrate
config/ja.json with empirical values.

Data sources:
    1. p1atdev/open2ch newsplus-cleaned (HuggingFace) — Casual Japanese
    2. BCCWJ 白書 (data/bccwj/hakusho/) — Formal Japanese (if available)
    3. BCCWJ Yahoo知恵袋 (data/bccwj/chiebukuro/) — Semi-formal Japanese (if available)

Metrics:
    1. sentence_length_cv (文長CV)
    2. hedge_rate (曖昧表現率)
    3. self_correction_rate (自己訂正率)
    4. morphemes_per_sentence (形態素数/文)
    5. kanji_ratio (漢字含有率 — Flesch代替)
    6. cushion_rate (クッション表現率)
    7. filler_rate (フィラー率)
"""

from __future__ import annotations

import json
import random
import statistics
from pathlib import Path
from typing import Any

import numpy as np
from scipy import stats

from analysis.metrics_ja import (
    measure_sentence_length_cv_ja,
    measure_hedge_rate_ja,
    measure_self_correction_rate_ja,
    measure_morphemes_per_sentence_ja,
    measure_kanji_ratio_ja,
    measure_cushion_rate_ja,
    measure_filler_rate_ja,
    split_sentences_ja,
)


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SAMPLE_SIZE = 10_000
SEED = 42
RESULTS_DIR = Path(__file__).parent / "results"
BCCWJ_DIR = Path(__file__).parent.parent / "data" / "bccwj"
EN_STATS_FILE = RESULTS_DIR / "full_statistics.json"

METRICS = [
    "sentence_length_cv",
    "hedge_rate",
    "self_correction_rate",
    "morphemes_per_sentence",
    "kanji_ratio",
    "cushion_rate",
    "filler_rate",
]


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------

def extract_open2ch_texts(dataset, sample_size: int = SAMPLE_SIZE) -> list[str]:
    """Extract individual post texts from open2ch dialogue dataset.

    Each sample has dialogue.content (list of posts). We flatten
    all posts and sample from the pool.
    """
    all_texts: list[str] = []
    for sample in dataset:
        dialogue = sample.get("dialogue", {})
        contents = dialogue.get("content", [])
        for text in contents:
            text = text.strip()
            if len(text) >= 10:  # skip very short posts
                all_texts.append(text)

    rng = random.Random(SEED)
    if len(all_texts) > sample_size:
        all_texts = rng.sample(all_texts, sample_size)
    return all_texts


def load_bccwj_texts(subdir: str) -> list[str]:
    """Load texts from BCCWJ directory (if available).

    Reads all .txt files in the specified subdirectory.
    Returns empty list if directory doesn't exist.
    """
    path = BCCWJ_DIR / subdir
    if not path.exists():
        return []
    texts: list[str] = []
    for fp in sorted(path.glob("*.txt")):
        content = fp.read_text(encoding="utf-8").strip()
        if content:
            texts.append(content)
    return texts


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def analyze_texts(texts: list[str]) -> dict[str, list[float]]:
    """Run all 7 Japanese metrics on a list of texts."""
    results: dict[str, list[float]] = {m: [] for m in METRICS}

    for text in texts:
        cv = measure_sentence_length_cv_ja(text)
        if cv is not None:
            results["sentence_length_cv"].append(cv)

        results["hedge_rate"].append(measure_hedge_rate_ja(text))
        results["self_correction_rate"].append(measure_self_correction_rate_ja(text))
        results["morphemes_per_sentence"].append(measure_morphemes_per_sentence_ja(text))
        results["kanji_ratio"].append(measure_kanji_ratio_ja(text))
        results["cushion_rate"].append(1.0 if measure_cushion_rate_ja(text) else 0.0)
        results["filler_rate"].append(measure_filler_rate_ja(text))

    return results


def compute_summary(results: dict[str, list[float]]) -> dict[str, dict[str, float]]:
    """Compute mean, std, median for each metric."""
    summary: dict[str, dict[str, float]] = {}
    for metric in METRICS:
        vals = results[metric]
        if not vals:
            summary[metric] = {"mean": 0.0, "std": 0.0, "median": 0.0, "n": 0}
            continue
        arr = np.array(vals)
        summary[metric] = {
            "mean": float(np.mean(arr)),
            "std": float(np.std(arr)),
            "median": float(np.median(arr)),
            "n": len(arr),
        }
    return summary


def compute_comparison(
    summaries: dict[str, dict[str, dict[str, float]]],
) -> dict[str, dict[str, Any]]:
    """Compute t-tests between corpora pairs."""
    comparison: dict[str, dict[str, Any]] = {}
    corpus_names = list(summaries.keys())
    if len(corpus_names) < 2:
        return comparison

    for metric in METRICS:
        comparison[metric] = {}
        for i, c1 in enumerate(corpus_names):
            for c2 in corpus_names[i + 1:]:
                key = f"{c1}_vs_{c2}"
                vals1 = summaries[c1].get(metric, {})
                vals2 = summaries[c2].get(metric, {})
                comparison[metric][key] = {
                    f"{c1}_mean": vals1.get("mean", 0),
                    f"{c2}_mean": vals2.get("mean", 0),
                    "diff": vals1.get("mean", 0) - vals2.get("mean", 0),
                }
    return comparison


# ---------------------------------------------------------------------------
# Cross-cultural comparison
# ---------------------------------------------------------------------------

def generate_cross_cultural_report(
    ja_summaries: dict[str, dict[str, dict[str, float]]],
) -> str:
    """Generate cross-cultural comparison with English DPO results."""
    lines = [
        "# Cross-Cultural Parameter Comparison",
        "",
        "English data: HumanLLMs/Human-Like-DPO-Dataset (n=10,884)",
        "",
    ]

    # Load English stats
    en_stats: dict[str, Any] = {}
    if EN_STATS_FILE.exists():
        en_stats = json.loads(EN_STATS_FILE.read_text(encoding="utf-8"))

    # Mapping: EN metric name → JA metric name (for comparable ones)
    comparable = {
        "sentence_length_cv": ("sentence_length_cv", "文長CV"),
        "hedge_rate": ("hedge_rate", "Hedge/曖昧表現率"),
        "self_correction_rate": ("self_correction_rate", "自己訂正率"),
        "cushion": ("cushion_rate", "クッション率"),
        "filler_rate": ("filler_rate", "フィラー率"),
    }

    # Header
    header = "| 指標 | EN Human-Like | EN Formal |"
    divider = "|------|--------------|----------|"
    for corpus_name in ja_summaries:
        header += f" JA {corpus_name} |"
        divider += "---------|"

    lines += [header, divider]

    for en_key, (ja_key, label) in comparable.items():
        en_data = en_stats.get(en_key, {})
        en_human = en_data.get("human_mean", "-")
        en_formal = en_data.get("formal_mean", "-")

        row = f"| {label} | "
        row += f"{en_human:.4f} | " if isinstance(en_human, float) else f"{en_human} | "
        row += f"{en_formal:.4f} | " if isinstance(en_formal, float) else f"{en_formal} | "

        for corpus_name, corpus_summary in ja_summaries.items():
            ja_val = corpus_summary.get(ja_key, {}).get("mean", "-")
            row += f"{ja_val:.4f} | " if isinstance(ja_val, float) else f"{ja_val} | "

        lines.append(row)

    # Non-comparable metrics (JA only)
    lines += [
        "",
        "### Japanese-only metrics",
        "",
        "| 指標 |",
    ]
    ja_only = {
        "morphemes_per_sentence": "形態素数/文",
        "kanji_ratio": "漢字含有率",
    }
    header2 = "| 指標 |"
    divider2 = "|------|"
    for corpus_name in ja_summaries:
        header2 += f" JA {corpus_name} |"
        divider2 += "---------|"
    lines[-2] = header2
    lines[-1] = divider2

    for ja_key, label in ja_only.items():
        row = f"| {label} |"
        for corpus_name, corpus_summary in ja_summaries.items():
            ja_val = corpus_summary.get(ja_key, {}).get("mean", "-")
            row += f" {ja_val:.4f} |" if isinstance(ja_val, float) else f" {ja_val} |"
        lines.append(row)

    # Analysis
    lines += [
        "",
        "---",
        "",
        "## Analysis",
        "",
        "### Universal patterns (base parameter candidates)",
        "- Metrics with similar ratios across EN and JA suggest language-agnostic defaults",
        "",
        "### Culture-specific divergence",
        "- Metrics with large EN/JA differences should be reflected in config/ja.json",
        "- Japanese cushion rate is expected to be higher (high-context culture)",
        "- Japanese kanji ratio replaces Flesch for readability assessment",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Config updater
# ---------------------------------------------------------------------------

def generate_ja_config_update(
    casual_summary: dict[str, dict[str, float]],
) -> dict[str, Any]:
    """Generate updated parameters for config/ja.json based on analysis."""
    return {
        "hedge_probability": round(casual_summary["hedge_rate"]["mean"], 4),
        "self_correction_rate": round(casual_summary["self_correction_rate"]["mean"], 4),
        "sentence_length_cv": round(casual_summary["sentence_length_cv"]["mean"], 4),
        "morphemes_per_sentence": round(casual_summary["morphemes_per_sentence"]["mean"], 2),
        "kanji_ratio_casual": round(casual_summary["kanji_ratio"]["mean"], 4),
        "filler_rate": round(casual_summary["filler_rate"]["mean"], 4),
        "cushion_rate": round(casual_summary["cushion_rate"]["mean"], 4),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    from datasets import load_dataset

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # --- open2ch ---
    print("Loading p1atdev/open2ch newsplus-cleaned...")
    ds = load_dataset("p1atdev/open2ch", "newsplus-cleaned", split="train")
    print(f"Loaded {len(ds):,} dialogue samples.")

    print(f"Extracting texts (target: {SAMPLE_SIZE:,} posts, seed={SEED})...")
    open2ch_texts = extract_open2ch_texts(ds, SAMPLE_SIZE)
    print(f"Extracted {len(open2ch_texts):,} texts for analysis.")

    print("Analyzing open2ch texts (7 metrics)...")
    open2ch_results = analyze_texts(open2ch_texts)
    open2ch_summary = compute_summary(open2ch_results)

    # --- BCCWJ (optional) ---
    ja_summaries: dict[str, dict[str, dict[str, float]]] = {}

    hakusho_texts = load_bccwj_texts("hakusho")
    if hakusho_texts:
        print(f"Analyzing BCCWJ 白書 ({len(hakusho_texts)} files)...")
        hakusho_results = analyze_texts(hakusho_texts)
        hakusho_summary = compute_summary(hakusho_results)
        ja_summaries["Formal"] = hakusho_summary
    else:
        print("BCCWJ 白書 not found (data/bccwj/hakusho/) — skipping.")

    chiebukuro_texts = load_bccwj_texts("chiebukuro")
    if chiebukuro_texts:
        print(f"Analyzing BCCWJ 知恵袋 ({len(chiebukuro_texts)} files)...")
        chiebukuro_results = analyze_texts(chiebukuro_texts)
        chiebukuro_summary = compute_summary(chiebukuro_results)
        ja_summaries["Semi"] = chiebukuro_summary
    else:
        print("BCCWJ 知恵袋 not found (data/bccwj/chiebukuro/) — skipping.")

    ja_summaries["Casual"] = open2ch_summary

    # --- Output results ---
    # Japanese statistics
    ja_stats_path = RESULTS_DIR / "ja_statistics.json"

    def _serialize(obj):
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        raise TypeError(f"Not serializable: {type(obj)}")

    ja_stats_path.write_text(
        json.dumps(ja_summaries, indent=2, default=_serialize, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"\nJapanese statistics: {ja_stats_path}")

    # Cross-cultural comparison
    report = generate_cross_cultural_report(ja_summaries)
    report_path = RESULTS_DIR / "cross_cultural_comparison.md"
    report_path.write_text(report, encoding="utf-8")
    print(f"Cross-cultural comparison: {report_path}")

    # Config update values
    config_update = generate_ja_config_update(open2ch_summary)
    config_update_path = RESULTS_DIR / "ja_recommended_params.json"
    config_update_path.write_text(
        json.dumps(config_update, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Recommended JA params: {config_update_path}")

    # --- Print summary ---
    print(f"\n{'='*60}")
    print("JAPANESE PARAMETER EXTRACTION RESULTS")
    print(f"{'='*60}")

    for corpus_name, summary in ja_summaries.items():
        print(f"\n--- {corpus_name} ---")
        for metric in METRICS:
            data = summary.get(metric, {})
            mean = data.get("mean", 0)
            std = data.get("std", 0)
            n = data.get("n", 0)
            print(f"  {metric:<30} mean={mean:.4f}  std={std:.4f}  n={n}")

    print(f"\n{'='*60}")
    print("RECOMMENDED config/ja.json UPDATE:")
    print(json.dumps(config_update, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

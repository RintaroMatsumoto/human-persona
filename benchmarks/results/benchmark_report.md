# DPO Benchmark Evaluation Report — v2

**Date:** 2026-03-25 02:46 UTC
**Model:** local (DPO rejected)
**Evaluation Mode:** Held-out (80/20 split)
**Evaluation Sample Size:** 500
**Seed:** 42
**Bootstrap Resamples:** 1000

---

## Methodology

This benchmark uses a proper **held-out evaluation** protocol:
1. The DPO dataset is split 80/20 (seed=42)
2. Reference statistics (human-like targets) are computed from the 80% **train** split
3. Pipeline is evaluated on the 20% **test** split (never seen during calibration)
4. This prevents self-referential score inflation

---

## Results

| Metric | Raw | +Pipeline | Target | Score | 95% CI | Wasserstein | Weight |
|--------|-----|-----------|--------|-------|--------|-------------|--------|
| Sentence Length CV | 0.4246 | 0.6280 | 0.6333 | 0.974 | [0.614, 0.641] | 0.0225 | 1.16 |
| Hedge Rate | 0.0187 | 0.0887 | 0.0818 | 0.892 | [0.081, 0.097] | 0.0117 | 0.87 |
| Self-Correction Rate | 0.0006 | 0.0023 | 0.0019 | 0.601 | [0.001, 0.004] | 0.0006 | 0.10 |
| Words/Sentence | 18.4440 | 13.2834 | 13.5322 | 0.948 | [13.052, 13.522] | 0.5736 | 1.45 |
| Cushion Rate | 0.0160 | 0.1560 | 0.1572 | 0.991 | [0.124, 0.186] | 0.0260 | 0.54 |
| Filler Rate | 0.0008 | 0.1577 | 0.1653 | 0.954 | [0.148, 0.167] | 0.0193 | 1.88 |

### Dual-Score Summary

| Scoring Method | Score | 95% CI | Meaning |
|----------------|-------|--------|---------|
| **Mean Alignment** | 0.945 | [0.902, 0.961] | Pipeline means match human-like targets |
| **Distribution Alignment** | 0.864 | [0.811, 0.877] | Full distributional match (Wasserstein) |

**Raw API baseline:** 0.003
**Pipeline improvement:** +0.942

---

## Distribution Tests (KS test, 4/6 pass)

Kolmogorov-Smirnov test: H0 = pipeline and human-like distributions are identical.

| Metric | KS Statistic | p-value | Result |
|--------|-------------|---------|--------|
| Sentence Length CV | 0.058 | 3.6991e-01 | PASS |
| Hedge Rate | 0.098 | 1.6379e-02 | **FAIL** |
| Self-Correction Rate | 0.010 | 1.0000e+00 | PASS |
| Words/Sentence | 0.114 | 2.9901e-03 | **FAIL** |
| Cushion Rate | 0.026 | 9.9595e-01 | PASS |
| Filler Rate | 0.082 | 6.9301e-02 | PASS |

---

## Wasserstein-Based Scores (per metric)

Score = 1.0 - W(pipeline, human) / W(formal, human).
Compares full distributions, not just means.

| Metric | W(formal,human) | W(pipe,human) | Wass Score | Mean Score | Gap |
|--------|----------------|---------------|------------|------------|-----|
| Sentence Length CV | 0.2137 | 0.0225 | 0.895 | 0.974 | +0.079 |
| Hedge Rate | 0.0611 | 0.0117 | 0.808 | 0.892 | +0.084 |
| Self-Correction Rate | 0.0013 | 0.0006 | 0.534 | 0.601 | +0.068 |
| Words/Sentence | 4.6831 | 0.5736 | 0.878 | 0.948 | +0.071 |
| Cushion Rate | 0.1660 | 0.0260 | 0.843 | 0.991 | +0.148 |
| Filler Rate | 0.1677 | 0.0193 | 0.885 | 0.954 | +0.069 |

---

## Metric Weights (Effect-Size Based)

Weights are proportional to Cohen's d between human-like and formal distributions.
Metrics that better discriminate human from AI text receive higher weight.

| Metric | Cohen's d | Weight |
|--------|-----------|--------|
| Sentence Length CV | 1.086 | 1.16 |
| Hedge Rate | 0.818 | 0.87 |
| Self-Correction Rate | 0.090 | 0.10 |
| Words/Sentence | -1.356 | 1.45 |
| Cushion Rate | 0.505 | 0.54 |
| Filler Rate | 1.755 | 1.88 |

---

## Score Interpretation

- **1.0** = Matches Human-Like distribution perfectly
- **0.0** = As far from Human-Like as Formal is (or worse)
- Score = 1.0 - |persona_mean - humanlike_mean| / |humanlike_mean - formal_mean|
- Wasserstein distance measures how far the full pipeline *distribution* is from human-like

---

## Weakest Metrics

- **Self-Correction Rate**: score=0.601, current=0.0023, target=0.0019 (overshoot)
- **Hedge Rate**: score=0.892, current=0.0887, target=0.0818 (overshoot)
- **Words/Sentence**: score=0.948, current=13.2834, target=13.5322 (undershoot)
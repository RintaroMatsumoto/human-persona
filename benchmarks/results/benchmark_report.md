# DPO Benchmark Evaluation Report

**Date:** 2026-03-24 10:38 UTC
**Model:** deepseek-chat
**Sample Size:** 500
**Seed:** 42

---

## Results

| Metric | Raw API | +Pipeline | Human-Like Target | Score (Raw) | Score (+Pipeline) |
|--------|---------|-----------|-------------------|-------------|-------------------|
| Sentence Length CV | 0.6863 | 0.6757 | 0.6340 | 1.000 | 1.000 |
| Hedge Rate | 0.0586 | 0.1307 | 0.0817 | 0.641 | 1.000 |
| Self-Correction Rate | 0.0038 | 0.1054 | 0.0430 | 0.071 | 1.000 |
| Words/Sentence | 17.6647 | 17.9906 | 13.5262 | 0.133 | 0.065 |
| Cushion Rate | 0.1940 | 0.2800 | 0.1578 | 1.000 | 1.000 |
| Filler Rate | 0.1702 | 0.3117 | 0.3340 | 0.298 | 0.904 |

**Overall Score (Raw API):** 0.516
**Overall Score (+Pipeline):** 0.846
**Pipeline Improvement:** +0.330 (+63.9%)

---

## Score Interpretation

- **1.0** = Matches Human-Like distribution perfectly
- **0.0** = Matches Formal (AI) distribution
- Score = |persona_mean - formal_mean| / |humanlike_mean - formal_mean|

## Weights

| Metric | Weight |
|--------|--------|
| Sentence Length CV | 1.0 |
| Hedge Rate | 1.5 |
| Self-Correction Rate | 1.0 |
| Words/Sentence | 1.0 |
| Cushion Rate | 1.0 |
| Filler Rate | 1.5 |

---

## Improvement Recommendations

- **Words/Sentence**: score=0.065, current=17.9906, target=13.5262
- **Filler Rate**: score=0.904, current=0.3117, target=0.3340
- **Sentence Length CV**: score=1.000, current=0.6757, target=0.6340
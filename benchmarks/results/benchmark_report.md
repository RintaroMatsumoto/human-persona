# DPO Benchmark Evaluation Report

**Date:** 2026-03-24 11:12 UTC
**Model:** local (DPO rejected)
**Sample Size:** 500
**Seed:** 42

---

## Results

| Metric | Raw API | +Pipeline | Human-Like Target | Score (Raw) | Score (+Pipeline) |
|--------|---------|-----------|-------------------|-------------|-------------------|
| Sentence Length CV | 0.4374 | 0.5317 | 0.6340 | 0.028 | 0.494 |
| Hedge Rate | 0.0175 | 0.0940 | 0.0817 | 0.003 | 1.000 |
| Self-Correction Rate | 0.0011 | 0.1032 | 0.0430 | 0.006 | 1.000 |
| Words/Sentence | 18.2546 | 14.5094 | 13.5262 | 0.009 | 0.794 |
| Cushion Rate | 0.0240 | 0.1860 | 0.1578 | 0.038 | 1.000 |
| Filler Rate | 0.0997 | 0.3812 | 0.3340 | 0.004 | 1.000 |

**Overall Score (Raw API):** 0.013
**Overall Score (+Pipeline):** 0.898
**Pipeline Improvement:** +0.885 (+6729.5%)

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

- **Sentence Length CV**: score=0.494, current=0.5317, target=0.6340
- **Words/Sentence**: score=0.794, current=14.5094, target=13.5262
- **Hedge Rate**: score=1.000, current=0.0940, target=0.0817
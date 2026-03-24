# DPO Benchmark Evaluation Report

**Date:** 2026-03-24 11:09 UTC
**Model:** local (DPO rejected)
**Sample Size:** 500
**Seed:** 42

---

## Results

| Metric | Raw API | +Pipeline | Human-Like Target | Score (Raw) | Score (+Pipeline) |
|--------|---------|-----------|-------------------|-------------|-------------------|
| Sentence Length CV | 0.4374 | 0.5326 | 0.6340 | 0.028 | 0.499 |
| Hedge Rate | 0.0175 | 0.0949 | 0.0817 | 0.003 | 1.000 |
| Self-Correction Rate | 0.0011 | 0.1129 | 0.0430 | 0.006 | 1.000 |
| Words/Sentence | 18.2546 | 14.4770 | 13.5262 | 0.009 | 0.801 |
| Cushion Rate | 0.0240 | 0.1800 | 0.1578 | 0.038 | 1.000 |
| Filler Rate | 0.0997 | 0.2211 | 0.3340 | 0.004 | 0.516 |

**Overall Score (Raw API):** 0.013
**Overall Score (+Pipeline):** 0.796
**Pipeline Improvement:** +0.783 (+5953.1%)

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

- **Sentence Length CV**: score=0.499, current=0.5326, target=0.6340
- **Filler Rate**: score=0.516, current=0.2211, target=0.3340
- **Words/Sentence**: score=0.801, current=14.4770, target=13.5262